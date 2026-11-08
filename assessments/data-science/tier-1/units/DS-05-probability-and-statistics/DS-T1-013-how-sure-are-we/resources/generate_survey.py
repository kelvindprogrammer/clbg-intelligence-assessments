#!/usr/bin/env python3
"""Generator for the DS-T1-013 synthetic POS-agent survey.

Writes agent_survey.csv: one row per surveyed (fictional) mobile-money / POS agent.
Daily transaction values are lognormal with an LGA-specific median; fraud attempts in the
last 30 days are Bernoulli with a small LGA-specific probability. Agent IDs are sequence
numbers; there are no names, phone numbers or locations finer than LGA.

Usage: python generate_survey.py --out DIR --seed 2026
"""
from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path

import numpy as np

# LGA: (sample size, median daily value in naira, sdlog, fraud-attempt probability)
LGAS = {
    "Kano Municipal": (38, 95_000, 1.0, 0.05),
    "Nassarawa (Kano)": (22, 70_000, 1.1, 0.03),
    "Ikeja": (60, 180_000, 1.2, 0.06),
    "Surulere": (45, 140_000, 1.1, 0.04),
    "Port Harcourt": (30, 150_000, 1.3, 0.05),
    "Obio/Akpor": (18, 110_000, 1.0, 0.02),
}


def write(out: Path, seed: int) -> None:
    out.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(seed)
    rows = []
    aid = 1
    for lga, (n, med, sdlog, p) in LGAS.items():
        values = rng.lognormal(math.log(med), sdlog, size=n)
        fraud = rng.random(n) < p
        months = rng.integers(1, 97, size=n)
        for v, f, m in zip(values, fraud, months):
            rows.append([f"AG-{aid:04d}", lga, int(round(v, -2)), int(f), int(m)])
            aid += 1
    with open(out / "agent_survey.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["agent_id", "lga", "daily_value_ngn", "fraud_attempt_30d", "months_operating"])
        w.writerows(rows)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--seed", type=int, default=2026)
    a = ap.parse_args()
    write(Path(a.out), a.seed)


if __name__ == "__main__":
    main()
