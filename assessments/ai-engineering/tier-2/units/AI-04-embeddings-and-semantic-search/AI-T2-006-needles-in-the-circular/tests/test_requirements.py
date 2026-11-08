"""Public requirement tests (FAIL on the starter). Hidden tests use other worlds and corpora."""
import math

import numpy as np
import pytest

import circulars
import hybridsearch as h
from toyembed import tokenize


def test_r1_chunk_text_windows():
    text = " ".join(f"w{i}" for i in range(10))
    assert h.chunk_text(text, 4, 1) == ["w0 w1 w2 w3", "w3 w4 w5 w6", "w6 w7 w8 w9"]
    assert h.chunk_text(text, 4, 0) == ["w0 w1 w2 w3", "w4 w5 w6 w7", "w8 w9"]
    assert h.chunk_text(text, 20, 5) == [text] and h.chunk_text("", 4, 1) == []
    assert h.chunk_text("a  b\nc", 2, 0) == ["a b", "c"]


@pytest.mark.parametrize("size,overlap", [(4, 4), (4, 5), (0, 0), (3, -1)])
def test_r1_bad_arguments(size, overlap):
    with pytest.raises(ValueError):
        h.chunk_text("a b c d e", size, overlap)


def test_r2_bm25_matches_formula():
    docs = [["a", "b", "a"], ["b", "c"]]
    bm = h.BM25(docs)
    idf_a, idf_b = math.log(2.0), math.log(1.2)
    avg = 2.5

    def term(idf, f, ln):
        return idf * f * 2.5 / (f + 1.5 * (0.25 + 0.75 * ln / avg))
    s = bm.score(["a"])
    assert s == pytest.approx([term(idf_a, 2, 3), 0.0])
    s = bm.score(["a", "b", "b", "zzz"])                     # duplicates count once; unknown ignored
    assert s == pytest.approx([term(idf_a, 2, 3) + term(idf_b, 1, 3), term(idf_b, 1, 2)])
    assert bm.score([]).tolist() == [0.0, 0.0]


def test_r3_rrf():
    assert h.rrf([[1, 2, 3], [3, 1, 2]]) == [1, 3, 2]
    assert h.rrf([[1, 2], [2]], k=1) == [2, 1]
    assert h.rrf([[5], [4]]) == [4, 5]                      # exact tie: smaller id first
    assert h.rrf([[1, 2], [2, 1]], weights=[1.0, 3.0]) == [2, 1]
    assert h.rrf([]) == []


class Fixed:
    def __init__(self, table):
        self.table = table

    def search(self, q, k=5):
        return self.table[q][:k]


def test_r4_evaluate():
    s = Fixed({"q1": [5, 1, 2, 9], "q2": [7, 8], "q3": [1]})
    r = h.evaluate(s, ["q1", "q2", "q3"], [[1, 2], [0], []], k=2)
    assert r["n_queries"] == 2 and r["recall"] == pytest.approx(0.25) and r["mrr"] == pytest.approx(0.25)


@pytest.fixture(scope="module")
def world_and_searcher():
    w = circulars.make_circular_world(2026)
    dq, dr, _ = w["dev"]
    return w, h.build_searcher(w["docs"], w["embed"], dq, dr)


def _baselines(w):
    docs_tok = [tokenize(d) for d in w["docs"]]
    bm = h.BM25(docs_tok)
    E = w["embed"](w["docs"])
    E = E / np.maximum(np.linalg.norm(E, axis=1, keepdims=True), 1e-12)

    class BM:
        def search(self, q, k=5):
            return [int(i) for i in np.argsort(-bm.score(tokenize(q)), kind="stable")[:k]]

    class Dense:
        def search(self, q, k=5):
            v = w["embed"]([q])[0]
            v = v / max(np.linalg.norm(v), 1e-12)
            return [int(i) for i in np.argsort(-(E @ v), kind="stable")[:k]]
    return BM(), Dense()


def test_r5_searcher_contract(world_and_searcher):
    w, s = world_and_searcher
    out = s.search(w["test"][0][0], k=7)
    assert len(out) == 7 and len(set(out)) == 7 and all(0 <= d < 60 for d in out)


def test_r5_hybrid_beats_whole_document_baselines(world_and_searcher):
    w, s = world_and_searcher
    tq, tr, _ = w["test"]
    bm, dense = _baselines(w)
    mine = h.evaluate(s, tq, tr)
    best = max(h.evaluate(bm, tq, tr)["mrr"], h.evaluate(dense, tq, tr)["mrr"])
    assert mine["mrr"] >= 0.65 and mine["mrr"] >= best + 0.15 and mine["recall"] >= 0.5


def test_r5_both_query_kinds_are_served(world_and_searcher):
    w, s = world_and_searcher
    tq, tr, kinds = w["test"]
    for kind, bar in (("id", 0.85), ("topic", 0.5)):
        ix = [i for i, k in enumerate(kinds) if k == kind]
        assert h.evaluate(s, [tq[i] for i in ix], [tr[i] for i in ix])["mrr"] >= bar, kind
