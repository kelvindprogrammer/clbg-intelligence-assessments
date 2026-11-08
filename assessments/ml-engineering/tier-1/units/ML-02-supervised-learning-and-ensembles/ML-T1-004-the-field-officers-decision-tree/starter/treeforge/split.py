import numpy as np


def gini(y):
    raise NotImplementedError("R1: Gini impurity of an integer label array")


def best_split(X, y, min_samples_leaf=1):
    raise NotImplementedError("R2: return (feature, threshold, gain) or None; sort once per feature, use cumulative class counts")
