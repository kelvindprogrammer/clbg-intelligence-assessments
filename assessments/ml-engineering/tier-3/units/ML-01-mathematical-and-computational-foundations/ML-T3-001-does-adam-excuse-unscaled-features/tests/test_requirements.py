"""Public requirement tests (FAIL on the starter). Hidden tests use other n, d and seeds."""
import numpy as np
import pytest

import datagen
import optlab as ol

KAPPAS = [4, 16, 64, 256]


@pytest.fixture(scope="module")
def prob():
    X, y = datagen.make_logistic(1500, 8, 50, 2026)
    return X, y, ol.solve_reference(X, y)


def test_r1_gradient_and_hessian_by_finite_differences():
    X, y = datagen.make_logistic(200, 4, 10, 1)
    w = np.random.default_rng(0).normal(size=4) * 0.3
    f, g = ol.loss_grad(w, X, y, 0.1)
    e = 1e-6
    ng = np.array([(ol.loss_grad(w + e * np.eye(4)[i], X, y, 0.1)[0] - ol.loss_grad(w - e * np.eye(4)[i], X, y, 0.1)[0]) / (2 * e) for i in range(4)])
    assert np.abs(g - ng).max() < 1e-6
    nh = np.array([(ol.loss_grad(w + e * np.eye(4)[i], X, y, 0.1)[1] - ol.loss_grad(w - e * np.eye(4)[i], X, y, 0.1)[1]) / (2 * e) for i in range(4)])
    assert np.abs(ol.hessian(w, X, y, 0.1) - nh).max() < 1e-5


def test_r1_stable_for_huge_scores():
    X = np.array([[1e4, 0], [-1e4, 0.0]])
    with np.errstate(over="raise", invalid="raise", divide="raise"):
        f, g = ol.loss_grad(np.array([1.0, 0.0]), X, np.array([0.0, 1.0]))
    assert np.isfinite(f) and np.isfinite(g).all()


def test_r2_reference_matches_sklearn(prob):
    from sklearn.linear_model import LogisticRegression
    X, y, (w, f) = prob
    assert np.linalg.norm(ol.loss_grad(w, X, y)[1]) < 1e-10
    sk = LogisticRegression(C=1e12, fit_intercept=False, max_iter=5000, tol=1e-12).fit(X, y)
    assert abs(ol.loss_grad(sk.coef_.ravel(), X, y)[0] - f) < 1e-7


@pytest.mark.parametrize("name", ["gradient_descent", "nesterov"])
def test_r3_r4_converge_to_reference(prob, name):
    X, y, (ws, fs) = prob
    t = getattr(ol, name)(X, y, fs)
    assert t.converged and t.f - fs <= 1e-6 + 1e-12
    assert np.isclose(ol.loss_grad(t.w, X, y)[0], t.f)
    assert t.evals >= t.iters


def test_r3_diag_returns_original_coordinates(prob):
    X, y, (ws, fs) = prob
    t = ol.gradient_descent(X, y, fs, precond="diag")
    assert t.converged and abs(ol.loss_grad(t.w, X, y)[0] - fs) <= 1e-6 + 1e-12


def test_r4_acceleration_helps_on_ill_conditioned():
    X, y = datagen.make_logistic(1500, 8, 256, 3)
    fs = ol.solve_reference(X, y)[1]
    assert ol.nesterov(X, y, fs).iters * 3 < ol.gradient_descent(X, y, fs).iters


def test_r5_newton_few_iterations_any_conditioning():
    for kappa in (4, 1000):
        X, y = datagen.make_logistic(1500, 8, kappa, 4)
        fs = ol.solve_reference(X, y)[1]
        t = ol.newton(X, y, fs)
        assert t.converged and t.iters <= 15 and t.evals > t.iters


def test_r6_adam_decreases_loss_and_is_deterministic(prob):
    X, y, (ws, fs) = prob
    a, b = ol.adam(X, y, fs, max_iter=300), ol.adam(X, y, fs, max_iter=300)
    assert np.array_equal(a.w, b.w)
    assert a.f < ol.loss_grad(np.zeros(8), X, y)[0]


def test_r7_censoring_flag():
    X, y = datagen.make_logistic(1500, 8, 256, 5)
    fs = ol.solve_reference(X, y)[1]
    t = ol.gradient_descent(X, y, fs, max_iter=20)
    assert (not t.converged) and t.iters == 20


def test_r8_run_study_records_and_determinism():
    r1 = ol.run_study([4, 16], ["gd", "newton"], [0, 1])
    r2 = ol.run_study([4, 16], ["gd", "newton"], [0, 1])
    assert r1 == r2 and len(r1) == 8
    assert set(r1[0]) == {"method", "kappa", "seed", "kind", "iters", "evals", "converged"}
    cens = ol.run_study([64], ["gd"], [0], max_iter=10)[0]
    assert (not cens["converged"]) and cens["iters"] == 10


def _slopes(kind, methods):
    recs = ol.run_study(KAPPAS, methods, [0, 1], kind=kind)
    out = {}
    for m in methods:
        rs = [r for r in recs if r["method"] == m]
        assert all(r["converged"] for r in rs), m
        out[m] = ol.loglog_slope([r["kappa"] for r in rs], [r["iters"] for r in rs])[0]
    return out


def test_scaling_exponents_on_scale_conditioning():
    s = _slopes("scale", ["gd", "nesterov", "gd_diag"])
    assert 0.8 <= s["gd"] <= 1.1 and 0.4 <= s["nesterov"] <= 0.7 and s["gd_diag"] < 0.15


def test_diagonal_preconditioner_fails_on_correlated_conditioning():
    assert _slopes("rotated", ["gd_diag"])["gd_diag"] > 0.6


def test_r9_loglog_slope_known_exponent_and_coverage():
    x = np.array([4, 16, 64, 256.0])
    s, lo, hi = ol.loglog_slope(x, 3 * x ** 0.5)
    assert abs(s - 0.5) < 0.05 and lo <= 0.5 <= hi
    rng = np.random.default_rng(0)
    hit = 0
    for _ in range(60):
        xs = np.repeat(x, 3)
        ys = 3 * xs ** 0.5 * np.exp(rng.normal(0, 0.1, len(xs)))
        _, lo, hi = ol.loglog_slope(xs, ys, n_boot=200, seed=1)
        hit += lo <= 0.5 <= hi
    assert hit / 60 >= 0.85
