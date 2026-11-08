"""Does a population have segments, and how many? Replace each R<n> stub with your own method.

Allowed: numpy and scikit-learn. There is no single correct design here; the hidden evaluation measures
whether your decisions are sound on populations you have not seen, including ones with NO segments."""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np


@dataclass
class Members:
    X: np.ndarray        # (n, 8) raw features in natural units (naira, months, rates, counts)
    names: list
    trade: np.ndarray    # categorical column; assume it carries no structure unless you show otherwise


@dataclass
class StructureReport:
    k: int                                          # number of segments; 1 means "no segments supported"
    gaps: dict = field(default_factory=dict)        # k -> (gap statistic, standard error), if you use one
    stability: dict = field(default_factory=dict)   # k -> mean pairwise ARI, if you use one
    rationale: str = ""                             # one or two sentences quoting your evidence


def load_members(path) -> Members:
    with open(path, encoding="utf-8") as f:
        header = f.readline().strip().split(",")
    names = header[1:-1]
    X = np.genfromtxt(path, delimiter=",", skip_header=1, usecols=range(1, len(header) - 1))
    trade = np.genfromtxt(path, delimiter=",", skip_header=1, usecols=(len(header) - 1,), dtype=str)
    return Members(np.asarray(X, float), names, trade)


def prepare(X: np.ndarray) -> np.ndarray:
    """R1: return a finite (n, p) matrix ready for distance-based clustering. It must not be dominated by
    any one column's units or tail, must give the same result if a column is rescaled (naira to kobo),
    and must be deterministic. You decide what to transform and why; report the ablation."""
    raise NotImplementedError("R1: preprocessing for heterogeneous, heavy-tailed columns")


def null_samples(Xp: np.ndarray, n_null: int, seed: int, kind: str = "gaussian_cov") -> list:
    """R2: n_null reference datasets of the same shape as Xp that contain NO cluster structure.
    kind='gaussian_cov': multivariate normal with the sample mean and covariance of Xp.
    kind='uniform_pca': uniform over the bounding box of Xp in its principal-component axes.
    Unknown kind -> ValueError. Seeded and deterministic."""
    raise NotImplementedError("R2: null reference distributions")


def gap_statistic(Xp: np.ndarray, k_max: int, n_null: int = 10, seed: int = 0,
                  null_kind: str = "gaussian_cov") -> dict:
    """R3: {k: (gap, se)} for k = 1..k_max, where gap(k) = mean over nulls of log W_k(null) - log W_k(data),
    W_k is the k-means inertia, and se = std of the null log W_k * sqrt(1 + 1/n_null)."""
    raise NotImplementedError("R3: gap statistic")


def stability(Xp: np.ndarray, k: int, n_boot: int = 10, seed: int = 0) -> float:
    """R4: mean pairwise adjusted Rand index between clusterings of the FULL data obtained from k-means fitted
    on n_boot random 80% subsamples (assign every point to the nearest fitted centre). Return 1.0 for k < 2.
    Seeded and deterministic."""
    raise NotImplementedError("R4: subsample stability")


def estimate_k(X: np.ndarray, k_max: int = 6, seed: int = 0) -> StructureReport:
    """R5: your decision procedure from RAW features to a number of segments (1 = none). Combine the
    ingredients above or your own; justify the thresholds in the report. Must finish within 30 seconds
    for n = 700, be deterministic given seed, and not depend on the order of the rows."""
    raise NotImplementedError("R5: structure estimate")
