"""Public requirement tests (R1-R4)."""
import numpy as np
import pandas as pd
import pytest
from sklearn.metrics import roc_auc_score

import regimes as rg


@pytest.fixture(scope="module")
def smooth():
    X, y = rg.make_task("smooth", 3000, 11)
    return X[:1000], y[:1000], X[1000:], y[1000:]


@pytest.mark.parametrize("name", ["mlp", "gbm", "logreg"])
def test_r1_fit_predict_is_valid_deterministic_and_skilled(name, smooth):
    Xtr, ytr, Xte, yte = smooth
    p = np.asarray(rg.fit_predict(name, Xtr, ytr, Xte, seed=1))
    assert p.shape == (len(Xte),) and ((p >= 0) & (p <= 1)).all()
    assert np.array_equal(p, rg.fit_predict(name, Xtr, ytr, Xte, seed=1))
    assert roc_auc_score(yte, p) > 0.72


def test_r1_unknown_model_raises(smooth):
    with pytest.raises(ValueError):
        rg.fit_predict("svm", smooth[0], smooth[1], smooth[2])


def test_r2_run_study_schema_and_determinism():
    kw = dict(kinds=["axis", "smooth"], sizes=[100, 200], seeds=[0, 1], n_noise=2, models=("gbm", "logreg"), n_test=500)
    a = rg.run_study(**kw)
    assert list(a.columns) == ["model", "kind", "n", "seed", "auc"] and len(a) == 2 * 2 * 2 * 2
    assert a["auc"].between(0.4, 1.0).all()
    b = rg.run_study(**kw)
    assert a.reset_index(drop=True).equals(b.reset_index(drop=True))
    assert set(map(tuple, a[["model", "kind", "n", "seed"]].to_numpy())) == {
        (m, k, n, s) for m in ("gbm", "logreg") for k in ("axis", "smooth") for n in (100, 200) for s in (0, 1)}


def _frame():
    rows = []
    for kind, offs in (("smooth", {100: -0.05, 300: -0.01, 1000: 0.02, 3000: 0.03}), ("axis", {100: -0.05, 300: -0.04, 1000: -0.03, 3000: -0.02})):
        for n, off in offs.items():
            for s in range(6):
                rows.append(("mlp", kind, n, s, 0.8 + off + 0.002 * s))
                rows.append(("gbm", kind, n, s, 0.8 + 0.002 * s))
    return pd.DataFrame(rows, columns=["model", "kind", "n", "seed", "auc"])


def test_r3_paired_summary_values_and_determinism():
    s = rg.paired_summary(_frame(), "mlp", "gbm", n_boot=200, seed=2)
    assert list(s.columns) == ["kind", "n", "mean_diff", "lo", "hi", "n_seeds"] and len(s) == 8
    r = s[(s.kind == "smooth") & (s.n == 1000)].iloc[0]
    assert r.mean_diff == pytest.approx(0.02) and r.n_seeds == 6
    assert r.lo <= r.mean_diff <= r.hi and r.hi - r.lo < 1e-9, "paired differences are constant here, so the interval collapses"
    assert s.equals(rg.paired_summary(_frame(), "mlp", "gbm", n_boot=200, seed=2))


def test_r3_interval_widens_with_noise():
    f = _frame()
    f.loc[(f.model == "mlp"), "auc"] += np.random.default_rng(0).normal(0, 0.02, (f.model == "mlp").sum())
    s = rg.paired_summary(f, "mlp", "gbm", n_boot=300, seed=1)
    assert (s.hi - s.lo).max() > 0.005


def test_r4_crossover_semantics():
    s = rg.paired_summary(_frame(), "mlp", "gbm", n_boot=50, seed=0)
    assert rg.crossover(s, "smooth") == 1000
    assert rg.crossover(s, "axis") is None
    flip = s.copy()
    flip.loc[(flip.kind == "smooth") & (flip.n == 3000), "mean_diff"] = -0.01
    assert rg.crossover(flip, "smooth") is None, "a win that flips back is not a crossover"
