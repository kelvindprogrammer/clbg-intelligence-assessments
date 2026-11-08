import numpy as np


def run_study(kappas, methods, seeds, kind="scale", n=1500, d=8, max_iter=None, l2=0.0):
    raise NotImplementedError("R8: one record per (method, kappa, seed)")


def loglog_slope(x, y, n_boot=500, seed=0):
    raise NotImplementedError("R9: (slope, lo, hi) with a percentile bootstrap")
