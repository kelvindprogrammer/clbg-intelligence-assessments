import numpy as np


def detect_break(y, min_seg=20):
    raise NotImplementedError("R1: locate one structural break in the log price; return its first index")


def interval_score(y, lo, hi, alpha=0.1):
    raise NotImplementedError("R2: mean Winkler/interval score")


def coverage(y, lo, hi):
    raise NotImplementedError("R2: share of observations inside [lo, hi]")


class BreakAwareForecaster:
    def __init__(self, alpha=0.1, horizon=13):
        self.alpha, self.horizon = alpha, horizon

    def fit(self, y):
        raise NotImplementedError("R3: use only y; decide how much history to trust after a shock")

    def predict(self):
        raise NotImplementedError("R3: return (point, lo, hi), each an array of length horizon")
