"""Public requirement tests. These FAIL on the starter until you implement the package.

They are a sample of the requirements. Assessors run a larger hidden suite with other
distributions, seeds and edge cases. Write your own tests in tests/test_member_*.py.
"""
import math

import numpy as np
import pytest
from scipy import stats

import sure_ci as s


# ---------------------------------------------------------------- R1-R2
def test_t_interval_matches_scipy():
    x = np.array([3.1, 4.7, 2.2, 5.9, 4.4, 3.8, 6.1, 2.9])
    lo, hi = s.t_interval(x, 0.90)
    ref = stats.t.interval(0.90, df=7, loc=x.mean(), scale=stats.sem(x))
    assert (lo, hi) == pytest.approx(ref, rel=1e-10)


@pytest.mark.parametrize("k,n", [(0, 25), (1, 40), (3, 40), (17, 30), (30, 30)])
def test_wilson_and_exact_match_scipy(k, n):
    bt = stats.binomtest(k, n)
    assert s.wilson_interval(k, n) == pytest.approx(tuple(bt.proportion_ci(0.95, method="wilson")), abs=1e-10)
    assert s.clopper_pearson_interval(k, n) == pytest.approx(tuple(bt.proportion_ci(0.95, method="exact")), abs=1e-10)


def test_wald_degenerates_at_zero_events():
    assert s.wald_interval(0, 40) == (0.0, 0.0)          # the failure the study must expose
    lo, hi = s.wald_interval(8, 40)
    assert (lo, hi) == pytest.approx((0.2 - 1.959964 * math.sqrt(0.2 * 0.8 / 40), 0.2 + 1.959964 * math.sqrt(0.2 * 0.8 / 40)), rel=1e-6)


@pytest.mark.parametrize("bad", [lambda: s.wilson_interval(5, 3), lambda: s.t_interval([1.0]),
                                 lambda: s.wald_interval(1, 10, level=1.5)])
def test_invalid_input_raises(bad):
    with pytest.raises(ValueError):
        bad()


# ---------------------------------------------------------------- R3-R4
def test_bootstrap_replicates_shape_and_reproducibility():
    x = np.arange(1.0, 21.0)
    a = s.bootstrap_replicates(x, np.mean, 500, np.random.default_rng(3))
    b = s.bootstrap_replicates(x, np.mean, 500, np.random.default_rng(3))
    assert a.shape == (500,) and np.array_equal(a, b)
    assert abs(a.mean() - x.mean()) < 0.5 and a.std() == pytest.approx(x.std() / math.sqrt(20), rel=0.15)


def test_basic_is_percentile_reflected():
    x = np.random.default_rng(4).lognormal(0, 1, 25)
    p = s.percentile_interval(x, np.mean, B=4000, rng=np.random.default_rng(9))
    b = s.basic_interval(x, np.mean, B=4000, rng=np.random.default_rng(9))
    assert b == pytest.approx((2 * x.mean() - p[1], 2 * x.mean() - p[0]), rel=1e-12)


def test_jackknife_values():
    x = np.array([1.0, 2.0, 6.0])
    assert np.allclose(s.jackknife_values(x, np.mean), [4.0, 3.5, 1.5])


def test_bca_close_to_scipy_on_skewed_data():
    x = np.random.default_rng(1).lognormal(0, 1.2, 30)
    lo, hi = s.bca_interval(x, np.mean, B=20000, rng=np.random.default_rng(5))
    try:
        ref = stats.bootstrap((x,), np.mean, n_resamples=20000, method="BCa", rng=np.random.default_rng(6))
    except TypeError:  # older SciPy
        ref = stats.bootstrap((x,), np.mean, n_resamples=20000, method="BCa", random_state=np.random.default_rng(6))
    width = hi - lo
    assert abs(lo - ref.confidence_interval.low) < 0.05 * width
    assert abs(hi - ref.confidence_interval.high) < 0.05 * width


def test_bca_constant_sample():
    assert s.bca_interval(np.full(12, 7.0), np.mean, B=200, rng=np.random.default_rng(0)) == (7.0, 7.0)


# ---------------------------------------------------------------- R5
def test_coverage_of_t_interval_on_normal_data():
    r = s.coverage_experiment(lambda rng, n: rng.normal(10, 2, n), 10.0, lambda x, rng: s.t_interval(x),
                              n=15, reps=4000, rng=np.random.default_rng(2026))
    assert abs(r.coverage - 0.95) < 4 * math.sqrt(0.95 * 0.05 / 4000)
    assert r.mc_se == pytest.approx(math.sqrt(r.coverage * (1 - r.coverage) / 4000))
    assert r.coverage + r.miss_below + r.miss_above == pytest.approx(1.0)


# ---------------------------------------------------------------- R6-R7
def test_study_reveals_the_known_failures():
    df = s.run_study(reps=400, B=400, seed=7, ns=(40,))
    assert list(df.columns) == s.STUDY_COLUMNS
    assert len(df) == 10
    get = lambda e, m: df[(df.estimand == e) & (df.method == m)].iloc[0]
    assert get("proportion", "wald").coverage < 0.88       # Wald collapses for p = 0.04, n = 40
    assert get("proportion", "wilson").coverage > 0.92
    t = get("mean", "t")
    assert t.coverage < 0.93 and t.miss_below > 4 * t.miss_above   # one-sided failure on skewed data


def test_survey_analysis(survey):
    out = s.analyse_survey(survey, B=2000, seed=1)
    assert list(out.columns) == s.SURVEY_COLUMNS
    assert list(out["lga"]) == sorted(survey["lga"].unique())
    assert (out["n"].sum()) == len(survey)
    zero = out[out["fraud_k"] == 0]
    assert len(zero) >= 1 and (zero["fraud_wilson_hi"] > 0.05).all()
    assert ((out["mean_bca_lo"] < out["mean"]) & (out["mean"] < out["mean_bca_hi"])).all()
