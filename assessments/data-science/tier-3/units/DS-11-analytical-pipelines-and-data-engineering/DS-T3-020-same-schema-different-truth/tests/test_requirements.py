"""Public requirement tests (a sample; assessors run a hidden suite on freshly generated, faulted feeds).
The public stream's faults are NOT listed here; finding them is part of the work. These tests use clean batches
(0-14) with faults you can see being injected."""
import numpy as np
import pandas as pd
import pytest

from conftest import BATCHES, CONTRACT

import contractgate as cg


@pytest.fixture(scope="module")
def batches():
    return cg.load_batches(BATCHES)


@pytest.fixture(scope="module")
def contract():
    return cg.load_contract(CONTRACT)


def test_r1_infer_schema(batches):
    s = cg.infer_schema(batches[0])
    assert s == {"market_id": "string", "state": "string", "commodity": "string", "observed_on": "string",
                 "price_ngn_per_kg": "float", "n_quotes": "int"}


def test_r2_schema_diff_codes(batches, contract):
    base = cg.infer_schema(batches[0])
    assert cg.diff_schema(contract, base) == []
    assert cg.diff_schema(contract, {k: v for k, v in base.items() if k != "n_quotes"}) == ["schema:missing_column:n_quotes"]
    assert cg.diff_schema(contract, {**base, "n_quotes": "string"}) == ["schema:type_change:n_quotes"]
    assert cg.diff_schema(contract, {**base, "n_quotes": "float"}) == []          # int contract accepts float data
    assert cg.diff_schema(contract, {**base, "state": "float"}) == ["schema:type_change:state"]
    assert cg.diff_schema(contract, {**base, "note": "string"}) == ["schema:new_column:note"]


def test_r3_rules_fire_only_above_the_allowed_rate(batches, contract):
    b = batches[1].copy()
    assert cg.validate_batch(b, contract) == []
    b.loc[b.index[:2], "n_quotes"] = np.nan
    assert "rule:null:n_quotes" in cg.validate_batch(b, contract)
    s = batches[1].copy(); s["state"] = s["state"].astype(object); s.loc[s.index[:20], "state"] = None
    assert "rule:null:state" not in cg.validate_batch(s, contract)       # contract allows up to 30% for state
    d = batches[1].copy(); d.loc[d.index[:1], "commodity"] = "Cassava"
    assert cg.validate_batch(d, contract) == []                          # 1 row of 100 is within 1%
    d.loc[d.index[:3], "commodity"] = "Cassava"
    assert "rule:category:commodity" in cg.validate_batch(d, contract)


def test_r3_skips_retyped_columns_without_crashing(batches, contract):
    b = batches[2].copy(); b["n_quotes"] = b["n_quotes"].astype(str) + " quotes"
    del b["observed_on"]
    assert not any(r.endswith(":n_quotes") or r.endswith(":observed_on") for r in cg.validate_batch(b, contract))


def test_r4_baseline_and_drift_on_clean_data_and_unit_change(batches, contract):
    base = cg.fit_baseline(batches[:10], contract)
    for b in batches[10:15]:
        assert cg.detect_drift(b, base) == []
    shifted = b.copy(); shifted["price_ngn_per_kg"] *= 100
    assert cg.detect_drift(shifted, base) == ["drift:scale_shift:price_ngn_per_kg"]
    gone = b.drop(columns=["price_ngn_per_kg"])
    assert not any(r.startswith("drift:scale_shift") for r in cg.detect_drift(gone, base))


def test_r4_inflation_and_a_sunday_are_not_drift(batches, contract):
    base = cg.fit_baseline(batches[:10], contract)
    b = batches[14].copy()
    b["price_ngn_per_kg"] *= 1.12          # 12% rise: a bad month, not a unit change
    assert cg.detect_drift(b, base) == []
    small = batches[14].iloc[:60]
    assert cg.detect_drift(small, base) == []


def test_r5_gate_decisions(batches, contract):
    base = cg.fit_baseline(batches[:10], contract)
    clean = cg.gate(batches[12], contract, base)
    assert clean.action == "accept" and clean.reasons == []
    assert cg.gate(batches[12].rename(columns={"n_quotes": "quotes"}), contract, base).action == "block"
    plus = batches[12].copy(); plus["note"] = None
    d = cg.gate(plus, contract, base)
    assert d.action == "accept" and d.reasons == ["schema:new_column:note"]


def test_r6_run_stream_on_clean_prefix(batches, contract):
    out = cg.run_stream(batches[:15], contract, n_baseline=10)
    assert len(out) == 5 and sum(d.action == "accept" for d in out) >= 4


@pytest.mark.parametrize("kind", list(cg.KINDS))
def test_r7_inject_fault_has_the_required_effect(batches, kind):
    b = batches[3]
    out = cg.inject_fault(b, kind, seed=1)
    assert out is not b
    assert not out.equals(b) or kind == "new_column"
    if kind == "unit_change":
        assert (out["price_ngn_per_kg"] / b["price_ngn_per_kg"]).round(2).eq(100).all()
    if kind == "dup_keys":
        assert 1.2 <= len(out) / len(b) <= 1.3
    if kind == "date_flip":
        assert out["observed_on"].iloc[0] == b["observed_on"].iloc[0][3:5] + "/" + b["observed_on"].iloc[0][:2] + "/" + b["observed_on"].iloc[0][6:]
    with pytest.raises(ValueError):
        cg.inject_fault(b, "gremlins")


def test_r8_operating_characteristics_shape_and_bar(batches, contract):
    oc = cg.operating_characteristics(batches, contract)
    assert list(oc.columns) == ["kind", "n", "detected", "rate"] and oc["kind"].tolist() == ["clean", *cg.KINDS]
    assert oc.loc[0, "rate"] <= 0.2
    assert (oc.loc[1:, "rate"] >= 0.8).all(), oc
