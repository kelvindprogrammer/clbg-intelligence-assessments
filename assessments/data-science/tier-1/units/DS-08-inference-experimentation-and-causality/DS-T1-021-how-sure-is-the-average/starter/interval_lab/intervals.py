"""Interval estimators. Implement R1, R2, R5 and R6 exactly as specified in the README."""
import numpy as np


def t_interval(x, level=0.95):
    """R1: Student-t confidence interval for the mean. Returns (lo, hi) as floats."""
    raise NotImplementedError("R1: t_interval")


def bootstrap_ci(x, stat=np.mean, level=0.95, n_boot=2000, seed=0):
    """R2: percentile bootstrap interval for stat(x). Returns (lo, hi) as floats."""
    raise NotImplementedError("R2: bootstrap_ci")


def diff_means_ci_bootstrap(a, b, level=0.95, n_boot=2000, seed=0):
    """R5: percentile bootstrap interval for mean(a) - mean(b), resampling a and b separately."""
    raise NotImplementedError("R5: diff_means_ci_bootstrap")


def required_n(sd, margin, level=0.95):
    """R6: smallest n whose normal-theory interval half-width is <= margin."""
    raise NotImplementedError("R6: required_n")
