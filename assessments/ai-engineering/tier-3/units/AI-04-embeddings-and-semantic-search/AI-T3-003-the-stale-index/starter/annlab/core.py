"""An inverted-file (IVF) approximate nearest-neighbour index from scratch. Numpy only; no faiss, no scikit-learn."""
from __future__ import annotations

import numpy as np


def kmeans(X, k: int, seed: int = 0, iters: int = 20):
    """R1: deterministic Lloyd's k-means; returns centroids (k, d). Same seed, same result. An emptied cluster must be
    re-seeded (no NaN); k larger than the number of distinct points must not crash. Initialisation is your choice."""
    raise NotImplementedError("R1: kmeans")


def exact_search(X, q, k: int):
    """R2: ids of the k vectors with the highest dot product with q, best first; ties to the lower id."""
    raise NotImplementedError("R2: exact_search")


def recall_at_k(found, truth) -> float:
    """R2: mean over queries of |found ∩ truth| / |truth|."""
    raise NotImplementedError("R2: recall_at_k")


class IVFIndex:
    """R3: coarse quantiser + inverted lists. Vectors are unit length, score = dot product."""

    def __init__(self, n_lists: int, seed: int = 0):
        self.n_lists, self.seed = n_lists, seed

    def build(self, X) -> "IVFIndex":
        """Train centroids on X, assign every vector to its nearest centroid (Euclidean), record the mean
        distance of build vectors to their centroid as `self.build_qerr`. Return self."""
        raise NotImplementedError("R3: build")

    def add(self, X_new) -> list[int]:
        """Append vectors WITHOUT retraining: assign each to its nearest existing centroid. Ids continue from the
        current size; return the new ids."""
        raise NotImplementedError("R3: add")

    def list_sizes(self) -> list[int]:
        raise NotImplementedError("R3: list_sizes")

    def search(self, q, k: int, nprobe: int):
        """Probe the `nprobe` lists whose centroids are nearest to q (ties to the lower list id), rank the vectors in
        them by dot product (ties to the lower id) and return (ids[:k], ndist). `ndist` counts vector-distance
        computations: n_lists centroid comparisons plus every vector scanned in the probed lists."""
        raise NotImplementedError("R3: search")


def evaluate_index(index, Q, k: int, nprobe: int, truth=None):
    """R4: (mean recall@k against exact search over index.X, mean ndist per query)."""
    raise NotImplementedError("R4: evaluate_index")


def segment_recall(index, Q, segments, k: int, nprobe: int) -> dict:
    """R4: recall@k per segment label (e.g. 'head', 'tail')."""
    raise NotImplementedError("R4: segment_recall")


def choose_config(X, Q, k: int, budget_ndist: float, n_lists_grid=(16, 32, 64, 128), nprobe_grid=(1, 2, 4, 8, 16, 32), seed: int = 0):
    """R5: return (n_lists, nprobe) with the highest mean recall@k whose mean ndist per query is <= budget_ndist
    (nprobe may not exceed n_lists). Returns None if nothing fits."""
    raise NotImplementedError("R5: choose_config")


def drift_report(index, X_new) -> dict:
    """R6: monitoring signals for a batch of new vectors against a built index; must include 'qerr_ratio' (mean
    distance of the new vectors to their nearest centroid divided by index.build_qerr) and 'imbalance'
    (largest list size / mean list size). Add more signals if you like."""
    raise NotImplementedError("R6: drift_report")


def should_rebuild(report: dict) -> bool:
    """R6: your rebuild policy. The assessors define 'rebuild needed' as: recall@10 at nprobe=4 of the stale index (new
    vectors added without retraining) is at least 0.05 below that of an index rebuilt on all vectors. Justify your
    thresholds in the report with a calibration experiment on worlds you generate, not on the hidden ones."""
    raise NotImplementedError("R6: should_rebuild")
