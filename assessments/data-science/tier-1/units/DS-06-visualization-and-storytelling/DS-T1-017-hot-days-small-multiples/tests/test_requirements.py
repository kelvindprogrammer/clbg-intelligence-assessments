"""Public requirement tests. These FAIL on the starter until you implement the package.

All data here is synthetic, in POWER's layout, so the tests run offline. The hidden
suite uses other synthetic files (other layouts, gaps, leap years and city sets).
"""
import numpy as np
import pandas as pd
import pytest

import climate_story as cs
from powerfixture import synthetic_daily, write_power


@pytest.fixture(scope="module")
def daily():
    return synthetic_daily((1991, 2024), seed=4)


@pytest.fixture(scope="module")
def parsed(daily, tmp_path_factory):
    p = write_power(tmp_path_factory.mktemp("p") / "kano.csv", daily, missing_idx=[10, 11])
    return cs.read_power_csv(p)


# ---------------------------------------------------------------- R1
def test_read_power_csv_structure(parsed, daily):
    assert list(parsed.columns) == ["date", "t2m_max", "prectotcorr"]
    assert pd.api.types.is_datetime64_any_dtype(parsed["date"])
    assert len(parsed) == len(daily)
    assert parsed["date"].iloc[0] == pd.Timestamp("1991-01-01") and parsed["date"].iloc[-1] == pd.Timestamp("2024-12-31")


def test_missing_marker_becomes_nan(parsed):
    assert parsed["t2m_max"].isna().sum() == 2
    assert (parsed["t2m_max"].dropna() > -100).all()


def test_doy_handles_leap_years(parsed):
    row = parsed[parsed["date"] == pd.Timestamp("2024-12-31")]
    assert len(row) == 1
    assert (parsed["date"] == pd.Timestamp("2024-02-29")).sum() == 1


def test_month_day_layout_and_no_header(daily, tmp_path):
    p = write_power(tmp_path / "x.csv", daily.iloc[:400], layout="mdy", header=False)
    df = cs.read_power_csv(p)
    assert df["date"].iloc[59] == pd.Timestamp("1991-03-01")
    np.testing.assert_allclose(df["t2m_max"], daily["t2m_max"].iloc[:400])


# ---------------------------------------------------------------- R2
def test_annual_hot_days_counts(daily):
    a = cs.annual_hot_days(daily, 35.0)
    expected = (daily["t2m_max"] >= 35.0).groupby(daily["date"].dt.year).sum()
    assert list(a.index) == list(range(1991, 2025))
    np.testing.assert_allclose(a.to_numpy(float), expected.to_numpy(float))


def test_threshold_is_inclusive():
    d = pd.DataFrame({"date": pd.date_range("2001-01-01", "2001-12-31"), "t2m_max": 30.0})
    d.loc[:4, "t2m_max"] = 40.0
    assert cs.annual_hot_days(d, 40.0).loc[2001] == 5


def test_low_coverage_year_is_nan_not_low(daily):
    d = daily.copy()
    y2000 = d["date"].dt.year == 2000
    idx = d.index[y2000][:40]          # 40 of 366 days missing: coverage 89.1% < 90%
    d.loc[idx, "t2m_max"] = np.nan
    a = cs.annual_hot_days(d, 35.0)
    assert np.isnan(a.loc[2000])
    d2 = daily.copy()
    d2.loc[d2.index[y2000][:36], "t2m_max"] = np.nan   # 36 missing: coverage 90.2% >= 90%
    assert not np.isnan(cs.annual_hot_days(d2, 35.0).loc[2000])


# ---------------------------------------------------------------- R3 / R4 / R5
def test_percentile_threshold(daily):
    y = daily["date"].dt.year
    expected = np.quantile(daily.loc[(y >= 1991) & (y <= 2005), "t2m_max"], 0.9)
    assert cs.percentile_threshold(daily) == pytest.approx(expected)


def test_period_change(daily):
    a = pd.Series(np.arange(1991, 2025, dtype=float) - 1990, index=range(1991, 2025))
    pc = cs.period_change(a)
    assert pc["base_mean"] == pytest.approx(8.0) and pc["recent_mean"] == pytest.approx(27.0)
    assert pc["change"] == pytest.approx(19.0) and pc["n_base"] == 15 and pc["n_recent"] == 15


def test_period_change_refuses_thin_periods():
    a = pd.Series(1.0, index=range(1991, 2025))
    a.loc[1991:1996] = np.nan                     # only 9 valid base years
    with pytest.raises(ValueError):
        cs.period_change(a)


def test_monthly_climatology(daily):
    c = cs.monthly_climatology(daily, (2010, 2024))
    assert list(c.index) == list(range(1, 13))
    sub = daily[daily["date"].dt.year.between(2010, 2024)]
    assert c.loc[4] == pytest.approx(sub.loc[sub["date"].dt.month == 4, "t2m_max"].mean())


# ---------------------------------------------------------------- R6
def _series():
    rng = np.random.default_rng(0)
    lat = {"Lagos": 6.45, "Kano": 12.0, "Abuja": 9.06, "Sokoto": 13.06, "Enugu": 6.44}
    s = {c: pd.Series(rng.integers(0, 90, 34).astype(float), index=range(1991, 2025)) for c in lat}
    return s, lat


def test_small_multiples_layout():
    s, lat = _series()
    fig = cs.small_multiples(s, lat, title="Hot days", ylabel="Days", xlabel="Year", source="NASA POWER (synthetic test)")
    assert len(fig.axes) == 5, "one axes per city, unused grid cells removed"
    titles = [ax.get_title(loc="left") or ax.get_title() for ax in fig.axes]
    assert titles == ["Sokoto", "Kano", "Abuja", "Lagos", "Enugu"], "north to south in reading order"
    lims = {tuple(np.round(ax.get_ylim(), 6)) for ax in fig.axes}
    assert len(lims) == 1, "shared y-axis by default"
    assert fig.axes[0].get_ylim()[0] == 0, "counts start at zero"
    assert fig.axes[0].get_ylabel().strip()
    assert fig._suptitle is not None and fig._suptitle.get_text() == "Hot days"
    assert any(t.get_text().startswith("Source:") and "NASA POWER" in t.get_text() for t in fig.texts)


def test_small_multiples_draws_each_series():
    s, lat = _series()
    fig = cs.small_multiples(s, lat, title="t", ylabel="Days", kind="bar")
    by_title = {(ax.get_title(loc="left") or ax.get_title()): ax for ax in fig.axes}
    for city, ser in s.items():
        heights = [p.get_height() for c in by_title[city].containers for p in c.patches]
        np.testing.assert_allclose(heights, ser.to_numpy(float))


def test_small_multiples_rejects_unknown_latitude():
    s, lat = _series()
    del lat["Kano"]
    with pytest.raises(ValueError):
        cs.small_multiples(s, lat, title="t", ylabel="y")
