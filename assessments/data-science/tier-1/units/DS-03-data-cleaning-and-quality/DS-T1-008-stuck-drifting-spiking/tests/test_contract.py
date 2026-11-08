"""Contract tests: these pass on the unmodified starter."""
import hashlib
import inspect

import pytest

from conftest import DATA

pytestmark = pytest.mark.contract

EXPECTED_SHA256 = "b61cf56051806bb936129a913edf19d14979feaf77157c33b655b031b712f42a"


def test_dataset_is_unmodified():
    assert hashlib.sha256(DATA.read_bytes()).hexdigest() == EXPECTED_SHA256, \
        "sensor_readings.csv has been modified. Restore the original file."


def test_dataset_shape_and_columns(raw):
    from sensorqc.pipeline import INPUT_COLUMNS
    assert list(raw.columns) == INPUT_COLUMNS
    assert len(raw) == 17068
    assert raw["reading_id"].is_unique
    assert set(raw["device_id"]) == {"LAG-01", "LAG-02", "LAG-03", "LAG-04", "LAG-05"}


def test_config_and_devices(config):
    from sensorqc.pipeline import load_devices
    assert set(config["range"]) == {"pm25", "temp_c", "rh_pct"}
    assert config["expected_interval_s"] == 300
    assert set(load_devices()) == {"LAG-01", "LAG-02", "LAG-03", "LAG-04", "LAG-05"}


def test_flag_bits_are_distinct_powers_of_two():
    import sensorqc as qc
    bits = [qc.MISSING, qc.RANGE, qc.STUCK, qc.SPIKE, qc.CLOCK_STEP, qc.HUMIDITY, qc.DRIFT_CORRECTED]
    assert len(set(bits)) == 7 and all(b & (b - 1) == 0 for b in bits)
    assert qc.BAD_BITS == qc.RANGE | qc.STUCK | qc.SPIKE | qc.CLOCK_STEP


def test_public_api_signatures():
    import sensorqc as qc
    for name in ["range_flags", "stuck_flags", "spike_flags", "find_gaps", "qc_level", "estimate_clock",
                 "run_qc", "hourly_means", "load_readings", "load_config"]:
        assert callable(getattr(qc, name)), name
    assert list(inspect.signature(qc.spike_flags).parameters) == ["values", "half_window", "k", "min_abs"]
    assert list(inspect.signature(qc.estimate_clock).parameters) == ["device_time", "received_at", "deployed_on",
                                                                     "future_tolerance_s"]
