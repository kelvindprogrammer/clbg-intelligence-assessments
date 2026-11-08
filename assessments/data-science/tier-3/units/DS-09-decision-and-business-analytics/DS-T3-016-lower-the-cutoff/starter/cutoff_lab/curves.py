import numpy as np
import pandas as pd

TERMS = {"gain": 25.0, "loss": 70.0}


def load_applications(path):
    """Provided. `defaulted` is NaN for applicants who were not funded."""
    return pd.read_csv(path)


class DefaultCurve:
    """Provided. Probability of default as a logistic polynomial in z = (score - 600) / 100."""

    def __init__(self, coef):
        self.coef = np.asarray(coef, float)

    def predict(self, score):
        z = (np.asarray(score, float) - 600.0) / 100.0
        x = np.vander(z, len(self.coef), increasing=True)
        return 1.0 / (1.0 + np.exp(-(x @ self.coef)))


def default_rate_by_band(df, edges=None):
    """R1: DataFrame with columns band, n_apps, n_funded, naive_rate, ipw_rate (see README)."""
    raise NotImplementedError("R1: default_rate_by_band")


def fit_default_curve(df, method, degree=2):
    """R2: weighted logistic regression of default on a polynomial in z. method: 'approved_only' or 'ipw'."""
    raise NotImplementedError("R2: fit_default_curve")
