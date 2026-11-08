"""Data-generating processes (PROVIDED; do not edit). Cooperative-level clustering of insurance claim sizes."""
from __future__ import annotations

import numpy as np


def simulate(k, m, sigma_u, sigma_e, rng):
    """Clustered log-normal claims. Returns (y, cluster) arrays.

    k clusters (farmer cooperatives); m is an int (balanced) or a sequence of k cluster sizes.
    log y_ij = u_i + e_ij with u_i ~ N(0, sigma_u^2) and e_ij ~ N(0, sigma_e^2).
    """
    sizes = [int(m)] * k if np.isscalar(m) else [int(s) for s in m]
    assert len(sizes) == k
    u = rng.normal(0.0, sigma_u, size=k)
    cluster = np.repeat(np.arange(k), sizes)
    y = np.exp(u[cluster] + rng.normal(0.0, sigma_e, size=cluster.size))
    return y, cluster


def true_mean(sigma_u, sigma_e):
    """Population mean of y: exp((sigma_u^2 + sigma_e^2) / 2)."""
    return float(np.exp((sigma_u ** 2 + sigma_e ** 2) / 2.0))


def simulate_normal(k, m, icc, rng, total_sd=1.0):
    """Gaussian clustered data with a known intraclass correlation (for testing estimators). Returns (y, cluster)."""
    sizes = [int(m)] * k if np.isscalar(m) else [int(s) for s in m]
    su, se = total_sd * np.sqrt(icc), total_sd * np.sqrt(1.0 - icc)
    u = rng.normal(0.0, su, size=k)
    cluster = np.repeat(np.arange(k), sizes)
    return u[cluster] + rng.normal(0.0, se, size=cluster.size), cluster
