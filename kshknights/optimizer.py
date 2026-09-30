"""Exact roster optimizer (mixed-integer program solved by HiGHS through scipy).

Round roster: 6 main = starting five in one formation (G-F-C: 1-2-2, 1-3-1, 2-1-2, 2-2-1, 3-1-1)
+ sixth man (any position), all at 100%; 4 bench slots G, F, F, C at 50%; 1 head coach.
Decision variables per candidate i: x_i roster, m_i main six, s_i starter, c_i captain;
per formation k: y_k (exactly one chosen).
Objective: sum proj_i * (bench*(x_i - m_i) + m_i + (cap-1)*c_i) + coach projection.
Constraints: formation, bench composition, budget, <=6 players per club, trade limit, locks, bans.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.optimize import Bounds, LinearConstraint, milp

POS = ("G", "F", "C")


def parse_formations(rules: dict) -> list[dict]:
    out = []
    for f in rules["formations"]:
        g, fw, c = (int(v) for v in str(f).split("-"))
        out.append({"name": str(f), "G": g, "F": fw, "C": c})
    return out


def optimize(cands: pd.DataFrame, rules: dict, budget: float, owned: set[str],
             max_trades: int | None, lock: set[str], ban: set[str]) -> dict:
    """cands columns: key, pos (G/F/C/HC), team, price, proj."""
    c = cands.reset_index(drop=True).copy()
    c = c[~c["key"].isin(ban - owned)].reset_index(drop=True)
    forms = parse_formations(rules)
    n, nf = len(c), len(forms)
    is_pl = (c["pos"] != "HC").to_numpy()
    X, M, S, K, Y = 0, n, 2 * n, 3 * n, 4 * n
    nv = 4 * n + nf
    bm, cm = rules["bench_multiplier"], rules["captain_multiplier"]
    proj = c["proj"].to_numpy(dtype=float)
    pos_arr = c["pos"].to_numpy()

    obj = np.zeros(nv)
    obj[X:X + n] = np.where(is_pl, bm * proj, proj)          # bench share; coach full
    obj[M:M + n] = np.where(is_pl, (1 - bm) * proj, 0)       # main six top-up to 100%
    obj[K:K + n] = np.where(is_pl, (cm - 1) * proj, 0)       # captain extra
    obj[X:X + n] -= 1e-4 * c["price"].to_numpy()             # tie-break: keep credits

    A, lo, hi = [], [], []

    def add(row, l, h):
        A.append(row); lo.append(l); hi.append(h)

    def blk(b, mask):
        r = np.zeros(nv); r[b:b + n] = mask; return r

    main_n = 5 + int(rules.get("sixth_man", 1))
    add(blk(X, ~is_pl), rules.get("coach", 1), rules.get("coach", 1))
    add(blk(M, is_pl), main_n, main_n)
    add(blk(S, is_pl), 5, 5)
    add(blk(K, is_pl), 1, 1)
    r = np.zeros(nv); r[Y:Y + nf] = 1; add(r, 1, 1)
    for p in POS:
        m = pos_arr == p
        # bench composition: x - m per position fixed
        r = blk(X, m) - blk(M, m); add(r, rules["bench"][p], rules["bench"][p])
        # starters per position = chosen formation's count
        r = blk(S, m); r[Y:Y + nf] = [-f[p] for f in forms]; add(r, 0, 0)
    add(blk(X, c["price"].to_numpy()), 0, budget)
    for t in c.loc[is_pl, "team"].unique():
        add(blk(X, ((c["team"] == t).to_numpy() & is_pl)), 0, rules["max_per_team"])
    for i in range(n):  # captain <= starter <= main <= roster
        for up, dn in ((X, M), (M, S), (S, K)):
            r = np.zeros(nv); r[dn + i] = 1; r[up + i] = -1; add(r, -np.inf, 0)
    if owned and max_trades is not None:
        keep = c["key"].isin(owned).to_numpy()
        add(blk(X, keep), int(keep.sum()) - max_trades, np.inf)

    lb, ub = np.zeros(nv), np.ones(nv)
    ub[M:Y] = np.tile(is_pl.astype(float), 3)
    for i, k in enumerate(c["key"]):
        if k in lock and k in owned:
            lb[X + i] = 1

    res = milp(-obj, constraints=LinearConstraint(np.array(A), lo, hi), integrality=np.ones(nv),
               bounds=Bounds(lb, ub), options={"time_limit": 60})
    if res.x is None:
        return {"status": "infeasible", "message": res.message}
    v = np.round(res.x).astype(int)
    c["on"], c["main"], c["starter"], c["captain"] = v[X:X + n], v[M:M + n], v[S:S + n], v[K:K + n]
    formation = forms[int(np.argmax(v[Y:Y + nf]))]["name"]
    roster = c[c["on"] == 1].copy()
    roster["role"] = np.select(
        [roster["pos"] == "HC", roster["captain"] == 1, roster["starter"] == 1, roster["main"] == 1],
        ["Coach", "Captain", "Starter", "6th man"], "Bench")
    roster["expected"] = np.where(roster["pos"] == "HC", roster["proj"],
                                  roster["proj"] * np.select([roster["captain"] == 1, roster["main"] == 1],
                                                             [cm, 1.0], bm))
    order = {"Captain": 0, "Starter": 1, "6th man": 2, "Bench": 3, "Coach": 4}
    porder = {"G": 0, "F": 1, "C": 2, "HC": 3}
    roster = roster.assign(_r=roster["role"].map(order), _p=roster["pos"].map(porder)) \
        .sort_values(["_r", "_p", "proj"], ascending=[True, True, False]).drop(columns=["_r", "_p"])
    return {
        "status": "ok",
        "roster": roster,
        "formation": formation,
        "total": float(roster["expected"].sum()),
        "cost": float(roster["price"].sum()),
        "budget": budget,
        "sell": sorted(owned - set(roster["key"])),
        "buy": sorted(set(roster["key"]) - owned) if owned else [],
    }
