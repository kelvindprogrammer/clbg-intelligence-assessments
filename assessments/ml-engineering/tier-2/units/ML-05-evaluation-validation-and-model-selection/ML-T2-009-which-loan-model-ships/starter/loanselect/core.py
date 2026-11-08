"""Starter for ML-T2-009. Signatures are fixed; everything inside is yours.

You may add modules, helpers and dependencies from requirements.txt. The cost rates below are the lender's
policy numbers and must not be changed.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np  # noqa: F401
import pandas as pd

FN_RATE = 0.6   # an approved loan that defaults loses 60% of its amount
FP_RATE = 0.08  # a refused loan that would have been repaid loses 8% of its amount in forgone fees


def usable_features(df):
    """R1: list of column names that may be used as model inputs at decision time."""
    raise NotImplementedError("R1: usable_features")


def matured(df):
    """R2: rows whose outcome is known by the snapshot, with a fresh 0..n-1 index."""
    raise NotImplementedError("R2: matured")


def forward_splits(df, n_splits=4, val_days=45):
    """R3: list of (train_idx, val_idx) positional index arrays for a matured, reset-index frame.

    Validation windows are consecutive blocks of `val_days` ending at the latest disbursement date; the
    last window is the most recent. A training loan is allowed only if its due date
    (disbursed_on + term_days) is on or before the validation window's first day.
    """
    raise NotImplementedError("R3: forward_splits")


def expected_cost(y, p, amount, threshold, fn_rate=FN_RATE, fp_rate=FP_RATE):
    """R4: cost per naira lent. A loan is approved when p < threshold."""
    raise NotImplementedError("R4: expected_cost")


def best_threshold(y, p, amount, fn_rate=FN_RATE, fp_rate=FP_RATE):
    """R5: return (threshold, cost) minimising expected_cost over a sensible grid of candidates."""
    raise NotImplementedError("R5: best_threshold")


def bootstrap_ci(values, n_boot=1000, seed=0, alpha=0.05):
    """R6: percentile bootstrap interval (lo, hi) for the mean of `values`. Deterministic for a seed."""
    raise NotImplementedError("R6: bootstrap_ci")


@dataclass
class Recommendation:
    model: object            # must offer predict_proba(df) -> 1-D array of default probabilities for raw frames
    threshold: float         # approve when predicted probability < threshold
    features: list
    model_name: str
    cv_cost: float           # forward-chaining estimate of cost per naira lent at `threshold`
    cv_ci: tuple             # (lo, hi) interval for cv_cost
    table: pd.DataFrame = field(default_factory=pd.DataFrame)  # your candidate comparison


def select_and_fit(train_df, seed=0):
    """R7: compare at least two candidate models by forward-chaining cost, choose a threshold without touching
    any data from the future, fit the winner on all matured loans, and return a Recommendation."""
    raise NotImplementedError("R7: select_and_fit")
