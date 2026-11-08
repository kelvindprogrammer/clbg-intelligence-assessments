"""Contract tests: pass on the unmodified starter."""
import numpy as np
import pytest

import datagen

pytestmark = pytest.mark.contract


def test_api_exists():
    import titlerank as r
    for n in ["recall_at_k", "ndcg_at_k", "hit_rate_at_k", "leave_last_out", "item_cosine", "recommend",
              "popularity_recommend", "evaluate"]:
        assert callable(getattr(r, n)), n


def test_datagen_deterministic_sorted_no_repeats():
    a, b = datagen.make_views(seed=3), datagen.make_views(seed=3)
    assert all(np.array_equal(x, y) for x, y in zip(a, b))
    u, i, t, g = a
    assert np.all(np.diff(t) >= 0) and len(u) == len(i) == len(t) and len(g) == 120
    assert len({(x, y) for x, y in zip(u, i)}) == len(u)
    assert 600 * 8 <= len(u) <= 600 * 25


def test_genre_structure_present():
    u, i, t, g = datagen.make_views(seed=3)
    top = np.mean([np.bincount(g[i][u == k], minlength=6).max() / (u == k).sum() for k in range(100)])
    assert top > 0.6
