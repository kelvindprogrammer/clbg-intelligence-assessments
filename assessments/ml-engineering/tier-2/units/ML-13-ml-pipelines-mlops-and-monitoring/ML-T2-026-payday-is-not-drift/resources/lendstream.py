"""Synthetic digital-lender application stream for ML-T2-026. Fictional applicants only.

    python resources/lendstream.py --out DIR --seed 3

Each day is generated independently from (seed, day), so a day's batch never depends on later days.
"""
import argparse
from pathlib import Path

import numpy as np

NAMES = ["loan_amount_ngn", "monthly_income_ngn", "age", "app_hour", "device_new", "credit_checks_6m", "formal_employer"]
PERIOD = 30


def _base(rng, n, salary):
    amt = rng.lognormal(10.0, 0.5, n) * (1.5 if salary else 1.0)
    inc = rng.lognormal(11.6, 0.5, n)
    age = np.clip(rng.normal(34, 8, n), 18, 65)
    hour = np.mod(rng.normal(12 if salary else 14, 3 if salary else 4, n), 24)
    dev = (rng.random(n) < 0.15).astype(float)
    chk = rng.poisson(2.0, n).astype(float)
    frm = (rng.random(n) < (0.6 if salary else 0.45)).astype(float)
    return np.column_stack([amt, inc, age, hour, dev, chk, frm])


def _channel(rng, n, salary):
    amt = rng.lognormal(9.7, 0.5, n) * (1.5 if salary else 1.0)
    inc = rng.lognormal(11.0, 0.5, n)
    age = np.clip(rng.normal(24, 5, n), 18, 65)
    hour = np.mod(rng.normal(23, 2.5, n), 24)
    dev = (rng.random(n) < 0.6).astype(float)
    chk = rng.poisson(0.5, n).astype(float)
    frm = (rng.random(n) < 0.15).astype(float)
    return np.column_stack([amt, inc, age, hour, dev, chk, frm])


def make_stream(seed=0, days=240, drift_day=None, ramp_days=1, share=0.35, batch=400, low_volume=()):
    """Return (batches, names): batches is a list of (day, X) with X of shape (n_day, 7).

    Every PERIOD days a salary week (cycle days 25 to 29) shifts several features: that is benign
    seasonality. From `drift_day` a new partner channel supplies a growing share of applicants
    (reaching `share` after `ramp_days`). Days in `low_volume` have only 40 applications.
    """
    out = []
    for day in range(days):
        rng = np.random.default_rng([seed, day])
        n = 40 if day in set(low_volume) else batch
        salary = (day % PERIOD) >= 25
        X = _base(rng, n, salary)
        if drift_day is not None and day >= drift_day:
            f = share * min(1.0, (day - drift_day + 1) / max(1, ramp_days))
            m = rng.random(n) < f
            if m.any():
                X[m] = _channel(rng, int(m.sum()), salary)
        out.append((day, X))
    return out, list(NAMES)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--seed", type=int, default=3)
    a = ap.parse_args()
    batches, names = make_stream(seed=a.seed, drift_day=160)
    rows = np.vstack([np.column_stack([np.full(len(X), d), X]) for d, X in batches])
    Path(a.out).mkdir(parents=True, exist_ok=True)
    np.savetxt(Path(a.out) / "applications.csv", rows, delimiter=",", header=",".join(["day"] + names), comments="")
