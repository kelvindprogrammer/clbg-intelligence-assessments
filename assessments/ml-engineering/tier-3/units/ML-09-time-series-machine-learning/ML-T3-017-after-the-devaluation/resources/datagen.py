"""Deterministic synthetic weekly staple-food price series with a policy shock (ML-T3-017, fictional market)."""
import numpy as np


def make_price(n=230, seed=2026, shock=1.0):
    """Return (price, info). Price is naira per 50 kg bag. At a random week `break_week` in [150, 180) a currency
    shock moves the level up (gradually, about 8-week adjustment), adds drift, and raises volatility about 1.8x.
    `shock=0` gives the same series with no policy shock (a control for false alarms)."""
    rng = np.random.default_rng(seed)
    b = int(rng.integers(150, 180))
    t = np.arange(n)
    after = np.clip(t - b, 0, None)
    lvl = (t >= b) * shock * (0.28 * (1 - np.exp(-after / 8.0)) + 0.0025 * after)
    sd = np.where((t >= b) & (shock > 0), 0.022, 0.012)
    e = np.zeros(n)
    z = rng.normal(0, 1, n)
    for i in range(1, n):
        e[i] = 0.7 * e[i - 1] + sd[i] * z[i]
    logp = np.log(38000.0) + 0.0012 * t + 0.03 * np.sin(2 * np.pi * t / 52.0) + lvl + e
    return np.exp(logp), {"break_week": b, "n": n}


if __name__ == "__main__":
    import argparse
    import os
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--seed", type=int, default=2026)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    p, _ = make_price(seed=a.seed)           # the break week is deliberately not written to the file
    np.savetxt(os.path.join(a.out, "rice_price.csv"), np.column_stack([np.arange(len(p)), p]), delimiter=",", fmt="%.2f", header="week,naira_per_50kg", comments="")
