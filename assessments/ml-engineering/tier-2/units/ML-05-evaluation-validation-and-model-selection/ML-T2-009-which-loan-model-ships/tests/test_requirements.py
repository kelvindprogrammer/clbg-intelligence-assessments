"""Public requirement tests (R1-R7). They fail on the starter and pass on a correct solution."""
import numpy as np
import pandas as pd
import pytest

import loanselect as ls


@pytest.fixture(scope="module")
def mature(loans):
    return ls.matured(loans)


def test_r1_usable_features_exclude_leaks_and_ids(loans):
    f = ls.usable_features(loans)
    assert "collection_calls_made" not in f, "collection calls happen AFTER a loan goes bad"
    assert not {"loan_id", "customer_id", "defaulted", "disbursed_on"} & set(f)
    assert {"amount_ngn", "avg_monthly_inflow_ngn", "agent_region", "prior_defaults"} <= set(f)


def test_r2_matured_drops_unlabelled_rows(loans, mature):
    assert len(mature) == len(loans) - 213
    assert mature["defaulted"].notna().all() and list(mature.index) == list(range(len(mature)))


def test_r3_forward_splits_respect_time_and_maturity(mature):
    splits = ls.forward_splits(mature, n_splits=4, val_days=45)
    assert len(splits) == 4
    disb = pd.to_datetime(mature["disbursed_on"])
    due = disb + pd.to_timedelta(mature["term_days"], unit="D")
    prev_end = None
    for tr, va in splits:
        assert len(tr) > 100 and len(va) > 50
        assert not set(tr) & set(va)
        assert due.iloc[tr].max() <= disb.iloc[va].min(), "a training loan had not matured when validation began"
        if prev_end is not None:
            assert disb.iloc[va].min() > prev_end
        prev_end = disb.iloc[va].max()
    assert prev_end == disb.max()


def test_r4_expected_cost_exact():
    y, p, a = [1, 0, 0, 1], [0.1, 0.9, 0.2, 0.8], [100, 200, 300, 400]
    assert ls.expected_cost(y, p, a, 0.5) == pytest.approx((0.6 * 100 + 0.08 * 200) / 1000)
    assert ls.expected_cost(y, p, a, 0.0) == pytest.approx(0.08 * 500 / 1000)  # reject everyone
    assert ls.expected_cost(y, p, a, 1.01) == pytest.approx(0.6 * 500 / 1000)  # approve everyone


def test_r5_best_threshold_beats_fixed_half():
    rng = np.random.default_rng(1)
    y = (rng.random(2000) < 0.12).astype(int)
    p = np.clip(0.12 + 0.25 * (y - 0.12) + rng.normal(0, 0.1, 2000), 0.001, 0.999)
    a = rng.integers(10, 100, 2000)
    t, c = ls.best_threshold(y, p, a)
    assert 0 < t < 1 and c == pytest.approx(ls.expected_cost(y, p, a, t))
    assert c <= ls.expected_cost(y, p, a, 0.5) and c <= ls.expected_cost(y, p, a, 0.12)
    grid = [ls.expected_cost(y, p, a, g) for g in np.linspace(0.01, 0.99, 99)]
    assert c <= min(grid) + 1e-12


def test_r6_bootstrap_ci_behaviour():
    assert ls.bootstrap_ci([0.5] * 10) == pytest.approx((0.5, 0.5))
    v = np.random.default_rng(0).normal(1.0, 0.3, 40)
    lo, hi = ls.bootstrap_ci(v, seed=3)
    assert lo < v.mean() < hi and (lo, hi) == ls.bootstrap_ci(v, seed=3)
    w = np.random.default_rng(0).normal(1.0, 0.3, 400)
    assert ls.bootstrap_ci(w)[1] - ls.bootstrap_ci(w)[0] < hi - lo


@pytest.fixture(scope="module")
def rec(loans):
    return ls.select_and_fit(loans, seed=0)


def test_r7_recommendation_fields(rec):
    assert 0 < rec.threshold < 1 and rec.model_name
    assert "collection_calls_made" not in rec.features
    assert rec.cv_ci[0] <= rec.cv_cost <= rec.cv_ci[1] + 1e-9
    assert isinstance(rec.table, pd.DataFrame) and len(rec.table) >= 2, "compare at least two candidates"


def test_r7_cv_estimate_is_not_leaky(rec):
    # A model that sees collection calls scores ~0.01 under random CV. An honest forward estimate is far higher.
    assert 0.03 < rec.cv_cost < 0.09


def test_r7_predict_handles_unseen_region_and_new_rows(rec, loans):
    new = loans.tail(5).copy()
    new["agent_region"] = "Abuja"
    p = np.asarray(rec.model.predict_proba(new))
    assert p.shape == (5,) and ((0 <= p) & (p <= 1)).all()


def test_r7_deterministic(loans, rec):
    again = ls.select_and_fit(loans, seed=0)
    assert again.threshold == rec.threshold and again.cv_cost == rec.cv_cost


def test_r7_forward_to_recent_matured_loans_beats_no_model(loans):
    cut = "2025-09-01"
    early = loans[pd.to_datetime(loans["disbursed_on"]) + pd.to_timedelta(loans["term_days"], unit="D") <= cut]
    late = ls.matured(loans[pd.to_datetime(loans["disbursed_on"]) >= cut])
    r = ls.select_and_fit(early, seed=0)
    y, a = late["defaulted"].astype(int).to_numpy(), late["amount_ngn"].to_numpy()
    p = np.asarray(r.model.predict_proba(late))
    base = min(ls.expected_cost(y, p * 0, a, 1.0), ls.expected_cost(y, p * 0 + 1, a, 0.0))
    assert ls.expected_cost(y, p, a, r.threshold) <= base * 1.02
