"""Public requirement tests. They FAIL on the starter. Hidden tests regenerate the applicant book."""
import numpy as np
import pandas as pd
import pytest

import cutoff_lab as cl
from conftest import DATA

TERMS = {"gain": 25.0, "loss": 70.0}


class Const:
    def __init__(self, f):
        self.f = f

    def predict(self, s):
        return self.f(np.asarray(s, float))


# R1
def test_band_table_shows_the_blind_spot():
    df = cl.load_applications(DATA)
    t = cl.default_rate_by_band(df)
    assert list(t.columns) == ["band", "n_apps", "n_funded", "naive_rate", "ipw_rate"]
    assert t["n_apps"].sum() == len(df)
    below = t[t["band"].isin(["300-499", "500-549", "550-574", "575-599"])]
    assert below["naive_rate"].isna().all() and below["ipw_rate"].notna().all()
    assert t.loc[t["band"] == "600-649", "naive_rate"].iloc[0] == pytest.approx(t.loc[t["band"] == "600-649", "ipw_rate"].iloc[0])
    assert below["ipw_rate"].iloc[-1] < below["ipw_rate"].iloc[1]  # lower scores default more


def test_ipw_rate_weights_by_inverse_propensity():
    df = pd.DataFrame({"score": [520, 520, 520, 520], "approved": 0, "explored": 1, "propensity": [0.5, 0.5, 0.1, 0.1],
                       "defaulted": [1.0, 0.0, 0.0, 0.0]})
    r = cl.default_rate_by_band(df, edges=[500, 550]).iloc[0]
    w = np.array([2, 2, 10, 10])
    assert r["ipw_rate"] == pytest.approx((w * [1, 0, 0, 0]).sum() / w.sum())


# R2
def test_fit_recovers_logistic_parameters():
    rng = np.random.default_rng(0)
    s = rng.integers(400, 800, 30000)
    z = (s - 600) / 100
    y = (rng.random(len(s)) < 1 / (1 + np.exp(-(-1.0 - 1.2 * z)))).astype(float)
    df = pd.DataFrame({"score": s, "approved": 1, "explored": 0, "propensity": 1.0, "defaulted": y})
    c = cl.fit_default_curve(df, "approved_only", degree=1)
    assert c.coef == pytest.approx([-1.0, -1.2], abs=0.08)


def test_unknown_method_is_rejected():
    with pytest.raises(ValueError):
        cl.fit_default_curve(cl.load_applications(DATA), "heckman")


# R3, R4
def test_expected_profit_by_hand():
    df = pd.DataFrame({"score": [500, 600, 700]})
    curve = Const(lambda s: np.full_like(s, 0.1))
    assert cl.expected_profit(600, df, curve, TERMS) == pytest.approx(2 * (0.9 * 25 - 0.1 * 70) / 3)
    assert cl.expected_profit(800, df, curve, TERMS) == 0


def test_best_cutoff_finds_the_break_even_score():
    df = pd.DataFrame({"score": np.arange(300, 851)})
    curve = Const(lambda s: np.clip((700 - s) / 400, 0.01, 0.99))  # p* = 25/95 at s = 595
    c, p = cl.best_cutoff(df, curve, TERMS)
    assert c == 595 and p == pytest.approx(cl.expected_profit(595, df, curve, TERMS))


def test_best_cutoff_ties_go_to_the_lowest_cutoff():
    df = pd.DataFrame({"score": [400, 410, 420]})
    zero = Const(lambda s: np.full_like(s, 0.0))
    assert cl.best_cutoff(df, zero, TERMS, grid=[300, 350, 400])[0] == 300


# R5
def test_bootstrap_is_deterministic_and_follows_the_draw_order():
    df = cl.load_applications(DATA)
    a = cl.bootstrap_cutoff(df, "ipw", 2, TERMS, n_boot=6, seed=4)
    b = cl.bootstrap_cutoff(df, "ipw", 2, TERMS, n_boot=6, seed=4)
    assert (a["cutoffs"] == b["cutoffs"]).all() and a["ci_low"] <= a["median"] <= a["ci_high"]
    rng = np.random.default_rng(4)
    exp = []
    for _ in range(6):
        d = df.iloc[rng.integers(0, len(df), len(df))].reset_index(drop=True)
        exp.append(cl.best_cutoff(d, cl.fit_default_curve(d, "ipw", 2), TERMS)[0])
    assert list(a["cutoffs"]) == exp


# R6, R7
def test_scenario_table_and_minimax_regret():
    df = pd.DataFrame({"score": np.arange(400, 801)})
    curve = Const(lambda s: np.clip((750 - s) / 500, 0.01, 0.9))
    t = cl.scenario_profits(df, curve, TERMS, [500, 600, 700], [1.0, 1.5])
    assert list(t.columns) == ["cutoff", "multiplier", "profit"] and len(t) == 6
    hi = t[t["multiplier"] == 1.5].set_index("cutoff")["profit"]
    lo = t[t["multiplier"] == 1.0].set_index("cutoff")["profit"]
    assert (hi < lo).all()
    hand = pd.DataFrame({"cutoff": [1, 2, 3, 1, 2, 3], "multiplier": [1, 1, 1, 2, 2, 2], "profit": [10, 9, 5, 0, 4, 5]})
    assert cl.minimax_regret(hand) == 2  # regrets: c1 -> max(0, 5)=5, c2 -> max(1, 1)=1, c3 -> max(5, 0)=5


# the decision on the official book
def test_naive_extrapolation_is_too_aggressive_and_ipw_is_not():
    df = cl.load_applications(DATA)
    naive = cl.best_cutoff(df, cl.fit_default_curve(df, "approved_only", 1), TERMS)[0]
    ipw = cl.best_cutoff(df, cl.fit_default_curve(df, "ipw", 2), TERMS)[0]
    assert naive <= 540
    assert 565 <= ipw <= 615


def test_recommend_keys_and_logic():
    df = cl.load_applications(DATA)
    r = cl.recommend(df, TERMS, n_boot=30, seed=1)
    assert set(r) >= {"ipw_cutoff", "naive_cutoff", "ci_low", "ci_high", "robust_cutoff", "naive_claimed_profit",
                      "naive_cutoff_profit_under_ipw"}
    assert r["naive_claimed_profit"] > r["naive_cutoff_profit_under_ipw"]
    assert r["ci_low"] <= r["ipw_cutoff"] <= r["ci_high"] + 15
    assert r["robust_cutoff"] >= r["ipw_cutoff"] - 5
