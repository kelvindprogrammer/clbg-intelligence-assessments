"""Public requirement tests (a sample; assessors run a hidden suite on freshly generated households)."""
import numpy as np
import pytest

from conftest import DATA

import speccurve as sc


@pytest.fixture(scope="module")
def df():
    return sc.load_export(DATA)


def test_r1_ols_matches_numpy_and_hc1_formula():
    rng = np.random.RandomState(0)
    X = np.column_stack([np.ones(200), rng.randn(200, 2)])
    y = X @ [1.0, 2.0, -1.0] + rng.randn(200) * (1 + np.abs(X[:, 1]))
    beta, se = sc.ols(X, y)
    assert np.allclose(beta, np.linalg.lstsq(X, y, rcond=None)[0])
    e = y - X @ beta
    XtXi = np.linalg.inv(X.T @ X)
    V = 200 / 197 * XtXi @ (X.T @ (X * (e ** 2)[:, None])) @ XtXi
    assert np.allclose(se, np.sqrt(np.diag(V)))


def test_r2_logit_reaches_the_score_equations():
    rng = np.random.RandomState(1)
    X = np.column_stack([np.ones(500), rng.randn(500, 2)])
    t = (rng.rand(500) < 1 / (1 + np.exp(-(X @ [0.3, 1.0, -0.7])))).astype(float)
    b = sc.logit_fit(X, t)
    p = 1 / (1 + np.exp(-X @ b))
    assert np.abs(X.T @ (t - p)).max() < 1e-6 and np.allclose(b, [0.3, 1.0, -0.7], atol=0.4)


def test_r3_estimate_ols_equals_a_direct_computation(df):
    r = sc.estimate(df, {"outcome": "raw", "controls": "none", "method": "ols", "trim": False})
    y = df["savings_ngn"].to_numpy(float); t = df["trained"].to_numpy(float)
    assert r["effect"] == pytest.approx((y[t == 1].mean() - y[t == 0].mean()) / y.std(ddof=1)) and r["n"] == 1600


def test_r3_trimming_and_log_change_the_sample_and_scale(df):
    a = sc.estimate(df, {"outcome": "raw", "controls": "core", "method": "ols", "trim": False})
    b = sc.estimate(df, {"outcome": "raw", "controls": "core", "method": "ols", "trim": True})
    c = sc.estimate(df, {"outcome": "log", "controls": "core", "method": "ols", "trim": False})
    assert b["n"] == (df["savings_ngn"] <= df["savings_ngn"].quantile(0.99)).sum() < a["n"]
    assert len({round(a["effect"], 4), round(b["effect"], 4), round(c["effect"], 4)}) == 3


def test_r3_ipw_is_deterministic_and_close_to_ols_on_core(df):
    spec = {"outcome": "raw", "controls": "core", "method": "ipw", "trim": True}
    a, b = sc.estimate(df, spec, n_boot=30, seed=2), sc.estimate(df, spec, n_boot=30, seed=2)
    assert a == b and a["se"] > 0
    o = sc.estimate(df, {**spec, "method": "ols"})
    assert abs(a["effect"] - o["effect"]) < 0.25


def test_r4_curve_shape_order_and_columns(df):
    c = sc.spec_curve(df, n_boot=10)
    assert len(c) == 48 and list(c.columns) == ["outcome", "controls", "method", "trim", "effect", "se", "lo", "hi", "sig"]
    assert c.iloc[0][["outcome", "controls", "method", "trim"]].tolist() == ["raw", "none", "ols", False]
    assert c.iloc[1]["trim"] == True and c.iloc[2]["method"] == "ipw"   # noqa: E712
    small = sc.spec_curve(df, {"outcome": ["raw"], "controls": ["none", "core"], "method": ["ols"], "trim": [False]})
    assert len(small) == 2 and (small["lo"] < small["effect"]).all() and small["sig"].dtype == bool


def test_r5_summary_and_r6_filter(df):
    c = sc.spec_curve(df, n_boot=10)
    s = sc.summarise_curve(c)
    assert s["n_specs"] == 48 and 0 <= s["share_sig_positive"] <= s["share_positive"] <= 1
    assert s["min_effect"] <= s["median_effect"] <= s["max_effect"] and isinstance(s["sign_flips"], bool)
    g = sc.defensible(c, {"loan_taken", "visited_agent"})
    assert len(g) == 24 and set(g["controls"]) == {"none", "core", "core+demog"} and g.index.tolist() == list(range(24))
    assert len(sc.defensible(c, set())) == 48


def test_r7_e_value_matches_the_published_example():
    rr = 3.9
    d = np.log(rr) / 0.91
    assert sc.e_value(d)["point"] == pytest.approx(7.26, abs=0.01)
    assert sc.e_value(d, 0.2)["ci"] < sc.e_value(d)["point"]
    assert sc.e_value(0.5, -0.1)["ci"] == 1.0 and sc.e_value(-0.5)["point"] == pytest.approx(sc.e_value(0.5)["point"])
