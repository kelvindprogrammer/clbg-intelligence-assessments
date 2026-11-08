"""Contract tests: pass on the unmodified starter."""
import numpy as np
import pytest

import datagen

pytestmark = pytest.mark.contract


def test_api_exists():
    import breakcast as b
    for n in ["detect_break", "interval_score", "coverage", "BreakAwareForecaster"]:
        assert callable(getattr(b, n)), n


def test_datagen_deterministic_with_shock():
    (a, ia), (b, ib) = datagen.make_price(seed=3), datagen.make_price(seed=3)
    assert np.array_equal(a, b) and ia == ib and a.shape == (230,) and 150 <= ia["break_week"] < 180
    k = ia["break_week"]
    assert np.log(a[k + 20:k + 30]).mean() - np.log(a[k - 10:k]).mean() > 0.2


def test_control_series_has_no_shock():
    y, info = datagen.make_price(seed=3, shock=0.0)
    k = info["break_week"]
    assert abs(np.log(y[k + 20:k + 30]).mean() - np.log(y[k - 10:k]).mean()) < 0.1
