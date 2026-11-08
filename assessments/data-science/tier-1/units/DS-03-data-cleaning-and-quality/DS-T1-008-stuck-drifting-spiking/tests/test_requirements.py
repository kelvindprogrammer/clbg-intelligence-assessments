"""Public requirement tests. These FAIL on the starter until you implement the package.

They are a sample of the rules, not the full set. Assessors run a larger hidden suite on
re-generated feeds in which every fault sits on a different device, scored against ground
truth. Write your own tests in tests/test_member_*.py.
"""
import os
import subprocess
import sys

import numpy as np
import pandas as pd
import pytest

from conftest import DATA

import sensorqc as qc


# ---------------------------------------------------------------- R1
def test_range_flags():
    v = pd.Series([-1.0, 0.0, 50.0, 1000.0, 6553.5, np.nan], index=list("abcdef"))
    f = qc.range_flags(v, 0, 1000)
    assert list(f.index) == list("abcdef")
    assert f.tolist() == [True, False, False, False, True, False]


# ---------------------------------------------------------------- R2
def test_stuck_flags_runs_and_nan_breaks():
    v = pd.Series([1, 1, 1, 2, 2, np.nan, 2, 2, 2, 3], dtype=float)
    assert qc.stuck_flags(v, 3).tolist() == [True, True, True, False, False, False, True, True, True, False]


def test_stuck_flags_exact_threshold():
    v = pd.Series([5.0] * 11 + [6.0])
    assert not qc.stuck_flags(v, 12).any()
    assert qc.stuck_flags(v, 11).sum() == 11


# ---------------------------------------------------------------- R3
def test_spike_flags_isolated_spike():
    v = pd.Series([40, 42, 41, 43, 40, 400, 41, 42, 40, 43, 41], dtype=float)
    f = qc.spike_flags(v, half_window=3, k=4.0, min_abs=25)
    assert f.tolist() == [False] * 5 + [True] + [False] * 5


def test_spike_flags_ramp_is_not_a_spike():
    ramp = pd.Series(np.r_[np.full(10, 40.0), np.linspace(40, 200, 9), np.full(10, 200.0)])
    assert not qc.spike_flags(ramp, 3, 4.0, 25).any()


def test_spike_flags_min_abs_floor():
    v = pd.Series([20.0, 20.0, 20.0, 30.0, 20.0, 20.0, 20.0])  # MAD = 0, deviation 10
    assert not qc.spike_flags(v, 3, 4.0, 25).any()
    assert qc.spike_flags(v, 3, 4.0, 5).tolist() == [False, False, False, True, False, False, False]


def test_spike_flags_needs_enough_neighbours():
    v = pd.Series([np.nan, np.nan, np.nan, 500.0, np.nan, np.nan, 40.0])
    assert not qc.spike_flags(v, 3, 4.0, 25).any()


# ---------------------------------------------------------------- R4
def test_find_gaps():
    t = pd.Series(pd.to_datetime(["2026-03-02T00:00:00Z", "2026-03-02T00:05:00Z", "2026-03-02T00:25:00Z",
                                  "2026-03-02T00:30:00Z", "2026-03-02T00:36:00Z"]))
    g = qc.find_gaps(t, 300)
    assert list(g.columns) == ["gap_start", "gap_end", "missing_samples"]
    assert len(g) == 1 and int(g["missing_samples"].iloc[0]) == 3


# ---------------------------------------------------------------- R6
def test_qc_level_precedence():
    assert qc.qc_level(0) == "good"
    assert qc.qc_level(qc.DRIFT_CORRECTED) == "good"
    assert qc.qc_level(qc.HUMIDITY) == "suspect"
    assert qc.qc_level(qc.HUMIDITY | qc.SPIKE) == "bad"
    assert qc.qc_level(qc.CLOCK_STEP | qc.DRIFT_CORRECTED) == "bad"
    assert qc.qc_level(qc.MISSING | qc.CLOCK_STEP) == "missing"


# ---------------------------------------------------------------- R5
def _synthetic_clock(drift, n=2000, seed=0, late_uploads=True):
    rng = np.random.default_rng(seed)
    true = pd.date_range("2026-03-02", periods=n, freq="300s", tz="UTC")
    days = np.arange(n) * 300 / 86400
    dev = true - pd.to_timedelta(drift * days, unit="s")
    lat = rng.exponential(8, n) + 1
    if late_uploads:
        lat[rng.choice(n, n // 20, replace=False)] += rng.uniform(3600, 18000, n // 20)  # late batch uploads
    rec = true + pd.to_timedelta(lat, unit="s")
    fmt = lambda s: pd.Series(s.strftime("%Y-%m-%dT%H:%M:%S"))
    return fmt(dev), pd.Series(rec.strftime("%Y-%m-%dT%H:%M:%SZ"))


@pytest.mark.parametrize("drift", [0.0, 60.0, -45.0])
def test_estimate_clock_drift_is_robust_to_late_uploads(drift):
    dev, rec = _synthetic_clock(drift)
    ce = qc.estimate_clock(dev, rec, "2026-02-23", 300)
    assert ce.drift_s_per_day == pytest.approx(drift, abs=3)
    assert not ce.step_mask.any(), "late uploads are not clock faults"


def test_estimate_clock_steps():
    dev, rec = _synthetic_clock(20.0, n=600, late_uploads=False)
    dev.iloc[100:130] = pd.date_range("2000-01-01", periods=30, freq="300s").strftime("%Y-%m-%dT%H:%M:%S")
    ahead = pd.to_datetime(dev.iloc[300:320]) + pd.Timedelta(hours=2)
    dev.iloc[300:320] = ahead.dt.strftime("%Y-%m-%dT%H:%M:%S")
    ce = qc.estimate_clock(dev, rec, "2026-02-23", 300)
    expected = np.zeros(600, dtype=bool)
    expected[100:130] = expected[300:320] = True
    assert list(ce.step_mask.index) == list(dev.index)
    assert ce.step_mask.to_numpy().tolist() == expected.tolist()


# ---------------------------------------------------------------- R7-R8 (end-to-end)
@pytest.fixture(scope="module")
def result(raw, config):
    return qc.run_qc(raw, config)


def test_long_format_complete(result, raw):
    from sensorqc.pipeline import CLOCK_COLUMNS, GAP_COLUMNS, READING_COLUMNS
    r = result.readings
    assert list(r.columns) == READING_COLUMNS
    assert list(result.gaps.columns) == GAP_COLUMNS
    assert list(result.clocks.columns) == CLOCK_COLUMNS
    assert len(r) == 3 * len(raw)
    assert set(zip(r["reading_id"], r["variable"])) == {(i, v) for i in raw["reading_id"] for v in qc.VARIABLES}


def test_levels_consistent_with_bits(result):
    r = result.readings
    assert (r["qc_level"] == r["qc_flags"].astype(int).map(qc.qc_level)).all()


def test_clock_step_readings_have_no_timestamp(result):
    r = result.readings
    step = (r["qc_flags"].astype(int) & qc.CLOCK_STEP) > 0
    assert step.sum() > 0
    assert (r.loc[step, "timestamp_utc"].astype(str) == "").all()
    assert (r.loc[~step, "timestamp_utc"].astype(str) != "").all()


def test_sentinels_are_range_failures(result):
    r = result.readings
    sentinel = r["value"].astype(str).isin(["6553.5", "655.3", "-40.0"])
    assert sentinel.sum() > 0
    assert ((r.loc[sentinel, "qc_flags"].astype(int) & qc.RANGE) > 0).all()


def test_exactly_one_device_needs_drift_correction(result):
    c = result.clocks
    assert c["corrected"].astype(str).eq("True").sum() == 1
    assert c["drift_s_per_day"].astype(float).abs().max() > 30


def test_humidity_bit_only_on_pm25(result):
    r = result.readings
    hum = (r["qc_flags"].astype(int) & qc.HUMIDITY) > 0
    assert hum.sum() > 0 and set(r.loc[hum, "variable"]) == {"pm25"}


def test_hourly_coverage_rule(result):
    from sensorqc.pipeline import HOURLY_COLUMNS
    h = qc.hourly_means(result.readings, 0.75, 300)
    assert list(h.columns) == HOURLY_COLUMNS
    ok = h["status"] == "ok"
    assert (h.loc[ok, "n_good"] >= 9).all() and h.loc[ok, "mean"].notna().all()
    assert h.loc[~ok, "mean"].isna().all() and (h.loc[~ok, "n_good"] < 9).all()
    assert (~ok).sum() > 0


def test_cli_runs(tmp_path):
    proc = subprocess.run([sys.executable, "-m", "sensorqc", str(DATA), "--out", str(tmp_path)],
                          capture_output=True, text=True, timeout=300,
                          env={**os.environ, "PYTHONPATH": os.pathsep.join(p for p in sys.path if p)})
    assert proc.returncode == 0, proc.stderr
    for name in ["readings_qc.csv", "gaps.csv", "clocks.csv", "hourly.csv"]:
        assert (tmp_path / name).exists(), name
