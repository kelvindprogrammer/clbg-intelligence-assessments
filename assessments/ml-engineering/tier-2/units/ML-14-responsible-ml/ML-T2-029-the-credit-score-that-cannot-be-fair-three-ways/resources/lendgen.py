"""Synthetic agent-banking micro-loan data for ML-T2-029. Fictional traders only.

    python resources/lendgen.py --out DIR --seed 1
"""
import argparse
from pathlib import Path

import numpy as np

NAMES = ["income_proof", "wallet_txn_volume", "months_in_business", "prior_loans", "distance_to_agent_km", "phone_age_months"]


def make_lending(n=6000, seed=1):
    """Return X (n x 6), y (1 = repaid, 0 = defaulted), g (0 = urban, 1 = rural), names.

    Rural traders have a lower average repayment rate, less formal documentation (so a noisier income
    proof), fewer prior loans and live further from an agent.
    """
    rng = np.random.default_rng(seed)
    g = (rng.random(n) < 0.35).astype(int)
    c = rng.normal(np.where(g == 1, -0.15, 0.30), 1.0)
    y = (rng.random(n) < 1.0 / (1.0 + np.exp(-(1.5 * c + 0.9)))).astype(int)
    income = c + rng.normal(0, np.where(g == 1, 1.2, 0.6))
    wallet = 0.7 * c + rng.normal(0, 0.9, n)
    months = np.clip(24 + 8 * c + rng.normal(0, 14, n), 1, None)
    prior = rng.poisson(np.where(g == 1, 1.2, 2.4)).astype(float)
    dist = rng.gamma(2.0, np.where(g == 1, 6.0, 1.5))
    phone = rng.gamma(3.0, 8.0, n)
    X = np.column_stack([income, wallet, months, prior, dist, phone])
    return X, y, g, list(NAMES)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--seed", type=int, default=1)
    a = ap.parse_args()
    X, y, g, names = make_lending(seed=a.seed)
    Path(a.out).mkdir(parents=True, exist_ok=True)
    np.savetxt(Path(a.out) / "loans.csv", np.column_stack([X, g, y]), delimiter=",", fmt="%.5g",
               header=",".join(names + ["rural", "repaid"]), comments="")
