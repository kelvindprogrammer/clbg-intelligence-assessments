"""Leakage audit for a microfinance default model that scored AUC ~1.0 in the notebook. Replace each R<n> stub.
Allowed: numpy and scikit-learn."""
from __future__ import annotations

import numpy as np

TARGET = "default"
IDS = {"loan_id", "customer_id", "disbursed_month", TARGET}
INT_COLS = {"disbursed_month", "tenor_months", "prior_loans", "phone_changes_12m", "collections_calls",
            "restructured_flag", TARGET}


def load_loans(path) -> dict:
    """Provided: dict of column arrays (ints and floats converted, ids as str)."""
    with open(path, encoding="utf-8") as f:
        header = f.readline().strip().split(",")
    out = {}
    for j, name in enumerate(header):
        dt = str if name in ("loan_id", "customer_id") else float
        col = np.genfromtxt(path, delimiter=",", skip_header=1, usecols=(j,), dtype=dt)
        out[name] = col.astype(int) if name in INT_COLS else col
    return out


def load_dictionary(path) -> dict:
    """Provided: {feature: when it is recorded}. Values: application, post_disbursement, post_outcome."""
    rows = np.genfromtxt(path, delimiter=",", skip_header=1, dtype=str)
    return {a: b for a, b in rows}


def candidate_features(data) -> list:
    """Provided: columns that are neither identifiers, the month, nor the target."""
    return [c for c in data if c not in IDS]


def audit_features(data: dict, dictionary: dict, auc_threshold: float = 0.85) -> dict:
    """R1: for every candidate feature return {"verdict": "leak" | "ok", "auc": float, "reasons": [str, ...]}.
    A feature is a leak if the dictionary says it is not recorded at 'application' OR its single-feature AUC
    (max(auc, 1 - auc)) exceeds auc_threshold. A feature missing from the dictionary is taken as 'application'.
    Reasons must be non-empty for leaks and empty for ok features. Justify the 0.85 default in the report."""
    raise NotImplementedError("R1: leakage audit combining documentation and evidence")


def honest_split(data: dict, cutoff: int):
    """R2: (train_idx, test_idx) as int arrays. test = loans with disbursed_month >= cutoff. train = loans with
    disbursed_month < cutoff whose customer_id does NOT appear in the test set (repeat borrowers would otherwise
    appear on both sides)."""
    raise NotImplementedError("R2: temporal and customer-disjoint split")


def leaky_vs_honest(data: dict, dictionary: dict, cutoff: int = 18, seed: int = 0) -> dict:
    """R3: return {"auc_naive", "auc_honest", "dropped"}. auc_naive: random 70/30 row split with
    np.random.default_rng(seed).permutation, ALL candidate features. auc_honest: honest_split(cutoff) with the
    leak features removed. Model for both: StandardScaler + LogisticRegression(max_iter=2000) in one Pipeline
    fitted on the training rows only. 'dropped' is the sorted list of removed features."""
    raise NotImplementedError("R3: naive versus honest evaluation")


def psi(train_col, test_col, bins: int = 10) -> float:
    """R4: population stability index. Bin edges are the unique quantiles of train_col (bins+1 points, outer
    edges -inf/+inf); p, q = bin proportions of train and test, each floored at 1e-4;
    PSI = sum((q - p) * ln(q / p))."""
    raise NotImplementedError("R4: PSI")


def drift_check(data: dict, features: list, cutoff: int) -> dict:
    """R4: {feature: PSI between loans with disbursed_month < cutoff and those >= cutoff}."""
    raise NotImplementedError("R4: drift report")
