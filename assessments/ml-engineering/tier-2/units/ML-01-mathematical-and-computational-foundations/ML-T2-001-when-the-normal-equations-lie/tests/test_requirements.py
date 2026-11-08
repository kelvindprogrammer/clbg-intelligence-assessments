"""Public requirement tests (FAIL on the starter). Hidden tests re-seed and alter the collinear structure."""
import numpy as np
import pytest

import datagen
import loadfit as lf


@pytest.fixture(scope="module")
def feeder():
    return datagen.make_feeder(seed=2026)


def test_r1_diagnose_matches_numpy_and_finds_pair(feeder):
    X = feeder[0]
    d = lf.diagnose(X)
    assert abs(d["cond_raw"] / np.linalg.cond(X) - 1) < 0.01
    Z = (X - X.mean(0)) / X.std(0)
    assert abs(d["cond_standardised"] / np.linalg.cond(Z) - 1) < 0.01
    assert d["collinear_pairs"] == [(4, 5)]
    assert d["cond_standardised"] < d["cond_raw"]


def test_r1_constant_column_no_warning():
    X = np.random.default_rng(0).normal(size=(50, 3))
    X[:, 1] = 5.0
    with np.errstate(all="raise"):
        d = lf.diagnose(X)
    assert d["rank_standardised"] <= 2 and d["collinear_pairs"] == []


def test_r2_methods_agree_on_easy_data():
    rng = np.random.default_rng(1)
    X, w = rng.normal(size=(80, 5)), rng.normal(size=5)
    y = X @ w + 0.01 * rng.normal(size=80)
    ref = np.linalg.lstsq(X, y, rcond=None)[0]
    for m in ["normal", "qr", "svd"]:
        assert np.allclose(lf.solve(X, y, m), ref, atol=1e-8), m


def test_r2_qr_beats_normal_on_polynomial():
    x = np.linspace(0, 1, 60)
    X = np.vander(x, 10, increasing=True)
    w = np.linspace(1, 2, 10)
    y = X @ w
    e = {m: np.abs(lf.solve(X, y, m) - w).max() for m in ["normal", "qr", "svd"]}
    assert e["qr"] < 1e-6 and e["svd"] < 1e-6
    assert e["normal"] > 50 * e["qr"]


def test_r2_ridge_closed_form():
    rng = np.random.default_rng(2)
    X, y = rng.normal(size=(60, 4)), rng.normal(size=60)
    exp = np.linalg.solve(X.T @ X + 2.5 * np.eye(4), X.T @ y)
    assert np.allclose(lf.solve(X, y, "ridge", 2.5), exp, atol=1e-8)


def test_r2_ridge_handles_exact_duplicate_column():
    rng = np.random.default_rng(3)
    a = rng.normal(size=(40, 2))
    X = np.column_stack([a, a[:, 0]])
    y = a @ [1.0, 2.0]
    w = lf.solve(X, y, "ridge", 1e-6)
    assert np.isfinite(w).all() and np.allclose(X @ w, y, atol=1e-3)


def _expanding_scores(X, y, lams, n_blocks=5):
    edges = np.linspace(0, len(y), n_blocks + 1).astype(int)
    out = []
    for lam in lams:
        errs = []
        for k in range(1, n_blocks):
            tr, va = slice(0, edges[k]), slice(edges[k], edges[k + 1])
            mu, sd = X[tr].mean(0), X[tr].std(0)
            Z = (X[tr] - mu) / sd
            w = np.linalg.solve(Z.T @ Z + lam * np.eye(X.shape[1]), Z.T @ (y[tr] - y[tr].mean()))
            errs.append(np.mean((((X[va] - mu) / sd) @ w + y[tr].mean() - y[va]) ** 2))
        out.append(np.mean(errs))
    return out


def test_r3_blocked_cv_matches_independent_expanding_window(feeder):
    X, y = feeder[0], feeder[1]
    lams = np.logspace(-2, 3, 6)
    best = lf.blocked_cv_lambda(X, y, lams)
    assert best == lams[int(np.argmin(_expanding_scores(X, y, lams)))]


def test_r3_blocked_cv_is_not_shuffled_kfold(feeder):
    X, y = feeder[0], feeder[1]
    lams = np.logspace(-2, 3, 6)
    X2 = X.copy()
    X2[:, 3] = X2[:, 3][::-1]                 # nonsense lag column reversed: a time-aware CV cares about order
    got = lf.blocked_cv_lambda(X2, y, lams)
    assert got == lams[int(np.argmin(_expanding_scores(X2, y, lams)))]


def test_r4_model_interface(feeder):
    m = lf.fit_load_model(feeder[0], feeder[1])
    assert hasattr(m, "lam_") and hasattr(m, "coef_")
    assert m.predict(feeder[2]).shape == (300,)


def test_r4_and_r5_beat_baseline_on_official_data(feeder):
    Xa, ya, Xb, yb, _ = feeder
    r = lf.compare_solvers(Xa, ya, Xb, yb)
    assert set(r) >= {"normal_raw", "lstsq_raw", "fit_load_model"}
    assert r["fit_load_model"] <= 1.3
    assert r["fit_load_model"] <= r["normal_raw"] / 4
    assert r["lstsq_raw"] > 3 * r["fit_load_model"]      # numerically stable is not enough


def test_r4_predict_does_not_refit(feeder):
    Xa, ya, Xb, yb, _ = feeder
    m = lf.fit_load_model(Xa, ya)
    p1 = m.predict(Xb)
    _ = m.predict(Xb * 3 + 100)
    assert np.allclose(p1, m.predict(Xb))
