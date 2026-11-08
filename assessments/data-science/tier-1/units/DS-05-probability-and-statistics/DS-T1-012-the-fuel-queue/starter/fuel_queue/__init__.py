"""fuel_queue: queueing analysis for the DS-T1-012 filling-station problem.

The public API is fixed because the tests import it. Implement each function in its module.
"""
from .analytic import QueueMetrics, erlang_b, erlang_c, mmc_metrics
from .simulate import poisson_arrivals, simulate_empirical, simulate_fcfs, simulate_mmc
from .stats import InputEstimate, Interval, batch_means_ci, estimate_inputs, load_log
from .decision import Recommendation, Validation, recommend_pumps, validate_against_mmc

__all__ = [
    "QueueMetrics", "erlang_b", "erlang_c", "mmc_metrics",
    "poisson_arrivals", "simulate_empirical", "simulate_fcfs", "simulate_mmc",
    "InputEstimate", "Interval", "batch_means_ci", "estimate_inputs", "load_log",
    "Recommendation", "Validation", "recommend_pumps", "validate_against_mmc",
]
