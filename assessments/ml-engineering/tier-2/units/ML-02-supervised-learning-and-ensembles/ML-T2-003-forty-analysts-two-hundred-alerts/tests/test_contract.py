"""Contract tests: pass on the unmodified starter."""
import numpy as np
import pytest

import datagen

pytestmark = pytest.mark.contract


def test_api_exists():
    import alertmodel as am
    for n in ["find_leaky_columns", "time_split", "budget_recall", "budget_precision", "select_and_fit"]:
        assert callable(getattr(am, n)), n


def test_datagen_deterministic_imbalanced_with_leak():
    a, b = datagen.make_transactions(seed=3), datagen.make_transactions(seed=3)
    assert all(np.array_equal(x, y) for x, y in zip(a[:3], b[:3])) and a[3] == b[3]
    X, y, day, names = a
    assert 0.008 < y.mean() < 0.025 and names[-1] == "chargeback_flag" and X.shape == (24000, 10)
    assert np.all(np.diff(day) >= 0)
    assert X[y == 1, -1].mean() > 0.8 > 0.05 > X[y == 0, -1].mean()


def test_rename_and_reposition_leak():
    X, y, day, names = datagen.make_transactions(seed=3, leak_name="dispute_status", leak_position=2)
    assert names[2] == "dispute_status" and X[y == 1, 2].mean() > 0.8
