"""Contract tests: pass on the unmodified starter."""
import numpy as np
import pytest

import lendstream

pytestmark = pytest.mark.contract


def test_api_exists():
    import driftwatch as dw
    for n in ["psi", "ks_stat", "calibrate_threshold", "bonferroni_alpha", "DriftMonitor", "evaluate"]:
        assert callable(getattr(dw, n)), n


def test_stream_is_deterministic_and_days_are_independent():
    a, names = lendstream.make_stream(seed=3, days=40)
    b, _ = lendstream.make_stream(seed=3, days=60)
    assert len(names) == 7 and a[0][1].shape == (400, 7)
    assert all(np.array_equal(x[1], y[1]) for x, y in zip(a, b))


def test_salary_week_and_new_channel_exist():
    b, names = lendstream.make_stream(seed=3, days=200, drift_day=160)
    amt = lambda r: np.median(np.concatenate([b[i][1][:, 0] for i in r]))
    assert amt(range(25, 30)) > 1.3 * amt(range(5, 10))
    age = lambda r: np.mean(np.concatenate([b[i][1][:, 2] for i in r]))
    assert age(range(165, 175)) < age(range(100, 110)) - 1.5
    assert lendstream.make_stream(seed=3, days=5, low_volume=(2,))[0][2][1].shape[0] == 40
