"""Synthetic soil-fertility classification tasks (provided; do not modify). Deterministic given (kind, n, seed, n_noise).

kind 'smooth' : smooth nonlinear interactions of 6 informative features (favours networks)
kind 'axis'   : thresholds on single features (favours trees)
kind 'rotated': the 'axis' rule, but the learner sees the 6 informative features after a random rotation, so the
                rule is oblique in the observed coordinates (hurts trees)
Columns 6.. are pure-noise features (n_noise of them).
"""
import numpy as np

KINDS = ("smooth", "axis", "rotated")


def make_task(kind, n, seed, n_noise=6, label_noise=0.05):
    """Return X (n, 6 + n_noise) and y (n,) in {0, 1}."""
    rng = np.random.default_rng([seed, KINDS.index(kind), n_noise])
    S = rng.normal(size=(n, 6))
    if kind == "smooth":
        f = 1.6 * np.tanh(S[:, 0] + S[:, 1]) + S[:, 2] * S[:, 3] + 0.9 * np.sin(2 * S[:, 4]) - 0.5 * S[:, 5] ** 2 + 0.5
        observed = S
    else:
        f = (1.6 * (S[:, 0] > 0.3) - 1.6 * (S[:, 1] < -0.4) + 1.4 * ((S[:, 2] > 0) & (S[:, 3] > 0))
             - 0.9 * (S[:, 4] > 1.0) + 0.6 * (S[:, 5] > -0.5) - 0.6)
        observed = S
        if kind == "rotated":
            Q, _ = np.linalg.qr(rng.normal(size=(6, 6)))
            observed = S @ Q
    y = (rng.random(n) < 1 / (1 + np.exp(-2.0 * f))).astype(int)
    flip = rng.random(n) < label_noise
    y = np.where(flip, 1 - y, y)
    return np.hstack([observed, rng.normal(size=(n, n_noise))]), y
