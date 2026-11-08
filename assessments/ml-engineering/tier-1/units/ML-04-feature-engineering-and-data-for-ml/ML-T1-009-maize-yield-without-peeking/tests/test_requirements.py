"""Public requirement tests (R1-R5). Fail on the starter, pass on a correct solution."""
import numpy as np
import pytest
from sklearn.linear_model import Ridge
from sklearn.metrics import r2_score

import safeprep as sp
from conftest import DATA


@pytest.fixture(scope="module")
def farms():
    return sp.load_farms(DATA)


def split(d, cut=600):
    return {k: v[:cut] for k, v in d.items()}, {k: v[cut:] for k, v in d.items()}


def test_r1_imputer_learns_from_fit_only():
    A = np.array([[1.0, np.nan], [3.0, 4.0], [np.nan, 6.0], [5.0, 8.0]])
    imp = sp.MedianImputer().fit(A)
    B = np.array([[np.nan, np.nan], [100.0, 100.0]])
    out = imp.transform(B)
    assert out.shape == (2, 4)
    assert np.allclose(out[:, :2], [[3.0, 6.0], [100.0, 100.0]])
    assert np.allclose(out[:, 2:], [[1, 1], [0, 0]])


def test_r1_indicator_only_for_columns_missing_at_fit():
    A = np.array([[1.0, 2.0], [np.nan, 4.0], [3.0, 6.0]])
    imp = sp.MedianImputer().fit(A)
    out = imp.transform(np.array([[np.nan, np.nan]]))
    assert out.shape == (1, 3) and out[0, 1] == 4.0
    assert sp.MedianImputer(add_indicator=False).fit(A).transform(A).shape == (3, 2)
    with pytest.raises(ValueError):
        sp.MedianImputer().fit(np.array([[np.nan], [np.nan]]))


def test_r2_scaler_and_inverse():
    A = np.array([[1.0, 5.0], [2.0, 5.0], [3.0, 5.0]])
    sc = sp.StandardScaler().fit(A)
    Z = sc.transform(A)
    assert np.allclose(Z[:, 0].std(), 1) and np.allclose(Z[:, 1], 0)
    assert np.allclose(sc.inverse_transform(Z), A)
    assert np.allclose(sc.transform(np.array([[10.0, 5.0]])), [[(10 - 2) / np.sqrt(2 / 3), 0]])


def test_r3_onehot_unknown_and_rare():
    oh = sp.OneHotEncoder(min_count=2).fit(["b", "a", "b", "c", "a", "b"])
    assert list(oh.categories_) == ["a", "b"]
    M = oh.transform(["a", "c", "z", "b"])
    assert np.array_equal(M, [[1, 0], [0, 0], [0, 0], [0, 1]])


def test_r4_target_encoder_formula_and_unseen():
    v = np.array(["x", "x", "x", "y"])
    y = np.array([1.0, 2.0, 3.0, 10.0])
    te = sp.SmoothedTargetEncoder(smoothing=2.0).fit(v, y)
    g = y.mean()
    assert te.transform(["x"])[0] == pytest.approx((3 * 2.0 + 2 * g) / 5)
    assert te.transform(["y"])[0] == pytest.approx((1 * 10.0 + 2 * g) / 3)
    assert te.transform(["new"])[0] == pytest.approx(g)


def test_r4_out_of_fold_does_not_use_own_label():
    rng = np.random.default_rng(0)
    v = rng.choice(list("abcde"), 200)
    y = rng.normal(size=200)
    a = sp.SmoothedTargetEncoder(5.0).fit_transform(v, y, n_splits=5, seed=1)
    y2 = y.copy()
    y2[17] += 1000.0
    b = sp.SmoothedTargetEncoder(5.0).fit_transform(v, y2, n_splits=5, seed=1)
    assert a[17] == pytest.approx(b[17]), "a row's encoding must not depend on its own label"
    assert (np.abs(a - b) > 1e-6).sum() > 5, "other folds should see the change"


def test_r4_leave_one_out_is_exact():
    v = np.array(["p", "p", "p", "q", "q"])
    y = np.array([1.0, 2.0, 6.0, 4.0, 8.0])
    out = sp.SmoothedTargetEncoder(1.0).fit_transform(v, y, n_splits=5, seed=0)
    for i in range(5):
        keep = np.arange(5) != i
        g = y[keep].mean()
        m = keep & (v == v[i])
        expect = (m.sum() * y[m].mean() + 1.0 * g) / (m.sum() + 1.0)
        assert out[i] == pytest.approx(expect)


def test_r4_fit_transform_leaves_encoder_usable_and_deterministic():
    v = np.array(list("aabbbcc"))
    y = np.arange(7.0)
    te = sp.SmoothedTargetEncoder(2.0)
    a = te.fit_transform(v, y, 3, 4)
    assert np.array_equal(a, sp.SmoothedTargetEncoder(2.0).fit_transform(v, y, 3, 4))
    assert te.transform(["a"]).shape == (1,)


def test_r5_shapes_and_no_nans(farms):
    tr, te = split(farms)
    Xtr, Xte, ytr, yte = sp.make_features(tr, te)
    assert Xtr.shape[0] == 600 and Xte.shape[0] == 200 and Xtr.shape[1] == Xte.shape[1]
    assert np.isfinite(Xtr).all() and np.isfinite(Xte).all()
    assert np.array_equal(ytr, tr["yield_t_ha"]) and np.array_equal(yte, te["yield_t_ha"])


def test_r5_train_matrix_ignores_test_data(farms):
    tr, te = split(farms)
    Xtr, _, _, _ = sp.make_features(tr, te)
    te2 = {k: v.copy() for k, v in te.items()}
    te2["rainfall_mm"][:] = 5000.0
    te2["yield_t_ha"][:] = 99.0
    Xtr2, _, _, _ = sp.make_features(tr, te2)
    assert np.array_equal(Xtr, Xtr2)


def test_r5_test_rows_are_transformed_independently(farms):
    tr, te = split(farms)
    _, Xte, _, _ = sp.make_features(tr, te)
    one = {k: v[5:6] for k, v in te.items()}
    _, X1, _, _ = sp.make_features(tr, one)
    assert np.allclose(Xte[5], X1[0])


def test_r5_test_labels_never_enter_features(farms):
    tr, te = split(farms)
    _, Xte, _, _ = sp.make_features(tr, te)
    te2 = {k: v.copy() for k, v in te.items()}
    te2["yield_t_ha"] = te2["yield_t_ha"][::-1].copy()
    _, Xte2, _, _ = sp.make_features(tr, te2)
    assert np.array_equal(Xte, Xte2)


def test_r5_model_quality_and_honest_estimate(farms):
    tr, te = split(farms)
    Xtr, Xte, ytr, yte = sp.make_features(tr, te)
    m = Ridge(alpha=1.0).fit(Xtr, ytr)
    r2_test = r2_score(yte, m.predict(Xte))
    assert r2_test >= 0.55, r2_test
