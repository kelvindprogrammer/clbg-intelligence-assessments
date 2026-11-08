"""The model contract (README section B). Loading is provided; the density is yours."""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class SurveyData:
    village: np.ndarray   # integer index 0..J-1 per farm (villages sorted by name)
    n: np.ndarray         # plants inspected
    y: np.ndarray         # plants infested
    x: np.ndarray         # push-pull indicator (0/1)
    J: int


def load_survey(path_or_df) -> SurveyData:
    """Provided."""
    df = pd.read_csv(path_or_df) if not isinstance(path_or_df, pd.DataFrame) else path_or_df
    codes, uniq = pd.factorize(df["village"], sort=True)
    return SurveyData(codes.astype(int), df["plants_inspected"].to_numpy(float), df["plants_infested"].to_numpy(float),
                      df["push_pull"].to_numpy(float), len(uniq))


def logp_and_grad(theta, data: SurveyData, centred: bool = False):
    """Log posterior density (up to an additive constant) and its gradient on the unconstrained
    vector theta = [mu, beta, log_tau, a_1..a_J] (README section D.1, R4), for the centred
    (a_v = alpha_v) or non-centred (alpha_v = mu + tau * a_v) parameterisation, INCLUDING the
    log-Jacobian of tau = exp(log_tau). Returns (float, np.ndarray of the same length as theta)."""
    raise NotImplementedError("R4: implement logp_and_grad")
