"""Contract tests: pass on the unmodified starter."""
import numpy as np
import pytest

import datagen

pytestmark = pytest.mark.contract


def test_api_exists():
    import gridcast as g
    for n in ["make_lag_matrix", "walk_forward_splits", "seasonal_naive", "mase", "ArForecaster", "backtest"]:
        assert callable(getattr(g, n)), n


def test_datagen_deterministic_and_weekly():
    a, b = datagen.make_load(seed=3), datagen.make_load(seed=3)
    assert np.array_equal(a, b) and a.shape == (420,)
    wk = a.reshape(60, 7).mean(axis=0)
    assert wk[3] - wk[6] > 8          # weekday vs weekend gap


def test_forecaster_stores_hyperparameters():
    import gridcast as g
    m = g.ArForecaster(5, alpha=2.0)
    assert (m.n_lags, m.alpha) == (5, 2.0)
