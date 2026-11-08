"""Public requirement tests. These FAIL on the starter until you implement the package.

They are a sample. The hidden suite re-generates the logs with other seeds (different
misbanded feeders, collapse dates and coverage gaps), so hard-coded answers fail.
Add your own tests in tests/test_member_*.py.
"""
import datetime as dt
import json
import os
import subprocess
import sys

import numpy as np
import pandas as pd
import pytest

from conftest import DATA_DIR

import feeder_eda as fe

T = lambda s: pd.Timestamp(s)  # noqa: E731


# ---------------------------------------------------------------- R2
def test_merge_numbers():
    assert fe.merge_intervals([(5, 7), (1, 3), (2, 4), (4, 4.5), (8, 8)]) == [(1, 4.5), (5, 7)]


def test_merge_datetimes_touching():
    a = (dt.datetime(2025, 1, 1, 1), dt.datetime(2025, 1, 1, 2))
    b = (dt.datetime(2025, 1, 1, 2), dt.datetime(2025, 1, 1, 3))
    assert fe.merge_intervals([b, a]) == [(a[0], b[1])]


# ---------------------------------------------------------------- R1
def _raw(rows):
    return pd.DataFrame(rows, columns=["event_id", "feeder_id", "start", "end", "cause", "logged_by"])


def test_parse_events_rules():
    raw = _raw([
        ("E1", "F1", "2025-01-01 10:00", "2025-01-01 12:00", "fault", "ops1"),
        ("E2", "F1", "2025-01-01 15:00", "", "load_shedding", "ops1"),          # open, closed by E3
        ("E3", "F1", "2025-01-01 18:30", "2025-01-01 19:00", "fault", "ops1"),
        ("E4", "F1", "2025-01-02 09:00", "2025-01-01 09:00", "fault", "ops1"),  # invalid
        ("E5", "F2", "2025-06-30 22:00", "", "fault", "ops1"),                  # open, closed at export
    ])
    before = raw.copy()
    clean, issues = fe.parse_events(raw)
    pd.testing.assert_frame_equal(raw, before)
    assert list(clean["event_id"]) == ["E1", "E2", "E3", "E5"]
    c = clean.set_index("event_id")
    assert c.loc["E2", "end"] == T("2025-01-01 18:30") and c.loc["E2", "closed_by"] == "next_event"
    assert c.loc["E5", "end"] == T("2025-07-01 00:00") and c.loc["E5", "closed_by"] == "export"
    assert c.loc["E1", "closed_by"] == "logged"
    assert dict(zip(issues["event_id"], issues["issue_type"])) == {
        "E2": "open_closed_at_next_event", "E4": "end_not_after_start", "E5": "open_closed_at_export"}


# ---------------------------------------------------------------- R3
def _toy():
    feeders = pd.DataFrame({"feeder_id": ["F1"], "business_unit": ["X"], "band": ["A"], "customers": [100]})
    cov = pd.DataFrame({"date": ["2025-01-01", "2025-01-02", "2025-01-03"], "business_unit": ["X"] * 3,
                        "logging_ok": [1, 1, 0]})
    clean = pd.DataFrame({"event_id": ["E1", "E2", "E3"], "feeder_id": ["F1"] * 3,
                          "start": [T("2025-01-01 22:00"), T("2025-01-01 23:00"), T("2025-01-02 10:00")],
                          "end": [T("2025-01-02 02:00"), T("2025-01-02 01:00"), T("2025-01-02 11:30")],
                          "cause": ["fault"] * 3, "logged_by": ["ops1", "ops2", "ops1"], "closed_by": ["logged"] * 3})
    return clean, feeders, cov


def test_daily_supply_midnight_overlap_and_coverage():
    clean, feeders, cov = _toy()
    d = fe.daily_supply(clean, feeders, cov, start=dt.datetime(2025, 1, 1), end=dt.datetime(2025, 1, 4))
    assert list(d.columns) == ["feeder_id", "date", "outage_hours", "supply_hours", "status"]
    assert list(d["date"]) == ["2025-01-01", "2025-01-02", "2025-01-03"]
    assert d["outage_hours"].iloc[0] == pytest.approx(2.0)      # 22:00-24:00, duplicate merged
    assert d["outage_hours"].iloc[1] == pytest.approx(3.5)      # 00:00-02:00 plus 10:00-11:30
    assert d["status"].iloc[2] == "no_coverage" and np.isnan(d["supply_hours"].iloc[2])


def test_daily_supply_naive_sum_double_counts():
    clean, feeders, cov = _toy()
    d = fe.daily_supply(clean, feeders, cov, start=dt.datetime(2025, 1, 1), end=dt.datetime(2025, 1, 4), merge=False)
    assert d["outage_hours"].iloc[0] == pytest.approx(3.0)
    assert d["outage_hours"].iloc[1] == pytest.approx(4.5)


# ---------------------------------------------------------------- R4 / R5
def test_feeder_summary_on_toy():
    clean, feeders, cov = _toy()
    d = fe.daily_supply(clean, feeders, cov, start=dt.datetime(2025, 1, 1), end=dt.datetime(2025, 1, 4))
    s = fe.feeder_summary(d, feeders).iloc[0]
    assert s["days_observed"] == 2 and s["mean_supply"] == pytest.approx((22 + 20.5) / 2)
    assert s["share_days_meeting_band"] == pytest.approx(1.0) and bool(s["meets_band_on_average"])


def test_block_bootstrap_properties():
    v = np.r_[np.full(70, 18.0), np.full(70, 22.0)]
    lo, hi = fe.block_bootstrap_mean_ci(v, n_boot=500, seed=1)
    assert lo < 20 < hi
    assert fe.block_bootstrap_mean_ci(v, n_boot=500, seed=1) == (lo, hi), "must be deterministic for a fixed seed"
    lo2, hi2 = fe.block_bootstrap_mean_ci(np.full(30, 7.0), n_boot=200)
    assert lo2 == pytest.approx(7.0) and hi2 == pytest.approx(7.0)
    with pytest.raises(ValueError):
        fe.block_bootstrap_mean_ci([np.nan, np.nan])


# ---------------------------------------------------------------- end-to-end
@pytest.fixture(scope="module")
def answers(raw):
    return fe.build_answers(*raw)


def test_answers_structure(answers, raw):
    assert sorted(answers) == ["q1", "q2", "q3", "q4", "q5", "q6"]
    assert sorted(answers["q3"]) == list("ABCDE")
    for b, r in answers["q3"].items():
        assert r["ci_low"] <= r["mean_supply"] <= r["ci_high"]
    q6 = answers["q6"]
    assert q6["naive_sum_bias"] == pytest.approx(q6["band_a_naive_sum_mean"] - q6["band_a_correct_mean"])
    assert q6["naive_sum_bias"] < 0, "summing overlapping events overstates outages, so it understates supply"
    assert q6["coverage_bias"] >= 0
    json.dumps(answers)


def test_bands_are_ordered(answers):
    means = [answers["q3"][b]["mean_supply"] for b in "ABCDE"]
    assert means == sorted(means, reverse=True)


def test_cli(tmp_path):
    proc = subprocess.run([sys.executable, "-m", "feeder_eda", str(DATA_DIR), "--out", str(tmp_path)],
                          capture_output=True, text=True, timeout=300,
                          env={**os.environ, "PYTHONPATH": os.pathsep.join(p for p in sys.path if p)})
    assert proc.returncode == 0, proc.stderr
    assert (tmp_path / "answers.json").exists() and (tmp_path / "daily_supply.csv").exists()
    d = pd.read_csv(tmp_path / "daily_supply.csv")
    assert len(d) == 48 * 181
