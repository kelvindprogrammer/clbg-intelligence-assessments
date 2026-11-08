"""Public requirement tests. They FAIL on the starter. Assessors run a larger hidden suite on regenerated data."""
import math

import numpy as np
import pytest
from scipy import stats

import interval_lab as il
from conftest import DATA


# R1
def test_t_interval_known_values():
    lo, hi = il.t_interval([1, 2, 3, 4, 5])
    h = stats.t.ppf(0.975, 4) * np.std([1, 2, 3, 4, 5], ddof=1) / math.sqrt(5)
    assert (lo, hi) == pytest.approx((3 - h, 3 + h))


def test_t_interval_rejects_tiny_samples_and_bad_levels():
    with pytest.raises(ValueError):
        il.t_interval([4.0])
    with pytest.raises(ValueError):
        il.t_interval([1, 2, 3], level=1.2)


# R2
def test_bootstrap_follows_the_stated_resampling_scheme():
    x = np.array([3.0, 8, 1, 9, 4, 7, 12, 5, 2, 6])
    rng = np.random.default_rng(5)
    idx = rng.integers(0, 10, size=(400, 10))
    expected = np.quantile(x[idx].mean(axis=1), [0.05, 0.95])
    assert il.bootstrap_ci(x, np.mean, level=0.90, n_boot=400, seed=5) == pytest.approx(tuple(expected))


def test_bootstrap_is_deterministic_and_seed_sensitive():
    x = np.random.default_rng(1).lognormal(0, 1, 40)
    assert il.bootstrap_ci(x, seed=3) == il.bootstrap_ci(x, seed=3)
    assert il.bootstrap_ci(x, seed=3) != il.bootstrap_ci(x, seed=4)


def test_bootstrap_supports_other_statistics_and_degenerate_data():
    assert il.bootstrap_ci([7.0, 7.0, 7.0, 7.0], np.median, n_boot=50) == (7.0, 7.0)
    lo, hi = il.bootstrap_ci(np.arange(1.0, 31), np.median, n_boot=500, seed=2)
    assert lo < 15.5 < hi


# R3
def test_coverage_of_t_interval_on_normal_data_is_near_nominal():
    c = il.coverage(lambda rng, n: rng.normal(10, 3, n), 10.0, il.t_interval, n=30, reps=1500, seed=1)
    assert 0.93 <= c <= 0.97


def test_coverage_of_t_interval_on_skewed_small_samples_falls_short():
    true_mean = math.exp(1.5 ** 2 / 2)
    c = il.coverage(lambda rng, n: rng.lognormal(0, 1.5, n), true_mean, il.t_interval, n=10, reps=1500, seed=1)
    assert c < 0.90


# R4
def test_summarise_regions_structure():
    df = il.load_transactions(DATA)
    t = il.summarise_regions(df, n_boot=300, seed=1)
    assert list(t.columns) == ["region", "n", "mean", "t_lo", "t_hi", "boot_lo", "boot_hi", "median", "med_lo", "med_hi", "reliable"]
    assert list(t["region"]) == sorted(df["region"].unique())
    assert t["n"].sum() == len(df)


def test_summarise_regions_reliability_and_brackets():
    df = il.load_transactions(DATA)
    t = il.summarise_regions(df, n_boot=300, seed=1)
    assert (t["reliable"] == (t["n"] >= 30)).all() and (~t["reliable"]).any()
    assert ((t["t_lo"] < t["mean"]) & (t["mean"] < t["t_hi"])).all()
    assert ((t["boot_lo"] < t["mean"]) & (t["mean"] < t["boot_hi"])).all()


def test_small_regions_have_wider_intervals_than_large_ones():
    t = il.summarise_regions(il.load_transactions(DATA), n_boot=300, seed=1).set_index("region")
    rel = lambda r: (t.loc[r, "t_hi"] - t.loc[r, "t_lo"]) / t.loc[r, "mean"]
    assert rel("Gombe") > 2 * rel("Lagos")


# R5
def test_diff_means_interval_detects_a_clear_gap_and_is_reproducible():
    rng = np.random.default_rng(0)
    a, b = rng.normal(120, 20, 60), rng.normal(100, 20, 50)
    lo, hi = il.diff_means_ci_bootstrap(a, b, n_boot=800, seed=9)
    assert 0 < lo < 20 < hi and (lo, hi) == il.diff_means_ci_bootstrap(a, b, n_boot=800, seed=9)


# R6
@pytest.mark.parametrize("sd,margin,expected", [(2000, 500, 62), (10, 10, 4), (1, 0.1, 385)])
def test_required_n(sd, margin, expected):
    assert il.required_n(sd, margin) == expected


def test_required_n_rejects_nonsense():
    with pytest.raises(ValueError):
        il.required_n(0, 1)
