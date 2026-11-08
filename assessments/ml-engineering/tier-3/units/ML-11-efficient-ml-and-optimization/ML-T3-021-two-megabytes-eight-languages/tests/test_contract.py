"""Contract tests: pass on the unmodified starter."""
import numpy as np
import pytest

import datagen

pytestmark = pytest.mark.contract


def test_api_exists():
    import langsqueeze as ls
    for n in ["accuracy", "quantise_cols", "cost_model", "distill_ridge", "pareto_front", "build_candidates", "choose"]:
        assert callable(getattr(ls, n)), n


def test_corpus_deterministic_shifted_and_hashed():
    (a, ya), (b, yb) = datagen.make_corpus(3, 40), datagen.make_corpus(3, 40)
    assert a == b and np.array_equal(ya, yb) and set(ya) <= set(range(8))
    s, _ = datagen.make_corpus(3, 200, shifted=True)
    c, _ = datagen.make_corpus(3, 200)
    assert np.mean([len(x.split()) for x in s]) < np.mean([len(x.split()) for x in c])
    assert datagen.vectorizer(256).transform(a).shape == (40, 256)


def test_quantise_cols_is_symmetric_and_bounded():
    import langsqueeze as ls
    W = np.random.default_rng(0).normal(size=(30, 4))
    Q = ls.quantise_cols(W, 4)
    assert all(len(np.unique(Q[:, j])) <= 15 for j in range(4)) and np.abs(Q - W).max() < np.abs(W).max()
