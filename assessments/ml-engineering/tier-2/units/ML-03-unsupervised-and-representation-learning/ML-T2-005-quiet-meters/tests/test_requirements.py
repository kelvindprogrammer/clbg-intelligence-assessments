"""Public requirement tests (R1-R6). They fail on the starter and pass on a sound solution."""
import numpy as np
import pytest
from sklearn.metrics import average_precision_score

import meter_audit as ma
from conftest import DATA


@pytest.fixture(scope="module")
def d():
    return ma.load_meters(DATA)


def test_r1_features_shape_finite_deterministic(d):
    F = ma.build_features(d.readings, d.tariff)
    assert F.shape[0] == len(d.readings) and F.shape[1] >= 4 and np.isfinite(F).all()
    assert np.array_equal(F, ma.build_features(d.readings, d.tariff))


def test_r1_features_scale_free_and_pure(d):
    R0 = d.readings.copy()
    F = ma.build_features(d.readings, d.tariff)
    F3 = ma.build_features(d.readings * 1000.0, d.tariff)
    assert np.allclose(F, F3, rtol=1e-4, atol=1e-4)
    assert np.array_equal(R0, d.readings)


def test_r1_big_consumers_are_not_special(d):
    """Multiplying one meter by 5 (a bigger customer, same behaviour) should not move it much in feature space."""
    F = ma.build_features(d.readings, d.tariff)
    R = d.readings.copy()
    R[7] *= 5
    F2 = ma.build_features(R, d.tariff)
    spread = F.std(axis=0) + 1e-9
    assert (np.abs(F2[7] - F[7]) / spread).max() < 0.5


def test_r2_baseline_exact():
    R = np.ones((6, 3, 4))
    R[:, :, 0] = np.arange(1, 7)[:, None]            # daily totals 4,5,6,7,8,9 -> means
    t = np.zeros(6, int)
    s = ma.score_meters(R, t, "baseline")
    means = R.sum(axis=2).mean(axis=1)
    med = np.median(means)
    mad = np.median(np.abs(means - med)) * 1.4826
    assert np.allclose(s, np.abs(means - med) / mad)


def test_r2_baseline_is_per_class():
    R = np.ones((6, 3, 4))
    R[3:] *= 100
    t = np.array([0, 0, 0, 1, 1, 1])
    R[2] *= 2
    s = ma.score_meters(R, t, "baseline")
    assert s[3:].max() < 2 and s[2] > s[0]


@pytest.mark.parametrize("m", ["iforest", "lof", "pca"])
def test_r3_detectors_shape_and_seed(d, m):
    a = ma.score_meters(d.readings, d.tariff, m, 3)
    assert a.shape == (len(d.readings),) and np.isfinite(a).all()
    assert np.allclose(a, ma.score_meters(d.readings, d.tariff, m, 3))


def test_r3_unknown_method(d):
    with pytest.raises(ValueError):
        ma.score_meters(d.readings, d.tariff, "autoencoder")


def test_r4_metrics_match_sklearn():
    rng = np.random.default_rng(0)
    s, y = rng.normal(size=80), (rng.random(80) < 0.2).astype(int)
    assert ma.average_precision(s, y) == pytest.approx(average_precision_score(y, s))
    top = np.argsort(-s)[:10]
    assert ma.precision_at_k(s, y, 10) == pytest.approx(y[top].mean())
    assert ma.average_precision(s, np.zeros(80, int)) == 0.0


def test_r5_evaluate_structure_and_determinism(d):
    a, b = ma.evaluate_methods(d, seed=1, n_boot=100), ma.evaluate_methods(d, seed=1, n_boot=100)
    assert set(a) == set(ma.METHODS) and a == b
    for v in a.values():
        lo, hi = v["ci"]
        assert 0 <= lo <= hi <= 1 and 0 <= v["ap"] <= 1


def test_r5_intervals_reflect_small_audit(d):
    ev = ma.evaluate_methods(d, seed=0, n_boot=200)
    widths = [v["ci"][1] - v["ci"][0] for v in ev.values()]
    assert max(widths) > 0.1, "with only a handful of confirmed thefts the intervals must be wide"


def test_r6_recommendation_contract(d):
    r = ma.recommend(d, 25, seed=0)
    assert r.method in ma.METHODS and r.method != "baseline"
    assert len(r.top_idx) == 25 and len(set(r.top_idx.tolist())) == 25
    assert r.top_idx.min() >= 0 and r.top_idx.max() < len(d.readings)
    assert isinstance(r.rationale, str) and len(r.rationale) >= 40


def test_r6_beats_baseline_on_audit_sample(d):
    """Detectors never see labels; measure on the audited meters. In-sample for method choice, so the bar is modest."""
    r = ma.recommend(d, 25, seed=0)
    s = ma.score_meters(d.readings, d.tariff, r.method, 0)[d.audit_idx]
    b = ma.score_meters(d.readings, d.tariff, "baseline")[d.audit_idx]
    assert ma.average_precision(s, d.audit_y) >= 0.45
    assert ma.average_precision(s, d.audit_y) >= ma.average_precision(b, d.audit_y) + 0.25
