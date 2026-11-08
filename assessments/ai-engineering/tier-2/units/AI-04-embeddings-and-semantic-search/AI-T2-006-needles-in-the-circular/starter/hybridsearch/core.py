"""Chunking, BM25, rank fusion and a hybrid searcher. Numpy and the standard library only."""
from __future__ import annotations

from toyembed import tokenize  # noqa: F401  (the tokenizer used by the embedder; use it for BM25 too)


def chunk_text(text: str, size: int, overlap: int) -> list[str]:
    """R1: split on whitespace into windows of `size` words advancing by `size - overlap`.
    Windows start at word 0; stop after the first window whose end reaches the last word; empty text gives [].
    Raise ValueError unless 0 <= overlap < size."""
    raise NotImplementedError("R1: chunk_text")


class BM25:
    """R2: Okapi BM25 over pre-tokenised documents (lists of tokens)."""

    def __init__(self, docs_tokens, k1: float = 1.5, b: float = 0.75):
        self.k1, self.b = k1, b
        raise NotImplementedError("R2: build term frequencies, document lengths, idf")

    def score(self, query_tokens):
        """Numpy array with one score per document. Each DISTINCT query term counts once; unknown terms are ignored.
        idf = ln(1 + (N - df + 0.5) / (df + 0.5)); term score = idf * f * (k1 + 1) / (f + k1 * (1 - b + b * len / avglen))."""
        raise NotImplementedError("R2: score")


def rrf(rankings, k: int = 60, weights=None) -> list:
    """R3: reciprocal rank fusion. score(d) = sum over rankings of weight / (k + rank), rank 1-based;
    documents missing from a ranking add nothing. Return ids by descending score, ties by smaller id."""
    raise NotImplementedError("R3: rrf")


def evaluate(searcher, queries, relevant, k: int = 5) -> dict:
    """R4: {'recall': mean |top-k ∩ rel| / |rel|, 'mrr': mean reciprocal rank over the first 20 results (0 if absent),
    'n_queries'} over queries with a non-empty relevant set. `searcher.search(query, k)` returns a list of document ids."""
    raise NotImplementedError("R4: evaluate")


def build_searcher(docs, embed, dev_queries, dev_relevant):
    """R5: build and TUNE a retriever. `docs` are long strings, `embed(list_of_str)` returns an (n, d) array,
    dev_queries/dev_relevant are labelled development queries. Return an object with
    search(query: str, k: int = 5) -> list[int] of DOCUMENT ids, best first (no duplicates).
    Chunking, the lexical and dense components, the fusion and every parameter are yours to choose and justify.
    Never use the test queries."""
    raise NotImplementedError("R5: build_searcher")
