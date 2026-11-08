"""Public requirement tests (R1-R3)."""
import numpy as np
import pytest
from sklearn.metrics import average_precision_score

import meterfault as mf

FEATURES = 11


def test_r1_preprocessor_standardises_and_tames_tails(meters):
    pre = mf.fit_preprocessor(meters)
    X = np.asarray(pre.transform(meters))
    assert X.shape == (len(meters), FEATURES) and np.isfinite(X).all()
    assert np.allclose(X.mean(0), 0, atol=0.05) and np.allclose(X.std(0), 1, atol=0.05)
    skew = ((X - X.mean(0)) ** 3).mean(0) / X.std(0) ** 3
    assert np.abs(skew).max() < 1.5, "heavy-tailed columns must be transformed, not just scaled"


def test_r1_preprocessor_uses_training_statistics_only(meters):
    pre = mf.fit_preprocessor(meters.iloc[:1500])
    shifted = meters.iloc[1500:].copy()
    shifted["avg_token_ngn"] = shifted["avg_token_ngn"] * 3
    X = np.asarray(pre.transform(shifted))
    j = [c for c in meters.columns if c not in ("meter_id", "tampered")].index("avg_token_ngn")
    assert X[:, j].mean() > 0.5, "test data must be scaled with the training mean, not re-centred"
    before = meters.copy()
    pre.transform(meters)
    assert meters.equals(before), "transform must not mutate its input"


def _curve(tr, va):
    return {"train_loss": list(tr), "val_loss": list(va)}


def test_r2_diagnose_canonical_curves():
    e = np.arange(60)
    ok = _curve(0.7 * np.exp(-e / 15) + 0.2, 0.7 * np.exp(-e / 15) + 0.25)
    over = _curve(0.7 * np.exp(-e / 10) + 0.02, np.r_[0.7 * np.exp(-e[:20] / 10) + 0.25, 0.25 + 0.01 * np.arange(1, 41)])
    under = _curve(0.69 - 0.0005 * e, 0.69 - 0.0004 * e)
    unstable = _curve(np.where(e % 2 == 0, 0.5, 2.5) + 0 * e, np.where(e % 2 == 0, 0.6, 3.0) + 0 * e)
    nan = _curve([0.7, 0.6, float("nan"), float("nan")], [0.7, 0.65, float("nan"), float("nan")])
    assert mf.diagnose(ok) == "ok"
    assert mf.diagnose(over) == "overfit"
    assert mf.diagnose(under) == "underfit"
    assert mf.diagnose(unstable) == "unstable"
    assert mf.diagnose(nan) == "unstable"


@pytest.fixture(scope="module")
def model(meters):
    return mf.fit_model(meters, seed=0)


def test_r3_history_and_early_stopping(model):
    h = model.history
    assert len(h["train_loss"]) == len(h["val_loss"]) >= 5
    assert 0 <= model.best_epoch < len(h["val_loss"])
    assert h["val_loss"][model.best_epoch] == pytest.approx(min(h["val_loss"]), abs=1e-6)
    assert len(h["val_loss"]) < 400 and model.config


def test_r3_best_weights_are_restored_and_val_is_clean(model, meters):
    y = meters["tampered"].to_numpy()
    vi = np.asarray(model.val_idx)
    assert len(set(vi)) == len(vi) and 0.1 * len(meters) < len(vi) < 0.35 * len(meters)
    assert abs(y[vi].mean() - y.mean()) < 0.02, "validation split must be stratified"
    p = np.clip(model.predict_proba(meters.iloc[vi]), 1e-7, 1 - 1e-7)
    ll = -np.mean(y[vi] * np.log(p) + (1 - y[vi]) * np.log(1 - p))
    assert ll == pytest.approx(model.history["val_loss"][model.best_epoch], abs=1e-6), "weights of the best epoch must be restored"


def test_r3_predict_on_frame_without_label(model, meters):
    p = np.asarray(model.predict_proba(meters.drop(columns=["tampered", "meter_id"]).head(50)))
    assert p.shape == (50,) and ((p >= 0) & (p <= 1)).all()


def test_r3_deterministic_and_ranks_positives_higher(meters):
    a, b = mf.fit_model(meters, seed=1), mf.fit_model(meters, seed=1)
    pa, pb = np.asarray(a.predict_proba(meters)), np.asarray(b.predict_proba(meters))
    assert np.array_equal(pa, pb)
    y = meters["tampered"].to_numpy()
    assert pa[y == 1].mean() > 2 * pa[y == 0].mean()


def test_r3_beats_no_skill_on_later_rows(meters):
    m = mf.fit_model(meters.iloc[:1800], seed=0)
    te = meters.iloc[1800:]
    ap = average_precision_score(te["tampered"], m.predict_proba(te))
    assert ap > 3 * te["tampered"].mean()
