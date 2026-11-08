"""Public requirement tests: they FAIL on the starter. The hidden suite adds other parameter
regimes (including bounded tails), a coverage experiment for your interval method and a
non-stationary check. Write your own tests in tests/test_member_*.py."""
import math

import numpy as np
import pandas as pd
import pytest
from scipy import stats

import eva


def _gev_sample(xi, loc, scale, n, seed):
    return stats.genextreme.rvs(-xi, loc=loc, scale=scale, size=n, random_state=np.random.default_rng(seed))


def test_annual_maxima_respects_coverage(daily):
    am = eva.annual_maxima(daily)
    assert list(am.columns) == ["year", "max_mm", "coverage"]
    assert (am["coverage"] >= 0.9).all() and am["year"].is_monotonic_increasing
    all_years = eva.annual_maxima(daily, min_coverage=0.0)
    assert len(all_years) == 44 and len(am) < 44
    y = all_years.set_index("year")
    assert y.loc[1985, "max_mm"] == pytest.approx(daily[daily.date.dt.year == 1985]["rain_mm"].max())


def test_gev_recovers_known_parameters_and_sign():
    x = _gev_sample(0.15, 100.0, 30.0, 3000, 1)
    p = eva.fit_gev(x)
    assert p.shape == pytest.approx(0.15, abs=0.04), "shape convention: xi > 0 is a heavy upper tail"
    assert p.loc == pytest.approx(100.0, rel=0.03) and p.scale == pytest.approx(30.0, rel=0.06)


def test_gev_return_level_formula():
    p = eva.GEVParams(100.0, 30.0, 0.15)
    for T in (2, 25, 100):
        assert eva.gev_return_level(p, T) == pytest.approx(stats.genextreme.ppf(1 - 1 / T, -0.15, 100, 30), rel=1e-9)
    g = eva.GEVParams(100.0, 30.0, 0.0)
    assert eva.gev_return_level(g, 100) == pytest.approx(stats.gumbel_r.ppf(0.99, 100, 30), rel=1e-9)
    with pytest.raises(ValueError):
        eva.gev_return_level(p, 1.0)


def test_return_level_ci_contains_estimate_and_narrows():
    small = _gev_sample(0.1, 100, 30, 40, 2)
    big = _gev_sample(0.1, 100, 30, 400, 3)
    z, lo, hi = eva.return_level_ci(small, 25)
    zb, lob, hib = eva.return_level_ci(big, 25)
    assert lo < z < hi and lob < zb < hib
    assert (hib - lob) < 0.6 * (hi - lo)
    truth = stats.genextreme.ppf(1 - 1 / 25, -0.1, 100, 30)
    assert lob < truth < hib


def test_decluster_runs_toy_series():
    v = [0, 5, 7, 0, 6, 0, 0, 0, 9, np.nan, 0, 8, 8]
    assert list(eva.decluster_runs(v, 4.0, run_length=2)) == [7, 9, 8]
    assert list(eva.decluster_runs(v, 4.0, run_length=1)) == [7, 6, 9, 8]


def test_gpd_fit_and_return_level():
    e = stats.genpareto.rvs(0.2, scale=20, size=4000, random_state=np.random.default_rng(4))
    s, xi = eva.fit_gpd(e)
    assert xi == pytest.approx(0.2, abs=0.05) and s == pytest.approx(20, rel=0.08)
    z = eva.gpd_return_level(50.0, 20.0, 0.2, 3.0, 100)
    assert z == pytest.approx(50 + 20 / 0.2 * (300 ** 0.2 - 1), rel=1e-12)
    assert eva.gpd_return_level(50.0, 20.0, 0.0, 3.0, 100) == pytest.approx(50 + 20 * math.log(300), rel=1e-9)


def test_official_record_gives_plausible_levels(daily):
    am = eva.annual_maxima(daily)
    p = eva.fit_gev(am["max_mm"])
    z25 = eva.gev_return_level(p, 25)
    assert am["max_mm"].median() < z25 < 3 * am["max_mm"].max()
