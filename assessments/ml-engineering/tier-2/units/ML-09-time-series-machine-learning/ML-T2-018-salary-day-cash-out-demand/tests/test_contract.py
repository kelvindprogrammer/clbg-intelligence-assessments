"""Contract tests: pass on the unmodified starter."""
import numpy as np
import pytest

import datagen

pytestmark = pytest.mark.contract


def test_api_exists():
    import agentdemand as a
    for n in ["make_features", "wape", "evaluate", "fit_forecaster"]:
        assert callable(getattr(a, n)), n


def test_datagen_deterministic_with_calendar():
    (a, ca), (b, cb) = datagen.make_demand(seed=3), datagen.make_demand(seed=3)
    assert np.array_equal(a, b) and a.shape == (30, 300) and set(ca) == {"dow", "payday", "eve"}
    assert ca["payday"].sum() == 40 and ca["eve"][-28:].sum() >= 1 and np.array_equal(ca["eve"], cb["eve"])


def test_payday_effect_present_in_data():
    Y, cal = datagen.make_demand(seed=3)
    p = cal["payday"] == 1
    assert Y[:, p].mean() > 1.4 * Y[:, ~p].mean()
