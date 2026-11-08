"""Public requirement tests (FAIL on the starter). Hidden tests use other seeds and a renamed leaky column."""
import numpy as np
import pytest
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

import alertmodel as am
import datagen


@pytest.fixture(scope="module")
def data():
    X, y, day, names = datagen.make_transactions(seed=2026)
    tr, va, te = am.time_split(day, 40, 50)
    return X, y, day, names, tr, va, te


def test_r1_finds_only_the_leak(data):
    X, y, day, names, *_ = data
    assert am.find_leaky_columns(X, y, names) == ["chargeback_flag"]


def test_r1_works_for_any_name_and_position():
    X, y, day, names = datagen.make_transactions(seed=5, leak_name="dispute_status", leak_position=3)
    assert am.find_leaky_columns(X, y, names) == ["dispute_status"]


def test_r1_constant_column_is_safe():
    X = np.column_stack([np.ones(100), np.arange(100.0)])
    y = (np.arange(100) % 2).astype(int)
    assert am.find_leaky_columns(X, y, ["c", "v"]) == []


def test_r2_time_split_no_overlap_or_lookahead(data):
    X, y, day, names, tr, va, te = data
    assert day[tr].max() < 40 <= day[va].min() and day[va].max() < 50 <= day[te].min()
    assert len(tr) + len(va) + len(te) == len(day)
    assert all(np.all(np.diff(i) > 0) for i in (tr, va, te))


def test_r3_budget_recall_by_hand():
    day = np.array([0, 0, 0, 0, 1, 1, 1, 1, 1, 1])
    y = np.array([1, 0, 0, 0, 0, 1, 0, 0, 0, 1])
    s = np.array([.9, .1, .2, .3, .5, .8, .1, .2, .3, .4])
    # budget 0.25: day0 -> ceil(1.0)=1, day1 -> ceil(1.5)=2
    assert am.budget_recall(day, y, s, 0.25) == pytest.approx(2 / 3)         # catches rows 0 and 5, misses row 9
    assert am.budget_precision(day, y, s, 0.25) == pytest.approx(2 / 3)       # flagged rows 0, 4, 5 -> 2 positives of 3


def test_r3_ties_go_to_earlier_row():
    day = np.zeros(6, dtype=int)
    y = np.array([0, 0, 0, 1, 0, 0])
    assert am.budget_recall(day, y, np.ones(6), 0.5) == 0.0                   # rows 0,1,2 flagged
    y2 = np.array([0, 0, 1, 0, 0, 0])
    assert am.budget_recall(day, y2, np.ones(6), 0.5) == 1.0


def test_r3_perfect_and_worst_scores(data):
    X, y, day, names, tr, va, te = data
    d, yy = day[te], y[te]
    assert am.budget_recall(d, yy, yy.astype(float), 0.04) > 0.95
    assert am.budget_recall(d, yy, -yy.astype(float), 0.04) < 0.05


@pytest.fixture(scope="module")
def fitted(data):
    X, y, day, names, tr, va, te = data
    return am.select_and_fit(X[tr], y[tr], X[va], y[va], day[va], names)


def test_r4_interface(fitted, data):
    X, y, day, names, tr, va, te = data
    assert fitted.chosen_ in fitted.report_ and "logreg_baseline" in fitted.report_ and len(fitted.report_) >= 3
    assert fitted.dropped_ == ["chargeback_flag"]
    assert fitted.predict_score(X[te]).shape == (len(te),)


def test_r4_beats_baseline_on_test_period(fitted, data):
    X, y, day, names, tr, va, te = data
    keep = [i for i, n in enumerate(names) if n != "chargeback_flag"]
    base = make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000, class_weight="balanced")).fit(X[tr][:, keep], y[tr])
    rb = am.budget_recall(day[te], y[te], base.predict_proba(X[te][:, keep])[:, 1], 0.04)
    rm = am.budget_recall(day[te], y[te], fitted.predict_score(X[te]), 0.04)
    assert rm >= 0.55 and rm >= 1.4 * rb, (rm, rb)


def test_r4_ignores_leaky_column_and_row_order(fitted, data):
    X, y, day, names, tr, va, te = data
    Xt = X[te].copy()
    s0 = fitted.predict_score(Xt)
    Xz = Xt.copy()
    Xz[:, names.index("chargeback_flag")] = 0.0
    assert np.allclose(fitted.predict_score(Xz), s0)
    perm = np.random.default_rng(0).permutation(len(Xt))
    assert np.allclose(fitted.predict_score(Xt[perm]), s0[perm])
