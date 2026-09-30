"""Match fantasy export players to EuroLeague API Player_IDs and fantasy club codes to API codes."""
from __future__ import annotations

import unicodedata

import pandas as pd
from rapidfuzz import fuzz

MIN_SCORE = 86


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode()
    return " ".join(s.lower().replace("-", " ").replace(".", " ").replace("'", "").split())


def api_name_to_first_last(api_name: str) -> str:
    """'VEZENKOV, ALEKSANDAR' -> 'aleksandar vezenkov'."""
    if "," in api_name:
        last, first = api_name.split(",", 1)
        return norm(f"{first} {last}")
    return norm(api_name)


def players_index(logs: pd.DataFrame, season: int) -> pd.DataFrame:
    """Latest known team and name per Player_ID; current season preferred."""
    idx = logs.sort_values(["Season", "Date"]).groupby("Player_ID").agg(
        Player=("Player", "last"), Team=("Team", "last"), LastSeason=("Season", "max")).reset_index()
    idx["norm"] = idx["Player"].map(api_name_to_first_last)
    idx["current"] = idx["LastSeason"] == season
    return idx


def _best(fp_name: str, cands: pd.DataFrame) -> tuple[str | None, float]:
    if cands.empty:
        return None, 0.0
    scores = cands["norm"].map(lambda n: max(fuzz.token_sort_ratio(fp_name, n),
                                               fuzz.token_set_ratio(fp_name, n) - 5))
    i = scores.idxmax()
    return cands.loc[i, "Player_ID"], float(scores.loc[i])


def match_players(fantasy: pd.DataFrame, idx: pd.DataFrame, overrides: dict) -> tuple[pd.DataFrame, dict]:
    """Adds Player_ID + match_score to fantasy players. Returns (fantasy, team_map)."""
    f = fantasy.copy()
    f["norm"] = f["name"].map(norm)
    ids_available = set(idx["Player_ID"])
    pov = {str(k): str(v) for k, v in (overrides.get("players") or {}).items()}

    # Pass 1: numeric fantasy ID often equals the API person code (e.g. 3469 -> P003469);
    # accepted only if the names also agree. Otherwise fuzzy name match, current season first.
    pid, score = [], []
    for _, r in f.iterrows():
        if r["pos"] == "HC":
            pid.append(None); score.append(0.0); continue
        if r["key"] in pov:
            pid.append(pov[r["key"]]); score.append(100.0); continue
        hit = None
        if r["key"].isdigit():
            for cand in (f"P{int(r['key']):06d}", r["key"], f"{int(r['key']):06d}"):
                if cand in ids_available:
                    n2 = idx.loc[idx["Player_ID"] == cand, "norm"].iloc[0]
                    if fuzz.token_sort_ratio(r["norm"], n2) >= 70:
                        hit = (cand, 100.0)
                    break
        if hit is None:
            b, s = _best(r["norm"], idx[idx["current"]])
            if s < MIN_SCORE:
                b2, s2 = _best(r["norm"], idx)
                if s2 > s:
                    b, s = b2, s2
            hit = (b if s >= MIN_SCORE else None, s)
        pid.append(hit[0]); score.append(hit[1])
    f["Player_ID"] = pid
    f["match_score"] = score

    # Team map: majority vote of matched players' current API team, then manual overrides.
    m = f.dropna(subset=["Player_ID"]).merge(idx[["Player_ID", "Team", "current"]], on="Player_ID")
    m = m[m["current"]]
    team_map = (m.groupby("team")["Team"].agg(lambda s: s.value_counts().idxmax()).to_dict()
                if not m.empty else {})
    team_map.update({str(k): str(v) for k, v in (overrides.get("teams") or {}).items()})
    f["api_team"] = f["team"].map(team_map)
    return f.drop(columns=["norm"]), team_map
