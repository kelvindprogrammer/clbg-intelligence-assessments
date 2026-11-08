"""Deterministic synthetic prepaid-meter vend records (fictional DisCo; no real customers).

    python datagen.py --out DIR --seed 2026      # writes vends.jsonl and labels.json
"""
import argparse
import json
import os

import numpy as np

SCHEMA = {
    "token_amount_ngn": {"type": "float", "min": 100.0, "max": 200000.0},
    "kwh_registered": {"type": "float", "min": 0.1, "max": 2000.0},
    "vends_last_30d": {"type": "int", "min": 0, "max": 60},
    "meter_type": {"type": "category", "allowed": ["single_phase", "three_phase", "prepaid_cr"]},
    "days_since_last_vend": {"type": "float", "min": 0.0, "max": 365.0},
}


def make_vends(n=3000, seed=2026):
    """Return (records, y): records is a list of dicts matching SCHEMA, y is 1 for a suspected bypass vend."""
    rng = np.random.default_rng(seed)
    amount = np.clip(np.exp(rng.normal(8.5, 0.8, n)), 100, 200000).round(2)
    kwh = np.clip(amount / 95.0 * np.exp(rng.normal(0, 0.35, n)), 0.1, 2000).round(2)
    vends = np.clip(rng.poisson(6, n), 0, 60)
    mtype = rng.choice(["single_phase", "three_phase", "prepaid_cr"], n, p=[0.6, 0.15, 0.25])
    gap = np.clip(rng.exponential(12, n), 0, 365).round(1)
    za = (np.log(amount) - 8.5) / 0.8
    zk = (np.log(kwh) - np.log(amount / 95.0)) / 0.35
    z = -1.6 + 0.5 * za - 1.3 * zk + 0.12 * (vends - 6) + 0.9 * (mtype == "prepaid_cr") + 0.02 * gap
    y = (rng.random(n) < 1 / (1 + np.exp(-z))).astype(int)
    recs = [{"token_amount_ngn": float(amount[i]), "kwh_registered": float(kwh[i]), "vends_last_30d": int(vends[i]),
             "meter_type": str(mtype[i]), "days_since_last_vend": float(gap[i])} for i in range(n)]
    return recs, y


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--seed", type=int, default=2026)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    recs, y = make_vends(seed=a.seed)
    with open(os.path.join(a.out, "vends.jsonl"), "w") as f:
        for r in recs:
            f.write(json.dumps(r) + "\n")
    with open(os.path.join(a.out, "labels.json"), "w") as f:
        json.dump([int(v) for v in y], f)


if __name__ == "__main__":
    main()
