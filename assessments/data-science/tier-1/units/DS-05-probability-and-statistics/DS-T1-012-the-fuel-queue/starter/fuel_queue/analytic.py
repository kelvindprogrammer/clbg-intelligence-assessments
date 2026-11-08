"""Analytical M/M/c results (requirements R1-R2).

Derive these results yourself (see README section D.1) before coding them.
"""
from __future__ import annotations

from dataclasses import dataclass


def erlang_b(c: int, a: float) -> float:
    """Erlang-B blocking probability for c servers and offered load a = lam/mu.

    Must be numerically stable for c up to at least 500 (no factorials of large numbers).
    """
    raise NotImplementedError("R1: implement erlang_b")


def erlang_c(c: int, a: float) -> float:
    """Probability that an arriving customer must wait in an M/M/c queue, offered load a = lam/mu.

    Raises ValueError if c is not a positive integer, if a <= 0, or if the queue is unstable (a >= c).
    """
    raise NotImplementedError("R1: implement erlang_c")


@dataclass(frozen=True)
class QueueMetrics:
    lam: float      # arrival rate (customers per minute)
    mu: float       # service rate per pump (customers per minute)
    c: int          # number of pumps
    rho: float      # utilisation per pump, lam / (c * mu)
    p_wait: float   # P(Wq > 0), the Erlang-C probability
    lq: float       # mean number waiting in the queue
    wq: float       # mean wait in the queue (minutes)
    w: float        # mean time in the system (minutes)
    l: float        # mean number in the system

    def p_wait_exceeds(self, t: float) -> float:
        """P(Wq > t) for t >= 0 under M/M/c. Raises ValueError for t < 0."""
        raise NotImplementedError("R2: implement QueueMetrics.p_wait_exceeds")


def mmc_metrics(lam: float, mu: float, c: int) -> QueueMetrics:
    """Steady-state M/M/c metrics. Raises ValueError for non-positive rates or an unstable queue."""
    raise NotImplementedError("R2: implement mmc_metrics")
