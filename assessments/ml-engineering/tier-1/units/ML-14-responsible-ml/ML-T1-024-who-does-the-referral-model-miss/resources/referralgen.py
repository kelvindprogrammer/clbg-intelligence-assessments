"""Synthetic community-health referral model outputs for ML-T1-024. Fictional children only.

    python resources/referralgen.py --out DIR --seed 5

The file holds the outputs of a model that flags children for referral to a health facility.
"""
import argparse
from pathlib import Path

import numpy as np

ZONES = ["NC", "NE", "NW", "SE", "SS", "SW"]
SHARES = [0.30, 0.22, 0.19, 0.16, 0.118, 0.012]


def make_audit_data(n=2000, seed=5):
    """Return y_true, y_pred, score, group (numpy arrays). 1 = needs referral / is flagged."""
    rng = np.random.default_rng(seed)
    group = rng.choice(ZONES, size=n, p=SHARES)
    y = (rng.random(n) < np.where(group == "NE", 0.30, 0.22)).astype(int)
    snr = {z: 1.7 for z in ZONES}
    weak = ZONES[1 + int(rng.integers(0, 2)) * 3]  # NE or SE, depending on the seed
    snr[weak] = 0.75
    s = np.array([snr[g] for g in group])
    logit = (2 * y - 1) * s * 0.9 + rng.normal(0, 1.0, n) - 0.6
    score = 1.0 / (1.0 + np.exp(-logit))
    return y.astype(int), (score >= 0.5).astype(int), score, group


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--seed", type=int, default=5)
    a = ap.parse_args()
    y, p, s, g = make_audit_data(seed=a.seed)
    Path(a.out).mkdir(parents=True, exist_ok=True)
    with open(Path(a.out) / "referrals.csv", "w", encoding="utf-8") as f:
        f.write("zone,needs_referral,flagged,score\n")
        for gi, yi, pi, si in zip(g, y, p, s):
            f.write(f"{gi},{yi},{pi},{si:.5f}\n")
