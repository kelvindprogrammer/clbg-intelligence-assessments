"""Public requirement tests (FAIL on the starter). Hidden tests use other seeds and a longer history."""
import numpy as np
import pytest

import agentdemand as a
import datagen

T = 300
ORIGINS = [T - 28 + 7 * i for i in range(4)]


class Naive:
    def forecast(self, Yh, c, o):
        return np.column_stack([Yh[:, o + l - 8] for l in range(1, 8)])


@pytest.fixture(scope="module")
def world():
    return datagen.make_demand(seed=2026, T=T)


@pytest.fixture(scope="module")
def model(world):
    Y, cal = world
    return a.fit_forecaster(Y[:, :T - 28], cal)


def test_r1_features_shape_and_finite(world):
    Y, cal = world
    F = a.make_features(Y, cal, 200, 3)
    assert F.shape[0] == 30 and F.ndim == 2 and np.isfinite(F).all()
    assert a.make_features(Y, cal, 200, 5).shape == F.shape


def test_r1_features_are_causal(world):
    Y, cal = world
    Y2 = Y.copy()
    Y2[:, 200:] = 1e6
    for lead in (1, 4, 7):
        assert np.array_equal(a.make_features(Y, cal, 200, lead), a.make_features(Y2, cal, 200, lead))


def test_r1_features_react_to_the_calendar(world):
    Y, cal = world
    pay = a.make_features(Y, cal, 291, 4)        # target day 294 is a payday
    plain = a.make_features(Y, cal, 277, 4)      # target day 280 is not
    assert cal["payday"][294] == 1 and cal["payday"][280] == 0
    assert not np.array_equal(pay.mean(axis=0), plain.mean(axis=0))


def test_r2_wape_by_hand():
    assert a.wape(np.array([10.0, 0, 30]), np.array([12.0, 5, 20])) == pytest.approx(17 / 40)


def test_r3_evaluate_with_stub_model(world):
    Y, cal = world

    class Stub:
        def forecast(self, Yh, c, origin):
            return np.full((Yh.shape[0], 7), 10.0)

    truth = np.concatenate([Y[:, o:o + 3].ravel() for o in (100, 107)])
    assert a.evaluate(Stub(), Y, cal, [100, 107], horizon=3) == pytest.approx(a.wape(truth, np.full(truth.size, 10.0)))


def test_r4_model_interface(model):
    assert "seasonal_naive" in model.report_ and len(model.report_) >= 3 and model.chosen_ in model.report_
    assert all(np.isfinite(v) and v > 0 for v in model.report_.values())


def test_r4_forecast_shape_nonnegative_and_causal(model, world):
    Y, cal = world
    f = model.forecast(Y, cal, ORIGINS[0])
    assert f.shape == (30, 7) and np.isfinite(f).all() and (f >= 0).all()
    Y2 = Y.copy()
    Y2[:, ORIGINS[0]:] = 1e6
    assert np.allclose(f, model.forecast(Y2, cal, ORIGINS[0]))


def test_r5_beats_seasonal_naive_on_holdout(model, world):
    Y, cal = world
    ours, base = a.evaluate(model, Y, cal, ORIGINS), a.evaluate(Naive(), Y, cal, ORIGINS)
    assert ours <= 0.8 * base, (ours, base)


def test_r6_holdout_bias_is_small(model, world):
    Y, cal = world
    pred = np.concatenate([model.forecast(Y, cal, o).ravel() for o in ORIGINS])
    true = np.concatenate([Y[:, o:o + 7].ravel() for o in ORIGINS])
    assert abs(pred.sum() - true.sum()) / true.sum() < 0.10


def test_r7_payday_week_beats_naive(model, world):
    Y, cal = world
    o = 291
    t = Y[:, o:o + 7]
    assert a.wape(t, model.forecast(Y, cal, o)) < 0.8 * a.wape(t, Naive().forecast(Y, cal, o))
