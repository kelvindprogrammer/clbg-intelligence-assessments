"""Similarity search from scratch. Numpy only; do not use scikit-learn or any vector library."""
from __future__ import annotations


def normalize_rows(M):
    """R1: L2-normalise each row; all-zero rows stay all-zero (no NaN)."""
    raise NotImplementedError("R1: normalize_rows")


def scores(Q, D, metric: str):
    """R2: (n_queries, n_docs) matrix; higher is always better. metric in 'dot', 'cosine', 'l2'
    ('l2' is the NEGATIVE Euclidean distance). Cosine with a zero vector is 0. Unknown metric: ValueError."""
    raise NotImplementedError("R2: scores")


def top_k(Q, D, k: int, metric: str):
    """R3: (indices, scores), each (n_queries, min(k, n_docs)), best first; ties go to the LOWER doc index."""
    raise NotImplementedError("R3: top_k")


def recall_at_k(retrieved, relevant, k: int) -> float:
    """R4: mean over queries with at least one relevant doc of |top-k ∩ relevant| / |relevant|."""
    raise NotImplementedError("R4: recall_at_k")


def mrr(retrieved, relevant) -> float:
    """R4: mean reciprocal rank of the first relevant doc in the full retrieved list (0 if absent); skip queries with no relevant docs."""
    raise NotImplementedError("R4: mrr")


def ndcg_at_k(retrieved, relevant, k: int) -> float:
    """R4: binary-gain nDCG@k with discount 1/log2(rank+1) for 1-based rank; ideal list has min(k, |relevant|) hits."""
    raise NotImplementedError("R4: ndcg_at_k")


def evaluate(Q, D, relevant, metrics=("dot", "cosine", "l2"), k: int = 5) -> dict:
    """R5: {metric: {'recall', 'mrr', 'ndcg', 'n_queries'}} where n_queries counts queries with relevant docs."""
    raise NotImplementedError("R5: evaluate")
