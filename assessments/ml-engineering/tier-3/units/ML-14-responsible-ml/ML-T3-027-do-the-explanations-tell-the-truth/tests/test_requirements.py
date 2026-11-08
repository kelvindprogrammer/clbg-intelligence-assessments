"""Public requirement tests (FAIL on the starter). Hidden tests use other seeds, columns and model classes."""
import numpy as np
import pytest
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score

import screening
import xaudit as xa


def fitted(seed, strength=0.9, col=None, model="lr"):
    X, y, names = screening.make_screening(seed=seed, shortcut_col=col, shortcut_strength=strength)
    m = LogisticRegression(max_iter=500) if model == "lr" else RandomForestClassifier(40, min_samples_leaf=10, random_state=0)
    m.fit(X, y)
    return m, X, y, names


def test_r1_auc_hand_and_ties():
    assert xa.roc_auc([0, 0, 1, 1], [0.1, 0.4, 0.35, 0.8]) == 0.75
    assert xa.roc_auc([0, 1, 0, 1], [0.5, 0.5, 0.5, 0.5]) == 0.5
    rng = np.random.default_rng(0)
    y, s = rng.integers(0, 2, 300), np.round(rng.random(300), 1)
    assert xa.roc_auc(y, s) == pytest.approx(roc_auc_score(y, s), abs=1e-12)


def test_r2_permutation_importance_spec():
    m, X, y, names = fitted(1)
    f = lambda Z: m.predict_proba(Z)[:, 1]
    got = xa.permutation_importance(f, X, y, n_repeats=3, seed=2)
    rng = np.random.default_rng(2)
    base = roc_auc_score(y, f(X))
    want = []
    for j in range(X.shape[1]):
        dr = []
        for _ in range(3):
            Xp = X.copy(); Xp[:, j] = X[rng.permutation(len(X)), j]
            dr.append(base - roc_auc_score(y, f(Xp)))
        want.append(np.mean(dr))
    assert got == pytest.approx(want, abs=1e-12)
    assert np.array_equal(got, xa.permutation_importance(f, X, y, n_repeats=3, seed=2))


def test_r3_shapley_efficiency_and_dummy_feature():
    m, X, y, names = fitted(2, model="rf")
    f = lambda Z: m.predict_proba(Z)[:, 1]
    phi, base = xa.shapley_sampling(f, X[5], X[:80], n_perm=30, seed=1)
    assert phi.shape == (10,) and phi.sum() == pytest.approx(f(X[5:6])[0] - base, abs=1e-9)
    g = lambda Z: 2.0 * Z[:, 0] - Z[:, 2]  # columns 1, 3.. are dummies
    p2, b2 = xa.shapley_sampling(g, X[7], X[:50], n_perm=20, seed=3)
    assert np.all(p2[[1, 3, 4, 5, 6, 7, 8, 9]] == 0.0)


def test_r3_shapley_linear_is_exact():
    rng = np.random.default_rng(4)
    w_ = rng.normal(size=6)
    f = lambda Z: Z @ w_
    x, bg = rng.normal(size=6), np.tile(rng.normal(size=6), (10, 1))
    phi, base = xa.shapley_sampling(f, x, bg, n_perm=7, seed=0)
    assert phi == pytest.approx(w_ * (x - bg[0]), abs=1e-12) and base == pytest.approx(f(bg[:1])[0])
    p1, _ = xa.shapley_sampling(f, x, bg, n_perm=7, seed=0)
    assert np.array_equal(phi, p1)


def test_r4_deletion_curve_hand_example():
    f = lambda Z: Z.sum(axis=1)
    X = np.array([[3.0, 1.0, 2.0], [0.0, 5.0, 1.0]])
    A = np.array([[0.1, 0.0, 0.9], [0.0, 1.0, 0.2]])  # row 0 removes col 2 then 0; row 1 removes col 1 then 2
    c = xa.deletion_curve(f, X, A, baseline=np.zeros(3))
    assert c.tolist() == [(6 + 6) / 2, (4 + 1) / 2, (1 + 0) / 2, 0.0]
    assert xa.deletion_auc(c) == pytest.approx(np.sum((c[:-1] + c[1:]) / 2) / 3)


def test_r4_good_attributions_delete_faster_than_bad_ones():
    m, X, y, names = fitted(3, model="lr")
    f = lambda Z: m.predict_proba(Z)[:, 1]
    Xs = X[:60]
    A = np.array([xa.shapley_sampling(f, x, X[:60], n_perm=25, seed=i)[0] for i, x in enumerate(Xs)])
    base = X.mean(axis=0)
    good = xa.deletion_auc(xa.deletion_curve(f, Xs, A, base))
    rnd = xa.deletion_auc(xa.deletion_curve(f, Xs, np.random.default_rng(0).normal(size=A.shape), base))
    assert abs(good - rnd) > 0.02


def test_r5_agreement_hand_case():
    a = np.array([5.0, -4.0, 3.0, 0.1, 0.0])
    b = np.array([4.0, 0.2, -5.0, 3.0, 0.0])
    r = xa.agreement(a, b, 2)
    assert r["topk_jaccard"] == pytest.approx(1 / 3)
    assert xa.agreement(a, a, 3) == {"topk_jaccard": 1.0, "spearman": pytest.approx(1.0)}
    assert xa.agreement(a, -a, 3)["topk_jaccard"] == 1.0


def test_r5_stability_distinguishes_stable_and_random_methods():
    m, X, y, names = fitted(4, model="lr")
    w_ = m.coef_[0]
    stable = lambda f, x: w_ * x
    noise_rng = np.random.default_rng(9)
    erratic = lambda f, x: noise_rng.normal(size=len(x))
    f = lambda Z: m.predict_proba(Z)[:, 1]
    assert xa.stability(stable, f, X[:40], 1e-6, seed=0, k=3) == 1.0
    assert xa.stability(erratic, f, X[:40], 1e-6, seed=0, k=3) < 0.7


def test_r6_audit_flags_only_the_shortcut():
    for col in (None, 4):
        m, X, y, names = fitted(5, col=col, model="lr")
        Xr, yr, _ = screening.make_screening(seed=1005, shortcut_col=col)
        Xd, yd, _ = screening.make_screening(seed=5, shortcut_col=col, deployment=True)
        r = xa.shortcut_audit(lambda Z: m.predict_proba(Z)[:, 1], Xr, yr, Xd, yd)
        assert r["flagged"] == [names.index("device_offset")]


def test_r6_audit_is_quiet_on_a_clean_model_and_works_on_forests():
    m, X, y, names = fitted(6, strength=0.0, model="rf")
    Xr, yr, _ = screening.make_screening(seed=1006, shortcut_strength=0.0)
    Xd, yd, _ = screening.make_screening(seed=6, shortcut_strength=0.0, deployment=True)
    assert xa.shortcut_audit(lambda Z: m.predict_proba(Z)[:, 1], Xr, yr, Xd, yd)["flagged"] == []
    m2, X2, y2, n2 = fitted(7, model="rf")
    Xr2, yr2, _ = screening.make_screening(seed=1007)
    Xd2, yd2, _ = screening.make_screening(seed=7, deployment=True)
    assert xa.shortcut_audit(lambda Z: m2.predict_proba(Z)[:, 1], Xr2, yr2, Xd2, yd2)["flagged"] == [9]
