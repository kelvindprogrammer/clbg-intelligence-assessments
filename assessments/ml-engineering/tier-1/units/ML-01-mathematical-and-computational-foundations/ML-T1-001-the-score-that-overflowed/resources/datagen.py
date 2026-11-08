"""Deterministic synthetic data for ML-T1-001 (fictional telecom subscribers)."""
import numpy as np


def make_churn(n=2000, seed=2026):
    """Raw (badly scaled) churn features and a 0/1 label. Columns: spend_kobo, data_mb, tenure_days, dropped_calls."""
    rng = np.random.default_rng(seed)
    spend = np.exp(rng.normal(11.5, 0.8, n))            # about 1e5 kobo
    data = rng.gamma(2.0, 2500.0, n)                    # about 5e3 MB
    tenure = rng.uniform(30, 3000, n)
    drops = rng.poisson(3.0, n).astype(float)
    z = lambda v: (v - v.mean()) / v.std()
    logit = -0.4 + -1.1 * z(np.log(spend)) + 0.5 * z(data) - 0.9 * z(tenure) + 1.2 * z(drops)
    y = (rng.random(n) < 1.0 / (1.0 + np.exp(-logit))).astype(int)
    return np.column_stack([spend, data, tenure, drops]), y


def make_logits(n=64, k=3, seed=2026, scale=1000.0):
    """Extreme logits for stability tests."""
    rng = np.random.default_rng(seed)
    return rng.normal(0.0, scale, (n, k))


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--seed", type=int, default=2026)
    a = ap.parse_args()
    import os
    os.makedirs(a.out, exist_ok=True)
    X, y = make_churn(2000, a.seed)
    np.savetxt(os.path.join(a.out, "churn.csv"), np.column_stack([X, y]), delimiter=",", header="spend_kobo,data_mb,tenure_days,dropped_calls,churn", comments="")
