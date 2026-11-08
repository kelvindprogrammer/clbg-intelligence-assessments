"""Provided scaffolding. Do not change names or semantics."""
from dataclasses import dataclass, field

import numpy as np
from sklearn.linear_model import LogisticRegression


class LabelNotYetAvailable(Exception):
    """Raised when a policy asks for a label that would not yet be known at week t."""


def fit_model(X, y):
    """The one model family in play: logistic regression, fixed settings, raw features."""
    if len(np.unique(y)) < 2:
        raise ValueError("need both classes to fit")
    return LogisticRegression(C=1.0, max_iter=300).fit(X, y)


class Policy:
    """Subclass and override. `window` = how many most recent labelled weeks the default retrain uses."""

    window = 26

    def decide(self, t, view):
        return False

    def train_weeks(self, t, view):
        vis = view.visible_weeks
        return list(vis[-self.window:])


@dataclass
class Result:
    total_cost: float
    error_cost: float
    retrain_cost_total: float
    n_retrains: int
    retrain_weeks: list = field(default_factory=list)
    errors_by_week: np.ndarray = None
