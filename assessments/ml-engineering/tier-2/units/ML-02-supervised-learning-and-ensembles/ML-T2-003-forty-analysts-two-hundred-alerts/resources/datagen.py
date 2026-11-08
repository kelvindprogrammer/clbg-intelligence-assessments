"""Deterministic synthetic mobile-money transactions for ML-T2-003 (fictional)."""
import numpy as np

BASE = ["amount_ngn", "hour", "new_device", "sim_age_days", "txns_last_hour", "new_recipient", "agent_km", "balance_ratio", "channel"]


def make_transactions(n=24000, seed=2026, days=60, leak_name="chargeback_flag", leak_position=-1):
    """Return X, y, day, names. y=1 is fraud (about 1.4%). `leak_name` is set after fraud is confirmed
    (92% of frauds, 0.4% of legitimate). Fraud tactic C moves from night to daytime from day 45."""
    rng = np.random.default_rng(seed)
    day = np.sort(rng.integers(0, days, n))
    late = (day >= int(days * 0.75)).astype(float)
    amount = np.exp(rng.normal(8.5, 1.1, n))
    hp = np.r_[np.full(6, 0.015), np.full(16, 0.0495), np.full(2, 0.0)]
    hour = rng.choice(24, n, p=hp / hp.sum())
    new_dev = (rng.random(n) < 0.08).astype(float)
    sim = np.exp(rng.normal(5.5, 1.2, n))
    tx1 = rng.poisson(0.6, n).astype(float)
    newrec = (rng.random(n) < 0.3).astype(float)
    km = np.exp(rng.normal(0.8, 1.0, n))
    bal = np.clip(rng.beta(1.2, 6, n) * 2, 0, 1.5)
    chan = rng.integers(0, 3, n).astype(float)
    night = ((hour < 6) | (hour >= 22))
    A = (new_dev == 1) & (bal > 0.6)
    B = (sim < 60) & (newrec == 1) & (tx1 >= 2)
    C = np.where(late == 1, ~night, night) & (km > 5) & (bal > 0.5)
    p = np.clip(0.002 + 0.45 * A + 0.35 * B + 0.30 * C, 0, 0.9)
    y = (rng.random(n) < p).astype(int)
    leak = np.where(y == 1, rng.random(n) < 0.92, rng.random(n) < 0.004).astype(float)
    cols = [amount, hour.astype(float), new_dev, sim, tx1, newrec, km, bal, chan]
    names = list(BASE)
    pos = len(cols) if leak_position == -1 else leak_position
    cols.insert(pos, leak)
    names.insert(pos, leak_name)
    return np.column_stack(cols), y, day, names


if __name__ == "__main__":
    import argparse
    import os
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--seed", type=int, default=2026)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    X, y, day, names = make_transactions(seed=a.seed)
    np.savetxt(os.path.join(a.out, "transactions.csv"), np.column_stack([day, X, y]), delimiter=",", fmt="%.6g",
               header=",".join(["day"] + names + ["fraud"]), comments="")
