"""Markdown report."""
from __future__ import annotations

import pandas as pd


def _f(v, nd=1):
    return "–" if v is None or (isinstance(v, float) and pd.isna(v)) else f"{v:.{nd}f}"


def _table(df: pd.DataFrame, cols: list[tuple[str, str, int | None]]) -> str:
    head = "| " + " | ".join(h for _, h, _ in cols) + " |"
    sep = "|" + "|".join("---" for _ in cols) + "|"
    lines = [head, sep]
    for _, r in df.iterrows():
        cells = []
        for c, _, nd in cols:
            v = r.get(c)
            cells.append(_f(v, nd) if nd is not None else ("–" if pd.isna(v) else str(v)))
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


PLAYER_COLS = [("role", "Role", None), ("pos", "Pos", None), ("name", "Player", None),
               ("team", "Club", None), ("price", "Price", 1), ("proj_window", "Proj", 1),
               ("games", "G", 0), ("opps", "Opponents", None), ("last_fp", "Last", 1),
               ("l4_avg", "L4 avg", 1), ("season_avg", "Season", 1), ("min4", "Min L4", 1),
               ("plus", "Δ price", 1), ("flag", "Flags", None)]


def build(ctx: dict) -> str:
    out = []
    r = ctx["result"]
    out.append(f"# KshKnights weekly report — {ctx['run_date']}\n")
    out.append(f"- Data: box scores through {ctx['last_game_date']} "
               f"({ctx['games_cur']} games this season, {ctx['games_prior']} prior season)")
    out.append(f"- Fantasy export: matchdays {ctx['matchdays']} · file {ctx['file_hash']}"
               + (" · **STALE: same file as last run, prices may be outdated**" if ctx["stale"] else ""))
    out.append(f"- Window: {ctx['window']} · {ctx['n_games_window']} games")
    out.append(f"- Model: `{ctx['metrics'].get('chosen', 'heuristic')}` · validation MAE per game: "
               + ", ".join(f"{k} {v:.2f}" for k, v in ctx["metrics"].get("mae", {}).items())
               + (f" ({ctx['metrics']['note']})" if "note" in ctx["metrics"] else ""))
    out.append(f"- News check: {ctx['news_status']}")
    for w in ctx["warnings"]:
        out.append(f"- ⚠ {w}")
    out.append("")

    if r["status"] != "ok":
        out.append(f"**Optimizer failed:** {r.get('message')}")
        return "\n".join(out)

    roster = r["roster"]
    out.append("## Transfers")
    if ctx["owned"]:
        if r["sell"]:
            out.append(_table(ctx["cands"][ctx["cands"]["key"].isin(r["sell"])],
                              [("pos", "Pos", None), ("name", "SELL", None), ("team", "Club", None),
                               ("price", "Price", 1), ("proj_window", "Proj", 1)]))
            out.append("")
            out.append(_table(ctx["cands"][ctx["cands"]["key"].isin(r["buy"])],
                              [("pos", "Pos", None), ("name", "BUY", None), ("team", "Club", None),
                               ("price", "Price", 1), ("proj_window", "Proj", 1)]))
        else:
            out.append("No transfers: current squad is already optimal under the trade limit.")
        if ctx.get("hold_total") is not None:
            out.append(f"\nProjected gain from transfers: **{r['total'] - ctx['hold_total']:+.1f}** "
                       f"({ctx['hold_total']:.1f} → {r['total']:.1f})")
    else:
        out.append("No squad in `config/my_team.yaml`: optimal squad built from scratch.")
    out.append(f"\nBudget {r['budget']:.1f} · cost {r['cost']:.1f} · left {r['budget'] - r['cost']:.1f} · "
               f"expected lineup score **{r['total']:.1f}** (captain x2, bench 50%)")
    out.append(f"\nFormation (G-F-C): **{r['formation']}** · main 6 = starting five + 6th man · bench G-F-F-C\n")

    out.append("## Recommended roster")
    out.append(_table(roster, PLAYER_COLS))
    out.append("")
    top8 = roster[roster["pos"] != "HC"].nlargest(8, "proj_window")
    out.append("## Top 8 core")
    out.append(", ".join(f"{n} ({t}, {p:.1f})" for n, t, p in zip(top8["name"], top8["team"], top8["proj_window"])))
    out.append("")

    c = ctx["cands"]
    alt = c[~c["key"].isin(roster["key"]) & (c["games"] > 0)]
    out.append("## Best alternatives by position")
    for pos in ["G", "F", "C", "HC"]:
        a = alt[alt["pos"] == pos].nlargest(5, "proj_window")
        out.append(f"\n**{pos}**\n")
        out.append(_table(a, [("name", "Player", None), ("team", "Club", None), ("price", "Price", 1),
                              ("proj_window", "Proj", 1), ("value", "Proj/credit", 2),
                              ("l4_avg", "L4 avg", 1), ("flag", "Flags", None)]))
    out.append("\n## Value picks (projection per credit, ≤ 7.0 credits)")
    v = alt[(alt["price"] <= 7.0) & (alt["pos"] != "HC")].nlargest(8, "value")
    out.append(_table(v, [("pos", "Pos", None), ("name", "Player", None), ("team", "Club", None),
                          ("price", "Price", 1), ("proj_window", "Proj", 1), ("value", "Proj/credit", 2)]))

    flagged = c[c["flag"].fillna("") != ""].nlargest(15, "price")
    if not flagged.empty:
        out.append("\n## Availability / data flags (most expensive first)")
        out.append(_table(flagged, [("name", "Player", None), ("team", "Club", None), ("price", "Price", 1),
                                    ("flag", "Flag", None), ("news_source", "Source", None)]))
    if ctx["unmatched"]:
        out.append("\n## Unmatched fantasy players (projection = fantasy season average)")
        out.append(", ".join(ctx["unmatched"][:60]) + (" …" if len(ctx["unmatched"]) > 60 else ""))
        out.append("\nFix persistent mismatches in `config/overrides.yaml`.")
    out.append("\n---\nProj = projected fantasy points over the window (sum over games), after "
               "volatility penalty and availability discount. Last/L4/Season are fantasy points "
               "computed from box scores (PIR, +10% on wins).")
    return "\n".join(out)
