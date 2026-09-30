"""Weekly pipeline: fetch -> match -> model -> news -> optimize -> report."""
from __future__ import annotations

import argparse
import logging
import os
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

from . import fantasy as fz
from . import matching, model, news, optimizer, report
from .stats import StatsSource, player_logs, team_games

log = logging.getLogger("kshknights")
ROOT = Path(__file__).resolve().parent.parent


def _yaml(p: Path) -> dict:
    return (yaml.safe_load(p.read_text()) or {}) if p.exists() else {}


def _norm_keys(v) -> set[str]:
    return {str(int(x)) if isinstance(x, (int, float)) else str(x).strip() for x in (v or [])}


def run(run_date: pd.Timestamp, source: StatsSource | None = None, root: Path = ROOT,
        summary: bool = False) -> Path:
    cfg = _yaml(root / "config/settings.yaml")
    team_cfg = _yaml(root / "config/my_team.yaml")
    overrides = _yaml(root / "config/overrides.yaml")
    rules, mcfg = cfg["rules"], cfg["model"]
    season, prior = int(cfg["season"]), int(cfg["prior_season"])
    warnings: list[str] = []
    ds = run_date.strftime("%Y-%m-%d")

    # ---- fantasy export + season price history
    fpath = root / cfg["fantasy_file"]
    fan, matchdays = fz.load_fantasy(fpath)
    fh = fz.file_hash(fpath)
    hist, is_new = fz.update_price_history(fan, matchdays, fh, root / "data/history/prices.csv", ds)
    stale = (not is_new) and hist["date"].nunique() > 1
    trend = fz.price_trend(hist)
    fan["season_price_change"] = fan["key"].map(trend)

    # ---- box scores
    src = source or StatsSource(cfg["competition"], root / "data/cache", cfg.get("request_pause_seconds", 0.4),
                                cfg.get("max_fetch_seconds", 1500))
    box = pd.concat([src.boxscores(prior), src.boxscores(season)], ignore_index=True)
    if box.empty:
        raise SystemExit("No box score data available (API unreachable and cache empty).")
    box = box[pd.to_datetime(box["Date"]) <= run_date + pd.Timedelta(hours=23, minutes=59)]  # no look-ahead
    tg = team_games(box, rules)
    logs = player_logs(box, tg, rules)
    tg_ctx, team_now = model.team_context(tg, logs, season)
    feats = model.build_features(logs, tg_ctx, mcfg["last_n_weights"])
    proj_engine = model.Projector(mcfg, rules)
    proj_engine.fit(feats)

    # ---- matching
    idx = matching.players_index(logs, season)
    idx.to_csv(root / "data/cache/players_index.csv", index=False)
    fan, team_map = matching.match_players(fan, idx, overrides)
    missing_teams = sorted(set(fan["team"]) - set(team_map))
    if missing_teams:
        warnings.append(f"No API club code for fantasy clubs {missing_teams}; set them in config/overrides.yaml")

    # ---- upcoming games
    try:
        sched = src.schedule(season)
        games = model.upcoming_games(sched, run_date, mcfg["window_days"])
    except Exception as exc:
        games = pd.DataFrame(columns=["Date", "Round", "Team", "Opp", "home"])
        warnings.append(f"Schedule unavailable ({exc}); projections cover 0 games")
    if games.empty:
        warnings.append("No games found in the window; check season in config/settings.yaml")

    # ---- player projections
    state = model.player_state(logs, season, mcfg["last_n_weights"])
    cur_team = fan.dropna(subset=["Player_ID", "api_team"]).set_index("Player_ID")["api_team"]
    state["Team"] = state["Player_ID"].map(cur_team).fillna(state["Team"])  # respect transfers
    pp = _price_prior(fan, state)
    pw = model.project_window(state, games, team_now, proj_engine, mcfg, pp)

    c = fan.merge(pw, on="Player_ID", how="left").merge(
        state[["Player_ID", "l1", "wl4", "sm", "min4", "dnp_streak"]], on="Player_ID", how="left")
    c = c.rename(columns={"l1": "last_fp", "sm": "season_avg"})
    c["l4_avg"] = c["wl4"]
    team_games_n = games.groupby("Team").size()
    c["flag"] = ""
    # unmatched players: fall back to fantasy average x games
    um = c["pos"].ne("HC") & c["Player_ID"].isna()
    c.loc[um, "games"] = c.loc[um, "api_team"].map(team_games_n).fillna(0)
    c.loc[um, "proj_window"] = c.loc[um, "fpt_avg"].fillna(0) * c.loc[um, "games"]
    c.loc[um, "flag"] = "unmatched"
    # coaches
    coach = model.project_coaches(games, team_now, mcfg, rules) if not games.empty else pd.DataFrame(
        columns=["api_team", "games", "proj_window", "p_win_avg"])
    hc = c["pos"].eq("HC")
    cmap = coach.set_index("api_team") if not coach.empty else None
    if cmap is not None:
        c.loc[hc, "proj_window"] = c.loc[hc, "api_team"].map(cmap["proj_window"])
        c.loc[hc, "games"] = c.loc[hc, "api_team"].map(cmap["games"])
        c.loc[hc, "opps"] = c.loc[hc, "api_team"].map(
            games.assign(o=np.where(games["home"] == 1, "vs ", "@ ") + games["Opp"]).groupby("Team")["o"].agg(", ".join))
    c["games"] = c["games"].fillna(0)
    c["proj_window"] = c["proj_window"].fillna(0.0)
    c.loc[c["dnp_streak"].fillna(0) >= 1, "flag"] = c["flag"] + " DNP last " + c["dnp_streak"].fillna(0).astype(int).astype(str)
    c.loc[c["active"] == 0, ["proj_window"]] = 0.0

    # ---- AI news check (optional)
    owned = _norm_keys(team_cfg.get("players"))
    if team_cfg.get("coach"):
        owned.add(f"HC-{str(team_cfg['coach']).strip()}")
    owned &= set(c["key"])
    lock, ban = _norm_keys(team_cfg.get("lock")), _norm_keys(team_cfg.get("ban"))
    ncfg = cfg.get("ai_news", {})
    pl = c[c["pos"] != "HC"]
    check = pd.concat([pl.nlargest(int(ncfg.get("candidates", 30)), "proj_window"), pl[pl["key"].isin(owned)]]).drop_duplicates("key")
    statuses, err = news.check_availability(
        [{"key": k, "name": n, "team": t} for k, n, t in zip(check["key"], check["name"], check["team"])], ncfg, ds)
    news_status = err or (f"{len(statuses)} players checked" if statuses else "disabled")
    c["news_source"] = ""
    for k, s in statuses.items():
        i = c.index[c["key"] == k]
        if s["status"] in news.DISCOUNT:
            c.loc[i, "proj_window"] *= news.DISCOUNT[s["status"]]
            c.loc[i, "flag"] = c.loc[i, "flag"] + f" {s['status'].upper()}: {s['note']}"
            c.loc[i, "news_source"] = s["source"]
    c["value"] = c["proj_window"] / c["price"]
    c["flag"] = c["flag"].str.strip()

    # ---- optimize
    unlimited = ds in {str(d) for d in rules.get("unlimited_trade_windows", [])} or \
        str(team_cfg.get("trades_available", "")).lower() == "unlimited"
    max_trades = None if unlimited or not owned else int(team_cfg.get("trades_available", rules["trades_per_round"]))
    bank = float(team_cfg.get("credits_in_bank", 0) or 0)
    budget = bank + float(c.loc[c["key"].isin(owned), "price"].sum()) if owned else float(rules["budget_start"])
    cands = c[["key", "pos", "team", "price", "proj_window"]].rename(columns={"proj_window": "proj"})
    res = optimizer.optimize(cands, rules, budget, owned, max_trades, lock, ban)
    hold_total = None
    if owned and res["status"] == "ok":
        hold = optimizer.optimize(cands, rules, budget, owned, 0, lock, ban)
        hold_total = hold["total"] if hold["status"] == "ok" else None
        expected_n = 5 + int(rules.get("sixth_man", 1)) + sum(rules["bench"].values()) + int(rules.get("coach", 1))
        if len(owned) != expected_n:
            warnings.append(f"my_team.yaml lists {len(owned)} known players/coach; expected {expected_n}. Check IDs.")
    if res["status"] == "ok":
        res["roster"] = res["roster"].merge(c.drop(columns=["pos", "team", "price"]), on="key", how="left")

    # ---- report
    cur = box[box["Season"] == season]
    ctx = {
        "run_date": ds, "result": res, "cands": c, "owned": owned, "hold_total": hold_total,
        "last_game_date": str(pd.to_datetime(box["Date"]).max().date()),
        "games_cur": int(cur["Gamecode"].nunique()), "games_prior": int(box[box["Season"] == prior]["Gamecode"].nunique()),
        "matchdays": matchdays, "file_hash": fh, "stale": stale,
        "window": f"{(run_date + pd.Timedelta(days=1)).date()} → {(run_date + pd.Timedelta(days=mcfg['window_days'])).date()}",
        "n_games_window": int(len(games) // 2), "metrics": proj_engine.metrics, "news_status": news_status,
        "warnings": warnings,
        "unmatched": sorted(c.loc[um, "name"] + " (" + c.loc[um, "team"] + ")"),
    }
    md = report.build(ctx)
    rdir = root / "reports"
    rdir.mkdir(exist_ok=True)
    (rdir / f"{ds}.md").write_text(md)
    (rdir / "latest.md").write_text(md)
    c.sort_values("proj_window", ascending=False).to_csv(rdir / f"{ds}_projections.csv", index=False)
    if summary and os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a") as fh_:
            fh_.write(md)
    return rdir / f"{ds}.md"


def _price_prior(fan: pd.DataFrame, state: pd.DataFrame) -> pd.Series:
    """Fallback prior for players without last-season data: linear fit of prior FP on price."""
    m = fan.dropna(subset=["Player_ID"]).merge(state[["Player_ID", "prior"]], on="Player_ID")
    m = m.dropna(subset=["prior"])
    if len(m) < 20:
        a, b = 1.0, 0.0
    else:
        a, b = np.polyfit(m["price"], m["prior"], 1)
    s = fan.dropna(subset=["Player_ID"]).set_index("Player_ID")["price"] * a + b
    return s[~s.index.duplicated()]


def cli() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", help="run date YYYY-MM-DD (default: today UTC)")
    a = ap.parse_args()
    d = pd.Timestamp(a.date) if a.date else pd.Timestamp.utcnow().tz_localize(None).normalize()
    path = run(d, summary=True)
    print(f"REPORT={path}")


if __name__ == "__main__":
    cli()
