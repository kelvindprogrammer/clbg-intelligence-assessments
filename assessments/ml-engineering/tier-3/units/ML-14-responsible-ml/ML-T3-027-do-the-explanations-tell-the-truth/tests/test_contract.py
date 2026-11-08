"""Contract tests: pass on the unmodified starter."""
import numpy as np
import pytest

import screening

pytestmark = pytest.mark.contract


def test_api_exists():
    import xaudit as xa
    for n in ["roc_auc", "permutation_importance", "shapley_sampling", "deletion_curve", "deletion_auc",
              "agreement", "stability", "shortcut_audit"]:
        assert callable(getattr(xa, n)), n


def test_data_deterministic_with_movable_shortcut():
    a, b = screening.make_screening(seed=3), screening.make_screening(seed=3)
    assert np.array_equal(a[0], b[0]) and np.array_equal(a[1], b[1]) and a[2] == b[2]
    X, y, names = screening.make_screening(seed=3, shortcut_col=4)
    assert X.shape == (3000, 10) and names[4] == "device_offset" and names.count("device_offset") == 1


def test_shortcut_present_in_training_and_absent_in_deployment():
    X, y, names = screening.make_screening(seed=3)
    Xd, yd, _ = screening.make_screening(seed=3, deployment=True)
    j = names.index("device_offset")
    assert abs(np.corrcoef(X[:, j], y)[0, 1]) > 0.5 and abs(np.corrcoef(Xd[:, j], yd)[0, 1]) < 0.1
