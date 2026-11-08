"""Public requirement tests (FAIL on the starter). Hidden tests use other seeds, batch sizes and streams."""
import numpy as np
import pytest

import driftwatch as dw
import lendstream


def stream(seed, **kw):
    b, names = lendstream.make_stream(seed=seed, **kw)
    return b[:90], b[90:], names


def test_r1_psi_hand_values():
    ref = np.arange(100.0)
    assert dw.psi(ref, ref.copy(), bins=2) == pytest.approx(0.0, abs=1e-12)
    cur = np.concatenate([np.full(20, 10.0), np.full(80, 90.0)])
    want = (0.2 - 0.5) * np.log(0.2 / 0.5) + (0.8 - 0.5) * np.log(0.8 / 0.5)
    assert dw.psi(ref, cur, bins=2) == pytest.approx(want, rel=1e-9)
    empty = dw.psi(ref, np.full(50, 90.0), bins=2)
    floor = (1e-4 - 0.5) * np.log(1e-4 / 0.5) + (1.0 - 0.5) * np.log(1.0 / 0.5)
    assert empty == pytest.approx(floor, rel=1e-9)


def test_r1_psi_handles_ties_and_binary():
    ref = np.r_[np.zeros(85), np.ones(15)]
    assert np.isfinite(dw.psi(ref, np.r_[np.zeros(50), np.ones(50)]))
    assert dw.psi(ref, ref.copy()) == pytest.approx(0.0, abs=1e-12)
    assert np.isfinite(dw.psi(np.full(30, 2.0), np.full(10, 2.0)))


def test_r2_ks_matches_brute_force_with_ties():
    rng = np.random.default_rng(0)
    for _ in range(5):
        a, b = rng.integers(0, 6, 40).astype(float), rng.integers(1, 8, 55).astype(float)
        grid = np.unique(np.r_[a, b])
        want = max(abs(np.mean(a <= g) - np.mean(b <= g)) for g in grid)
        assert dw.ks_stat(a, b) == pytest.approx(want, abs=1e-12)
        assert dw.ks_stat(a, b) == pytest.approx(dw.ks_stat(b, a), abs=1e-12)
    assert dw.ks_stat([1, 2, 3], [1, 2, 3]) == 0.0
    assert dw.ks_stat([1, 2, 3], [10, 11]) == 1.0


def test_r3_calibrate_threshold_and_bonferroni():
    null = np.random.default_rng(1).normal(size=1000)
    thr = dw.calibrate_threshold(null, 0.01)
    assert 8 <= int(np.sum(null > thr)) <= 10
    assert dw.calibrate_threshold(null, 0.0001) == null.max()
    assert dw.calibrate_threshold(null, 0.5) < np.median(null) + 0.2
    assert dw.bonferroni_alpha(0.05, 10) == pytest.approx(0.005)


def test_r4_monitor_interface_is_causal_and_pure():
    ref, test, names = stream(1, drift_day=160, ramp_days=1)
    m1, m2 = dw.DriftMonitor(ref, names), dw.DriftMonitor(ref, names)
    X = test[10][1].copy()
    out = m1.update(test[10][0], X)
    assert isinstance(out, list) and set(out) <= set(names) and np.array_equal(X, test[10][1])
    full = [m2.update(d, x) for d, x in test[:60]]
    m3 = dw.DriftMonitor(ref, names)
    prefix = [m3.update(d, x) for d, x in test[:30]]
    assert prefix == full[:30]


def test_r4_no_false_alarms_through_salary_weeks_and_quiet_days():
    for seed in (1, 2):
        ref, test, names = stream(seed, drift_day=None, low_volume=(100, 101, 133))
        res = dw.evaluate(dw.DriftMonitor(ref, names), test, drift_day=10**6)
        assert res["n_false_alarms"] <= 2, (seed, res["false_alarm_days"])


def test_r4_detects_abrupt_channel_quickly():
    for seed in (1, 2, 3):
        ref, test, names = stream(seed, drift_day=160, low_volume=(150,))
        res = dw.evaluate(dw.DriftMonitor(ref, names), test, drift_day=160)
        assert res["n_false_alarms"] <= 2 and res["detected"] and res["delay"] <= 7, (seed, res)


def test_r4_detects_gradual_channel():
    ok = 0
    for seed in (1, 2, 3):
        ref, test, names = stream(seed, drift_day=160, ramp_days=30)
        res = dw.evaluate(dw.DriftMonitor(ref, names), test, drift_day=160)
        ok += int(res["detected"] and res["delay"] <= 25)
    assert ok >= 2


def test_r4_alarm_budget_parameter_matters():
    ref, test, names = stream(4, drift_day=None)
    lo = dw.evaluate(dw.DriftMonitor(ref, names, false_alarms_per_100d=0.5), test, 10**6)["n_false_alarms"]
    hi = dw.evaluate(dw.DriftMonitor(ref, names, false_alarms_per_100d=400.0), test, 10**6)["n_false_alarms"]
    assert hi > lo


def test_r5_evaluate_scores_a_scripted_monitor():
    class Scripted:
        def __init__(self, days):
            self.days = set(days)

        def update(self, day, X):
            return ["f"] if day in self.days else []

    stream_ = [(d, np.zeros((3, 1))) for d in range(10)]
    r = dw.evaluate(Scripted([2, 6, 8]), stream_, drift_day=5)
    assert r["alarm_days"] == [2, 6, 8] and r["false_alarm_days"] == [2] and r["n_false_alarms"] == 1
    assert r["detected"] is True and r["delay"] == 1
    r2 = dw.evaluate(Scripted([]), stream_, drift_day=5)
    assert r2["detected"] is False and r2["delay"] is None and r2["alarm_days"] == []
