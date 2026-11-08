"""Output analysis and input modelling (requirements R5-R6)."""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

LOG_COLUMNS = ["customer_id", "day", "arrival_min", "vehicle_type", "status", "service_min"]


@dataclass(frozen=True)
class Interval:
    estimate: float
    lower: float
    upper: float


@dataclass(frozen=True)
class InputEstimate:
    lam: float            # DEMAND arrival rate, customers per minute
    mean_service: float   # minutes
    cv_service: float     # coefficient of variation of service time (sample sd with ddof=1, over the mean)
    n_arrivals: int
    n_served: int
    service_sample: np.ndarray


def load_log(path) -> pd.DataFrame:
    """Read the station log (provided)."""
    df = pd.read_csv(path, dtype={"customer_id": str, "vehicle_type": str, "status": str})
    return df[LOG_COLUMNS]


def batch_means_ci(x, n_batches: int = 20, level: float = 0.95) -> Interval:
    """Confidence interval for the steady-state mean of a CORRELATED output series using
    non-overlapping batch means and a Student-t quantile with n_batches - 1 degrees of freedom.

    Use the first n_batches * (len(x) // n_batches) observations. Raises ValueError if
    n_batches < 2 or the series is shorter than n_batches.
    """
    raise NotImplementedError("R5: implement batch_means_ci")


def estimate_inputs(log: pd.DataFrame, window_min: float = 240.0) -> InputEstimate:
    """Estimate the demand rate and the service-time distribution from a station log.

    `window_min` is the length of ONE day's observation window; the log may cover several days.
    Think carefully about which rows represent demand.
    """
    raise NotImplementedError("R6: implement estimate_inputs")
