"""Validation against theory and the staffing decision (requirements R7-R8)."""
from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd

from .stats import Interval


@dataclass(frozen=True)
class Validation:
    analytic_wq: float
    sim_wq: Interval
    analytic_p_exceed: float
    sim_p_exceed: Interval
    agrees: bool          # True if BOTH analytic values lie inside their simulation intervals


@dataclass
class Recommendation:
    c_recommended: int | None   # from the simulation with empirical service times
    c_mmc: int | None           # what the M/M/c formula alone would recommend
    lam: float
    mean_service: float
    cv_service: float
    table: pd.DataFrame = field(repr=False)


def validate_against_mmc(lam, mu, c, t=10.0, n=200_000, warmup=10_000, seed=2026, n_batches=20) -> Validation:
    """Simulate an M/M/c queue (discarding `warmup` initial customers) and compare the mean wait
    and P(Wq > t) with the analytical values, using batch-means intervals."""
    raise NotImplementedError("R7: implement validate_against_mmc")


def recommend_pumps(log: pd.DataFrame, window_min: float = 240.0, target_wait: float = 10.0,
                    max_prob: float = 0.10, n_customers: int = 100_000, warmup: int = 5_000,
                    seed: int = 2026, c_max: int = 12, n_batches: int = 20) -> Recommendation:
    """Recommend the smallest number of pumps c such that the UPPER 95% batch-means bound of
    P(Wq > target_wait) is <= max_prob, simulating with the estimated demand rate and the
    empirical service times. Also report the M/M/c answer.

    `table` has one row per c considered, with at least the columns: c, rho, stable,
    p_exceed_sim, p_exceed_lower, p_exceed_upper, p_exceed_mmc. An unstable c (rho >= 1) must
    never be recommended, and must not be simulated as if it had a steady state.
    """
    raise NotImplementedError("R8: implement recommend_pumps")
