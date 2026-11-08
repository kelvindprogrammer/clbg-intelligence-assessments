"""Public requirement tests for the alignment primitives. These FAIL on the starter.

They pin the alignment rules that every design in your comparison depends on. The hidden suite
re-checks them on re-seeded synthetic series and on unseen edge cases.
"""
import json

import numpy as np
import pandas as pd
import pytest

from conftest import FAO, POWER

import climfuse as cf


def daily(start, end, value=1.0):
    d = pd.date_range(start, end, freq="D")
    return pd.DataFrame({"date": d, "value": value})


# ---------------------------------------------------------------- R1
def test_read_power_real_fixture():
    df = cf.read_power(POWER)
    assert list(df.columns) == ["date", "parameter", "value"]
    assert len(df) == 2 * 366 and df["value"].notna().all()
    rain = df[df.parameter == "PRECTOTCORR"].set_index("date")["value"]
    assert rain.loc["2020-08"].sum() > rain.loc["2020-01"].sum(), "August is wetter than January in Kaduna"


def test_read_power_fill_values_become_nan(tmp_path):
    doc = json.loads(POWER.read_text(encoding="utf-8"))
    doc["properties"]["parameter"]["PRECTOTCORR"]["20200715"] = -999.0
    p = tmp_path / "p.json"
    p.write_text(json.dumps(doc), encoding="utf-8")
    df = cf.read_power(p)
    v = df[(df.parameter == "PRECTOTCORR") & (df.date == "2020-07-15")]["value"]
    assert v.isna().all(), "-999 is POWER's fill value, not a rainfall amount"


# ---------------------------------------------------------------- R2
def test_season_sum_and_calendar():
    r = cf.season_aggregate(daily("2019-01-01", "2021-12-31"), "06-01", "09-30", "sum")
    assert list(r.columns[:5]) == ["year", "value", "n_days", "n_valid", "coverage"]
    assert r.set_index("year")["value"].to_dict() == {2019: 122.0, 2020: 122.0, 2021: 122.0}


def test_season_leap_years():
    r = cf.season_aggregate(daily("2020-01-01", "2021-12-31"), "02-01", "02-29", "sum").set_index("year")
    assert r.loc[2020, "n_days"] == 29 and r.loc[2021, "n_days"] == 28


def test_missing_rows_count_as_missing_and_coverage_rule():
    d = daily("2020-01-01", "2020-12-31")
    jjas = (d.date >= "2020-06-01") & (d.date <= "2020-09-30")
    idx = d[jjas].index
    few = d.drop(idx[:6])      # 6 of 122 days absent: coverage 0.951
    many = d.drop(idx[:20])    # 20 of 122 days absent: coverage 0.836
    r1 = cf.season_aggregate(few).set_index("year")
    r2 = cf.season_aggregate(many).set_index("year")
    assert r1.loc[2020, "coverage"] == pytest.approx(116 / 122, abs=1e-4)
    assert r1.loc[2020, "value"] == pytest.approx(122.0), "a sum over a short season is scaled to the full season"
    assert np.isnan(r2.loc[2020, "value"]), "below min_coverage the season is unknown, not small"


def test_nan_values_count_as_missing():
    d = daily("2020-01-01", "2020-12-31")
    d.loc[(d.date >= "2020-07-01") & (d.date < "2020-07-21"), "value"] = np.nan
    assert np.isnan(cf.season_aggregate(d).set_index("year").loc[2020, "value"])


def test_season_crossing_new_year_belongs_to_end_year():
    r = cf.season_aggregate(daily("2019-01-01", "2021-12-31"), "11-01", "02-28", "sum").set_index("year")
    assert r.loc[2020, "n_days"] == 30 + 31 + 31 + 29 - 1  # Nov 2019 + Dec 2019 + Jan 2020 + Feb 1-28 2020
    assert r.loc[2020, "value"] == pytest.approx(120.0)


def test_season_mean():
    d = daily("2020-01-01", "2020-12-31")
    d["value"] = np.where(d.date.dt.month == 7, 30.0, 20.0)
    r = cf.season_aggregate(d, "07-01", "08-31", "mean").set_index("year")
    assert r.loc[2020, "value"] == pytest.approx(25.0)


# ---------------------------------------------------------------- R3
def test_weighted_mean_renormalises():
    a = pd.Series({2000: 10.0, 2001: 10.0, 2002: np.nan})
    b = pd.Series({2000: 20.0, 2001: np.nan, 2002: np.nan})
    r = cf.weighted_mean({"a": a, "b": b}, {"a": 1, "b": 3}).set_index("year")
    assert r.loc[2000, "value"] == pytest.approx(17.5)
    assert r.loc[2001, "value"] == pytest.approx(10.0) and r.loc[2001, "weight_used"] == pytest.approx(0.25)
    assert np.isnan(r.loc[2002, "value"]) and r.loc[2002, "weight_used"] == 0
    with pytest.raises(ValueError):
        cf.weighted_mean({"a": a}, {"a": -1})


# ---------------------------------------------------------------- R4
def test_read_faostat_wide_real_extract():
    y = cf.read_faostat_wide(FAO, "Nigeria", ["Maize (corn)", "Sorghum"], "Yield")
    assert list(y.columns) == ["year", "item", "value", "unit", "flag"]
    maize = y[y.item == "Maize (corn)"].set_index("year")
    assert maize.loc[2024, "value"] == pytest.approx(2029.8) and maize.loc[2024, "flag"] == "X"
    assert maize.loc[2019, "flag"] == "E" and maize.loc[2015, "flag"] == "A"
    assert set(y.unit) == {"kg/ha"} and y.year.min() == 1961


# ---------------------------------------------------------------- R5
def test_detrend():
    s = pd.Series({y: 2.0 * y + 5 for y in range(1990, 2010)})
    assert cf.detrend(s, "linear").abs().max() < 1e-6
    s2 = s.copy()
    s2[1995] = np.nan
    d = cf.detrend(s2, "linear")
    assert np.isnan(d[1995]) and d.drop(1995).abs().max() < 1e-6
    assert cf.detrend(s, "first_difference").dropna().eq(2.0).all()


# ---------------------------------------------------------------- R6
def test_align_keeps_provenance_and_refuses_duplicates():
    a = pd.DataFrame({"year": [2000, 2001, 2002], "value": [1.0, 2.0, 3.0], "coverage": [1, 0.95, 1]})
    b = pd.DataFrame({"year": [2001, 2002], "value": [5.0, 6.0], "flag": ["A", "E"]})
    j = cf.align({"rain": a, "yield": b})
    assert list(j.year) == [2001, 2002]
    assert {"rain", "rain__coverage", "yield", "yield__flag"} <= set(j.columns)
    with pytest.raises(ValueError):
        cf.align({"x": pd.DataFrame({"year": [2000, 2000], "value": [1, 2]})})
