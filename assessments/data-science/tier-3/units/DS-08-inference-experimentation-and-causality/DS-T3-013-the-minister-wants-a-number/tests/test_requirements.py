"""Public requirement tests. They FAIL on the starter. Hidden tests use regenerated panels."""
import numpy as np
import pandas as pd
import pytest

import staggered_did as sd
from conftest import DATA


def panel(sizes, effect, T=10, drift_cohort=None, drift=0.0, noise=0.0, seed=0):
    """sizes: {cohort: n_units} (cohort 0 = never). effect(g, e) is the treatment effect e periods after adoption."""
    rng = np.random.default_rng(seed)
    rows, uid = [], 0
    for g, n in sizes.items():
        for _ in range(n):
            alpha = rng.normal(0, 1) if noise else 0.1 * uid
            for t in range(1, T + 1):
                y = alpha + 0.5 * t + (effect(g, t - g) if g and t >= g else 0.0)
                y += drift * t if g == drift_cohort else 0.0
                rows.append((f"u{uid}", t, g, y + rng.normal(0, noise) if noise else y))
            uid += 1
    return pd.DataFrame(rows, columns=["unit_id", "period", "cohort", "outcome"])


DYN = lambda g, e: {3: 4.0, 6: 1.0, 8: 0.5}[g] * (1 + e)
SIZES = {3: 5, 6: 5, 8: 5, 0: 8}


# R1
def test_twfe_matches_dummy_variable_ols():
    df = panel(SIZES, DYN, noise=0.5, seed=1)
    d = ((df["cohort"] > 0) & (df["period"] >= df["cohort"])).astype(float)
    X = np.column_stack([d, pd.get_dummies(df["unit_id"]).to_numpy(float), pd.get_dummies(df["period"]).to_numpy(float)[:, 1:]])
    beta = np.linalg.lstsq(X, df["outcome"].to_numpy(), rcond=None)[0][0]
    assert sd.twfe_att(df) == pytest.approx(beta, rel=1e-8)


def test_twfe_requires_a_balanced_panel():
    df = panel(SIZES, DYN)
    with pytest.raises(ValueError):
        sd.twfe_att(df.iloc[1:])


# R2
def test_group_time_table_layout():
    gt = sd.group_time_att(panel(SIZES, DYN))
    assert list(gt.columns) == ["g", "t", "att", "n_g", "n_c"]
    assert not ((gt["t"] == gt["g"] - 1)).any()
    assert set(gt["g"]) == {3, 6, 8} and (gt["n_c"] == 8).all()


def test_group_time_att_is_exact_without_noise():
    gt = sd.group_time_att(panel(SIZES, DYN))
    post = gt[gt["t"] >= gt["g"]]
    expected = [DYN(g, t - g) for g, t in zip(post["g"], post["t"])]
    assert post["att"].to_numpy() == pytest.approx(expected)
    assert gt[gt["t"] < gt["g"] - 1]["att"].abs().max() < 1e-9


def test_not_yet_controls_agree_when_trends_are_parallel():
    df = panel(SIZES, DYN)
    a = sd.aggregate_att(sd.group_time_att(df), "simple")
    b = sd.aggregate_att(sd.group_time_att(df, "not_yet"), "simple")
    assert a == pytest.approx(b)
    assert (sd.group_time_att(df, "not_yet")["n_c"] != 8).any()


# R3
def test_aggregations_and_their_weights():
    df = panel(SIZES, DYN)
    gt = sd.group_time_att(df)
    post = gt[gt["t"] >= gt["g"]]
    assert sd.aggregate_att(gt) == pytest.approx(np.average(post["att"], weights=post["n_g"]))
    ev = sd.aggregate_att(gt, "event")
    assert list(ev.columns) == ["e", "att"] and ev["e"].min() < 0 and ev["e"].min() == ev["e"].iloc[0]
    assert ev.loc[ev["e"] == -2, "att"].abs().max() < 1e-9
    co = sd.aggregate_att(gt, "cohort")
    assert list(co["g"]) == [3, 6, 8]
    with pytest.raises(ValueError):
        sd.aggregate_att(gt, "median")


def test_twfe_is_biased_under_heterogeneous_dynamic_effects_but_cs_is_not():
    df = panel(SIZES, DYN)
    gt = sd.group_time_att(df)
    post = gt[gt["t"] >= gt["g"]]
    truth = np.average([DYN(g, t - g) for g, t in zip(post["g"], post["t"])], weights=post["n_g"])
    assert sd.aggregate_att(gt) == pytest.approx(truth)
    assert abs(sd.twfe_att(df) - truth) > 0.15 * truth


# R4
def test_cluster_bootstrap_is_reproducible_and_positive():
    df = panel(SIZES, DYN, noise=0.5, seed=2)
    est = lambda d: sd.aggregate_att(sd.group_time_att(d))
    r1 = sd.cluster_bootstrap(df, est, n_boot=40, seed=3)
    assert r1 == sd.cluster_bootstrap(df, est, n_boot=40, seed=3)
    assert r1["se"] > 0 and r1["estimate"] == pytest.approx(est(df))


def test_cluster_bootstrap_follows_the_draw_order():
    df = panel(SIZES, DYN, noise=0.5, seed=2)
    est = lambda d: float(d["outcome"].mean())
    units = np.sort(df["unit_id"].unique())
    rng = np.random.default_rng(7)
    vals = []
    for _ in range(30):
        draw = rng.integers(0, len(units), len(units))
        vals.append(np.concatenate([df.loc[df["unit_id"] == units[k], "outcome"].to_numpy() for k in draw]).mean())
    assert sd.cluster_bootstrap(df, est, n_boot=30, seed=7)["se"] == pytest.approx(np.std(vals, ddof=1))


# R5
def test_pretrend_test_flags_a_differential_trend_but_not_parallel_trends():
    clean = sd.pretrend_test(panel(SIZES, DYN, noise=0.6, seed=4), n_boot=60, seed=1)
    bad = sd.pretrend_test(panel(SIZES, DYN, drift_cohort=6, drift=0.5, noise=0.6, seed=4), n_boot=60, seed=1)
    assert clean["p_value"] > 0.05 > bad["p_value"]


# R6 on the official panel
def test_analyze_on_the_official_panel():
    df = sd.load_panel(DATA)
    r = sd.analyze(df, n_boot=60, seed=1)
    assert set(r) >= {"twfe", "cs_simple", "cs_not_yet", "cs_se", "event", "pretrend_p", "twfe_minus_cs"}
    assert 2.9 <= r["cs_simple"] <= 3.5  # truth about 3.2; reference error about 0.1
    assert abs(r["twfe_minus_cs"]) > 0.5   # heterogeneity and dynamics bias the TWFE number
    assert r["cs_se"] > 0 and r["pretrend_p"] > 0.01
    assert abs(r["cs_not_yet"] - r["cs_simple"]) < 0.5
