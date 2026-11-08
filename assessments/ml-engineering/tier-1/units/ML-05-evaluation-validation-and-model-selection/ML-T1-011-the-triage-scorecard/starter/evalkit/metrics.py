"""Metrics implemented from scratch with numpy only (no sklearn in this package)."""
import numpy as np  # noqa: F401


def confusion_counts(y_true, y_pred):
    """R1: return (tp, fp, fn, tn) as ints for 0/1 arrays."""
    raise NotImplementedError("R1: confusion_counts")


def precision_recall_f1(y_true, y_pred):
    """R2: dict with keys precision, recall, f1, specificity, accuracy. Zero denominators give 0.0."""
    raise NotImplementedError("R2: precision_recall_f1")


def roc_auc(y_true, scores):
    """R3: rank-based ROC AUC with average ranks for tied scores. ValueError if one class is absent."""
    raise NotImplementedError("R3: roc_auc")


def average_precision(y_true, scores):
    """R4: step-wise average precision; tied scores form a single threshold."""
    raise NotImplementedError("R4: average_precision")


def threshold_for_recall(y_true, scores, target_recall):
    """R6: largest observed score t such that recall of (scores >= t) is >= target_recall."""
    raise NotImplementedError("R6: threshold_for_recall")


def expected_calibration_error(y_true, prob, n_bins=10):
    """R7: equal-width bins on [0, 1] (prob == 1.0 falls in the last bin); weighted mean |observed - predicted|."""
    raise NotImplementedError("R7: expected_calibration_error")
