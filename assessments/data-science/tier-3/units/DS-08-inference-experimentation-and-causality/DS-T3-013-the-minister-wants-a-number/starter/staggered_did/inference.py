"""Inference (R4-R5)."""


def cluster_bootstrap(df, estimator, n_boot=200, seed=0):
    """R4: unit-level (cluster) bootstrap. `estimator` may return a float or a 1-D array. Returns {"estimate", "se"}."""
    raise NotImplementedError("R4: cluster_bootstrap")


def pretrend_test(df, n_boot=200, seed=0):
    """R5: per-cohort placebo test with a Bonferroni-adjusted minimum p-value. Returns {"estimate", "se", "p_value"}."""
    raise NotImplementedError("R5: pretrend_test")
