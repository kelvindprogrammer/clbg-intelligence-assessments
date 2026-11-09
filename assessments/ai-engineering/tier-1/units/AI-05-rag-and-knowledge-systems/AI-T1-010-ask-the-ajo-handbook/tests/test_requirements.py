"""Requirement tests R1-R7. They fail on the starter and pass on a correct implementation."""
import math

import pytest

import handbook as h
import ragkit as r


def test_r1_tokenize():
    assert r.tokenize("The Loan, of 5000 naira; is due!") == ["loan", "5000", "naira", "due"]
    assert r.tokenize("") == []


def test_r2_chunk_windows_and_ids():
    ch = r.chunk_text("A", "one two three four five six seven", 3, 1)
    assert [c["text"] for c in ch] == ["one two three", "three four five", "five six seven"]
    assert [c["id"] for c in ch] == ["A#0", "A#1", "A#2"] and [c["start"] for c in ch] == [0, 2, 4]


def test_r2_short_tail_and_no_redundant_window():
    ch = r.chunk_text("B", "a b c d e", 3, 1)
    assert [c["text"] for c in ch] == ["a b c", "c d e"]
    assert len(r.chunk_text("B", "a b c", 3, 1)) == 1
    assert r.chunk_text("B", "", 3, 1) == []
    assert [c["text"] for c in r.chunk_text("B", "a b c d", 3, 0)] == ["a b c", "d"]


@pytest.mark.parametrize("size,ov", [(0, 0), (3, 3), (3, -1)])
def test_r2_bad_parameters(size, ov):
    with pytest.raises(ValueError):
        r.chunk_text("A", "a b c", size, ov)


def _tiny():
    return r.BM25Index([{"id": "A#0", "text": "loan interest rate"}, {"id": "B#0", "text": "loan loan guarantor"},
                        {"id": "C#0", "text": "meeting notice"}])


def test_r3_bm25_exact_scores():
    s = _tiny().score("loan interest")
    assert math.isclose(s["A#0"], 1.3735695926697864, rel_tol=1e-9)
    assert math.isclose(s["B#0"], 0.6454985466035854, rel_tol=1e-9)
    assert "C#0" not in s


def test_r3_search_order_ties_and_k():
    ix = r.BM25Index([{"id": "Z#0", "text": "alpha beta"}, {"id": "A#0", "text": "alpha beta"}, {"id": "M#0", "text": "gamma"}])
    assert [i for i, _ in ix.search("alpha", 5)] == ["A#0", "Z#0"]
    assert len(ix.search("alpha", 1)) == 1 and ix.search("zzz", 3) == []


def test_r3_repeated_query_words_count_once():
    ix = _tiny()
    assert ix.score("loan loan loan") == ix.score("loan")


def test_r4_context_budget_and_format():
    by = {"A#0": {"text": "one two three"}, "B#0": {"text": "four five"}, "C#0": {"text": "six"}}
    ctx, used = r.build_context([("A#0", 2.0), ("B#0", 1.0), ("C#0", .5)], by, 5)
    assert ctx == "[A#0] one two three\n\n[B#0] four five" and used == ["A#0", "B#0"]
    ctx, used = r.build_context([("A#0", 2.0), ("B#0", 1.0), ("C#0", .5)], by, 4)
    assert used == ["A#0"], "stop at the first chunk that does not fit; do not skip ahead"
    assert r.build_context([], by, 10) == ("", [])


def test_r5_extract_citations():
    a = "Pay on time [S01#0]. Loans need guarantors [S04#1] and [S01#0]. See [bogus] and [S2#x]."
    assert r.extract_citations(a) == ["S01#0", "S04#1"]


def test_r5_check_answer_verdicts():
    g = r.check_answer("Pay by the fifth [S01#0].", ["S01#0"])
    assert g["verdict"] == "grounded" and g["unsupported"] == [] and g["uncited_sentences"] == 0
    f = r.check_answer("Pay by the fifth [S77#0].", ["S01#0"])
    assert f["verdict"] == "forged" and f["unsupported"] == ["S77#0"]
    m = r.check_answer("Pay by the fifth [S01#0]. Also be kind.", ["S01#0"])
    assert m["verdict"] == "uncited" and m["uncited_sentences"] == 1
    assert r.check_answer("No citation here.", ["S01#0"])["verdict"] == "uncited"


def _index(size=30, ov=5, seed=7):
    docs = h.make_handbook(seed)
    return r.BM25Index([c for d in docs for c in r.chunk_text(d["id"], d["text"], size, ov)])


def test_r6_faithful_answer_passes():
    out = r.answer_question(h.make_model("faithful"), _index(), "What is the monthly contribution due from every member?", 3, 120)
    assert out["verdict"] == "grounded" and not out["abstained"] and out["answer"].endswith("].") and out["used"]


@pytest.mark.parametrize("mode,verdict", [("forger", "forged"), ("uncited", "uncited"), ("mixed", "uncited")])
def test_r6_unverified_answers_are_withheld(mode, verdict):
    out = r.answer_question(h.make_model(mode), _index(), "How many guarantors must each borrower present?", 3, 120)
    assert out["verdict"] == verdict and out["answer"] == "I could not verify an answer."


def test_r6_abstains_without_evidence():
    out = r.answer_question(h.make_model("faithful"), _index(), "xylophone zeppelin", 3, 120)
    assert out["abstained"] and out["answer"] == "I don't know." and out["verdict"] == "abstained"
    out = r.answer_question(h.make_model("faithful"), _index(), "monthly contribution", 3, 1)
    assert out["abstained"], "a budget too small for any chunk leaves nothing to cite"


def test_r7_evaluate_counts_document_level_hits():
    ix = r.BM25Index([{"id": "S01#0", "text": "loan interest"}, {"id": "S02#0", "text": "loan guarantor"}, {"id": "S02#1", "text": "interest loan interest"}])
    qa = [{"q": "interest", "gold": "S01"}, {"q": "guarantor", "gold": "S02"}, {"q": "zzz", "gold": "S01"}]
    e = r.evaluate(ix, qa, 1)
    assert math.isclose(e["recall_at_k"], 1 / 3) and math.isclose(e["mrr"], 1 / 3)
    e2 = r.evaluate(ix, qa, 3)
    assert math.isclose(e2["recall_at_k"], 2 / 3) and math.isclose(e2["mrr"], (0.5 + 1) / 3)
