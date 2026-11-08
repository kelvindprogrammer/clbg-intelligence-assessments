"""A public simulator you may use to test your methods. Ground truth is known here; on the real
cooperative file it is not. The hidden evaluation uses a harder and differently parameterised family,
so a method tuned only to this simulator will not pass."""
from __future__ import annotations

import numpy as np

FEATURES = ["monthly_contrib_ngn", "savings_balance_ngn", "loan_amt_ngn", "repay_rate",
            "tenure_months", "meeting_attendance", "contrib_volatility", "household_size"]


def _sigmoid(z):
    return 1 / (1 + np.exp(-z))


def simulate(k: int, n: int = 600, seed: int = 0, sep: float = 6.0, tail: float = 0.6):
    """Return (X, labels): raw features in natural units (naira, months, rates) and the true segment of
    each member. k = 1 gives a single correlated population with NO segments."""
    rng = np.random.default_rng(seed)
    d = 6
    L0 = np.linalg.cholesky(0.4 * np.ones((d, d)) + 0.6 * np.eye(d))
    means = [np.zeros(d)]
    while len(means) < k:
        c = rng.normal(size=d)
        c = c / np.linalg.norm(c) * rng.uniform(sep, 1.5 * sep)
        if all(np.linalg.norm(c - m) >= sep for m in means):
            means.append(c)
    w = rng.dirichlet(np.full(k, 6.0)) if k > 1 else np.ones(1)
    labels = rng.choice(k, size=n, p=w)
    Z = np.empty((n, d))
    for j in range(k):
        m = labels == j
        Z[m] = means[j] + rng.uniform(0.85, 1.2) * rng.normal(size=(m.sum(), d)) @ L0.T
    X = np.empty((n, 8))
    X[:, 0] = np.exp(np.log(9000) + tail * Z[:, 0])
    X[:, 1] = np.exp(np.log(70000) + 1.3 * tail * Z[:, 1])
    X[:, 2] = np.exp(np.log(120000) + 1.2 * tail * Z[:, 2])
    X[:, 3] = _sigmoid(0.9 * Z[:, 3] + 1.0)
    X[:, 4] = 6 + 60 * _sigmoid(0.8 * Z[:, 4])
    X[:, 5] = _sigmoid(0.9 * Z[:, 5])
    X[:, 6] = 0.2 * np.exp(0.3 * rng.normal(size=n) + 0.2 * Z[:, 0])
    X[:, 7] = 1 + rng.poisson(4, size=n)
    return X, labels
