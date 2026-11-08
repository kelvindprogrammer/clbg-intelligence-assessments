"""Contract tests: pass on the unmodified starter."""
import numpy as np
import pytest

import datagen

pytestmark = pytest.mark.contract


def test_api_exists():
    import leafscout as ls
    for n in ["augment", "extract_features", "macro_f1", "confusion_matrix", "per_class_recall", "fit_triage"]:
        assert callable(getattr(ls, n)), n


def test_datagen_deterministic_in_range():
    a, b = datagen.make_leaves(40, seed=3), datagen.make_leaves(40, seed=3)
    assert np.array_equal(a[0], b[0]) and np.array_equal(a[1], b[1])
    assert a[0].shape == (40, 24, 24, 3) and 0 <= a[0].min() and a[0].max() <= 1


def test_field_camera_is_darker_and_redder_than_lab():
    lab, field = datagen.make_leaves(200, 1, "lab")[0], datagen.make_leaves(200, 1, "field")[0]
    assert field.mean() < 0.75 * lab.mean() and field.mean((0, 1, 2))[2] / field.mean((0, 1, 2))[1] < lab.mean((0, 1, 2))[2] / lab.mean((0, 1, 2))[1]
