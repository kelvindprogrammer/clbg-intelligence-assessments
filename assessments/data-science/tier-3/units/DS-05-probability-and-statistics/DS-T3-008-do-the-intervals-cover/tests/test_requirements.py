"""Requirement tests. Thresholds are justified in README section G; fixed seeds make them deterministic for a given implementation,
and their margins cover the Monte Carlo noise a different (correct) implementation would show."""
import numpy as np
import pytest

import coverage_lab as cl

A = dict(k=40, m=10, sigma_u=0.0, sigma_e=1.0)   # no clustering
B = dict(k=20, m=25, sigma_u=1.0, sigma_e=1.0)   # strong clustering, heavy tail
KW = dict(reps=400, B=200, seed=11)


def test_icc_balanced():
    rng = np.random.default_rng(0)
    est = [cl.estimate_icc(*cl.simulate_normal(60, 15, 0.3, rng)) for _ in range(40)]
    assert abs(np.mean(est) - 0.3) < 0.03


def test_icc_unbalanced_and_zero():
    rng = np.random.default_rng(1)
    est = [cl.estimate_icc(*cl.simulate_normal(40, [5, 10, 20, 40] * 10, 0.2, rng)) for _ in range(40)]
    assert abs(np.mean(est) - 0.2) < 0.03
    est0 = [cl.estimate_icc(*cl.simulate_normal(40, 10, 0.0, rng)) for _ in range(40)]
    assert abs(np.mean(est0)) < 0.03


def test_iid_bootstrap_basics():
    y = np.random.default_rng(2).normal(10, 2, 200)
    lo, hi = cl.iid_bootstrap_ci(y, 500, 0.05, np.random.default_rng(3))
    assert lo < y.mean() < hi
    assert (hi - lo) == pytest.approx(2 * 1.96 * y.std(ddof=1) / np.sqrt(200), rel=0.15)
    assert cl.iid_bootstrap_ci(y, 500, 0.05, np.random.default_rng(3)) == (lo, hi)


def test_cluster_bootstrap_matches_robust_se():
    y, c = cl.simulate_normal(60, 15, 0.4, np.random.default_rng(4))
    lo, hi = cl.cluster_bootstrap_ci(y, c, 1000, 0.05, np.random.default_rng(5))
    sums = np.array([y[c == g].sum() for g in np.unique(c)])
    cnt = np.array([(c == g).sum() for g in np.unique(c)])
    mean = y.mean()
    se = np.sqrt(len(sums) / (len(sums) - 1) * ((sums - mean * cnt) ** 2).sum()) / len(y)
    assert (hi - lo) == pytest.approx(2 * 1.96 * se, rel=0.2)
    lo_i, hi_i = cl.iid_bootstrap_ci(y, 1000, 0.05, np.random.default_rng(5))
    assert (hi - lo) > 1.5 * (hi_i - lo_i)


def test_design_effect_ci_widens_under_clustering():
    y, c = cl.simulate_normal(50, 20, 0.4, np.random.default_rng(6))
    lo, hi = cl.design_effect_ci(y, c, 0.05)
    naive = 2 * 1.96 * y.std(ddof=1) / np.sqrt(len(y))
    assert (hi - lo) > 2.0 * naive
    y0, c0 = cl.simulate_normal(50, 20, 0.0, np.random.default_rng(7))
    lo0, hi0 = cl.design_effect_ci(y0, c0, 0.05)
    assert (hi0 - lo0) == pytest.approx(2 * 1.96 * y0.std(ddof=1) / np.sqrt(len(y0)), rel=0.35)


def test_coverage_without_clustering_is_nominal():
    r = cl.coverage_study("iid_bootstrap", **A, **KW)
    assert r["coverage"] >= 0.90  # nominal 0.95; the percentile bootstrap undercovers slightly for skewed data


def test_iid_bootstrap_fails_under_clustering():
    r = cl.coverage_study("iid_bootstrap", **B, **KW)
    assert r["coverage"] < 0.60  # reference ~0.44; a correct iid method must be far from 0.95 here


@pytest.mark.parametrize("method,floor", [("cluster_bootstrap", 0.80), ("design_effect", 0.78)])
def test_cluster_aware_methods_recover_most_coverage(method, floor):
    r = cl.coverage_study(method, **B, **KW)
    assert r["coverage"] >= floor
    assert r["mean_width"] > 1.8 * cl.coverage_study("iid_bootstrap", **B, **KW)["mean_width"]


def test_studentised_bootstrap_improves_coverage():
    kw = dict(reps=500, B=300, seed=11)
    plain = cl.coverage_study("cluster_bootstrap", **B, **kw)["coverage"]
    stud = cl.coverage_study("cluster_bootstrap_t", **B, **kw)["coverage"]
    assert stud >= 0.885 and stud > plain


def test_study_is_deterministic_and_reports_mcse():
    a = cl.coverage_study("cluster_bootstrap", k=10, m=10, sigma_u=0.5, sigma_e=0.5, reps=100, B=100, seed=3)
    b = cl.coverage_study("cluster_bootstrap", k=10, m=10, sigma_u=0.5, sigma_e=0.5, reps=100, B=100, seed=3)
    assert a == b and set(a) >= {"coverage", "mcse", "mean_width", "reps"}
    assert a["mcse"] == pytest.approx(np.sqrt(a["coverage"] * (1 - a["coverage"]) / 100))
    with pytest.raises(ValueError):
        cl.coverage_study("magic", k=5, m=5, sigma_u=0.1, sigma_e=0.1, reps=5, B=5, seed=1)


def test_reps_needed():
    assert cl.reps_needed(0.02) == 119
    assert cl.reps_needed(0.007) == 970
    assert cl.reps_needed(0.03, p=0.5) == 278
