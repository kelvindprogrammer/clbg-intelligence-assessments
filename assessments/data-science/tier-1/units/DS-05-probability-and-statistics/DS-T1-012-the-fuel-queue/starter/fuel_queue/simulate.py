"""Discrete-event simulation of a first-come-first-served multi-pump queue (requirements R3-R4)."""
from __future__ import annotations

import numpy as np


def simulate_fcfs(arrival_times, service_times, c: int) -> np.ndarray:
    """Return each customer's waiting time in the queue (time from arrival to start of service).

    Customers are served first-come-first-served by c identical pumps; the system starts empty
    at time 0. Output is in arrival order and has the same length as the inputs.
    Raises ValueError for mismatched or non-1-D inputs, c < 1, decreasing arrival times or
    negative service times.
    """
    raise NotImplementedError("R3: implement simulate_fcfs")


def poisson_arrivals(lam: float, n: int, rng: np.random.Generator) -> np.ndarray:
    """Arrival times of the first n customers of a Poisson process with rate lam (provided)."""
    return np.cumsum(rng.exponential(1.0 / lam, size=n))


def simulate_mmc(lam: float, mu: float, c: int, n: int, rng: np.random.Generator) -> np.ndarray:
    """Waits of n customers in an M/M/c queue that starts empty. Use only `rng` for randomness."""
    raise NotImplementedError("R4: implement simulate_mmc")


def simulate_empirical(lam: float, service_sample, c: int, n: int, rng: np.random.Generator) -> np.ndarray:
    """Waits of n customers with Poisson(lam) arrivals and service times drawn with replacement
    from the observed `service_sample`. Raises ValueError if the sample is empty."""
    raise NotImplementedError("R4: implement simulate_empirical")
