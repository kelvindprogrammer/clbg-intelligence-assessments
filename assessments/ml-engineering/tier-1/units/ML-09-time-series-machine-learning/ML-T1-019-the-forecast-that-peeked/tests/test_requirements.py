"""Public requirement tests (FAIL on the starter). Hidden tests use other seeds and shapes."""
import numpy as np
import pytest

import datagen
import gridcast as g


def test_r1_lag_matrix_by_hand():
    X, y = g.make_lag_matrix(np.array([1.0, 2, 3, 4, 5]), 2)
    assert X.tolist() == [[1, 2], [2, 3], [3, 4]] and y.tolist() == [3, 4, 5]


def test_r1_rejects_too_short():
    with pytest.raises(ValueError):
        g.make_lag_matrix(np.arange(3.0), 3)


def test_r2_expanding_splits():
    s = g.walk_forward_splits(20, 10, 3, 4)
    assert [(len(a), b.tolist()) for a, b in s] == [(10, [10, 11, 12]), (14, [14, 15, 16])]
    assert s[0][0].tolist() == list(range(10))


def test_r2_no_lookahead_and_last_fold_fits():
    for tr, te in g.walk_forward_splits(100, 50, 7, 7):
        assert tr.max() < te.min() and te.max() < 100 and len(te) == 7


def test_r3_seasonal_naive_repeats_last_season():
    out = g.seasonal_naive(np.array([9.0, 1, 2, 3, 4, 5, 6, 7]), 5, 3)
    assert out.tolist() == [5, 6, 7, 5, 6]


def test_r4_mase_by_hand():
    train = np.array([1.0, 2, 4, 7, 11])                    # lag-1 diffs 1,2,3,4 -> scale 2.5
    assert g.mase(np.array([12.0, 13]), np.array([11.0, 15]), train, 1) == pytest.approx(1.5 / 2.5)


def test_r4_mase_seasonal_scale():
    train = np.array([1.0, 5, 2, 6, 3, 7])                   # lag-2 diffs all 1 -> scale 1
    assert g.mase(np.array([4.0]), np.array([6.0]), train, 2) == pytest.approx(2.0)


def test_r5_recovers_ar2():
    e = np.random.default_rng(0).normal(0, 0.05, 600)
    s = np.zeros(600)
    s[:2] = 1.0
    for i in range(2, 600):
        s[i] = 0.5 * s[i - 1] + 0.3 * s[i - 2] + 1.0 + e[i]
    m = g.ArForecaster(2).fit(s)
    assert m.coef_[1] == pytest.approx(0.5, abs=0.03) and m.coef_[0] == pytest.approx(0.3, abs=0.03)
    assert m.forecast(3).shape == (3,)


def test_r5_ridge_shrinks_and_spares_intercept():
    s = datagen.make_load(seed=4)
    lo, hi = g.ArForecaster(10, 0.0).fit(s), g.ArForecaster(10, 1e12).fit(s)
    assert np.abs(hi.coef_).sum() < 1e-3 * np.abs(lo.coef_).sum()
    assert hi.intercept_ == pytest.approx(s[10:].mean(), rel=1e-2)


def test_r5_forecast_is_recursive_and_deterministic():
    s = datagen.make_load(seed=5)
    m = g.ArForecaster(7, 1.0).fit(s)
    f = m.forecast(4)
    first = m.intercept_ + s[-7:] @ m.coef_
    second = m.intercept_ + np.r_[s[-6:], f[0]] @ m.coef_
    assert f[0] == pytest.approx(first) and f[1] == pytest.approx(second) and np.array_equal(f, m.forecast(4))


def test_r6_backtest_shapes():
    s = datagen.make_load(seed=2026)
    r = g.backtest(s, lambda tr, h: g.seasonal_naive(tr, h, 7), 200, 7, 14, 7)
    assert r.shape == (len(g.walk_forward_splits(len(s), 200, 7, 14)),) and np.all(r > 0)


def test_r6_ar_beats_seasonal_naive_on_official_series():
    s = datagen.make_load(seed=2026)
    naive = g.backtest(s, lambda tr, h: g.seasonal_naive(tr, h, 7), 200, 7, 7, 7).mean()
    ar = g.backtest(s, lambda tr, h: g.ArForecaster(21, 1.0).fit(tr).forecast(h), 200, 7, 7, 7).mean()
    assert ar < 0.8 * naive, (ar, naive)
