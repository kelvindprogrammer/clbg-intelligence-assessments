"""Synthetic data generator for DS-T2-011 (public).

    python resources/generate_data.py --out resources/data --seed 2026

Writes four CSVs for the fictional "Naira Ledger Research" mobile-money quarterly:
  channel_value.csv      quarter, channel, value_ngn_bn          (USSD, App, Agent, Card, QR, Bank transfer)
  provider_failures.csv  quarter, provider, failure_rate_pct     (six fictional providers)
  agents_by_zone.csv     zone, active_agents                     (six geopolitical zones, latest quarter)
  fraud_reports.csv      quarter, reports_per_million
All values are invented. Deterministic for a fixed seed.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

QUARTERS = [f"{y}Q{q}" for y in range(2021, 2026) for q in range(1, 5)]
CHANNELS = {"USSD": (420, 0.02), "App": (260, 0.09), "Agent": (380, 0.03), "Card": (150, 0.01),
            "QR": (12, 0.16), "Bank transfer": (600, 0.06)}
PROVIDERS = [f"Provider {c}" for c in "ABCDEF"]   # anonymised, fictional
ZONES = ["North Central", "North East", "North West", "South East", "South South", "South West"]


def write(out: Path, seed: int) -> None:
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(seed)
    n = len(QUARTERS)
    rows = []
    for ch, (base, g) in CHANNELS.items():
        v = base * np.power(1 + g, np.arange(n)) * rng.lognormal(0, 0.04, n)
        rows += [{"quarter": q, "channel": ch, "value_ngn_bn": round(float(x), 1)} for q, x in zip(QUARTERS, v)]
    pd.DataFrame(rows).to_csv(out / "channel_value.csv", index=False, lineterminator="\n")

    rows = []
    for i, p in enumerate(PROVIDERS):
        lvl = rng.uniform(0.8, 2.4)
        trend = rng.uniform(-0.04, 0.01)
        f = np.clip(lvl + trend * np.arange(n) + rng.normal(0, 0.12, n), 0.2, None)
        if i == 3:
            f[12:15] += [1.6, 2.2, 0.9]       # one provider's outage episode in 2024
        rows += [{"quarter": q, "provider": p, "failure_rate_pct": round(float(x), 2)} for q, x in zip(QUARTERS, f)]
    pd.DataFrame(rows).to_csv(out / "provider_failures.csv", index=False, lineterminator="\n")

    agents = rng.integers(60_000, 420_000, len(ZONES))
    pd.DataFrame({"zone": ZONES, "active_agents": agents}).to_csv(out / "agents_by_zone.csv", index=False, lineterminator="\n")

    fr = 38 + 1.8 * np.arange(n) + rng.normal(0, 2.5, n)
    fr[13:] -= np.linspace(6, 14, n - 13)        # after a (fictional) 2024Q2 verification rule
    pd.DataFrame({"quarter": QUARTERS, "reports_per_million": np.round(fr, 1)}).to_csv(
        out / "fraud_reports.csv", index=False, lineterminator="\n")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", required=True)
    ap.add_argument("--seed", type=int, default=2026)
    a = ap.parse_args(argv)
    write(Path(a.out), a.seed)
    print(f"wrote 4 files to {a.out}")


if __name__ == "__main__":
    main()
