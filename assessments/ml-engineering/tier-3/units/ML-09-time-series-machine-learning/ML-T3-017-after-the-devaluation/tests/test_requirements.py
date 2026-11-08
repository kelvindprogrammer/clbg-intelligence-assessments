"""Public requirement tests (FAIL on the starter). Hidden tests use other seeds and more of them."""
import numpy as np
import pytest

import breakcast as b
import datagen

H = 13


def rolling(y, start, make=lambda: b.BreakAwareForecaster(alpha=0.1, horizon=H), step=3):
    cov, sc, wid = [], [], []
    for o in range(start, len(y) - H, step):
        p, lo, hi = make().fit(y[:o]).predict()
        t = y[o:o + H]
        cov.append(b.coverage(t, lo, hi))
        sc.append(b.interval_score(t, lo, hi))
        wid.append(np.mean((hi - lo) / p))
    return np.mean(cov), np.mean(sc), np.mean(wid)


def naive_interval(y, alpha=0.1):
    """Reference baseline: last value, interval from the full-history h-step log changes."""
    ly = np.log(y)
    q = np.quantile(np.concatenate([np.abs(ly[h:] - ly[:-h]) / np.sqrt(h) for h in range(1, H + 1)]), 1 - alpha)
    h = np.arange(1, H + 1)
    return np.exp(ly[-1]) * np.ones(H), np.exp(ly[-1] - q * np.sqrt(h)), np.exp(ly[-1] + q * np.sqrt(h))


class Naive:
    def __init__(self):
        pass

    def fit(self, y):
        self._y = y
        return self

    def predict(self):
        return naive_interval(self._y)


@pytest.fixture(scope="module")
def series():
    return datagen.make_price(seed=2026)


def test_r1_finds_the_break(series):
    y, info = series
    assert abs(b.detect_break(y) - info["break_week"]) <= 6


def test_r1_finds_it_with_little_post_break_data(series):
    y, info = series
    k = info["break_week"]
    assert abs(b.detect_break(y[:k + 30]) - k) <= 10


def test_r2_interval_score_and_coverage_by_hand():
    y, lo, hi = np.array([5.0, 1.0, 9.0]), np.array([4.0, 2.0, 6.0]), np.array([6.0, 4.0, 8.0])
    # widths 2, 2, 2; miss below by 1 (alpha 0.1 -> 20), miss above by 1 (20): (6 + 40) / 3
    assert b.interval_score(y, lo, hi, alpha=0.1) == pytest.approx(46 / 3)
    assert b.coverage(y, lo, hi) == pytest.approx(1 / 3)


def test_r3_interface_and_shape(series):
    y, _ = series
    p, lo, hi = b.BreakAwareForecaster(horizon=H).fit(y[:200]).predict()
    assert p.shape == lo.shape == hi.shape == (H,) and np.all(lo < p) and np.all(p < hi) and np.all(lo > 0)
    assert np.all(np.diff(hi - lo) > 0), "uncertainty should widen with the horizon"


def test_r3_uses_only_the_history_given(series):
    y, _ = series
    y2 = y.copy()
    y2[200:] = 1.0
    a = b.BreakAwareForecaster(horizon=H).fit(y[:200]).predict()
    c = b.BreakAwareForecaster(horizon=H).fit(y2[:200]).predict()
    assert all(np.allclose(u, v) for u, v in zip(a, c))


def test_r3_currency_unit_does_not_matter(series):
    y, _ = series
    a = b.BreakAwareForecaster(horizon=H).fit(y[:200]).predict()
    c = b.BreakAwareForecaster(horizon=H).fit(y[:200] / 1000.0).predict()
    assert all(np.allclose(u / 1000.0, v, rtol=1e-6) for u, v in zip(a, c))


def test_r4_calibrated_and_sharper_than_naive_after_the_shock(series):
    y, info = series
    start = info["break_week"] + 15
    cov, sc, _ = rolling(y, start)
    bcov, bsc, _ = rolling(y, start, make=Naive)
    assert cov >= 0.85 and sc <= 0.95 * bsc, (cov, sc, bcov, bsc)


def test_r4_intervals_are_not_trivially_wide(series):
    y, info = series
    _, _, wid = rolling(y, info["break_week"] + 15)
    assert wid < 0.25, wid


def test_r5_no_false_alarm_on_control_series():
    y, info = datagen.make_price(seed=2026, shock=0.0)
    cov, _, wid = rolling(y, info["break_week"] + 15)
    assert 0.80 <= cov and wid < 0.25, (cov, wid)
