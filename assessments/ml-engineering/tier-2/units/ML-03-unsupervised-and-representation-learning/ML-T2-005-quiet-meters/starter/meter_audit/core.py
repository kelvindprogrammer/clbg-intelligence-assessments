"""Quiet Meters: rank feeder meters by how suspicious their consumption looks. Replace each R<n> stub."""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

METHODS = ("baseline", "iforest", "lof", "pca")


@dataclass
class MeterData:
    readings: np.ndarray   # (n, days, 4) kWh per quarter-day band: night, morning, afternoon, evening
    tariff: np.ndarray     # (n,) 0 residential, 1 small business, 2 industrial
    audit_idx: np.ndarray  # indices of meters physically inspected
    audit_y: np.ndarray    # 1 = tampering confirmed, 0 = clean (same length as audit_idx)


@dataclass
class Recommendation:
    method: str            # one of METHODS (not "baseline")
    top_idx: np.ndarray    # the budget_k meters to inspect, most suspicious first
    rationale: str         # at least 40 characters, quoting the evidence for the choice


def load_meters(path) -> MeterData:
    z = np.load(path)
    return MeterData(z["readings"].astype(float), z["tariff"], z["audit_idx"], z["audit_y"])


def build_features(readings: np.ndarray, tariff: np.ndarray) -> np.ndarray:
    """R1: (n, f) feature matrix with f >= 4, finite, deterministic, built WITHOUT labels, and invariant
    to multiplying every reading by the same constant (a unit change from kWh to Wh must not matter).
    Design them so that a big legitimate consumer is not 'anomalous' merely for being big."""
    raise NotImplementedError("R1: scale-free behavioural features")


def score_meters(readings: np.ndarray, tariff: np.ndarray, method: str, seed: int = 0) -> np.ndarray:
    """R2/R3: higher = more suspicious. Unknown method -> ValueError.
    'baseline' (R2, exact): per tariff class, |x - median| / (1.4826 * MAD) of each meter's mean daily kWh.
    'iforest', 'lof', 'pca' (R3): detectors run on build_features; the choice of preprocessing and
    hyper-parameters is yours and must be justified in the report."""
    raise NotImplementedError("R2/R3: baseline and feature-based detectors")


def precision_at_k(scores, y, k: int) -> float:
    """R4: fraction of the k highest-scoring items that are positive (stable ordering for ties)."""
    raise NotImplementedError("R4: precision@k")


def average_precision(scores, y) -> float:
    """R4: average precision from its definition (mean of precision at each positive's rank); 0.0 if no positives."""
    raise NotImplementedError("R4: average precision")


def evaluate_methods(data: MeterData, seed: int = 0, n_boot: int = 200) -> dict:
    """R5: for every method in METHODS return {"ap": average precision on the audit sample,
    "ci": (low, high) 95% percentile bootstrap interval over audit meters}. Seeded, deterministic.
    Resamples with no positive are skipped."""
    raise NotImplementedError("R5: audit evaluation with uncertainty")


def recommend(data: MeterData, budget_k: int, seed: int = 0) -> Recommendation:
    """R6: choose a non-baseline method using the audit evidence AND its uncertainty, then return the
    budget_k meters to inspect next, with a rationale string."""
    raise NotImplementedError("R6: recommendation")
