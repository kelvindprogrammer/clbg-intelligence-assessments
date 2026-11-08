import numpy as np


def confusion_matrix(y_true, y_pred, k=3):
    raise NotImplementedError("R3: k x k integer matrix, rows are true classes")


def macro_f1(y_true, y_pred, k=3):
    raise NotImplementedError("R3: unweighted mean of per-class F1 (a class with no support and no predictions scores 0)")


def per_class_recall(y_true, y_pred, k=3):
    raise NotImplementedError("R3: length-k array of recalls")
