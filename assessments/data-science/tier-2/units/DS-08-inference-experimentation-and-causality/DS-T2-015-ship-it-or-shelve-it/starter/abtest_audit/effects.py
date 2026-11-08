"""Effect estimators. R3, R4 and R5."""


def conversion_effect(df, level=0.95):
    """R3: two-proportion comparison on a one-row-per-user frame.

    Returns {"rate_a", "rate_b", "lift", "ci_low", "ci_high", "p_value"} where lift = rate_b - rate_a.
    """
    raise NotImplementedError("R3: conversion_effect")


def revenue_effect(df, level=0.95, n_boot=2000, seed=0):
    """R4: robust effect of arm B on revenue per assigned user (zeros included).

    Returns {"estimate", "ci_low", "ci_high", "p_value", "naive_p_value"}. You choose the method (see README R4).
    """
    raise NotImplementedError("R4: revenue_effect")


def holm_adjust(pvals):
    """R5: Holm-Bonferroni adjusted p-values, returned in the input order."""
    raise NotImplementedError("R5: holm_adjust")
