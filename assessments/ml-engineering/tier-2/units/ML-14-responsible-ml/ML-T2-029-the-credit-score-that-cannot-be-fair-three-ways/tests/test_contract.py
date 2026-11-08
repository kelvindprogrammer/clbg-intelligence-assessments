"""Contract tests: pass on the unmodified starter."""
import numpy as np
import pytest

import lendgen

pytestmark = pytest.mark.contract


def test_api_exists():
    import fairlend as fl
    for n in ["fairness_report", "reweighing_weights", "group_thresholds", "tradeoff_curve", "select_and_mitigate"]:
        assert callable(getattr(fl, n)), n


def test_data_deterministic_with_group_differences():
    a, b = lendgen.make_lending(seed=3), lendgen.make_lending(seed=3)
    assert all(np.array_equal(x, y) for x, y in zip(a[:3], b[:3]))
    X, y, g, names = a
    assert X.shape == (6000, 6) and len(names) == 6 and set(np.unique(g)) == {0, 1}
    assert y[g == 0].mean() > y[g == 1].mean() + 0.05
