"""Public requirement tests (FAIL on the starter). Hidden tests use other seeds, noise and sample sizes."""
import itertools

import numpy as np
import pytest
from sklearn.ensemble import BaggingRegressor, GradientBoostingRegressor
from sklearn.tree import DecisionTreeRegressor

import datagen
from bvlab import bias_variance, grid_study


class Const:
    def fit(self, X, y):
        return self

    def predict(self, X):
        return np.full(len(X), 1.0)


def noisy_oracle_factory(s=1.0):
    ctr = itertools.count()

    class M:
        def fit(self, X, y):
            self.rng = np.random.default_rng(next(ctr) + 7)
            return self

        def predict(self, X):
            return datagen.f_true(X) + self.rng.normal(0, s, len(X))
    return M


def test_r2_constant_model_known_answer():
    r = bias_variance(Const, rounds=20, seed=1)
    Xe, _ = datagen.sample(1000, 10 ** 6 + 1, 0, 0.5)
    assert r["variance"] < 1e-12
    assert r["bias2"] == pytest.approx(np.mean((1.0 - datagen.f_true(Xe)) ** 2), rel=1e-9)
    assert r["noise"] == 0.25


def test_r2_noisy_oracle_needs_the_correction():
    r = bias_variance(noisy_oracle_factory(), rounds=40, seed=2)
    assert abs(r["variance"] - 1.0) < 0.05
    assert abs(r["bias2"]) < 0.01                 # the uncorrected estimate would be about 0.025


def test_r2_identity_for_deep_tree():
    r = bias_variance(DecisionTreeRegressor, rounds=30, seed=3)
    assert abs(r["mse"] - (r["bias2"] + r["variance"] + r["noise"])) < 0.05 * r["mse"]


def test_r3_standard_errors_shrink_with_rounds():
    a = bias_variance(DecisionTreeRegressor, rounds=40, seed=4)
    b = bias_variance(DecisionTreeRegressor, rounds=160, seed=4)
    for k in ("se_bias2", "se_variance", "se_mse"):
        assert 0 < a[k] < np.inf
    assert b["se_variance"] < 0.75 * a["se_variance"]


def test_determinism_and_keys():
    a = bias_variance(lambda: DecisionTreeRegressor(max_depth=3, random_state=0), rounds=10, seed=5)
    assert a == pytest.approx(bias_variance(lambda: DecisionTreeRegressor(max_depth=3, random_state=0), rounds=10, seed=5), rel=1e-9)
    assert set(a) == {"bias2", "variance", "noise", "mse", "se_bias2", "se_variance", "se_mse"}


def test_depth_shifts_error_from_bias_to_variance():
    shallow = bias_variance(lambda: DecisionTreeRegressor(max_depth=1), rounds=30, seed=6)
    deep = bias_variance(DecisionTreeRegressor, rounds=30, seed=6)
    assert shallow["bias2"] > 3 * shallow["variance"]
    assert deep["variance"] > 4 * deep["bias2"]


def test_bagging_cuts_variance_not_bias():
    deep = bias_variance(DecisionTreeRegressor, rounds=24, seed=7)
    bag = bias_variance(lambda: BaggingRegressor(DecisionTreeRegressor(), n_estimators=25, random_state=0), rounds=24, seed=7)
    assert bag["variance"] < 0.5 * deep["variance"]
    assert abs(bag["bias2"] - deep["bias2"]) < 0.2


def test_boosting_stages_trade_bias_for_variance():
    mk = lambda n: (lambda: GradientBoostingRegressor(n_estimators=n, max_depth=3, learning_rate=0.1, random_state=0))
    few = bias_variance(mk(10), rounds=15, seed=8)
    many = bias_variance(mk(100), rounds=15, seed=8)
    assert many["bias2"] < few["bias2"] and many["variance"] > few["variance"]


def test_more_training_data_lowers_variance():
    small = bias_variance(DecisionTreeRegressor, n_train=150, rounds=24, seed=9)
    large = bias_variance(DecisionTreeRegressor, n_train=900, rounds=24, seed=9)
    assert large["variance"] < 0.75 * small["variance"]


def test_noise_term_and_irrelevant_features():
    lo = bias_variance(DecisionTreeRegressor, rounds=20, seed=10, noise_sd=0.3)
    hi = bias_variance(DecisionTreeRegressor, rounds=20, seed=10, noise_sd=1.0)
    assert lo["noise"] == pytest.approx(0.09) and hi["noise"] == pytest.approx(1.0) and hi["variance"] > lo["variance"]
    irr = bias_variance(DecisionTreeRegressor, rounds=20, seed=10, n_irrelevant=6)
    base = bias_variance(DecisionTreeRegressor, rounds=20, seed=10)
    assert irr["mse"] > base["mse"]


def test_r4_grid_study_merges_overrides():
    recs = grid_study([("d1", lambda: DecisionTreeRegressor(max_depth=1), {}),
                       ("deep_noisy", DecisionTreeRegressor, {"noise_sd": 1.0})], rounds=10, seed=11)
    assert [r["label"] for r in recs] == ["d1", "deep_noisy"]
    assert recs[1]["noise_sd"] == 1.0 and recs[1]["noise"] == pytest.approx(1.0) and recs[0]["noise"] == pytest.approx(0.25)
