import numpy as np

from .core import Policy


def calibrate_cost(sizes, times_ms):
    raise NotImplementedError("R1: robust fit of time = a + b * size; spikes must not move the answer; a, b >= 0")


def simulate(arrivals, policy, cost):
    raise NotImplementedError("R2: exact single-worker FIFO micro-batching simulation; cost = (a_ms, b_ms)")


def summarize(result, slo_ms):
    raise NotImplementedError("R3: p50, p99, shed_rate, mean_batch, utilisation, slo_ok")


def tune_policy(arrivals, cost, slo_ms=100.0, max_shed=0.005):
    raise NotImplementedError("R4: choose a Policy that meets the SLO now and under 25% more traffic")
