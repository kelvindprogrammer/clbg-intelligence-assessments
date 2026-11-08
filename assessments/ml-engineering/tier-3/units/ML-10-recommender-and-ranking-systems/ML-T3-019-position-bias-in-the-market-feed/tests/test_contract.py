"""Contract tests: pass on the unmodified starter."""
import numpy as np
import pytest

import datagen

pytestmark = pytest.mark.contract


def test_api_exists():
    import feedrank as f
    for n in ["estimate_exam", "rank_within_queries", "ips_value", "fit_ranker", "exposure_share"]:
        assert callable(getattr(f, n)), n


def test_datagen_deterministic_and_shaped():
    a, b = datagen.make_logs(n_queries=500, seed=3), datagen.make_logs(n_queries=500, seed=3)
    assert all(np.array_equal(a[k], b[k]) for k in a)
    assert a["X"].shape == (500 * datagen.K, datagen.D) and a["pos"].max() == datagen.K - 1
    assert 0.05 < a["randomized"].mean() < 0.15 and 0.05 < a["click"].mean() < 0.4


def test_logs_contain_visible_position_bias():
    d = datagen.make_logs(seed=3)
    ctr = [d["click"][d["pos"] == k].mean() for k in range(datagen.K)]
    assert ctr[0] > 2.5 * ctr[-1]
