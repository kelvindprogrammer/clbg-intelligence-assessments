"""Public requirement tests. They FAIL on the starter. Hidden tests run other experiment scenarios."""
import numpy as np
import pandas as pd
import pytest

import abtest_audit as ab
from conftest import DATA


def frame(n_a, n_b, p_a=0.12, p_b=0.12, seed=0, whale=None):
    """whale=(count, value) turns the first `count` B users into big spenders."""
    rng = np.random.default_rng(seed)
    rows = []
    for arm, n, p in (("A", n_a, p_a), ("B", n_b, p_b)):
        conv = (rng.random(n) < p).astype(int)
        rev = np.round(rng.lognormal(7.6, 0.9, n)) * conv
        rows.append(pd.DataFrame({"user_id": [f"{arm}{i}" for i in range(n)], "arm": arm, "assign_day": 1,
                                  "device": "ios", "converted": conv, "revenue_ngn": rev}))
    df = pd.concat(rows, ignore_index=True)
    if whale:
        count, value = whale
        idx = df.index[df["arm"] == "B"][:count]
        df.loc[idx, ["converted", "revenue_ngn"]] = [1, value]
    return df


# R1
def test_srm_flags_a_lopsided_split_and_passes_a_fair_one():
    assert ab.srm_check(frame(5000, 4300))["flagged"]
    ok = ab.srm_check(frame(5000, 4960))
    assert not ok["flagged"] and ok["n_a"] == 5000 and ok["n_b"] == 4960


# R2
def test_find_contaminated():
    df = pd.DataFrame({"user_id": ["u1", "u1", "u2", "u3", "u3", "u4"], "arm": list("ABAAAB")})
    assert ab.find_contaminated(df) == {"u1"}


# R3
def test_conversion_effect_matches_the_formulae():
    df = frame(4000, 4000, 0.10, 0.12, seed=2)
    r = ab.conversion_effect(df)
    pa, pb = df.groupby("arm")["converted"].mean()
    assert r["lift"] == pytest.approx(pb - pa)
    assert r["ci_low"] < r["lift"] < r["ci_high"]
    assert 0 < r["p_value"] < 0.2


def test_conversion_null_has_large_p_value():
    assert ab.conversion_effect(frame(4000, 4000, 0.12, 0.12, seed=6))["p_value"] > 0.05


# R4
def test_revenue_effect_is_robust_to_one_whale():
    base = ab.revenue_effect(frame(3000, 3000, seed=4), n_boot=400)
    whale = ab.revenue_effect(frame(3000, 3000, seed=4, whale=(1, 40_000_000)), n_boot=400)
    assert abs(whale["estimate"] - base["estimate"]) < 0.25 * abs(base["estimate"]) + 30


def test_cluster_of_big_spenders_does_not_manufacture_significance():
    r = ab.revenue_effect(frame(3000, 3000, seed=4, whale=(14, 250_000)), n_boot=400)
    assert r["naive_p_value"] < 0.05 < r["p_value"]


def test_revenue_effect_is_reproducible_and_ordered():
    df = frame(1500, 1500, 0.1, 0.13, seed=8)
    r1, r2 = ab.revenue_effect(df, seed=3, n_boot=300), ab.revenue_effect(df, seed=3, n_boot=300)
    assert r1 == r2 and r1["ci_low"] <= r1["estimate"] <= r1["ci_high"]


# R5
def test_holm_adjust_known_values_and_order():
    assert ab.holm_adjust([0.04, 0.01, 0.03]) == pytest.approx([0.06, 0.03, 0.06])
    assert ab.holm_adjust([0.5]) == [0.5]
    assert max(ab.holm_adjust([0.9, 0.8])) <= 1.0


# R6
def test_peeking_inflates_false_positives():
    one = ab.peeking_inflation(200, 1, 4000, seed=1)
    ten = ab.peeking_inflation(200, 10, 4000, seed=1)
    assert 0.035 <= one <= 0.065
    assert 0.14 <= ten <= 0.25


# R7
def test_verdict_structure_and_srm_short_circuit():
    v = ab.analyze_experiment(frame(5000, 4000))
    assert v["verdict"] == "invalid" and v["srm"]["flagged"]
    assert v["conversion"] is None


def test_verdict_on_the_official_export():
    df = ab.load_experiment(DATA)
    v = ab.analyze_experiment(df)
    assert v["n_contaminated"] > 30
    assert set(v) >= {"verdict", "srm", "n_contaminated", "conversion", "revenue", "adjusted_p"}
    assert v["verdict"] == "ship"
    assert v["adjusted_p"]["conversion"] >= v["conversion"]["p_value"]
