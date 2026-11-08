"""Public requirement tests (a sample; assessors run a hidden suite on a freshly generated survey)."""
import json

import numpy as np
import pytest

from conftest import DATA

import claimcheck as cc


@pytest.fixture(scope="module")
def df():
    return cc.load_export(DATA)


def test_r1_wilson_matches_known_values():
    lo, hi = cc.wilson_ci(83, 100)
    assert lo == pytest.approx(0.74452, abs=1e-4) and hi == pytest.approx(0.89106, abs=1e-4)
    assert cc.wilson_ci(0, 20)[0] == 0.0 and 0 < cc.wilson_ci(0, 20)[1] < 0.2
    assert cc.wilson_ci(20, 20)[1] == 1.0
    lo99, hi99 = cc.wilson_ci(83, 100, level=0.99)
    assert lo99 < lo and hi99 > hi


def test_r2_difference_in_proportions():
    d, lo, hi = cc.diff_in_proportions(83, 100, 71, 100)
    assert d == pytest.approx(0.12) and lo == pytest.approx(0.004545, abs=1e-5) and hi == pytest.approx(0.235455, abs=1e-5)


def test_r3_bootstrap_ci_is_deterministic_and_sensible():
    v = np.array([1, 0, 1, 1, 0, 0, 1, 1, 1, 0, 1, 0])
    a = cc.bootstrap_ci(v, np.mean, n_boot=500, seed=1)
    assert a == cc.bootstrap_ci(v, np.mean, n_boot=500, seed=1)
    x = np.linspace(0, 10, 37)
    assert cc.bootstrap_ci(x, np.mean, n_boot=300, seed=1) != cc.bootstrap_ci(x, np.mean, n_boot=300, seed=2)
    assert a[0] == pytest.approx(0.25, abs=0.05) and a[1] == pytest.approx(0.833, abs=0.05)
    assert all(isinstance(x, float) for x in a)
    lo, hi = cc.bootstrap_ci(np.arange(100.0), np.median, n_boot=300, seed=0)
    assert 35 < lo < 50 < hi < 65


def test_r4_cluster_did_on_the_export(df):
    r = cc.cluster_did(df, n_boot=1000, seed=0)
    assert set(r) == {"estimate", "lo", "hi", "naive_lo", "naive_hi", "programme_change", "comparison_change", "width_ratio"}
    g = df.groupby(["group", "period"])["regular"].mean()
    assert r["programme_change"] == pytest.approx(g["programme", "after"] - g["programme", "before"])
    assert r["estimate"] == pytest.approx(r["programme_change"] - r["comparison_change"])
    assert r["lo"] == pytest.approx(-0.0098, abs=0.02) and r["hi"] == pytest.approx(0.1847, abs=0.02)
    assert r["naive_lo"] == pytest.approx(0.0187, abs=0.003) and r["naive_hi"] == pytest.approx(0.1535, abs=0.003)
    assert r["width_ratio"] > 1.2


def test_r4_ignores_row_order_and_respects_seed(df):
    a = cc.cluster_did(df, n_boot=300, seed=4)
    shuffled = df.sample(frac=1.0, random_state=1).reset_index(drop=True)
    assert cc.cluster_did(shuffled, n_boot=300, seed=4) == a
    assert cc.cluster_did(df, n_boot=300, seed=5)["lo"] != a["lo"]


def test_r5_verdict_rules():
    base = {"programme_change": 0.09, "estimate": 0.09}
    assert cc.verdict({**base, "lo": -0.01, "hi": 0.18}) == "inconclusive"
    assert cc.verdict({**base, "lo": 0.02, "hi": 0.15}) == "supported"
    assert cc.verdict({**base, "lo": 0.01, "hi": 0.05}) == "overstated"
    assert cc.verdict({**base, "lo": 0.01, "hi": 0.05}, claimed=0.03) == "supported"


def test_r5_verdict_on_the_export(df):
    r = cc.cluster_did(df, n_boot=1000, seed=0)
    assert cc.verdict(r) == "inconclusive"
    assert r["naive_lo"] > 0     # the pupil-level interval would have said 'significant'


def test_r6_manifest(df, tmp_path):
    p = tmp_path / "m.json"
    m = cc.write_manifest(p, DATA, seed=7)
    assert json.loads(p.read_text()) == m
    assert set(m) == {"data_sha256", "seed", "n_rows", "python", "pandas"} and m["seed"] == 7 and m["n_rows"] == 2880
    import hashlib
    assert m["data_sha256"] == hashlib.sha256(DATA.read_bytes()).hexdigest()
    q = tmp_path / "m2.json"
    cc.write_manifest(q, DATA, seed=7)
    assert p.read_bytes() == q.read_bytes()
