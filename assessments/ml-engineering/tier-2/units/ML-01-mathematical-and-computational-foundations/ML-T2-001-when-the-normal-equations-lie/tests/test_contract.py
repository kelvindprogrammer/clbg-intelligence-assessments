"""Contract tests: pass on the unmodified starter."""
import numpy as np
import pytest

import datagen

pytestmark = pytest.mark.contract


def test_api_exists():
    import loadfit
    for n in ["diagnose", "solve", "blocked_cv_lambda", "fit_load_model", "compare_solvers"]:
        assert callable(getattr(loadfit, n)), n


def test_datagen_deterministic_and_shifted():
    a = datagen.make_feeder(seed=3)
    b = datagen.make_feeder(seed=3)
    assert all(np.array_equal(x, y) for x, y in zip(a[:4], b[:4]))
    Xa, ya, Xb, yb, names = a
    assert Xa.shape == (900, 8) and Xb.shape == (300, 8) and len(names) == 8
    assert Xb[:, 0].mean() - Xa[:, 0].mean() > 3.0          # hotter test period
    res = lambda X: (X[:, 2] - 0.7 * X[:, 0] - 0.3 * X[:, 1]).std()
    assert res(Xa) < 0.01 and res(Xb) > 0.3                 # vendor change in the heat-index feed


def test_collinearity_is_present():
    Xa = datagen.make_feeder()[0]
    assert abs(np.corrcoef(Xa[:, 4], Xa[:, 5])[0, 1]) > 0.9999
