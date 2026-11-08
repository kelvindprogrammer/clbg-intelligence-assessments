"""Contract tests: pass on the unmodified starter."""
import numpy as np
import pytest

import datagen

pytestmark = pytest.mark.contract


def test_api_exists():
    import treeforge as tf
    for n in ["gini", "best_split", "DecisionTree", "export_rules", "depth_sweep"]:
        assert hasattr(tf, n), n


def test_datagen_deterministic_three_classes():
    X1, y1 = datagen.make_cassava(300, 4)
    X2, y2 = datagen.make_cassava(300, 4)
    assert np.array_equal(X1, X2) and np.array_equal(y1, y2)
    assert X1.shape == (300, 5) and set(np.unique(datagen.make_cassava(2000, 1)[1])) == {0, 1, 2}


def test_xor_is_not_linearly_separable_by_one_feature():
    X, y = datagen.make_xor(2000, 1)
    for j in (0, 1):
        assert abs(y[X[:, j] > 0.5].mean() - y[X[:, j] <= 0.5].mean()) < 0.1
