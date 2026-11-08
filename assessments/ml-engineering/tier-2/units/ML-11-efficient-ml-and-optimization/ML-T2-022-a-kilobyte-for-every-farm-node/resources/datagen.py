"""Deterministic synthetic irrigation-node task and a trained float MLP (fictional sensors; no real farm).

    python datagen.py --out DIR --seed 2026      # writes task.npz (small) with the trained float weights
"""
import argparse
import os

import numpy as np
from sklearn.neural_network import MLPClassifier

CLASSES = ["wait", "irrigate_now", "salinity_alert", "sensor_fault"]


def make_task(seed=2026, n_train=3000, n_cal=800, n_test=2000, d=24):
    """Return dict of Xtr, ytr, Xcal, ycal, Xte, yte. Labels come from a fixed random tanh network plus noise."""
    g = np.random.default_rng(777)  # the 'physics' is fixed; only the sample changes with seed
    A, B = g.normal(0, 1, (d, 16)) / np.sqrt(d), g.normal(0, 1.4, (16, 4))
    rng = np.random.default_rng(seed)
    n = n_train + n_cal + n_test
    X = rng.normal(0, 1, (n, d))
    logits = np.tanh(X @ A) @ B + rng.gumbel(0, 0.35, (n, 4))
    y = logits.argmax(1)
    s1, s2 = n_train, n_train + n_cal
    return dict(Xtr=X[:s1], ytr=y[:s1], Xcal=X[s1:s2], ycal=y[s1:s2], Xte=X[s2:], yte=y[s2:])


def train_float_model(seed=2026, hidden=(64, 32), **kw):
    """Return (Ws, bs, task). Ws[i] has shape (n_in, n_out); hidden layers use ReLU; the last layer gives logits."""
    task = make_task(seed, **kw)
    m = MLPClassifier(hidden, activation="relu", max_iter=400, random_state=seed, alpha=1e-3)
    m.fit(task["Xtr"], task["ytr"])
    return [w.copy() for w in m.coefs_], [b.copy() for b in m.intercepts_], task


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--seed", type=int, default=2026)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    Ws, bs, task = train_float_model(a.seed)
    np.savez_compressed(os.path.join(a.out, "task.npz"), **task, **{f"W{i}": w for i, w in enumerate(Ws)},
                        **{f"b{i}": b for i, b in enumerate(bs)})


if __name__ == "__main__":
    main()
