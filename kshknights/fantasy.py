"""Load the EuroLeague Fantasy Challenge export (xlsx) and keep a season price history."""
from __future__ import annotations

import hashlib
import re
from pathlib import Path

import pandas as pd

POS_MAP = {"Guard": "G", "Forward": "F", "Center": "C", "Head Coach": "HC"}


def _key(row) -> str:
    if row["pos"] == "HC":
        return f"HC-{row['team']}"
    raw = row["raw_id"]
    try:
        return str(int(float(raw)))
    except (TypeError, ValueError):
        return f"{row['first']} {row['last']}|{row['team']}"


def file_hash(path: str | Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()[:16]


def load_fantasy(path: str | Path) -> tuple[pd.DataFrame, list[int]]:
    """Return (players, reference_matchdays)."""
    raw = pd.read_excel(path)
    matchdays: list[int] = []
    for v in (str(x) for x in raw["ID"].tolist()):
        m = re.search(r"Reference matchdays:\s*([\d,\s]+)", v)
        if m:
            matchdays = [int(x) for x in re.findall(r"\d+", m.group(1))]

    df = raw[raw["Position"].isin(POS_MAP)].copy()
    out = pd.DataFrame({
        "raw_id": df["ID"],
        "first": df["Name"].astype(str).str.strip(),
        "last": df["Surname"].astype(str).str.strip(),
        "pos": df["Position"].map(POS_MAP),
        "team": df["Team"].astype(str).str.strip(),
        "price": pd.to_numeric(df["Quotation"], errors="coerce"),
        "fpt_avg": pd.to_numeric(df["FPT"], errors="coerce"),
        "plus": pd.to_numeric(df["Plus"], errors="coerce"),
        "active": pd.to_numeric(df["Active"], errors="coerce").fillna(1).astype(int),
    })
    out["key"] = out.apply(_key, axis=1)
    out["name"] = out["first"] + " " + out["last"]
    out = out.dropna(subset=["price"]).drop_duplicates("key").reset_index(drop=True)
    return out, matchdays


def update_price_history(fantasy: pd.DataFrame, matchdays: list[int], src_hash: str,
                         history_path: str | Path, run_date: str) -> tuple[pd.DataFrame, bool]:
    """Append a price snapshot once per distinct export file. Returns (history, is_new_file)."""
    history_path = Path(history_path)
    snap = fantasy[["key", "name", "pos", "team", "price", "fpt_avg", "plus"]].copy()
    snap.insert(0, "file_hash", src_hash)
    snap.insert(0, "matchday", max(matchdays) if matchdays else None)
    snap.insert(0, "date", run_date)

    if history_path.exists():
        hist = pd.read_csv(history_path, dtype={"key": str})
        if src_hash in set(hist["file_hash"].astype(str)):
            return hist, False
        hist = pd.concat([hist, snap], ignore_index=True)
    else:
        hist = snap
    history_path.parent.mkdir(parents=True, exist_ok=True)
    hist.to_csv(history_path, index=False)
    return hist, True


def price_trend(history: pd.DataFrame) -> pd.Series:
    """Price change from first snapshot to latest, per key."""
    h = history.sort_values("date")
    first = h.groupby("key")["price"].first()
    last = h.groupby("key")["price"].last()
    return (last - first).rename("season_price_change")
