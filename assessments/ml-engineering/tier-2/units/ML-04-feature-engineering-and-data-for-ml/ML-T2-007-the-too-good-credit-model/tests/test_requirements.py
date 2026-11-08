"""Public requirement tests (R1-R4). Fail on the starter, pass on a sound solution."""
import numpy as np
import pytest

import loan_audit as la
from conftest import DATA, DICT

LEAKS = {"dpd_at_month_end", "collections_calls", "restructured_flag", "bureau_score_refreshed"}


@pytest.fixture(scope="module")
def d():
    return la.load_loans(DATA), la.load_dictionary(DICT)


def test_r1_audit_structure(d):
    data, dic = d
    a = la.audit_features(data, dic)
    assert set(a) == set(la.candidate_features(data))
    for v in a.values():
        assert v["verdict"] in ("leak", "ok") and 0.5 <= v["auc"] <= 1.0
        assert (v["verdict"] == "leak") == bool(v["reasons"])


def test_r1_finds_documented_and_hidden_leaks(d):
    data, dic = d
    a = la.audit_features(data, dic)
    assert {f for f, v in a.items() if v["verdict"] == "leak"} == LEAKS
    assert "AUC" in " ".join(a["bureau_score_refreshed"]["reasons"]) or "auc" in " ".join(a["bureau_score_refreshed"]["reasons"]).lower()


def test_r1_documentation_alone_is_not_enough(d):
    data, dic = d
    clean = {k: "application" for k in dic}
    a = la.audit_features(data, clean)
    assert a["dpd_at_month_end"]["verdict"] == "leak" and a["bureau_score_refreshed"]["verdict"] == "leak"
    assert a["credit_score"]["verdict"] == "ok"


def test_r1_threshold_is_respected(d):
    data, dic = d
    clean = {k: "application" for k in dic}
    strict = la.audit_features(data, clean, auc_threshold=0.6)
    assert strict["credit_score"]["verdict"] == "leak"


def test_r2_split_is_temporal_and_customer_disjoint(d):
    data, _ = d
    tr, te = la.honest_split(data, 18)
    m, c = data["disbursed_month"], data["customer_id"]
    assert len(tr) > 400 and len(te) > 100
    assert m[tr].max() < 18 <= m[te].min()
    assert not (set(c[tr]) & set(c[te]))
    assert set(te) == set(np.where(m >= 18)[0])


def test_r2_removes_overlapping_customers_only(d):
    data, _ = d
    tr, te = la.honest_split(data, 18)
    m, c = data["disbursed_month"], data["customer_id"]
    early = set(np.where(m < 18)[0])
    dropped = early - set(tr)
    assert dropped and all(c[i] in set(c[te]) for i in dropped)


def test_r3_naive_is_too_good_and_honest_is_modest(d):
    data, dic = d
    r = la.leaky_vs_honest(data, dic, 18, 0)
    assert r["auc_naive"] > 0.97
    assert 0.58 <= r["auc_honest"] <= 0.8
    assert r["auc_naive"] - r["auc_honest"] > 0.2
    assert r["dropped"] == sorted(LEAKS)


def test_r3_is_deterministic(d):
    data, dic = d
    assert la.leaky_vs_honest(data, dic, 18, 3) == la.leaky_vs_honest(data, dic, 18, 3)


def test_r4_psi_definition():
    a = np.arange(100.0)
    assert la.psi(a, a) == pytest.approx(0.0, abs=1e-12)
    shifted = la.psi(a, a + 50)
    assert shifted > 0.5
    assert la.psi(a, a + 50) > la.psi(a, a + 10) > 0


def test_r4_drift_report_flags_inflation(d):
    data, _ = d
    r = la.drift_check(data, ["amount_ngn", "income_ngn", "credit_score", "tenor_months"], 18)
    assert max(r, key=r.get) == "income_ngn" and r["income_ngn"] > 0.1
    assert r["tenor_months"] < 0.1
