"""Public requirement tests: behavioural checks of the contract. They FAIL on the starter.

The hidden evaluation scores your estimator against the LATENT true rates of these schools
and of re-generated states, and against next year's results. These public tests only check
behaviour that any sensible small-area estimator must have.
"""
import numpy as np
import pandas as pd
import pytest

import smallarea as sa


@pytest.fixture(scope="module")
def est(results, schools):
    return sa.estimate_rates(results, schools)


def _pooled(results):
    g = results.groupby("school_id")[["candidates", "credit_passes"]].sum()
    return g["credit_passes"] / g["candidates"], g["candidates"]


def test_output_contract(est, schools):
    assert list(est.columns) == sa.OUTPUT_COLUMNS
    assert list(est["school_id"]) == sorted(schools["school_id"])
    assert est[["estimate", "lower", "upper"]].notna().all().all()
    assert ((0 <= est.lower) & (est.lower <= est.estimate) & (est.estimate <= est.upper) & (est.upper <= 1)).all()


def test_level_changes_width(results, schools, est):
    wide = sa.estimate_rates(results, schools, level=0.99)
    w90 = (est.upper - est.lower).to_numpy()
    w99 = (wide.upper - wide.lower).to_numpy()
    assert (w99 >= w90 - 1e-12).all() and w99.mean() > 1.2 * w90.mean()


def test_tiny_perfect_schools_are_not_reported_as_perfect(est, results):
    raw, n = _pooled(results)
    perfect = raw[(raw == 1.0) & (n <= 8)].index
    assert len(perfect) >= 3
    e = est.set_index("school_id").loc[perfect]
    assert (e["estimate"] < 0.95).all()
    assert (e["upper"] - e["lower"] > 0.10).all()


def test_large_schools_stay_close_to_their_data(est, results):
    raw, n = _pooled(results)
    big = n[n >= 400].index
    e = est.set_index("school_id").loc[big, "estimate"]
    assert (abs(e - raw.loc[big]) < 0.03).all()


def test_intervals_narrow_with_more_data(est, results):
    _, n = _pooled(results)
    w = (est.set_index("school_id")["upper"] - est.set_index("school_id")["lower"]).loc[n.index]
    assert np.corrcoef(np.log(n), w)[0, 1] < -0.5


def test_beats_raw_on_a_held_out_year(results, schools):
    """Fit on 2022-2023, predict the 2024 rate. Raw rates are the baseline."""
    train = results[results.year < 2024]
    test = results[results.year == 2024].set_index("school_id")
    e = sa.estimate_rates(train, schools).set_index("school_id")["estimate"].loc[test.index]
    raw, _ = _pooled(train)
    y = test["credit_passes"] / test["candidates"]
    assert ((e - y) ** 2).mean() < 0.95 * ((raw.loc[test.index] - y) ** 2).mean()


def test_school_without_results(results, schools):
    extra = pd.concat([schools, pd.DataFrame([{"school_id": "SCH-9999", "lga": "LGA-01", "ownership": "public",
                                                "location": "rural"}])], ignore_index=True)
    e = sa.estimate_rates(results, extra).set_index("school_id").loc["SCH-9999"]
    assert 0 < e["lower"] < e["estimate"] < e["upper"] < 1


def test_select_schools(results, schools):
    top = sa.select_schools(results, schools, 10, "top")
    bottom = sa.select_schools(results, schools, 20, "bottom")
    assert len(set(top)) == 10 and len(set(bottom)) == 20 and not set(top) & set(bottom)
    raw, n = _pooled(results)
    assert n.loc[top].median() > 15, "an award list made of tiny schools is what raw ranking produces"
    with pytest.raises(ValueError):
        sa.select_schools(results, schools, 5, "middle")
