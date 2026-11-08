"""Public requirement tests (R1-R6). They fail on the starter and pass on a correct solution."""
import numpy as np
import pytest
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier

import leaderboard_audit as la


def test_r1_hanley_se_known_values():
    assert la.auc_se_hanley(0.83, 96, 1104) == pytest.approx(0.026186, abs=2e-5)
    assert la.auc_se_hanley(0.5, 50, 50) == pytest.approx(0.0577, abs=1e-3)
    assert la.auc_se_hanley(0.8, 400, 4400) < la.auc_se_hanley(0.8, 100, 1100)


def test_r2_inflation_grows_with_candidates_and_is_zero_for_one():
    se = la.auc_se_hanley(0.83, 96, 1104)
    one = la.winner_inflation(1, 96, 1104, 0.83, n_sims=600, seed=1)
    ten = la.winner_inflation(10, 96, 1104, 0.83, n_sims=600, seed=1)
    forty = la.winner_inflation(40, 96, 1104, 0.83, n_sims=600, seed=1)
    assert abs(one) < 0.2 * se and 0.9 * se < ten < forty
    assert 1.3 * se < forty < 2.1 * se, "expected winner's-curse bonus of roughly 1.7 standard errors"
    assert la.winner_inflation(10, 96, 1104, 0.83, n_sims=100, seed=5) == la.winner_inflation(10, 96, 1104, 0.83, n_sims=100, seed=5)


def test_r2_inflation_shrinks_with_larger_eval_set():
    small = la.winner_inflation(20, 96, 1104, 0.83, n_sims=300, seed=2)
    big = la.winner_inflation(20, 384, 4416, 0.83, n_sims=300, seed=2)
    assert big < 0.7 * small


def _noise_problem(seed):
    rng = np.random.default_rng(seed)
    X = rng.normal(size=(300, 20))
    y = (rng.random(300) < 0.12).astype(int)
    cfgs = [dict(max_depth=d, min_samples_leaf=m, random_state=r) for d in (2, 3, 4, 6) for m in (3, 8, 15) for r in (0, 1)]
    return X, y, cfgs


@pytest.mark.parametrize("seed", [0, 1])
def test_r3_nested_cv_is_honest_on_pure_noise(seed):
    X, y, cfgs = _noise_problem(seed)
    r = la.nested_cv_auc(X, y, cfgs, lambda c: DecisionTreeClassifier(**c), seed=seed)
    assert abs(r["nested_mean"] - 0.5) < 0.09, "labels are noise; an honest AUC is near 0.5"
    assert r["naive_best_cv_auc"] > r["nested_mean"] + 0.03, "the best-of-24 naive score should look flattering"
    assert len(r["outer_auc"]) == 5 and len(r["chosen"]) == 5


def test_r3_nested_cv_on_dev_data(dev):
    X, y = dev.drop(columns="is_fraud").to_numpy(), dev["is_fraud"].to_numpy()
    cfgs = [dict(C=c) for c in (0.001, 0.01, 0.1, 1, 10, 100)]
    r = la.nested_cv_auc(X, y, cfgs, lambda c: make_pipeline(StandardScaler(), LogisticRegression(max_iter=500, **c)))
    assert 0.80 < r["nested_mean"] < 0.97
    assert r["naive_best_cv_auc"] >= r["nested_mean"] - 0.01


def test_r4_paired_bootstrap():
    rng = np.random.default_rng(0)
    y = (rng.random(800) < 0.2).astype(int)
    a = rng.normal(size=800) + 1.5 * y
    b = a + rng.normal(0, 0.8, 800) - 0.3 * y
    d, lo, hi = la.paired_bootstrap_auc_diff(y, a, b, seed=3)
    assert lo < d < hi and lo > 0
    assert la.paired_bootstrap_auc_diff(y, a, a, seed=3) == (0.0, 0.0, 0.0)
    assert la.paired_bootstrap_auc_diff(y, a, b, seed=3) == (d, lo, hi)


def test_r5_required_n_properties():
    n = la.required_n(0.02, 0.85, 0.08)
    n_corr = la.required_n(0.02, 0.85, 0.08, corr=0.6)
    assert 20_000 < n < 40_000 and n_corr < 0.5 * n
    assert la.required_n(0.04, 0.85, 0.08) < 0.35 * n, "required size scales with 1 / delta^2"
    npos = round(n * 0.08)
    z = 1.959964 + 0.841621
    assert z * np.sqrt(2) * la.auc_se_hanley(0.85, npos, n - npos) <= 0.02 * 1.01
    m = int(n * 0.95)
    assert z * np.sqrt(2) * la.auc_se_hanley(0.85, round(m * 0.08), m - round(m * 0.08)) > 0.02


def test_r6_shrinkage_pulls_towards_mean_and_keeps_order(board):
    best = board.groupby("team_id")["public_auc"].max().to_numpy()
    s = np.asarray(la.shrink_public_scores(best, 96, 1104))
    assert s.shape == best.shape
    assert s.std() < best.std() and abs(s.mean() - best.mean()) < 0.01
    assert (np.argsort(s) == np.argsort(best)).all()
    assert s.max() < best.max() - 0.005
