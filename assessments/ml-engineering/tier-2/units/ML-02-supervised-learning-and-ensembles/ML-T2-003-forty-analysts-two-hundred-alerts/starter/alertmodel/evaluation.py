import numpy as np


def find_leaky_columns(X, y, names, auc_threshold=0.9):
    raise NotImplementedError("R1: single-feature AUC screen (document its limits in the report)")


def time_split(day, train_end, val_end):
    raise NotImplementedError("R2: (train_idx, val_idx, test_idx) with no look-ahead")


def budget_recall(day, y, score, budget_frac):
    raise NotImplementedError("R3: share of all positives inside each day's top ceil(frac * n_day) scores")


def budget_precision(day, y, score, budget_frac):
    raise NotImplementedError("R3: share of flagged transactions that are positive")
