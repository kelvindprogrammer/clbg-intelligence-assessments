#!/usr/bin/env python3
"""Generator for the DS-T3-007 synthetic fall-armyworm scouting survey.

Fictional maize farms in 30 fictional villages. Each farm was scouted once: a number of plants
inspected and the number showing fall-armyworm damage. `push_pull` records whether the farm
used push-pull intercropping (desmodium and a border of Napier/Brachiaria grass).

The data follow the hierarchical logistic model in the README (section B) with fixed
"true" parameters below. The generator is public because the assessment is about
computation and calibration, not about discovering hidden values. Use it (or your own
prior-predictive simulator) for simulation-based calibration.

Usage: python generate_survey.py --out DIR --seed 2026 [--tau 0.35]
"""
from __future__ import annotations

import argparse
import csv
from pathlib import Path

import numpy as np

TRUE = {"mu": -0.4, "beta": -0.8, "tau": 0.35}
N_VILLAGES = 30


def write(out: Path, seed: int, tau: float = TRUE["tau"]) -> None:
    out.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(seed)
    alpha = TRUE["mu"] + tau * rng.standard_normal(N_VILLAGES)
    # Many villages have very few scouted farms: that is where the funnel lives.
    n_farms = np.clip(rng.geometric(0.12, N_VILLAGES), 1, 30)
    rows = []
    fid = 1
    for v in range(N_VILLAGES):
        for _ in range(int(n_farms[v])):
            n = int(rng.choice([20, 30, 50], p=[0.5, 0.3, 0.2]))
            x = int(rng.random() < 0.25)
            p = 1 / (1 + np.exp(-(alpha[v] + TRUE["beta"] * x)))
            rows.append([f"V{v + 1:02d}", f"F{fid:04d}", n, int(rng.binomial(n, p)), x])
            fid += 1
    with open(out / "armyworm_survey.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["village", "farm_id", "plants_inspected", "plants_infested", "push_pull"])
        w.writerows(rows)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--seed", type=int, default=2026)
    ap.add_argument("--tau", type=float, default=TRUE["tau"])
    a = ap.parse_args()
    write(Path(a.out), a.seed, a.tau)


if __name__ == "__main__":
    main()
