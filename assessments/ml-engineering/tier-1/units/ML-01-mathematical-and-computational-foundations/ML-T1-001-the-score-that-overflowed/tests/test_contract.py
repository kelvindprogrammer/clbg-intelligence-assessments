"""Contract tests: pass on the unmodified starter."""
import inspect

import numpy as np
import pytest

import datagen

pytestmark = pytest.mark.contract


def test_api_exists():
    import stablemath as sm
    for name in ["logsumexp", "softmax", "log_softmax", "sigmoid", "bce_with_logits", "softmax_cross_entropy", "numeric_grad", "LogisticRegression"]:
        assert hasattr(sm, name), name
    assert list(inspect.signature(sm.logsumexp).parameters) == ["a", "axis", "keepdims"]


def test_datagen_is_deterministic():
    X1, y1 = datagen.make_churn(300, 5)
    X2, y2 = datagen.make_churn(300, 5)
    assert np.array_equal(X1, X2) and np.array_equal(y1, y2)
    assert X1.shape == (300, 4) and set(np.unique(y1)) <= {0, 1}


def test_naive_code_really_fails():
    from stablemath.naive import naive_softmax
    with np.errstate(all="ignore"):
        assert np.isnan(naive_softmax(np.array([[1000.0, 0.0, -5.0]]))).any()

