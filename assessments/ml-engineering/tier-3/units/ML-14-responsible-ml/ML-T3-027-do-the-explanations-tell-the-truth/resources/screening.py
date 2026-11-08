"""Synthetic TB-screening tabular data with a planted shortcut, for ML-T3-027. Fictional patients only.

    python resources/screening.py --out DIR --seed 1

A screening-device offset is recorded for every patient. During the outreach camps used for training, sicker
patients were screened first on one device, so the offset is correlated with the label; in deployment the
devices are used at random and the correlation is gone.
"""
import argparse
from pathlib import Path

import numpy as np

BASE = ["cough_days", "weight_loss_kg", "night_sweats", "fever_days", "spo2", "resp_rate", "age", "contact_score", "bmi"]


def make_screening(n=3000, seed=0, shortcut_col=None, shortcut_strength=0.9, deployment=False):
    """Return X (n x 10), y, names. The device column sits at `shortcut_col` (default: last)."""
    rng = np.random.default_rng([seed, 31, int(deployment)])
    cough, wl, sw = rng.normal(size=(3, n))
    fever = 0.5 * cough + np.sqrt(0.75) * rng.normal(size=n)
    spo2 = -0.6 * cough + 0.8 * rng.normal(size=n)
    resp = 0.5 * fever + np.sqrt(0.75) * rng.normal(size=n)
    age, contact, bmi = rng.normal(size=(3, n))
    z = 1.0 * cough + 0.8 * wl + 0.7 * sw + 0.6 * fever - 0.2
    y = (rng.random(n) < 1.0 / (1.0 + np.exp(-z))).astype(int)
    if deployment:
        dev = rng.normal(0, np.sqrt(shortcut_strength ** 2 + 0.49), n)
    else:
        dev = (2 * y - 1) * shortcut_strength + rng.normal(0, 0.7, n)
    cols = [cough, wl, sw, fever, spo2, resp, age, contact, bmi]
    names = list(BASE)
    pos = len(cols) if shortcut_col is None else int(shortcut_col)
    cols.insert(pos, dev)
    names.insert(pos, "device_offset")
    return np.column_stack(cols), y, names


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--seed", type=int, default=1)
    a = ap.parse_args()
    Path(a.out).mkdir(parents=True, exist_ok=True)
    for nm, dep in (("train", False), ("deploy", True)):
        X, y, names = make_screening(seed=a.seed, deployment=dep)
        np.savetxt(Path(a.out) / f"{nm}.csv", np.column_stack([X, y]), delimiter=",", fmt="%.5g", header=",".join(names + ["tb"]), comments="")
