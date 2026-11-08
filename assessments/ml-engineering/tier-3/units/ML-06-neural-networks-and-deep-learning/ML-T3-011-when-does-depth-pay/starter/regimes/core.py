"""Starter for ML-T3-011. `tasks.make_task` and `nn_core.MLP` are provided. Signatures are fixed."""
from __future__ import annotations

import numpy as np  # noqa: F401
import pandas as pd  # noqa: F401

from .nn_core import MLP  # noqa: F401
from .tasks import KINDS, make_task  # noqa: F401

MODELS = ("mlp", "gbm", "logreg")


def fit_predict(model_name, Xtr, ytr, Xte, seed=0):
    """R1: fit `model_name` ('mlp' | 'gbm' | 'logreg') on (Xtr, ytr) and return P(y=1) for Xte (1-D array).
    The API gives you no test labels: any tuning (early stopping, widths) must use only a validation split
    carved from the training data. 'gbm' is scikit-learn's HistGradientBoostingClassifier, 'logreg' a
    standardised LogisticRegression, 'mlp' your own tuned use of nn_core.MLP. Deterministic for a seed.
    Spend your tuning effort fairly across the three models and say what you did in REPORT.md."""
    raise NotImplementedError("R1: fit_predict")


def run_study(kinds, sizes, seeds, n_noise=6, models=MODELS, n_test=4000):
    """R2: for every kind, training size n, seed and model, draw make_task(kind, n + n_test, seed, n_noise),
    train on the first n rows, and record test AUC on the remaining n_test rows.
    Return a DataFrame with columns ['model', 'kind', 'n', 'seed', 'auc'], one row per combination."""
    raise NotImplementedError("R2: run_study")


def paired_summary(df, a, b, n_boot=1000, seed=0):
    """R3: for each (kind, n), pair models a and b by seed and return a DataFrame with columns
    ['kind', 'n', 'mean_diff', 'lo', 'hi', 'n_seeds'] where mean_diff = mean(auc_a - auc_b) and (lo, hi) is a 95%
    percentile bootstrap interval of that mean over seeds. Deterministic for a seed."""
    raise NotImplementedError("R3: paired_summary")


def crossover(summary, kind):
    """R4: smallest training size n such that mean_diff > 0 for that n and every larger n in `summary` for this
    kind (model a beats model b from there on); None if there is no such n."""
    raise NotImplementedError("R4: crossover")
