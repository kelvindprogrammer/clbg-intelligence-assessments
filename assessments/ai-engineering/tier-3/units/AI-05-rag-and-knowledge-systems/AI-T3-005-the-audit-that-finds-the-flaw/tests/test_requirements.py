"""Requirement tests R1-R6. They fail on the starter and pass on a correct implementation."""
import math

import legalaid as L
import ragaudit as r

KB = [{"id": "P1", "text": "Notice is 30 days."}, {"id": "P2", "text": "Deposit is 10 percent."},
      {"id": "P3", "text": "Repair within 14 days."}]
ITEMS = [{"id": "a", "q": "q1", "answerable": True, "gold_doc": "P1", "gold": "30"},
         {"id": "b", "q": "q2", "answerable": True, "gold_doc": "P2", "gold": "10"},
         {"id": "c", "q": "q3", "answerable": True, "gold_doc": "P3", "gold": "14"},
         {"id": "d", "q": "q4", "answerable": False, "gold_doc": "", "gold": ""}]


def R(answer, cited, retrieved, abstained=False):
    return {"answer": answer, "cited": cited, "retrieved": retrieved, "abstained": abstained}


RES = [R("The answer is 30.", ["P1"], ["P2", "P1"]),          # correct, gold rank 2
       R("The answer is 99.", ["P2"], ["P2", "P1"]),          # wrong and unsupported, gold rank 1
       R(None, [], ["P1", "P2"], True),                       # gold missed, abstained
       R("The answer is 5.", ["P9"], ["P1"])]                 # answered an unanswerable item, forged citation


def test_r1_retrieval_metrics():
    m = r.retrieval_metrics(RES, ITEMS, k=2)
    assert math.isclose(m["recall_at_k"], 2 / 3) and math.isclose(m["mrr"], (0.5 + 1) / 3)
    assert r.retrieval_metrics(RES, ITEMS, k=1)["recall_at_k"] == 1 / 3
    assert r.retrieval_metrics([], [], 5) == {"recall_at_k": 0.0, "mrr": 0.0}


def test_r2_answer_metrics():
    m = r.answer_metrics(RES, ITEMS, KB)
    assert math.isclose(m["accuracy"], 1 / 3)
    assert math.isclose(m["faithful_rate"], 1 / 3)          # only "30" is supported by retrieved text
    assert math.isclose(m["citation_valid_rate"], 2 / 3)    # P9 was never retrieved
    assert m["uncited_rate"] == 0.0


def test_r2_uncited_and_empty_edges():
    res = [R("The answer is 30.", [], ["P1"])]
    m = r.answer_metrics(res, ITEMS[:1], KB)
    assert m["uncited_rate"] == 1.0 and m["citation_valid_rate"] == 1.0
    e = r.answer_metrics([R(None, [], [], True)], ITEMS[:1], KB)
    assert e["accuracy"] == 0.0 and e["faithful_rate"] == 1.0 and e["uncited_rate"] == 0.0


def test_r3_abstention_metrics():
    m = r.abstention_metrics(RES, ITEMS)
    # answerable with gold retrieved: a (answered), b (answered); c missed. unanswerable d answered.
    assert m["over_abstain_rate"] == 0.0 and m["under_abstain_rate"] == 1.0 and m["answered_on_miss_rate"] == 0.0
    res2 = [R(None, [], ["P1"], True), RES[1], R("The answer is 14.", [], ["P1"]), RES[3]]
    m2 = r.abstention_metrics(res2, ITEMS)
    assert m2["over_abstain_rate"] == 0.5 and m2["answered_on_miss_rate"] == 1.0


def test_r4_bootstrap_ci_exact_and_deterministic():
    v = [0, 1, 1, 0, 1, 1, 1, 0, 1, 1]
    a = r.bootstrap_ci(v, n_boot=200, seed=3)
    assert a == r.bootstrap_ci(v, n_boot=200, seed=3)
    assert math.isclose(a[0], 0.4) and math.isclose(a[1], 1.0)
    assert r.bootstrap_ci([1, 1, 1], 50, 0) == (1.0, 1.0)


def test_r4_empty_raises():
    try:
        r.bootstrap_ci([])
    except ValueError:
        return
    raise AssertionError("empty input must raise ValueError")


def test_r5_paired_compare():
    a = [1, 1, 1, 1, 1, 1, 0, 1]
    b = [0, 0, 1, 0, 0, 1, 0, 0]
    out = r.paired_compare(a, b, n_boot=300, seed=1)
    assert math.isclose(out["diff"], 0.625) and out["significant"] is True and out["ci"][0] > 0
    same = r.paired_compare(a, a, n_boot=100, seed=1)
    assert same["diff"] == 0 and same["significant"] is False


def test_r6_audit_report_shape():
    items = L.make_items(1)
    rep = r.audit(L.make_system((), seed=1), L.make_kb(1), items, seed=1)
    assert set(rep) >= {"metrics", "flags"} and isinstance(rep["flags"], list) and rep["flags"] == sorted(rep["flags"])
    assert set(rep["metrics"]) >= {"recall_at_k", "mrr", "accuracy", "faithful_rate", "citation_valid_rate",
                                   "over_abstain_rate", "under_abstain_rate"}


def test_r6_clean_system_has_no_flags_across_seeds():
    for seed in range(6):
        rep = r.audit(L.make_system((), seed=seed), L.make_kb(seed), L.make_items(seed), seed=seed)
        assert rep["flags"] == [], (seed, rep["flags"])


def test_r6_each_planted_flaw_is_diagnosed_exactly():
    for flaw in L.FLAWS:
        want = sorted({flaw, "retrieval_miss"}) if flaw == "parametric_leak" else [flaw]
        for seed in (1, 2, 3):
            rep = r.audit(L.make_system(flaw, seed=seed), L.make_kb(seed), L.make_items(seed), seed=seed)
            assert rep["flags"] == want, (flaw, seed, rep["flags"])


def test_r6_two_simultaneous_flaws():
    for pair in [("unfaithful", "over_abstain"), ("citation_forgery", "under_abstain")]:
        for seed in (1, 2):
            rep = r.audit(L.make_system(pair, seed=seed), L.make_kb(seed), L.make_items(seed), seed=seed)
            assert rep["flags"] == sorted(pair), (pair, seed, rep["flags"])


def test_r6_accuracy_alone_hides_the_leak():
    kb, items = L.make_kb(2), L.make_items(2)
    leak = r.audit(L.make_system("parametric_leak", seed=2), kb, items, seed=2)["metrics"]
    assert leak["accuracy"] >= 0.9 and leak["recall_at_k"] < 0.8
