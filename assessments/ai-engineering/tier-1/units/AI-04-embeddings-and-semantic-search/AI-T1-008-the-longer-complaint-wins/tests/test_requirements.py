"""Public requirement tests (FAIL on the starter). Hidden tests use other worlds and edge cases."""
import math

import numpy as np
import pytest

import faqs
import simsearch as ss


def test_r1_normalize_rows_and_zero_rows():
    M = np.array([[3.0, 4.0], [0.0, 0.0], [0.0, -2.0]])
    out = ss.normalize_rows(M)
    assert np.allclose(out, [[0.6, 0.8], [0, 0], [0, -1]]) and not np.isnan(out).any()
    assert M[0, 0] == 3.0                      # input untouched


def test_r2_scores_values():
    Q = np.array([[1.0, 0.0], [0.0, 0.0]])
    D = np.array([[2.0, 0.0], [0.0, 3.0], [1.0, 1.0]])
    assert np.allclose(ss.scores(Q, D, "dot"), [[2, 0, 1], [0, 0, 0]])
    assert np.allclose(ss.scores(Q, D, "cosine"), [[1, 0, 1 / math.sqrt(2)], [0, 0, 0]])
    assert np.allclose(ss.scores(Q, D, "l2")[0], [-1, -math.sqrt(10), -1])
    with pytest.raises(ValueError):
        ss.scores(Q, D, "manhattan")


def test_r3_top_k_order_ties_and_short_corpus():
    Q = np.array([[1.0, 0.0]])
    D = np.array([[1.0, 0.0], [2.0, 0.0], [2.0, 0.0], [0.0, 1.0]])
    idx, sc = ss.top_k(Q, D, 3, "dot")
    assert idx.tolist() == [[1, 2, 0]] and sc.tolist() == [[2.0, 2.0, 1.0]]
    idx, _ = ss.top_k(Q, D, 3, "cosine")
    assert idx.tolist() == [[0, 1, 2]]                         # three-way tie, lowest index first
    assert ss.top_k(Q, D, 10, "l2")[0].shape == (1, 4)


def test_r4_recall_mrr_ndcg_hand_values():
    retrieved = [[5, 1, 2, 9], [7, 8, 9, 0], [3, 4, 6, 1]]
    relevant = [[1, 2], [0], []]
    assert ss.recall_at_k(retrieved, relevant, 2) == pytest.approx((0.5 + 0.0) / 2)
    assert ss.recall_at_k(retrieved, relevant, 4) == pytest.approx((1.0 + 1.0) / 2)
    assert ss.mrr(retrieved, relevant) == pytest.approx((1 / 2 + 1 / 4) / 2)
    dcg = 1 / math.log2(3) + 1 / math.log2(4)
    idcg = 1 + 1 / math.log2(3)
    assert ss.ndcg_at_k(retrieved, relevant, 4) == pytest.approx((dcg / idcg + (1 / math.log2(5)) / 1.0) / 2)


def test_r4_absent_relevant_gives_zero_rr():
    assert ss.mrr([[1, 2, 3]], [[9]]) == 0.0 and ss.recall_at_k([[1, 2, 3]], [[9]], 3) == 0.0


def test_r5_evaluate_structure_and_query_count():
    w = faqs.make_faq_world(5, n_queries=40)
    rel = list(w["relevant"])
    rel[0] = []
    r = ss.evaluate(w["embed"](w["queries"]), w["embed"](w["docs"]), rel, metrics=("cosine", "dot"), k=5)
    assert set(r) == {"cosine", "dot"} and r["cosine"]["n_queries"] == 39
    assert set(r["dot"]) == {"recall", "mrr", "ndcg", "n_queries"}


def test_dot_product_prefers_long_documents_and_cosine_does_not():
    w = faqs.make_faq_world(2026)
    Q, D = w["embed"](w["queries"]), w["embed"](w["docs"])
    res = ss.evaluate(Q, D, w["relevant"], metrics=("dot", "cosine", "l2"), k=5)
    assert res["cosine"]["mrr"] > 0.95 and res["dot"]["mrr"] < 0.6
    idx, _ = ss.top_k(Q, D, 5, "dot")
    hub = np.isin(idx, w["boiler_ids"]).mean()
    idx_c, _ = ss.top_k(Q, D, 5, "cosine")
    assert hub > 0.5 and np.isin(idx_c, w["boiler_ids"]).mean() < 0.02
