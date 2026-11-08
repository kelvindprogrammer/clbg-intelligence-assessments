"""Contract tests: pass on the unmodified starter."""
import numpy as np
import pytest

import catalogue

pytestmark = pytest.mark.contract


def test_api_exists():
    import annlab as a
    for n in ["kmeans", "exact_search", "recall_at_k", "evaluate_index", "segment_recall", "choose_config",
              "drift_report", "should_rebuild"]:
        assert callable(getattr(a, n)), n
    assert isinstance(a.IVFIndex, type)


def test_catalogue_is_deterministic_unit_and_skewed():
    a, b = catalogue.make_catalogue(3), catalogue.make_catalogue(3)
    assert np.array_equal(a["X"], b["X"]) and a["X"].shape == (5000, 32)
    assert np.allclose(np.linalg.norm(a["X"], axis=1), 1.0)
    sizes = np.bincount(a["label"], minlength=40)
    assert sizes.max() > 8 * sizes.min() or sizes.min() == 0 or sizes.max() > 600


def test_queries_and_drift_shapes():
    w = catalogue.make_catalogue(3)
    Q, seg = catalogue.make_queries(w, 100, 1)
    assert Q.shape == (100, 32) and set(seg) == {"head", "tail"}
    Xn = catalogue.make_drift(w, 0.5, 300, 2)
    assert Xn.shape == (300, 32) and np.allclose(np.linalg.norm(Xn, axis=1), 1.0)
