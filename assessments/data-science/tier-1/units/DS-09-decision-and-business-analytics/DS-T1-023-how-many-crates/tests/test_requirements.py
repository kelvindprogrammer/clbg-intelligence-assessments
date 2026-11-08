"""Public requirement tests. They FAIL on the starter. Hidden tests regenerate the sales history."""
import numpy as np
import pytest
from scipy import stats

import crate_planner as cp
from conftest import DATA

P, C, S = 20000, 12000, 5000


def test_critical_ratio_and_validation():
    assert cp.critical_ratio(P, C, S) == pytest.approx(8000 / 15000)
    for bad in [(10, 12, 5), (20, 12, 12), (20, 12, 15)]:
        with pytest.raises(ValueError):
            cp.critical_ratio(*bad)


def test_expected_profit_by_hand():
    # q=3 against demands 1, 3, 5: profits 1*20+2*5-36 = -6 (in thousands), 3*20-36 = 24, 24
    assert cp.expected_profit(3, [1, 3, 5], 20, 12, 5) == pytest.approx((-6 + 24 + 24) / 3)
    assert cp.expected_profit(0, [4, 4], P, C, S) == 0


def test_best_quantity_on_a_known_sample():
    q, prof = cp.best_quantity([2, 4, 6, 8, 10], P, C, S)
    assert q == 6  # critical ratio 0.533: the third of five order statistics
    assert prof == pytest.approx(cp.expected_profit(6, [2, 4, 6, 8, 10], P, C, S))


def test_best_quantity_tie_goes_to_smaller_q():
    assert cp.best_quantity([5, 5, 5], 10, 5, 0)[0] == 5
    assert cp.best_quantity([3], 10, 5, 0)[0] == 3


def test_poisson_quantity_matches_cdf_rule():
    cr = cp.critical_ratio(P, C, S)
    for lam in (3.0, 8.0, 14.0):
        q = cp.poisson_quantity(lam, P, C, S)
        assert stats.poisson.cdf(q, lam) >= cr > stats.poisson.cdf(q - 1, lam)


def test_exact_poisson_profit_agrees_with_simulation_and_peaks_at_the_rule():
    lam = 10.0
    rng = np.random.default_rng(0)
    sim = cp.expected_profit(9, rng.poisson(lam, 200_000), P, C, S)
    assert cp.expected_profit_poisson(9, lam, P, C, S) == pytest.approx(sim, rel=0.01)
    qs = range(0, 25)
    best = max(qs, key=lambda q: cp.expected_profit_poisson(q, lam, P, C, S))
    assert best == cp.poisson_quantity(lam, P, C, S)


def test_censored_flags():
    import pandas as pd
    df = pd.DataFrame({"crates_stocked": [8, 8, 10, 0], "crates_sold": [8, 5, 10, 0]})
    assert cp.censored_flags(df).tolist() == [True, False, True, False]


def test_censored_mle_beats_the_naive_mean_on_capped_data():
    rng = np.random.default_rng(1)
    demand = rng.poisson(14, 3000)
    cap = rng.integers(8, 13, 3000)
    sold = np.minimum(demand, cap)
    assert sold.mean() < 11
    assert cp.censored_poisson_mle(sold, cap) == pytest.approx(14, rel=0.04)


def test_censored_mle_equals_the_mean_when_nothing_is_censored():
    sold = np.array([3, 4, 5, 6, 2, 4])
    assert cp.censored_poisson_mle(sold, sold + 10) == pytest.approx(sold.mean(), rel=1e-4)


def test_plan_table_on_the_official_history():
    df = cp.load_sales(DATA)
    t = cp.plan_by_day_type(df, P, C, S).set_index("day_type")
    assert list(cp.plan_by_day_type(df, P, C, S).columns) == ["day_type", "n_days", "share_censored", "lambda_naive", "lambda_mle", "q_naive", "q_mle"]
    assert t["n_days"].sum() == 240
    assert t.loc["market_day", "share_censored"] > 0.5
    assert t.loc["market_day", "lambda_mle"] > t.loc["market_day", "lambda_naive"] + 1
    assert t.loc["market_day", "q_mle"] > t.loc["market_day", "q_naive"]
    assert t.loc["weekday", "q_mle"] >= t.loc["weekday", "q_naive"]
