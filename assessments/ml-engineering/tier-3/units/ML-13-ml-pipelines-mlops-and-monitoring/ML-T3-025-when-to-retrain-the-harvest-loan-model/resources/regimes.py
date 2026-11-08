"""Synthetic weekly loan-outcome streams with three drift regimes, for ML-T3-025. Fictional borrowers only.

    python resources/regimes.py --out DIR --seed 1

Loan outcomes (default or repaid) become known `delay` weeks after the loan is scored.
"""
import argparse
from pathlib import Path

import numpy as np

KINDS = ("shock", "creep", "seasonal")
D = 8


def make_regime(kind, seed, weeks=130, n=200, delay=12):
    """Return a dict: X (weeks, n, 8), y (weeks, n) in {0,1}, delay, kind.

    shock:    an abrupt change in how features relate to default (no change in the features themselves).
    creep:    a slow rotation of the relationship plus a slow shift of two features (inflation).
    seasonal: the relationship alternates with the farming calendar (a 52-week cycle).
    The onset and the weights depend on the seed.
    """
    if kind not in KINDS:
        raise ValueError(kind)
    rng = np.random.default_rng([seed, 7919])
    w0 = rng.normal(size=D)
    w0 *= 1.6 / np.linalg.norm(w0)
    w1 = w0.copy()
    flip = np.argsort(-np.abs(w0))[:3]
    w1[flip] *= -1.0
    w2 = rng.normal(size=D)
    w2 *= 1.6 / np.linalg.norm(w2)
    onset = int(rng.integers(55, 71))
    X = np.empty((weeks, n, D))
    y = np.empty((weeks, n), dtype=np.int64)
    for t in range(weeks):
        r = np.random.default_rng([seed, 104729, t])
        x = r.normal(size=(n, D))
        if kind == "shock":
            wt = w1 if t >= onset else w0
        elif kind == "creep":
            a = min(1.0, max(0.0, (t - onset) / 40.0))
            wt = (1 - a) * w0 + a * w2
            x[:, 0] += a * 1.5
            x[:, 3] += a * 1.2
        else:
            wt = w1 if (t % 52) >= 26 else w0
        z = x @ wt - 0.8
        y[t] = (r.random(n) < 1.0 / (1.0 + np.exp(-z))).astype(np.int64)
        X[t] = x
    return {"X": X, "y": y, "delay": delay, "kind": kind}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--seed", type=int, default=1)
    a = ap.parse_args()
    Path(a.out).mkdir(parents=True, exist_ok=True)
    for kd in KINDS:
        s = make_regime(kd, a.seed)
        rows = np.column_stack([np.repeat(np.arange(s["X"].shape[0]), s["X"].shape[1]), s["X"].reshape(-1, D), s["y"].reshape(-1)])
        np.savetxt(Path(a.out) / f"{kd}.csv", rows, delimiter=",", fmt="%.5g")
