"""Contract tests: these pass on the unmodified starter.

They check that the data is intact and the public API exists with the required signatures.
"""
import hashlib
import inspect

import numpy as np
import pytest

from conftest import DATA

pytestmark = pytest.mark.contract

EXPECTED_SHA256 = "9e72e2ff93d829a1d6d902c6fcb872b49c63b21c26863f7e22e8b946d52da1c9"


def test_dataset_is_unmodified():
    digest = hashlib.sha256(DATA.read_bytes()).hexdigest()
    assert digest == EXPECTED_SHA256, "station_log.csv has been modified. Restore the original file."


def test_log_schema(log):
    from fuel_queue.stats import LOG_COLUMNS
    assert list(log.columns) == LOG_COLUMNS
    assert len(log) == 1303
    assert log["customer_id"].is_unique
    assert set(log["status"]) == {"served", "balked"}
    assert sorted(log["day"].unique()) == [1, 2, 3, 4, 5]
    assert log["arrival_min"].between(0, 240).all()
    served = log[log["status"] == "served"]
    assert served["service_min"].notna().all()
    assert log.loc[log["status"] == "balked", "service_min"].isna().all()


def test_public_api():
    import fuel_queue as fq
    for name in ["erlang_b", "erlang_c", "mmc_metrics", "simulate_fcfs", "simulate_mmc", "simulate_empirical",
                 "poisson_arrivals", "batch_means_ci", "estimate_inputs", "load_log", "validate_against_mmc",
                 "recommend_pumps"]:
        assert callable(getattr(fq, name)), name
    sig = inspect.signature(fq.recommend_pumps)
    for p in ["window_min", "target_wait", "max_prob", "n_customers", "warmup", "seed", "c_max"]:
        assert p in sig.parameters, p
    assert sig.parameters["target_wait"].default == 10.0
    assert sig.parameters["max_prob"].default == 0.10


def test_provided_helpers_work():
    import fuel_queue as fq
    t = fq.poisson_arrivals(2.0, 1000, np.random.default_rng(0))
    assert t.shape == (1000,) and np.all(np.diff(t) > 0)
    iv = fq.Interval(1.0, 0.5, 1.5)
    assert iv.lower < iv.estimate < iv.upper
