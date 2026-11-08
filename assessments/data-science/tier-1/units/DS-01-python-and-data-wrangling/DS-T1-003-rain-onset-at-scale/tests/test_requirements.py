"""Public requirement tests. These FAIL on the starter until you implement rainfall/fast.py.

They are a sample. Assessors run a larger hidden suite with different adversarial records
and a larger timing benchmark. Add your own tests in tests/test_member_*.py.
"""
import time

import numpy as np
import pandas as pd
import pytest

from conftest import assert_equivalent, random_case

import rainfall as rf


@pytest.mark.parametrize("name", ["monthly_totals", "longest_dry_spell", "onset_dates", "standardised_anomalies"])
def test_equivalent_on_sample(sample, name):
    assert_equivalent(getattr(rf.legacy, name)(sample), getattr(rf.fast, name)(sample))


@pytest.mark.parametrize("seed", range(8))
@pytest.mark.parametrize("name", ["monthly_totals", "longest_dry_spell", "onset_dates", "standardised_anomalies"])
def test_equivalent_on_awkward_records(seed, name):
    df = random_case(seed)
    assert_equivalent(getattr(rf.legacy, name)(df), getattr(rf.fast, name)(df))


def _days(start, values, station="X"):
    d = pd.date_range(start, periods=len(values), freq="D").astype("datetime64[ns]")
    return pd.DataFrame({"station_id": station, "date": d, "rain_mm": np.array(values, dtype=float)})


def test_absent_day_counts_as_missing_in_monthly_totals():
    df = _days("2004-02-01", [1.0] * 29).drop(index=10)   # 2004 is a leap year; 11 Feb has no row
    out = rf.fast.monthly_totals(df)
    feb = out[(out["year"] == 2004) & (out["month"] == 2)].iloc[0]
    assert feb["n_missing"] == 1 and np.isnan(feb["total_mm"])
    assert len(out) == 12                                   # every month of the station's year


def test_missing_day_breaks_a_dry_spell():
    vals = [0.0] * 5 + [np.nan] + [0.0] * 4 + [5.0]
    out = rf.fast.longest_dry_spell(_days("2010-04-01", vals))
    assert out["longest_dry_spell"].tolist() == [5]


def test_onset_rejects_a_false_start():
    # 25 mm over 3 days on 1 March, then 7 dry days: a false start. Real onset on 15 March.
    vals = [10.0, 10.0, 5.0] + [0.0] * 11 + [8.0, 8.0, 8.0] + [3.0] * 40
    out = rf.fast.onset_dates(_days("2010-03-01", vals))
    assert out["onset_date"].tolist() == [pd.Timestamp("2010-03-15")]
    assert out["onset_doy"].tolist() == [74]


def test_onset_needs_a_complete_lookahead():
    vals = [10.0, 10.0, 5.0] + [3.0] * 20                  # data ends before d+30
    out = rf.fast.onset_dates(_days("2010-03-01", vals))
    assert out["onset_date"].isna().all() and out["onset_doy"].isna().all()


def test_fast_is_meaningfully_faster_on_sample(sample):
    """A loose public check. The real speed criteria are in README section G."""
    for name in ["monthly_totals", "onset_dates"]:
        t0 = time.perf_counter()
        getattr(rf.legacy, name)(sample)
        legacy = time.perf_counter() - t0
        best = min(_timed(getattr(rf.fast, name), sample) for _ in range(3))
        assert legacy / best >= 3, f"{name}: only {legacy / best:.1f}x faster than legacy"


def _timed(fn, df):
    t0 = time.perf_counter()
    fn(df)
    return time.perf_counter() - t0
