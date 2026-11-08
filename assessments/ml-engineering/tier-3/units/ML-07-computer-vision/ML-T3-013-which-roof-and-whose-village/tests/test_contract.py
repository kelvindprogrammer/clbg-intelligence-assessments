"""Contract tests: pass on the unmodified starter."""
import numpy as np
import pytest

import datagen

pytestmark = pytest.mark.contract


def test_api_exists():
    import roofmap as rm
    for n in ["village_block_split", "cluster_bootstrap_ci", "patch_dictionary", "encode", "fit_roof_classifier"]:
        assert callable(getattr(rm, n)), n


def test_datagen_deterministic_and_shaped():
    a, b = datagen.make_tiles(6, 10, seed=3), datagen.make_tiles(6, 10, seed=3)
    assert all(np.array_equal(x, y) for x, y in zip(a, b)) and a[0].shape == (60, 20, 20, 3)
    assert 0 <= a[0].min() and a[0].max() <= 1 and set(a[1]) <= {0, 1, 2} and len(set(a[2])) == 6


def test_villages_differ_more_than_tiles_within_a_village():
    X, y, v = datagen.make_tiles(20, 30, seed=1)
    per_tile = X.mean((1, 2, 3))
    between = np.var([per_tile[v == k].mean() for k in range(20)])
    within = np.mean([per_tile[v == k].var() for k in range(20)])
    assert between > within


def test_label_budget_respects_exclusions():
    X, y, v = datagen.make_tiles(20, 30, seed=1)
    idx = datagen.label_budget(y, v, n_villages=5, n_per_class=10, seed=0, exclude=[0, 1, 2])
    assert len(idx) == 30 and len(set(v[idx])) <= 5 and not set(v[idx]) & {0, 1, 2}
