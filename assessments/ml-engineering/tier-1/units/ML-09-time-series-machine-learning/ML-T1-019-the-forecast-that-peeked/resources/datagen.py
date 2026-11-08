"""Deterministic synthetic daily feeder load (MW) for ML-T1-019 (fictional feeder)."""
import numpy as np


def make_load(n=420, seed=2026):
    """Weekly pattern + slow growth + annual swing + AR(1) noise. Returns a float array of length n."""
    rng = np.random.default_rng(seed)
    t = np.arange(n)
    weekly = np.array([0.0, 2.0, 3.5, 4.0, 3.0, -6.0, -8.0])[t % 7]   # weekends are lighter
    noise = np.zeros(n)
    for i in range(1, n):
        noise[i] = 0.55 * noise[i - 1] + rng.normal(0, 1.0)
    return 80.0 + 0.25 * t + 4.0 * np.sin(2 * np.pi * t / 365.0) + weekly + noise


if __name__ == "__main__":
    import argparse
    import os
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--seed", type=int, default=2026)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    s = make_load(seed=a.seed)
    np.savetxt(os.path.join(a.out, "feeder_load.csv"), np.column_stack([np.arange(len(s)), s]), delimiter=",", fmt="%.4f", header="day,load_mw", comments="")
