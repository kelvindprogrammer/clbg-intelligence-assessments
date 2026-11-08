"""Contract tests: pass on the unmodified starter."""
import numpy as np
import pytest

import datagen

pytestmark = pytest.mark.contract


def test_api_exists():
    import bvlab
    assert callable(bvlab.bias_variance) and callable(bvlab.grid_study)


def test_datagen_deterministic_and_known_truth():
    X1, y1 = datagen.sample(200, 4, 2, 0.3)
    X2, y2 = datagen.sample(200, 4, 2, 0.3)
    assert np.array_equal(X1, X2) and np.array_equal(y1, y2) and X1.shape == (200, 6)
    Xb, yb = datagen.sample(20000, 5, 0, 0.5)
    assert abs(np.var(yb - datagen.f_true(Xb)) - 0.25) < 0.01


def test_irrelevant_columns_do_not_enter_truth():
    X, _ = datagen.sample(100, 1, 3)
    X2 = X.copy()
    X2[:, 4:] = 0.0
    assert np.array_equal(datagen.f_true(X), datagen.f_true(X2))
