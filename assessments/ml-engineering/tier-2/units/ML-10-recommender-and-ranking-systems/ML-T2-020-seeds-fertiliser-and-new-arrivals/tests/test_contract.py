"""Contract tests: pass on the unmodified starter."""
import numpy as np
import pytest

import datagen

pytestmark = pytest.mark.contract


def test_api_exists():
    import inputrec as r
    for n in ["time_split", "interaction_matrix", "recall_at_k", "fit_recommender"]:
        assert callable(getattr(r, n)), n


def test_datagen_deterministic_with_cold_items():
    a, b = datagen.make_purchases(seed=3), datagen.make_purchases(seed=3)
    assert all(np.array_equal(a[k], b[k]) for k in ("user", "item", "t", "item_attrs"))
    assert a["item_attrs"].shape == (150, 9) and len(a["cold_items"]) == 25 and np.all(np.diff(a["t"]) >= 0)
    assert 10_000 < len(a["user"]) < 30_000 and a["t"].max() < 335


def test_cold_items_have_no_history_before_cutoff():
    d = datagen.make_purchases(seed=3)
    before = d["t"] < d["cutoff"]
    assert not np.isin(d["item"][before], d["cold_items"]).any()
    assert np.isin(d["item"][~before], d["cold_items"]).mean() > 0.2
