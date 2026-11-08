"""Public requirement tests (R1-R4). Fail on the starter, pass on a sound solution.
Only the 60 expert labels are available as evidence here, so the checks are deliberately statistical."""
import numpy as np
import pytest

import label_lab as ll
from conftest import DATA, GOLD


@pytest.fixture(scope="module")
def d():
    return ll.load_labels(DATA, GOLD)


def test_r1_oof_shape_normalised_deterministic(d):
    P = ll.oof_proba(d.X, d.y, 5, 0)
    assert P.shape == (1200, 3) and np.allclose(P.sum(axis=1), 1) and (P >= 0).all()
    assert np.array_equal(P, ll.oof_proba(d.X, d.y, 5, 0))
    acc = (P.argmax(axis=1) == d.y).mean()
    assert 0.8 < acc < 0.97, "out-of-fold agreement with noisy labels should be high but not perfect"


def test_r1_oof_is_not_in_sample(d):
    """A 1-nearest-neighbour style memoriser would score 100% in sample; out-of-fold it must not."""
    P = ll.oof_proba(d.X, d.y, 5, 1)
    own = P[np.arange(len(d.y)), d.y]
    assert own.mean() < 0.95 and (own < 0.2).sum() > 40


def test_r2_estimate_structure(d):
    r = ll.estimate_noise(d.X, d.y, d.annotator, 0)
    assert set(r) == {"overall", "per_annotator"} and set(r["per_annotator"]) == {0, 1, 2, 3}
    assert all(0 <= v <= 1 for v in r["per_annotator"].values())


def test_r2_estimate_agrees_with_expert_sample(d):
    r = ll.estimate_noise(d.X, d.y, d.annotator, 0)
    gold_rate = (d.y[d.gold_idx] != d.gold_y).mean()
    assert abs(r["overall"] - gold_rate) < 0.09, (r["overall"], gold_rate)
    assert 0.03 < r["overall"] < 0.25


def test_r2_annotators_are_not_exchangeable(d):
    r = ll.estimate_noise(d.X, d.y, d.annotator, 0)["per_annotator"]
    assert max(r.values()) > 2 * min(r.values()), "different agents have clearly different reliability"


def test_r3_selection_contract(d):
    sel = ll.select_for_relabel(d.X, d.y, d.annotator, 150, 0)
    assert len(sel) == 150 and len(set(sel.tolist())) == 150 and sel.min() >= 0 and sel.max() < 1200
    assert np.array_equal(sel, ll.select_for_relabel(d.X, d.y, d.annotator, 150, 0))


def test_r3_selection_concentrates_wrong_labels(d):
    sel = set(ll.select_for_relabel(d.X, d.y, d.annotator, 300, 0).tolist())
    wrong = d.y[d.gold_idx] != d.gold_y
    hit = np.array([i in sel for i in d.gold_idx])
    assert wrong.sum() >= 4
    assert hit[wrong].mean() >= 0.6, "most expert-confirmed mislabels should be selected"
    assert hit[~wrong].mean() < 0.4, "correct labels should mostly be left alone"


def test_r4_model_contract_and_quality(d):
    m = ll.fit_robust(d.X, d.y, d.annotator, 0)
    p = m.predict(d.X[d.gold_idx])
    assert p.shape == (60,) and (p == d.gold_y).mean() >= 0.8
    assert np.array_equal(p, ll.fit_robust(d.X, d.y, d.annotator, 0).predict(d.X[d.gold_idx]))
