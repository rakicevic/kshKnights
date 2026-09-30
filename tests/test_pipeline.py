"""Offline end-to-end test: synthetic box scores shaped like the EuroLeague API, real fantasy export.
Run: python -m pytest -q  (no network needed)."""
from __future__ import annotations

import shutil
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

from kshknights import fantasy as fz
from kshknights.main import run

ROOT = Path(__file__).resolve().parent.parent
API_CODE = {"PAO": "PAN", "RMB": "MAD", "FBT": "ULK", "EFS": "IST", "KBA": "BAS", "CZV": "RED",
            "PBB": "PRS", "VBC": "PAM", "BAY": "MUN", "HTA": "HTA", "MTA": "TEL", "BJK": "BES"}


class FakeSource:
    def __init__(self, fan: pd.DataFrame, rng: np.random.Generator):
        self.fan = fan[fan["pos"] != "HC"].copy()
        self.rng = rng
        self.fan["api_team"] = self.fan["team"].map(lambda t: API_CODE.get(t, t))
        self.fan["pid"] = [f"P{int(k):06d}" if k.isdigit() else f"PX{i:05d}" for i, k in enumerate(self.fan["key"])]
        self.fan["api_name"] = self.fan["last"].str.upper() + ", " + self.fan["first"].str.upper()
        self.teams = sorted(self.fan["api_team"].unique())
        self.skill = dict(zip(self.fan["pid"], self.fan["price"] * 1.1 + rng.normal(0, 2, len(self.fan))))
        self.strength = {t: rng.normal(0, 5) for t in self.teams}

    def _pairs(self, rnd):
        t = list(self.teams)
        self.rng.shuffle(t)
        return list(zip(t[::2], t[1::2]))

    def boxscores(self, season: int) -> pd.DataFrame:
        rounds = 34 if season == 2025 else 2
        start = pd.Timestamp(f"{season}-10-01")
        rows, gc = [], 0
        for rnd in range(1, rounds + 1):
            date = start + pd.Timedelta(days=7 * (rnd - 1) + 1)
            for home, away in self._pairs(rnd):
                gc += 1
                for team, is_home in ((home, 1), (away, 0)):
                    pts_total = 0
                    for _, p in self.fan[self.fan["api_team"] == team].iterrows():
                        dnp = self.rng.random() < 0.08
                        val = 0 if dnp else self.rng.normal(self.skill[p["pid"]], 6)
                        pts = 0 if dnp else max(0, int(val * 0.8))
                        pts_total += pts
                        rows.append({"Season": season, "Gamecode": gc, "Home": is_home, "Player_ID": p["pid"],
                                     "IsStarter": 0, "IsPlaying": int(not dnp), "Team": team,
                                     "Player": p["api_name"], "Minutes": "DNP" if dnp else f"{self.rng.integers(8, 34)}:12",
                                     "Points": pts, "Valuation": round(val), "Round": rnd, "Date": date})
                    pts_total += int(self.strength[team] + (3 if is_home else 0))
                    rows.append({"Season": season, "Gamecode": gc, "Home": is_home, "Player_ID": None,
                                 "Team": team, "Player": "Team", "Points": 0, "Round": rnd, "Date": date})
                    rows.append({"Season": season, "Gamecode": gc, "Home": is_home, "Player_ID": None,
                                 "Team": team, "Player": "Total", "Points": max(pts_total, 50), "Round": rnd, "Date": date})
        return pd.DataFrame(rows)

    def schedule(self, season: int) -> pd.DataFrame:
        d = pd.Timestamp("2026-10-07")
        pairs = self._pairs(3)
        return pd.DataFrame({"Date": [d] * len(pairs), "Round": 3,
                             "HomeCode": [a for a, _ in pairs], "AwayCode": [b for _, b in pairs]})


def _setup(tmp_path: Path, team: dict) -> Path:
    for sub in ("config", "data/fantasy"):
        (tmp_path / sub).mkdir(parents=True, exist_ok=True)
    shutil.copy(ROOT / "config/settings.yaml", tmp_path / "config/settings.yaml")
    shutil.copy(ROOT / "config/overrides.yaml", tmp_path / "config/overrides.yaml")
    shutil.copy(ROOT / "data/fantasy/players_stats.xlsx", tmp_path / "data/fantasy/players_stats.xlsx")
    cfg = yaml.safe_load((tmp_path / "config/settings.yaml").read_text())
    cfg["ai_news"]["enabled"] = False
    (tmp_path / "config/settings.yaml").write_text(yaml.safe_dump(cfg))
    (tmp_path / "config/my_team.yaml").write_text(yaml.safe_dump(team))
    (tmp_path / "data/cache").mkdir(parents=True, exist_ok=True)
    return tmp_path


def _check_roster(tmp_path: Path, budget: float):
    fan, _ = fz.load_fantasy(tmp_path / "data/fantasy/players_stats.xlsx")
    proj = pd.read_csv(tmp_path / "reports/2026-10-05_projections.csv", dtype={"key": str})
    md = (tmp_path / "reports/2026-10-05.md").read_text()
    assert "Recommended roster" in md and "Top 8 core" in md
    return fan, proj, md


def test_scratch_build(tmp_path):
    root = _setup(tmp_path, {"players": [], "coach": "", "credits_in_bank": 0, "trades_available": 4})
    fan, _ = fz.load_fantasy(root / "data/fantasy/players_stats.xlsx")
    run(pd.Timestamp("2026-10-05"), FakeSource(fan, np.random.default_rng(1)), root)
    _, proj, md = _check_roster(root, 100)
    assert "Budget 100.0" in md
    _assert_lineup(root)
    assert proj["Player_ID"].notna().sum() > 300  # matching worked
    assert "unmatched" not in set(proj["flag"].fillna(""))


def test_trade_limit(tmp_path):
    fan, _ = fz.load_fantasy(ROOT / "data/fantasy/players_stats.xlsx")
    cheap = fan[fan["pos"] != "HC"].sort_values("price")
    squad = (list(cheap[cheap.pos == "G"].key[:3]) + list(cheap[cheap.pos == "F"].key[:5])
             + list(cheap[cheap.pos == "C"].key[:2]))
    team = {"players": squad, "coach": "KBA", "credits_in_bank": 50.0, "trades_available": 4}
    root = _setup(tmp_path, team)
    run(pd.Timestamp("2026-10-05"), FakeSource(fan, np.random.default_rng(2)), root)
    md = (root / "reports/2026-10-05.md").read_text()
    sells = md.split("| SELL |")[1].split("\n\n")[0].count("\n") - 1 if "| SELL |" in md else 0
    assert sells <= 4
    assert "Projected gain from transfers" in md


def _assert_lineup(root: Path):
    md = (root / "reports/2026-10-05.md").read_text()
    table = md.split("## Recommended roster")[1].split("## Top 8 core")[0]
    rows = [l.split("|")[1:-1] for l in table.strip().splitlines()[2:]]
    roles = [(r[0].strip(), r[1].strip()) for r in rows]
    assert len(roles) == 11
    bench = sorted(p for role, p in roles if role == "Bench")
    assert bench == ["C", "F", "F", "G"]
    starters = [p for role, p in roles if role in ("Starter", "Captain")]
    form = f"{starters.count('G')}-{starters.count('F')}-{starters.count('C')}"
    assert form in {"1-2-2", "1-3-1", "2-1-2", "2-2-1", "3-1-1"}
    assert sum(role == "6th man" for role, _ in roles) == 1
    assert sum(role == "Captain" for role, _ in roles) == 1
    assert sum(role == "Coach" for role, _ in roles) == 1
    assert f"**{form}**" in md
