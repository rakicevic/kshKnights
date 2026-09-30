"""EuroLeague box scores and schedule from the official public API (same data as
euroleaguebasketball.net player pages), with an incremental on-disk cache."""
from __future__ import annotations

import logging
import time
from pathlib import Path

import numpy as np
import pandas as pd

log = logging.getLogger(__name__)

BOX_COLS = [
    "Season", "Gamecode", "Home", "Player_ID", "IsStarter", "IsPlaying", "Team", "Player",
    "Minutes", "Points", "FieldGoalsMade2", "FieldGoalsAttempted2", "FieldGoalsMade3",
    "FieldGoalsAttempted3", "FreeThrowsMade", "FreeThrowsAttempted", "OffensiveRebounds",
    "DefensiveRebounds", "TotalRebounds", "Assistances", "Steals", "Turnovers", "BlocksFavour",
    "BlocksAgainst", "FoulsCommited", "FoulsReceived", "Valuation", "Plusminus",
]


def _first_col(df: pd.DataFrame, candidates: list[str]) -> str | None:
    for c in candidates:
        if c in df.columns:
            return c
    return None


class StatsSource:
    def __init__(self, competition: str = "E", cache_dir: str | Path = "data/cache",
                 pause: float = 0.4, max_fetch_seconds: float = 1500):
        self.competition = competition
        self.max_fetch_seconds = max_fetch_seconds
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.pause = pause

    # ---------- raw API ----------
    def _played_games(self, season: int) -> pd.DataFrame:
        from euroleague_api.EuroLeagueData import EuroLeagueData
        df = EuroLeagueData(self.competition).get_gamecodes_season(season)
        # The wrapper's `played` flag is unreliable (string -> bool cast), so require a score.
        scored = (pd.to_numeric(df.get("homescore"), errors="coerce").fillna(0)
                  + pd.to_numeric(df.get("awayscore"), errors="coerce").fillna(0)) > 0
        df = df[scored]
        date_col = _first_col(df, ["date", "Date"])
        out = pd.DataFrame({
            "Gamecode": df["gameCode"].astype(int),
            "Round": df["Round"].astype(int),
            "Date": pd.to_datetime(df[date_col], errors="coerce", format="mixed") if date_col else pd.NaT,
        })
        return out.drop_duplicates("Gamecode")

    def _boxscore(self, season: int, gamecode: int) -> pd.DataFrame:
        from euroleague_api.boxscore_data import BoxScoreData
        return BoxScoreData(self.competition).get_players_boxscore_stats(season, gamecode)

    def schedule(self, season: int) -> pd.DataFrame:
        """All games of the season (played and upcoming): Date, Round, HomeCode, AwayCode."""
        from euroleague_api.schedule import Schedule
        df = Schedule(self.competition).get_schedule(season)
        date_col = _first_col(df, ["date", "Date"])
        home_col = _first_col(df, ["homecode", "HomeCode", "homeCode"])
        away_col = _first_col(df, ["awaycode", "AwayCode", "awayCode"])
        if not (date_col and home_col and away_col):
            raise RuntimeError(f"Unexpected schedule columns: {list(df.columns)}")
        out = pd.DataFrame({
            "Date": pd.to_datetime(df[date_col], errors="coerce", format="mixed"),
            "Round": pd.to_numeric(df["gameday"], errors="coerce"),
            "HomeCode": df[home_col].astype(str).str.strip(),
            "AwayCode": df[away_col].astype(str).str.strip(),
        })
        return out.dropna(subset=["Date"]).reset_index(drop=True)

    # ---------- cached box scores ----------
    def boxscores(self, season: int) -> pd.DataFrame:
        path = self.cache_dir / f"boxscores_{self.competition}{season}.csv.gz"
        cached = pd.read_csv(path) if path.exists() else pd.DataFrame(columns=BOX_COLS + ["Round", "Date"])
        have = set(cached["Gamecode"].dropna().astype(int)) if len(cached) else set()

        try:
            games = self._played_games(season)
        except Exception as exc:  # network/API failure: fall back to cache
            log.error("Could not list games for season %s: %s", season, exc)
            return self._normalize(cached)

        missing = games[~games["Gamecode"].isin(have)]
        total = len(missing)
        log.info("Season %s: %d games played, %d cached, %d to download", season, len(games), len(have), total)
        new_parts, failed, t0 = [], 0, time.time()

        def flush():
            nonlocal cached, new_parts
            if new_parts:
                cached = pd.concat([cached] + new_parts, ignore_index=True)
                cached.to_csv(path, index=False, compression="gzip")
                new_parts = []

        for i, (_, g) in enumerate(missing.iterrows(), 1):
            if time.time() - t0 > self.max_fetch_seconds:
                log.warning("Season %s: time budget reached after %d/%d games; rest next run", season, i - 1, total)
                break
            try:
                bx = self._boxscore(season, int(g["Gamecode"]))
                bx["Round"] = g["Round"]
                bx["Date"] = g["Date"]
                new_parts.append(bx[[c for c in BOX_COLS if c in bx.columns] + ["Round", "Date"]])
            except Exception as exc:
                failed += 1
                log.warning("Box score %s/%s failed: %s", season, g["Gamecode"], exc)
                if failed >= 10 and failed == i:
                    log.error("Season %s: first %d requests all failed; API unreachable, using cache", season, failed)
                    break
            if i % 10 == 0 or i == total:
                log.info("Season %s: %d/%d games (%.0fs elapsed)", season, i, total, time.time() - t0)
            if i % 25 == 0:
                flush()  # keep progress even if the job is killed
            time.sleep(self.pause)
        flush()
        return self._normalize(cached)

    @staticmethod
    def _normalize(df: pd.DataFrame) -> pd.DataFrame:
        if df.empty:
            return df
        df = df.copy()
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce", format="mixed")
        df["Player"] = df["Player"].astype(str).str.strip()
        df["Team"] = df["Team"].astype(str).str.strip()
        return df


# ---------- derived tables ----------
def _minutes(v) -> float:
    if isinstance(v, (int, float)) and not pd.isna(v):
        return float(v)
    s = str(v)
    if ":" in s:
        m, sec = s.split(":", 1)
        try:
            return int(m) + int(sec) / 60
        except ValueError:
            return 0.0
    return 0.0


def team_games(box: pd.DataFrame, rules: dict) -> pd.DataFrame:
    """One row per team per game: points, opponent, margin, win, coach points."""
    tot = box[box["Player"] == "Total"][["Season", "Gamecode", "Round", "Date", "Team", "Home", "Points"]]
    tot = tot.drop_duplicates(["Season", "Gamecode", "Team"])
    opp = tot[["Season", "Gamecode", "Team", "Points"]].rename(columns={"Team": "Opp", "Points": "OppPoints"})
    tg = tot.merge(opp, on=["Season", "Gamecode"])
    tg = tg[tg["Team"] != tg["Opp"]].copy()
    tg["Margin"] = tg["Points"].astype(float) - tg["OppPoints"].astype(float)
    tg["Win"] = (tg["Margin"] > 0).astype(int)
    tg["CoachPts"] = tg["Margin"].apply(lambda m: coach_points_for_margin(m, rules))
    return tg.reset_index(drop=True)


def coach_points_for_margin(m: float, rules: dict) -> float:
    cp = rules["coach_points"]
    a = abs(m)
    if m > 0:
        return cp["win_1_10"] if a <= 10 else cp["win_11_20"] if a <= 20 else cp["win_20_plus"]
    return cp["loss_1_10"] if a <= 10 else cp["loss_11_20"] if a <= 20 else cp["loss_20_plus"]


def player_logs(box: pd.DataFrame, tg: pd.DataFrame, rules: dict) -> pd.DataFrame:
    """One row per player per game he was listed for. FP = PIR x (1 + win bonus if team won).
    DNP rows are kept with FP 0 because availability risk is part of the projection."""
    p = box[~box["Player"].isin(["Team", "Total"])].copy()
    p = p[p["Player_ID"].notna()]
    p["Player_ID"] = p["Player_ID"].astype(str).str.strip()
    p["Min"] = p["Minutes"].apply(_minutes)
    p["PIR"] = pd.to_numeric(p["Valuation"], errors="coerce").fillna(0.0)
    p = p.merge(tg[["Season", "Gamecode", "Team", "Opp", "Win", "Margin"]],
                on=["Season", "Gamecode", "Team"], how="left")
    p["Win"] = p["Win"].fillna(0)
    p["FP"] = np.where(p["Win"] == 1, p["PIR"] * (1 + rules["win_bonus"]), p["PIR"])
    p["Played"] = (p["Min"] > 0).astype(int)
    keep = ["Season", "Gamecode", "Round", "Date", "Home", "Player_ID", "Player", "Team", "Opp",
            "Min", "Played", "PIR", "FP", "Win", "Margin", "Points", "TotalRebounds", "Assistances"]
    return p[[c for c in keep if c in p.columns]].sort_values(["Player_ID", "Date", "Gamecode"]).reset_index(drop=True)
