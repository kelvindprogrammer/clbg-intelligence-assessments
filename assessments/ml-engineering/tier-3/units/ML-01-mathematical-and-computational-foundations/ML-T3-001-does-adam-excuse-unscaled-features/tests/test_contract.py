"""Contract tests: pass on the unmodified starter."""
import dataclasses

import numpy as np
import pytest

import datagen

pytestmark = pytest.mark.contract


def test_api_and_trace():
    import optlab as ol
    for n in ["loss_grad", "hessian", "solve_reference", "gradient_descent", "nesterov", "newton", "adam", "run_study", "loglog_slope"]:
        assert callable(getattr(ol, n)), n
    assert [f.name for f in dataclasses.fields(ol.Trace)] == ["w", "f", "iters", "evals", "converged"]


def test_datagen_deterministic_and_nonseparable():
    X1, y1 = datagen.make_logistic(400, 6, 100, 3)
    X2, y2 = datagen.make_logistic(400, 6, 100, 3)
    assert np.array_equal(X1, X2) and np.array_equal(y1, y2)
    assert 0.2 < y1.mean() < 0.8


def test_kinds_share_spectrum_but_differ_in_axes():
    Xs, _ = datagen.make_logistic(3000, 6, 400, 1, "scale")
    Xr, _ = datagen.make_logistic(3000, 6, 400, 1, "rotated")
    cs, cr = np.cov(Xs.T), np.cov(Xr.T)
    assert abs(np.linalg.cond(cs) / np.linalg.cond(cr) - 1) < 0.25
    off = lambda c: np.abs(c - np.diag(np.diag(c))).max() / np.abs(np.diag(c)).max()
    assert off(cs) < 0.1 < off(cr)
