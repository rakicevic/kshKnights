"""Projection engine.

Per-game fantasy points (FP) are projected from:
  * recent form: last 4 games, recency-weighted (4-3-2-1), plus median and volatility
    (captures the "2 good, 1 bad" pattern instead of chasing the last game)
  * season-to-date average, shrunk toward last season's level while the sample is small
  * minutes trend (role growing or shrinking)
  * opponent: FP it concedes vs league average; team strength -> win probability (+10% bonus)
  * home/away
Two predictors are trained on historical games and scored on a hold-out:
  heuristic (transparent formula) and gradient boosting (learned). The better one (or a blend)
  is used. Validation error is printed in the report so the model is never trusted blindly.
"""
from __future__ import annotations

import logging
from math import erf, sqrt

import numpy as np
import pandas as pd

log = logging.getLogger(__name__)

FEATURES = ["l1", "l2", "l3", "l4", "wl4", "med4", "std4", "sm", "n", "prior", "min4",
            "min_trend", "home", "opp_allow", "team_net", "opp_net", "p_win"]


def _phi(x: float) -> float:
    return 0.5 * (1 + erf(x / sqrt(2)))


# ---------------- team context ----------------
def team_context(tg: pd.DataFrame, logs: pd.DataFrame, season: int,
                 k: float = 5.0) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Per team-game, to-date (pre-game) net rating and FP conceded, shrunk to prior season."""
    tg = tg.sort_values(["Season", "Date", "Gamecode"]).copy()
    allowed = (logs.groupby(["Season", "Gamecode", "Opp"])["FP"].sum()
               .rename("FPAllowed").reset_index().rename(columns={"Opp": "Team"}))
    tg = tg.merge(allowed, on=["Season", "Gamecode", "Team"], how="left")

    prior = tg.groupby(["Season", "Team"]).agg(p_net=("Margin", "mean"), p_allow=("FPAllowed", "mean")).reset_index()
    prior["Season"] = prior["Season"] + 1
    tg = tg.merge(prior, on=["Season", "Team"], how="left")
    league_allow = tg.groupby("Season")["FPAllowed"].transform("mean")
    tg["p_net"] = tg["p_net"].fillna(0.0)
    tg["p_allow"] = tg["p_allow"].fillna(league_allow)

    g = tg.groupby(["Season", "Team"])
    tg["n_g"] = g.cumcount()
    tg["net_todate"] = g["Margin"].transform(lambda s: s.shift(1).expanding().mean()).fillna(0.0)
    tg["allow_todate"] = g["FPAllowed"].transform(lambda s: s.shift(1).expanding().mean())
    tg["allow_todate"] = tg["allow_todate"].fillna(tg["p_allow"])
    w = tg["n_g"] / (tg["n_g"] + k)
    tg["net"] = w * tg["net_todate"] + (1 - w) * tg["p_net"]
    tg["allow"] = w * tg["allow_todate"] + (1 - w) * tg["p_allow"]
    tg["allow_rel"] = tg["allow"] / league_allow

    # state after the latest game (for projecting upcoming games)
    last = tg.sort_values("Date").groupby(["Season", "Team"]).tail(1)
    s = tg.groupby(["Season", "Team"]).agg(net_all=("Margin", "mean"), allow_all=("FPAllowed", "mean")).reset_index()
    last = last.merge(s, on=["Season", "Team"]).reset_index(drop=True)
    n_after = last["n_g"] + 1
    w2 = n_after / (n_after + k)
    last["net_now"] = w2 * last["net_all"] + (1 - w2) * last["p_net"]
    last["allow_now"] = w2 * last["allow_all"] + (1 - w2) * last["p_allow"]
    league_now = tg[tg["Season"] == season]["FPAllowed"].mean()
    if pd.isna(league_now):
        league_now = tg["FPAllowed"].mean()
    last["allow_rel_now"] = last["allow_now"] / league_now
    now = last[last["Season"] == season].set_index("Team")[["net_now", "allow_rel_now"]]
    return tg, now


def win_prob(team_net: float, opp_net: float, home: int, hca: float, sigma: float) -> tuple[float, float]:
    mu = 0.5 * (team_net - opp_net) + (hca if home else -hca)
    return _phi(mu / sigma), mu


# ---------------- player features ----------------
def build_features(logs: pd.DataFrame, tg: pd.DataFrame, weights: list[float]) -> pd.DataFrame:
    df = logs.sort_values(["Player_ID", "Date", "Gamecode"]).copy()
    ctx = tg[["Season", "Gamecode", "Team", "net", "allow_rel"]]
    df = df.merge(ctx.rename(columns={"net": "team_net"}).drop(columns="allow_rel"),
                  on=["Season", "Gamecode", "Team"], how="left")
    df = df.merge(ctx.rename(columns={"Team": "Opp", "net": "opp_net", "allow_rel": "opp_allow"}),
                  on=["Season", "Gamecode", "Opp"], how="left")

    prior = df[df["FP"].notna()].groupby(["Player_ID", "Season"])["FP"].mean().rename("prior").reset_index()
    prior["Season"] = prior["Season"] + 1
    df = df.merge(prior, on=["Player_ID", "Season"], how="left")

    g = df.groupby(["Player_ID", "Season"])
    for i in range(1, 5):
        df[f"l{i}"] = g["FP"].shift(i)
    L = df[["l1", "l2", "l3", "l4"]].to_numpy(dtype=float)
    W = np.array(weights[:4], dtype=float)
    mask = ~np.isnan(L)
    df["wl4"] = np.where(mask.any(1), np.nansum(L * W, 1) / np.maximum((mask * W).sum(1), 1e-9), np.nan)
    df["med4"] = np.nanmedian(np.where(mask, L, np.nan), axis=1) if mask.any() else np.nan
    df["std4"] = np.where(mask.sum(1) >= 2, np.nanstd(np.where(mask, L, np.nan), axis=1), np.nan)
    df["sm"] = g["FP"].transform(lambda s: s.shift(1).expanding().mean())
    df["n"] = g.cumcount()
    df["min4"] = g["Min"].transform(lambda s: s.shift(1).rolling(4, min_periods=1).mean())
    min_season = g["Min"].transform(lambda s: s.shift(1).expanding().mean())
    df["min_trend"] = df["min4"] / min_season.replace(0, np.nan)
    df["home"] = df["Home"].astype(float)
    return df


def heuristic(df: pd.DataFrame, k: float, price_prior: pd.Series | None = None) -> np.ndarray:
    prior = df["prior"].copy()
    if price_prior is not None:
        prior = prior.fillna(price_prior)
    prior = prior.fillna(df["sm"]).fillna(df["wl4"]).fillna(5.0)
    form = 0.6 * df["wl4"].fillna(df["sm"]) + 0.4 * df["sm"].fillna(df["wl4"])
    form = form.fillna(prior)
    w = df["n"] / (df["n"] + k)
    base = w * form + (1 - w) * prior
    opp = df["opp_allow"].fillna(1.0).clip(0.8, 1.25) ** 0.5
    winadj = (1 + 0.10 * df["p_win"].fillna(0.5)) / 1.05
    return (base * opp * winadj).to_numpy()


class Projector:
    def __init__(self, cfg: dict, rules: dict):
        self.cfg = cfg
        self.rules = rules
        self.choice = "heuristic"
        self.metrics: dict = {}
        self.ml = None

    def fit(self, feats: pd.DataFrame) -> None:
        d = feats[feats["FP"].notna() & (feats["n"].ge(1) | feats["prior"].notna())].copy()
        d["p_win"] = [win_prob(t, o, h, self.cfg["home_court_pts"], self.cfg["margin_sigma"])[0]
                      for t, o, h in zip(d["team_net"].fillna(0), d["opp_net"].fillna(0), d["home"].fillna(0))]
        if len(d) < 300:
            self.metrics = {"note": f"only {len(d)} training rows; heuristic used"}
            return
        d = d.sort_values("Date")
        cut = int(len(d) * 0.85)
        tr, va = d.iloc[:cut], d.iloc[cut:]
        y = va["FP"].to_numpy()
        h_pred = heuristic(va, self.cfg["prior_games_k"])
        mae = {"heuristic": float(np.mean(np.abs(h_pred - y))),
               "naive_last_game": float(np.nanmean(np.abs(va["l1"].fillna(va["prior"]).fillna(5).to_numpy() - y)))}
        if self.cfg.get("ml", True):
            try:
                from sklearn.ensemble import HistGradientBoostingRegressor
                m = HistGradientBoostingRegressor(max_iter=300, learning_rate=0.05, max_leaf_nodes=15,
                                                  min_samples_leaf=40, l2_regularization=1.0, random_state=7)
                m.fit(tr[FEATURES], tr["FP"])
                ml_pred = m.predict(va[FEATURES])
                mae["ml"] = float(np.mean(np.abs(ml_pred - y)))
                mae["blend"] = float(np.mean(np.abs(0.5 * ml_pred + 0.5 * h_pred - y)))
                best = min(("heuristic", "ml", "blend"), key=lambda k: mae[k])
                if best != "heuristic":
                    self.ml = HistGradientBoostingRegressor(**m.get_params()).fit(d[FEATURES], d["FP"])
                self.choice = best
            except Exception as exc:  # never let ML break the weekly run
                log.warning("ML training failed, heuristic used: %s", exc)
        self.metrics = {"validation_games": int(len(va)), "mae": mae, "chosen": self.choice}

    def predict(self, rows: pd.DataFrame, price_prior: pd.Series | None = None) -> np.ndarray:
        h = heuristic(rows, self.cfg["prior_games_k"], price_prior)
        if self.choice == "heuristic" or self.ml is None:
            return h
        mlp = self.ml.predict(rows[FEATURES])
        return mlp if self.choice == "ml" else 0.5 * mlp + 0.5 * h


# ---------------- upcoming games ----------------
def upcoming_games(schedule: pd.DataFrame, run_date: pd.Timestamp, days: int) -> pd.DataFrame:
    start = run_date.normalize() + pd.Timedelta(days=1)
    end = run_date.normalize() + pd.Timedelta(days=days + 1)
    s = schedule[(schedule["Date"] >= start) & (schedule["Date"] < end)]
    home = s.rename(columns={"HomeCode": "Team", "AwayCode": "Opp"}).assign(home=1)
    away = s.rename(columns={"AwayCode": "Team", "HomeCode": "Opp"}).assign(home=0)
    return pd.concat([home, away], ignore_index=True)[["Date", "Round", "Team", "Opp", "home"]]


def player_state(feats_logs: pd.DataFrame, season: int, weights: list[float]) -> pd.DataFrame:
    """Features as of 'now' (after the latest game) for every player seen this or last season."""
    last = feats_logs.sort_values(["Date", "Gamecode"]).groupby("Player_ID").tail(1)
    cur = feats_logs[feats_logs["Season"] == season]
    rows = []
    for pid, grp in cur.sort_values(["Date", "Gamecode"]).groupby("Player_ID"):
        fp = grp["FP"].to_numpy(dtype=float)
        mins = grp["Min"].to_numpy(dtype=float)
        rec = fp[::-1][:4]
        l = list(rec) + [np.nan] * (4 - len(rec))
        w = np.array(weights[:len(rec)], dtype=float)
        rows.append({
            "Player_ID": pid, "l1": l[0], "l2": l[1], "l3": l[2], "l4": l[3],
            "wl4": float(np.sum(rec * w) / w.sum()), "med4": float(np.median(rec)),
            "std4": float(np.std(rec)) if len(rec) >= 2 else np.nan,
            "sm": float(np.mean(fp)), "n": len(fp),
            "min4": float(np.mean(mins[::-1][:4])),
            "min_trend": float(np.mean(mins[::-1][:4]) / np.mean(mins)) if np.mean(mins) > 0 else np.nan,
            "last_min": float(mins[-1]), "dnp_streak": int(_dnp_streak(mins)),
            "season_min": float(np.mean(mins)),
        })
    st = pd.DataFrame(rows)
    prior = (feats_logs[feats_logs["Season"] == season - 1].groupby("Player_ID")["FP"].mean().rename("prior"))
    base = last[["Player_ID", "Player", "Team", "Season"]].set_index("Player_ID")
    st = base.join(st.set_index("Player_ID"), how="left").join(prior, how="left").reset_index()
    st["n"] = st["n"].fillna(0)
    return st


def _dnp_streak(mins: np.ndarray) -> int:
    k = 0
    for m in mins[::-1]:
        if m > 0:
            break
        k += 1
    return k


def project_window(state: pd.DataFrame, games: pd.DataFrame, team_now: pd.DataFrame,
                   projector: Projector, cfg: dict, price_prior: pd.Series | None) -> pd.DataFrame:
    """Per-player projection summed over the player's games in the window."""
    if games.empty:
        return pd.DataFrame(columns=["Player_ID", "games", "proj_game", "proj_window", "p_win_avg", "opps"])
    rows = state.merge(games, on="Team", how="inner")
    rows["team_net"] = rows["Team"].map(team_now["net_now"]).fillna(0.0)
    rows["opp_net"] = rows["Opp"].map(team_now["net_now"]).fillna(0.0)
    rows["opp_allow"] = rows["Opp"].map(team_now["allow_rel_now"]).fillna(1.0)
    rows["p_win"] = [win_prob(t, o, h, cfg["home_court_pts"], cfg["margin_sigma"])[0]
                     for t, o, h in zip(rows["team_net"], rows["opp_net"], rows["home"])]
    pp = rows["Player_ID"].map(price_prior) if price_prior is not None else None
    rows["pred"] = projector.predict(rows, pp)
    # risk: penalise volatility; availability: recent DNPs
    rows["pred"] = rows["pred"] - cfg["risk_aversion"] * rows["std4"].fillna(0)
    avail = np.select([rows["dnp_streak"] >= 2, rows["dnp_streak"] == 1], [0.2, 0.5], 1.0)
    rows["pred"] = rows["pred"] * avail
    agg = rows.groupby("Player_ID").agg(
        games=("Opp", "size"), proj_window=("pred", "sum"), proj_game=("pred", "mean"),
        p_win_avg=("p_win", "mean"),
        opps=("Opp", lambda s: ", ".join(f"{'vs' if h else '@'} {o}" for o, h in zip(s, rows.loc[s.index, 'home'])))
    ).reset_index()
    return agg


def project_coaches(games: pd.DataFrame, team_now: pd.DataFrame, cfg: dict, rules: dict) -> pd.DataFrame:
    """Expected coach score per API team over the window from the margin distribution."""
    cp = rules["coach_points"]
    bands = [(0, 10, cp["win_1_10"]), (10, 20, cp["win_11_20"]), (20, 1e9, cp["win_20_plus"])]
    out = []
    for team, grp in games.groupby("Team"):
        total, pw = 0.0, []
        for _, g in grp.iterrows():
            p, mu = win_prob(team_now["net_now"].get(team, 0.0), team_now["net_now"].get(g["Opp"], 0.0),
                             g["home"], cfg["home_court_pts"], cfg["margin_sigma"])
            s = cfg["margin_sigma"]
            ev = 0.0
            for lo, hi, pts in bands:
                ev += pts * (_phi((hi - mu) / s) - _phi((lo - mu) / s))
            for lo, hi, pts in [(0, 10, cp["loss_1_10"]), (10, 20, cp["loss_11_20"]), (20, 1e9, cp["loss_20_plus"])]:
                ev += pts * (_phi((-lo - mu) / s) - _phi((-hi - mu) / s))
            total += ev
            pw.append(p)
        out.append({"api_team": team, "games": len(grp), "proj_window": total, "p_win_avg": float(np.mean(pw))})
    return pd.DataFrame(out)
