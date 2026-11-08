"""Public requirement tests. They FAIL on the starter. Hidden tests re-seed the data and use larger scales."""
import numpy as np
import pytest

import datagen
import stablemath as sm

RAISE = dict(over="raise", invalid="raise", divide="raise")


def test_r1_logsumexp_extreme():
    with np.errstate(**RAISE):
        out = sm.logsumexp(np.array([[1000.0, 1000.0], [-1000.0, -1000.0]]))
    assert np.allclose(out, [1000 + np.log(2), -1000 + np.log(2)], rtol=1e-12)


def test_r1_all_neg_inf_row():
    out = sm.logsumexp(np.array([[-np.inf, -np.inf], [0.0, 0.0]]))
    assert out[0] == -np.inf and np.isclose(out[1], np.log(2))


def test_r1_shift_invariance_and_axis():
    a = np.random.default_rng(1).normal(size=(5, 7)) * 30
    assert np.allclose(sm.logsumexp(a + 123.0, axis=0), sm.logsumexp(a, axis=0) + 123.0, rtol=1e-12)
    assert sm.logsumexp(a, axis=1, keepdims=True).shape == (5, 1)


@pytest.mark.parametrize("dtype", [np.float32, np.float64])
def test_r2_softmax_extreme(dtype):
    z = datagen.make_logits(50, 4, 3, scale=1e4).astype(dtype)
    with np.errstate(**RAISE):
        p = sm.softmax(z)
    assert p.dtype == dtype and np.isfinite(p).all()
    assert np.allclose(p.sum(axis=1), 1.0, atol=1e-5)


def test_r3_log_softmax_survives_underflow():
    z = np.array([[0.0, -2000.0, 5.0]])
    with np.errstate(**RAISE):
        ls = sm.log_softmax(z)
    assert np.isfinite(ls).all() and np.isclose(ls[0, 1], -2005 - np.log1p(np.exp(-5)), rtol=1e-12)


def test_r4_sigmoid_no_warning():
    z = np.array([-1e4, -50.0, 0.0, 50.0, 1e4])
    with np.errstate(**RAISE):
        s = sm.sigmoid(z)
    assert s[0] == 0.0 and s[-1] == 1.0 and s[2] == 0.5 and ((s >= 0) & (s <= 1)).all()


def test_r5_bce_exact_at_extremes():
    z = np.array([1000.0, -1000.0, 1000.0, -1000.0, 0.0])
    y = np.array([1, 0, 0, 1, 1])
    with np.errstate(**RAISE):
        out = sm.bce_with_logits(z, y)
    assert np.allclose(out, [0.0, 0.0, 1000.0, 1000.0, np.log(2)], rtol=1e-9, atol=1e-12)


def test_r5_bce_matches_definition_in_safe_range():
    rng = np.random.default_rng(4)
    z, y = rng.normal(0, 3, 200), rng.integers(0, 2, 200)
    p = 1 / (1 + np.exp(-z))
    assert np.allclose(sm.bce_with_logits(z, y), -(y * np.log(p) + (1 - y) * np.log(1 - p)), rtol=1e-9)


def test_r6_gradient_matches_finite_differences():
    rng = np.random.default_rng(7)
    logits, labels = rng.normal(0, 5, (6, 4)), rng.integers(0, 4, 6)
    loss, g = sm.softmax_cross_entropy(logits, labels)
    ng = sm.numeric_grad(lambda L: sm.softmax_cross_entropy(L, labels)[0], logits)
    assert g.shape == logits.shape and np.abs(g - ng).max() < 1e-6
    assert np.allclose(g.sum(axis=1), 0, atol=1e-12)


def test_r6_extreme_logits_finite():
    z = datagen.make_logits(20, 3, 9, scale=5e3)
    with np.errstate(**RAISE):
        loss, g = sm.softmax_cross_entropy(z, np.zeros(20, dtype=int))
    assert np.isfinite(loss) and np.isfinite(g).all()


def test_r7_numeric_grad_quadratic():
    x = np.array([1.0, -2.0, 3.0])
    assert np.allclose(sm.numeric_grad(lambda v: (v ** 2).sum(), x), 2 * x, atol=1e-6)


def test_r8_logreg_stable_and_close_to_sklearn():
    from sklearn.linear_model import LogisticRegression as SK
    X, y = datagen.make_churn(2000, 2026)
    with np.errstate(**RAISE):
        m = sm.LogisticRegression().fit(X, y)
    h = np.array(m.loss_history_)
    assert np.isfinite(h).all() and (np.diff(h) <= 1e-12).all()
    Z = (X - X.mean(0)) / X.std(0)
    sk = SK(C=1e8, max_iter=2000).fit(Z, y)
    p = np.clip(sk.predict_proba(Z)[:, 1], 1e-12, 1 - 1e-12)
    opt = float(-(y * np.log(p) + (1 - y) * np.log(1 - p)).mean())
    assert h[-1] - opt < 0.01
    Xt, yt = datagen.make_churn(1500, 77)
    agree = (m.predict(Xt) == sk.predict((Xt - X.mean(0)) / X.std(0))).mean()
    assert agree >= 0.97


def test_r8_inputs_not_mutated():
    X, y = datagen.make_churn(200, 1)
    X0 = X.copy()
    sm.LogisticRegression(steps=20).fit(X, y)
    assert np.array_equal(X, X0)
