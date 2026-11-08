"""Public requirement tests (FAIL on the starter). Hidden tests use other seeds and a different field-camera mix."""
import numpy as np
import pytest
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score

import datagen
import leafscout as ls


@pytest.fixture(scope="module")
def data():
    return (datagen.make_leaves(400, 1, "lab"), datagen.make_leaves(90, 2, "field"), datagen.make_leaves(600, 3, "field"))


def test_r1_augment_shape_range_and_no_mutation(data):
    X = data[0][0][:20]
    X0 = X.copy()
    A = ls.augment(X, np.random.default_rng(0), copies=3)
    assert A.shape == (60,) + X.shape[1:] and A.min() >= 0 and A.max() <= 1 and np.array_equal(X, X0)


def test_r1_augment_deterministic_and_varied(data):
    X = data[0][0][:20]
    a, b = ls.augment(X, np.random.default_rng(5)), ls.augment(X, np.random.default_rng(5))
    c = ls.augment(X, np.random.default_rng(6))
    assert np.array_equal(a, b) and not np.array_equal(a, c) and not np.array_equal(a[:20], a[20:40])


def test_r1_augment_keeps_identity_and_moves_toward_field(data):
    X = data[0][0][:30]
    A = ls.augment(X, np.random.default_rng(0), copies=2)
    same = [np.corrcoef(A[30 + i].ravel(), X[i].ravel())[0, 1] for i in range(30)]
    other = [np.corrcoef(A[30 + i].ravel(), X[(i + 1) % 30].ravel())[0, 1] for i in range(30)]
    assert np.mean(same) > np.mean(other) and A.mean() < 0.85 * X.mean()


def test_r2_features_finite_and_row_independent(data):
    X = data[1][0][:12]
    F = ls.extract_features(X)
    assert F.ndim == 2 and F.shape[0] == 12 and np.all(np.isfinite(F)) and F.shape[1] <= 200
    assert np.allclose(F[5], ls.extract_features(X[5:6])[0])


def test_r3_metrics_by_hand():
    yt, yp = np.array([0, 0, 1, 1, 2, 2, 2]), np.array([0, 1, 1, 1, 2, 0, 2])
    assert ls.confusion_matrix(yt, yp).tolist() == [[1, 1, 0], [0, 2, 0], [1, 0, 2]]
    assert ls.macro_f1(yt, yp) == pytest.approx(f1_score(yt, yp, average="macro"))
    assert ls.per_class_recall(yt, yp) == pytest.approx([0.5, 1.0, 2 / 3])


def test_r3_macro_f1_absent_class_scores_zero():
    assert ls.macro_f1(np.array([0, 0, 1, 1]), np.array([0, 0, 1, 1]), k=3) == pytest.approx(2 / 3)


@pytest.fixture(scope="module")
def fitted(data):
    (Xl, yl), (Xv, yv), _ = data
    return ls.fit_triage(Xl, yl, Xv, yv, seed=0)


def test_r4_interface(fitted, data):
    (Xl, yl), (Xv, yv), (Xt, yt) = data
    assert fitted.chosen_ in fitted.report_ and "raw_pixels_logreg" in fitted.report_ and len(fitted.report_) >= 3
    assert all(0 <= v <= 1 for v in fitted.report_.values())
    assert fitted.predict_proba(Xt[:10]).shape == (10, 3) and fitted.predict(Xt[:10]).shape == (10,)


def test_r4_beats_lab_trained_baseline_on_field_camera(fitted, data):
    (Xl, yl), (Xv, yv), (Xt, yt) = data
    base = LogisticRegression(max_iter=2000).fit(Xl.reshape(len(Xl), -1), yl)
    fb = f1_score(yt, base.predict(Xt.reshape(len(Xt), -1)), average="macro")
    fm = ls.macro_f1(yt, fitted.predict(Xt))
    assert fm >= 0.85 and fm >= 1.5 * fb, (fm, fb)
    assert ls.per_class_recall(yt, fitted.predict(Xt)).min() >= 0.75


def test_r4_predictions_are_per_image(fitted, data):
    Xt = data[2][0]
    p = fitted.predict(Xt[:40])
    assert np.array_equal(p[:10], fitted.predict(Xt[:10])) and np.array_equal(p[::-1], fitted.predict(Xt[:40][::-1]))
