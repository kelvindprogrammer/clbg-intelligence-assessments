"""Starter for ML-T2-012. `nn_core.MLP` is provided and works; the training PROCESS is what you design.

Signatures are fixed. You may add modules and helpers.
"""
from __future__ import annotations

import numpy as np  # noqa: F401
import pandas as pd  # noqa: F401

from .nn_core import MLP  # noqa: F401

NOT_FEATURES = {"meter_id", "tampered"}


def fit_preprocessor(train_df):
    """R1: learn, from train_df ONLY, how to turn the 11 feature columns into a network-ready matrix.
    Return an object with transform(df) -> ndarray (n, 11). It must tame heavy-tailed, wildly scaled columns
    using rules derived from the training data, not hard-coded column names, and must never use test data."""
    raise NotImplementedError("R1: fit_preprocessor")


def diagnose(history):
    """R2: history is {'train_loss': [...], 'val_loss': [...]} (equal-length lists of epoch losses).
    Return one of 'unstable', 'underfit', 'overfit', 'ok' using rules you define and document in REPORT.md."""
    raise NotImplementedError("R2: diagnose")


class FittedModel:
    """R3: container returned by fit_model. Required attributes:
      predict_proba(df) -> 1-D array of tamper probabilities for a raw frame (no label column needed)
      history: {'train_loss': [...], 'val_loss': [...]} with UNWEIGHTED mean log loss per epoch
      best_epoch: index into history of the epoch whose weights the model actually uses
      val_idx: positional row indices of train_df used as validation (stratified, never trained on)
      config: dict of the hyperparameters you chose
    """


def fit_model(train_df, seed=0):
    """R3: carve a stratified validation split from train_df, fit the preprocessor on the remaining rows only,
    train an MLP with early stopping on validation log loss, restore the best epoch's weights, and handle the
    class imbalance. Deterministic for a seed."""
    raise NotImplementedError("R3: fit_model")
