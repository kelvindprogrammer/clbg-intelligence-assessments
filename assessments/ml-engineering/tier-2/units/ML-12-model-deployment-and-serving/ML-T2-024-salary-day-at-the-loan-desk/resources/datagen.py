"""Deterministic synthetic salary-day traffic and noisy model-timing measurements (fictional lender).

    python datagen.py --out DIR --seed 2026      # writes arrivals.npy and timings.csv
"""
import argparse
import os

import numpy as np

SLO_MS = 100.0


def make_arrivals(seed=2026, surge=1.0):
    """Request arrival times in ms, sorted. 90 s: 60/s, then 300/s*surge for 30 s with a 150-request burst, then 60/s."""
    rng = np.random.default_rng(seed)
    parts = []
    for start, end, rate in [(0, 30, 60.0), (30, 60, 300.0 * surge), (60, 90, 60.0)]:
        n = rng.poisson(rate * (end - start))
        parts.append(rng.uniform(start * 1000.0, end * 1000.0, n))
    parts.append(rng.uniform(45000.0, 45020.0, 150))      # push-notification burst at t = 45 s
    return np.sort(np.concatenate(parts))


def make_timings(seed=2026):
    """Measured (batch_size, ms) pairs for the scoring model on the production CPU, with 3% garbage-collection spikes.

    Returns (sizes, times_ms, (a_true, b_true)); the true per-batch cost is a + b * size."""
    rng = np.random.default_rng(10_000 + seed)
    a, b = rng.uniform(9.0, 15.0), rng.uniform(0.6, 1.2)
    sizes = np.repeat([1, 2, 4, 8, 16, 32, 64], 12)
    t = a + b * sizes + rng.normal(0, 0.4, sizes.size)
    spike = rng.random(sizes.size) < 0.03
    t[spike] *= rng.uniform(3, 6, spike.sum())
    return sizes, t, (float(a), float(b))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--seed", type=int, default=2026)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    np.save(os.path.join(a.out, "arrivals.npy"), make_arrivals(a.seed))
    s, t, _ = make_timings(a.seed)
    np.savetxt(os.path.join(a.out, "timings.csv"), np.column_stack([s, t]), delimiter=",", header="batch_size,ms", comments="")


if __name__ == "__main__":
    main()
