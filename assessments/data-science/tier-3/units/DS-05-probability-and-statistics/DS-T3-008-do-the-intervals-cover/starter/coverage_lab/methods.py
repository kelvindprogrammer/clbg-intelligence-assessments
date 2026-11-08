"""Interval methods for the population mean of clustered data. Signatures are fixed; internals are yours.

`rng` is a numpy.random.Generator. Every interval is returned as a (lower, upper) tuple at level 1 - alpha.
"""
from __future__ import annotations


def estimate_icc(y, cluster) -> float:
    """Intraclass correlation estimate that is valid for unbalanced clusters (R1)."""
    raise NotImplementedError("R1: ANOVA-type estimator of the intraclass correlation")


def iid_bootstrap_ci(y, B, alpha, rng):
    """Percentile bootstrap interval for the mean, resampling observations as if independent (R2)."""
    raise NotImplementedError("R2: iid percentile bootstrap")


def cluster_bootstrap_ci(y, cluster, B, alpha, rng):
    """Percentile bootstrap interval resampling whole clusters with replacement (R3)."""
    raise NotImplementedError("R3: cluster percentile bootstrap")


def design_effect_ci(y, cluster, alpha):
    """Normal-theory interval whose variance is inflated by the design effect 1 + (mean cluster size - 1) * icc (R4)."""
    raise NotImplementedError("R4: design-effect adjusted normal interval")


def cluster_bootstrap_t_ci(y, cluster, B, alpha, rng):
    """Studentised (bootstrap-t) cluster bootstrap interval (R5). Choose and justify the standard error you studentise by."""
    raise NotImplementedError("R5: studentised cluster bootstrap")
