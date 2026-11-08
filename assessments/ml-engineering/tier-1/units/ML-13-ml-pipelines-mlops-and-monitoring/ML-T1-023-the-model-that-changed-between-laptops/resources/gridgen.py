"""Synthetic mini-grid customer table for ML-T1-023. Fictional customers only.

    python resources/gridgen.py --out DIR --seed 11
"""
import argparse
from pathlib import Path

import numpy as np

NAMES = ["avg_daily_kwh", "topup_gap_days", "last_topup_ngn", "tenure_months", "appliances", "rainy_season"]


def make_topups(n=1500, seed=11):
    """Return X (n x 6 float64), y (int64: 1 = customer lapses within 30 days), names."""
    rng = np.random.default_rng(seed)
    kwh = rng.gamma(3.0, 0.6, n)
    gap = rng.gamma(2.5, 4.0, n)
    last = np.round(rng.lognormal(7.6, 0.6, n) / 50) * 50
    tenure = rng.integers(1, 48, n).astype(float)
    appl = rng.integers(1, 9, n).astype(float)
    rain = rng.integers(0, 2, n).astype(float)
    z = 0.9 + 0.17 * gap - 0.6 * kwh - 0.0006 * last - 0.03 * tenure + 0.4 * rain + 0.1 * appl
    y = (rng.random(n) < 1 / (1 + np.exp(-z))).astype(np.int64)
    X = np.column_stack([kwh, gap, last, tenure, appl, rain]).astype(np.float64)
    return X, y, list(NAMES)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--seed", type=int, default=11)
    a = ap.parse_args()
    X, y, names = make_topups(seed=a.seed)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    np.savetxt(out / "topups.csv", np.column_stack([X, y]), delimiter=",", header=",".join(names + ["lapsed"]), comments="")
