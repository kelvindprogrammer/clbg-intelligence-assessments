"""Synthetic data generator for DS-T1-016 (public).

    python resources/generate_data.py --out resources/data --seed 2026

Writes four CSV files (all values synthetic, for training only):
  seed_adoption_survey.csv   state, farmers_surveyed, adopted
  maize_price_history.csv    market, month, price_ngn_per_100kg
  maize_price_forecast.csv   market, month, q0.025, q0.1, q0.25, q0.5, q0.75, q0.9, q0.975
  march_price_samples.csv    market, draw, price_ngn_per_100kg   (predictive draws for March)

The forecast table is produced by fitting each quantile separately, as many quick
models do, so some rows may contain crossing quantiles. That is deliberate.
Deterministic for a fixed seed.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

STATES = ["Kano", "Kaduna", "Katsina", "Niger", "Plateau", "Benue", "Oyo", "Ogun", "Taraba", "Bauchi",
          "Gombe", "Kwara", "Nasarawa", "Ekiti"]
MARKETS = {"Dawanau (Kano)": 41_000, "Giwa (Kaduna)": 39_500, "Bodija (Ibadan)": 46_500, "Mile 12 (Lagos)": 49_000}
QS = [0.025, 0.1, 0.25, 0.5, 0.75, 0.9, 0.975]


def survey(rng):
    n = rng.choice([4, 6, 9, 15, 25, 40, 60, 90, 150, 220, 300, 400], size=len(STATES), replace=True)
    n[STATES.index("Ekiti")] = 6          # tiny sample with zero adopters
    n[STATES.index("Taraba")] = 5          # tiny sample, all adopters
    n[STATES.index("Kano")] = 400
    p = rng.uniform(0.15, 0.7, len(STATES))
    k = rng.binomial(n, p)
    k[STATES.index("Ekiti")] = 0
    k[STATES.index("Taraba")] = 5
    return pd.DataFrame({"state": STATES, "farmers_surveyed": n.astype(int), "adopted": k.astype(int)})


def history(rng):
    months = pd.period_range("2024-01", "2026-11", freq="M")
    rows = []
    for m, level in MARKETS.items():
        trend = np.linspace(0.62, 1.0, len(months))
        season = 1 + 0.12 * np.cos((months.month.to_numpy() - 7) * 2 * np.pi / 12)  # lean season peaks in July
        price = level * trend * season * rng.lognormal(0, 0.035, len(months))
        rows += [{"market": m, "month": str(t), "price_ngn_per_100kg": int(round(v, -1))} for t, v in zip(months, price)]
    return pd.DataFrame(rows)


def forecast_and_samples(rng, hist):
    months = pd.period_range("2026-12", "2027-05", freq="M")
    rows, draws = [], []
    for mi, (m, level) in enumerate(MARKETS.items()):
        last = hist.loc[hist.market == m, "price_ngn_per_100kg"].iloc[-1]
        for h, t in enumerate(months, start=1):
            mu = last * (1 + 0.012 * h) * (1 + 0.06 * np.cos((t.month - 7) * 2 * np.pi / 12))
            sd = 0.045 * np.sqrt(h)
            z = np.array([-1.96, -1.2816, -0.6745, 0.0, 0.6745, 1.2816, 1.96])
            q = mu * np.exp(sd * z) * rng.lognormal(0, 0.004, len(z))
            if mi == 2 and h >= 4:            # one market's separately-fitted quantiles cross
                q[4], q[5] = q[5] * 1.0005, q[4]
            rows.append({"market": m, "month": str(t), **{f"q{qq}": int(round(v, -1)) for qq, v in zip(QS, q)}})
            if t.month == 3:
                s = mu * np.exp(sd * rng.standard_t(6, 4000) * 0.9)
                draws += [{"market": m, "draw": i, "price_ngn_per_100kg": int(round(v, -1))} for i, v in enumerate(s)]
    return pd.DataFrame(rows), pd.DataFrame(draws)


def write(out: Path, seed: int) -> None:
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(seed)
    s = survey(rng)
    h = history(rng)
    f, d = forecast_and_samples(rng, h)
    for name, df in [("seed_adoption_survey", s), ("maize_price_history", h), ("maize_price_forecast", f),
                     ("march_price_samples", d)]:
        df.to_csv(out / f"{name}.csv", index=False, lineterminator="\n")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", required=True)
    ap.add_argument("--seed", type=int, default=2026)
    a = ap.parse_args(argv)
    write(Path(a.out), a.seed)
    print(f"wrote 4 files to {a.out}")


if __name__ == "__main__":
    main()
