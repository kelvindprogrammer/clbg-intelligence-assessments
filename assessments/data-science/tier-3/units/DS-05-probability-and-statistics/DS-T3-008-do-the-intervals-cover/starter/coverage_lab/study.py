"""Monte Carlo coverage study. Signatures are fixed; internals are yours."""
from __future__ import annotations

METHODS = ("iid_bootstrap", "cluster_bootstrap", "design_effect", "cluster_bootstrap_t")


def coverage_study(method, k, m, sigma_u, sigma_e, reps, B, seed, alpha=0.05) -> dict:
    """Simulate `reps` datasets with dgp.simulate, build the interval with `method`, and return
    {'coverage', 'mcse', 'mean_width', 'reps'}. Must be deterministic given `seed`; raise ValueError for unknown methods (R6)."""
    raise NotImplementedError("R6: coverage, its Monte Carlo standard error and mean interval width")


def reps_needed(target_mcse, p=0.95) -> int:
    """Smallest number of replications whose Monte Carlo standard error of an estimated coverage p is <= target_mcse (R7)."""
    raise NotImplementedError("R7: invert the binomial standard error formula")
