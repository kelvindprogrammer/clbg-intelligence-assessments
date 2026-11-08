"""Contract tests: these pass on the unmodified starter."""
import hashlib
import inspect

import pytest

from conftest import DATA_DIR

pytestmark = pytest.mark.contract

EXPECTED_SHA256 = {
    "feeders.csv": "130e96752d0996ee3f4c73db3e9b7e213cdfe5eabb457e91c4e69f466c2f8082",
    "log_coverage.csv": "375c3c739999adbc97a47725120d299fa499c354046998e54bd547e0fa40182f",
    "outage_events.csv": "49e4136ac56faa48d9e6ad72aa7ef1e9f3f2afbfd6aa1210e130a18ebf72575b",
}


@pytest.mark.parametrize("name", sorted(EXPECTED_SHA256))
def test_data_files_unmodified(name):
    assert hashlib.sha256((DATA_DIR / name).read_bytes()).hexdigest() == EXPECTED_SHA256[name], \
        f"{name} has been modified. Restore the original file."


def test_shapes_and_columns(raw):
    events, feeders, coverage = raw
    assert list(events.columns) == ["event_id", "feeder_id", "start", "end", "cause", "logged_by"]
    assert list(feeders.columns) == ["feeder_id", "business_unit", "band", "customers"]
    assert list(coverage.columns) == ["date", "business_unit", "logging_ok"]
    assert len(feeders) == 48 and set(feeders["band"]) == set("ABCDE")
    assert events["event_id"].is_unique
    assert set(events["feeder_id"]) <= set(feeders["feeder_id"])
    assert len(coverage) == 181 * 4


def test_band_minimums():
    from feeder_eda import BAND_MIN_HOURS
    assert BAND_MIN_HOURS == {"A": 20, "B": 16, "C": 12, "D": 8, "E": 4}


def test_public_api():
    import feeder_eda as fe
    for name in ["merge_intervals", "parse_events", "daily_supply", "feeder_summary", "block_bootstrap_mean_ci",
                 "flag_misbanded", "band_summary", "grid_collapse_days", "build_answers"]:
        assert callable(getattr(fe, name)), name
    p = inspect.signature(fe.block_bootstrap_mean_ci).parameters
    assert (p["block"].default, p["n_boot"].default, p["seed"].default, p["alpha"].default) == (7, 2000, 0, 0.05)
    assert "merge" in inspect.signature(fe.daily_supply).parameters
