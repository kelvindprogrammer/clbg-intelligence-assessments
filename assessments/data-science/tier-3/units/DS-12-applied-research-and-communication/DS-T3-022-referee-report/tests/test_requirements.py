"""Public requirement tests (a sample; assessors run a hidden suite on freshly generated lending data).
They check your tools on small planted examples. What the tools reveal about the whitepaper is for your report."""
import numpy as np
import pandas as pd
import pytest

from conftest import DATA

import refereekit as rk


@pytest.fixture(scope="module")
def df():
    return rk.load_export(DATA)


def _toy():
    # Within each stratum the treated do worse (+10 points), but the treated sit mostly in the safe stratum A.
    rows = []
    for t, s, n, k in [(1, "A", 90, 18), (1, "B", 10, 6), (0, "A", 10, 1), (0, "B", 90, 45)]:
        rows += [{"treated": t, "stratum": s, "y": 1 if i < k else 0} for i in range(n)]
    return pd.DataFrame(rows)


def test_r1_simpson_reversal_detected():
    r = rk.simpson_check(_toy(), "y", "treated", "stratum")
    assert r["overall_diff"] == pytest.approx(0.24 - 0.46)
    assert r["stratum_diffs"] == pytest.approx({"A": 0.10, "B": 0.10})
    assert r["std_diff"] == pytest.approx(0.10) and r["reversal"] is True
    assert r["composition_shift"] == pytest.approx(0.8)


def test_r1_ignores_null_outcomes_and_strata_with_one_arm():
    d = _toy().astype({"y": "float"})
    d.loc[0, "y"] = np.nan
    d = pd.concat([d, pd.DataFrame({"treated": [1, 1], "stratum": ["C", "C"], "y": [1.0, 0.0]})], ignore_index=True)
    r = rk.simpson_check(d, "y", "treated", "stratum")
    assert set(r["stratum_diffs"]) == {"A", "B"}


def test_r1_on_the_export(df):
    r = rk.simpson_check(df[df["defaulted"].notna()], "defaulted", "treated", "risk_band")
    assert set(r["stratum_diffs"]) == {"low", "medium", "high"} and 0.1 < r["composition_shift"] < 0.35
    assert abs(r["std_diff"]) < abs(r["overall_diff"])


def test_r2_benjamini_hochberg_known_example():
    p = [0.01, 0.04, 0.03, 0.005, 0.5]
    adj, rej = rk.bh_adjust(p, q=0.05)
    assert np.allclose(adj, [0.025, 0.05, 0.05, 0.025, 0.5]) and rej.tolist() == [True, True, True, True, False]
    adj2, rej2 = rk.bh_adjust([0.2, 0.2, 0.2], q=0.1)
    assert np.allclose(adj2, 0.2) and not rej2.any()


def test_r3_subgroup_scan_structure_and_pvalue():
    rng = np.random.RandomState(0)
    d = pd.DataFrame({"treated": rng.randint(0, 2, 600), "g": rng.choice(["x", "y", "z"], 600), "h": rng.choice(["u", "v"], 600)})
    d["y"] = (rng.rand(600) < 0.3 + 0.2 * d["treated"] * (d["g"] == "x")).astype(int)
    s = rk.subgroup_scan(d, "y", "treated", ["h", "g"])
    assert list(s.columns) == ["column", "level", "n", "diff", "p"] and s["column"].tolist() == ["g", "g", "g", "h", "h"]
    assert s.set_index("level").loc["x", "p"] < 0.05 and s["p"].between(0, 1).all()
    assert s["n"].sum() == 1200


def test_r4_censoring_check_on_the_export(df):
    c = rk.censoring_check(df)
    assert c["matured_share"]["control"] == 1.0 and 0.7 < c["matured_share"]["treated"] < 0.9 and c["H"] == 90
    assert c["naive_default"]["control"] > c["common_window_default"]["control"]
    assert set(c) == {"matured_share", "naive_default", "H", "common_window_default"}


def test_r5_permutation_p_is_deterministic_and_a_valid_probability():
    rng = np.random.RandomState(3)
    d = pd.DataFrame({"treated": rng.randint(0, 2, 800), "score": rng.uniform(0, 100, 800)})
    d["y"] = (rng.rand(800) < 0.2).astype(int)           # no effect anywhere
    a = rk.max_stat_permutation_p(d, "y", "treated", "score", range(20, 80, 10), n_perm=199, seed=5)
    assert a == rk.max_stat_permutation_p(d, "y", "treated", "score", range(20, 80, 10), n_perm=199, seed=5)
    assert 1 / 200 <= a["p"] <= 1.0 and a["p"] > 0.05 and a["observed"] > 0
    d["y"] = (rng.rand(800) < 0.1 + 0.4 * d["treated"]).astype(int)    # a real, large effect
    assert rk.max_stat_permutation_p(d, "y", "treated", "score", range(20, 80, 10), n_perm=199, seed=5)["p"] <= 0.01


def test_r6_corrected_effect_uses_the_common_window(df):
    r = rk.corrected_effect(df, "risk_band", n_boot=200, seed=1)
    assert set(r) == {"estimate", "lo", "hi", "n", "H"} and r["H"] == 90
    assert r["n"] == (df["maturity_days"] <= 90).sum() and r["lo"] < r["estimate"] < r["hi"]
    naive = rk.simpson_check(df[df["defaulted"].notna()], "defaulted", "treated", "risk_band")["overall_diff"]
    assert abs(r["estimate"]) < abs(naive)
    assert r == rk.corrected_effect(df, "risk_band", n_boot=200, seed=1)
