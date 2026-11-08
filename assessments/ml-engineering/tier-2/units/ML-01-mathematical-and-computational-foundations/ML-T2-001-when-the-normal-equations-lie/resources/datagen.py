"""Deterministic synthetic hourly feeder data for ML-T2-001 (fictional)."""
import numpy as np


def make_feeder(n_train=900, n_test=300, seed=2026, vendor_noise=0.6, dup_pair="customers"):
    """Return X_train, y_train, X_test, y_test, names.

    Columns: temp_c, humidity, heat_index, temp_lag1, customers, customers_k, hour_sin, hour_cos.
    dup_pair='customers' keeps customers_k = customers/1000 (rounded). Any other value keeps it as an
    independent column (used by hidden tests together with different structure).
    """
    rng = np.random.default_rng(seed)
    n = n_train + n_test
    t = np.arange(n)
    hour = t % 24
    season = np.where(t < n_train, 0.0, 4.0)
    temp = 27 + 4 * np.sin(2 * np.pi * (hour - 15) / 24) + season + rng.normal(0, 1.5, n)
    hum = 65 - 8 * np.sin(2 * np.pi * (hour - 15) / 24) + rng.normal(0, 6, n)
    noise = np.where(t < n_train, 1e-3, vendor_noise)
    heat = 0.7 * temp + 0.3 * hum + rng.normal(0, 1, n) * noise
    lag = np.r_[temp[0], temp[:-1]]
    cons = 1.2e5 + t * 15.0 + rng.normal(0, 200, n)
    consk = np.round(cons / 1000.0, 1) if dup_pair == "customers" else rng.normal(50, 5, n)
    hs, hc = np.sin(2 * np.pi * hour / 24), np.cos(2 * np.pi * hour / 24)
    X = np.column_stack([temp, hum, heat, lag, cons, consk, hs, hc])
    y = 15 + 0.8 * temp + 0.04 * hum + 0.0001 * cons + 2.0 * hs - 1.2 * hc + rng.normal(0, 0.7, n)
    names = ["temp_c", "humidity", "heat_index", "temp_lag1", "customers", "customers_k", "hour_sin", "hour_cos"]
    return X[:n_train], y[:n_train], X[n_train:], y[n_train:], names


if __name__ == "__main__":
    import argparse
    import os
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--seed", type=int, default=2026)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    Xa, ya, Xb, yb, names = make_feeder(seed=a.seed)
    for tag, X, y in (("train", Xa, ya), ("test", Xb, yb)):
        np.savetxt(os.path.join(a.out, f"feeder_{tag}.csv"), np.column_stack([X, y]), delimiter=",",
                   header=",".join(names + ["load_mw"]), comments="", fmt="%.6g")
