#!/usr/bin/env python3
"""Synthetic smart-meter (AMI) data generator for DS-T2-001 "Feeder Hours, Out of Core".

Simulates 30-minute interval energy readings for residential and commercial meters on
11 kV distribution feeders of a fictional distribution company. Each feeder carries a
service band (A-E) and has its own real supply pattern: daily load-shedding blocks, longer
faults on some days, and some feeders that systematically under-deliver their band.

It writes:
  readings/YYYY-MM-DD.csv  one file per day of RECEIPT: meter_id,interval_start,kwh
                           interval_start is local time (WAT, +01:00), ISO 8601
  meters.csv               meter_id,feeder_id,customer_class
  feeders.csv              feeder_id,disco,band

Realistic defects, all documented in the README:
  - missing readings (communication failures), including meters silent for whole days
  - zero readings while supplied (no load)
  - exact duplicate readings re-sent by the head-end, sometimes in the NEXT day's file
  - rows in each file are not sorted

Usage:
  python generate_meters.py --out DIR --seed 2026                          # small public sample
  python generate_meters.py --out DIR --seed 2026 --meters 2000 --days 90  # benchmark (~8.6M rows)
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

BAND_MIN = {"A": 20, "B": 16, "C": 12, "D": 8, "E": 4}


def build_static(rng: np.random.Generator, n_meters: int):
    n_feeders = max(4, n_meters // 40)
    bands = rng.choice(list("ABCDE"), size=n_feeders, p=[0.3, 0.25, 0.2, 0.15, 0.1])
    feeders = pd.DataFrame({
        "feeder_id": [f"FDR-{i + 1:03d}" for i in range(n_feeders)],
        "disco": rng.choice(["Northgrid", "Riverline", "Savanna Power"], size=n_feeders),
        "band": bands,
    })
    # each feeder's true mean supply hours: most near their band, some under-deliver
    under = rng.random(n_feeders) < 0.35
    target = np.array([BAND_MIN[b] for b in bands], dtype=float)
    feeders["_mean_hours"] = np.clip(np.where(under, target - rng.uniform(2, 6, n_feeders),
                                              target + rng.uniform(0.3, 3.0, n_feeders)), 2, 23.5)
    feeder_of = rng.integers(0, n_feeders, size=n_meters)
    meters = pd.DataFrame({
        "meter_id": [f"M{100000 + i * 7 + int(rng.integers(0, 7))}" for i in range(n_meters)],
        "feeder_id": feeders["feeder_id"].to_numpy()[feeder_of],
        "customer_class": rng.choice(["R2", "C1", "R1"], size=n_meters, p=[0.75, 0.2, 0.05]),
    })
    return feeders, meters, feeder_of


def write(out: Path, seed: int, n_meters: int = 60, n_days: int = 7, start: str = "2026-07-01") -> None:
    rng = np.random.default_rng(seed)
    out.mkdir(parents=True, exist_ok=True)
    (out / "readings").mkdir(exist_ok=True)
    feeders, meters, feeder_of = build_static(rng, n_meters)
    meters.to_csv(out / "meters.csv", index=False, lineterminator="\n")
    feeders.drop(columns="_mean_hours").to_csv(out / "feeders.csv", index=False, lineterminator="\n")
    n_feeders = len(feeders)
    mean_hours = feeders["_mean_hours"].to_numpy()
    base_load = rng.gamma(2.0, 0.12, n_meters) * np.where(meters["customer_class"] == "C1", 3.0, 1.0)
    dead_prob = rng.uniform(0.0, 0.04, n_meters)
    days = pd.date_range(start, periods=n_days, freq="D")
    slot_hour = np.arange(48) / 2.0
    profile = 0.6 + 0.5 * np.exp(-((slot_hour - 20) ** 2) / 8) + 0.3 * np.exp(-((slot_hour - 7) ** 2) / 4)
    carry: pd.DataFrame | None = None
    for d_i, day in enumerate(days):
        # supply mask per feeder: hours off arranged as 1-3 blocks
        supplied = np.ones((n_feeders, 48), dtype=bool)
        for f in range(n_feeders):
            hours = np.clip(rng.normal(mean_hours[f], 1.5), 0, 24)
            if rng.random() < 0.05:
                hours = rng.uniform(0, 6)                       # a long fault
            off = int(round((24 - hours) * 2))
            blocks = int(rng.integers(1, 4))
            cuts = np.sort(rng.choice(np.arange(1, max(off, 1) + 1), size=min(blocks - 1, max(off - 1, 0)), replace=False)) if off > 1 else []
            lengths = np.diff(np.r_[0, cuts, off]).astype(int)
            for L in lengths:
                if L <= 0:
                    continue
                s = int(rng.integers(0, 48 - L + 1))
                supplied[f, s:s + L] = False
        sup = supplied[feeder_of]                                  # meters x 48
        load = base_load[:, None] * profile[None, :] * rng.lognormal(0, 0.35, (n_meters, 48)) / 2
        kwh = np.where(sup, np.round(load, 3), 0.0)
        kwh[sup & (rng.random((n_meters, 48)) < 0.04)] = 0.0       # no load while supplied
        present = rng.random((n_meters, 48)) >= 0.03
        present &= ~(rng.random(n_meters) < dead_prob)[:, None]   # meter silent all day
        mi, si = np.nonzero(present)
        ts = (day + pd.to_timedelta(si * 30, unit="min")).strftime("%Y-%m-%dT%H:%M:%S+01:00")
        df = pd.DataFrame({"meter_id": meters["meter_id"].to_numpy()[mi], "interval_start": ts,
                           "kwh": kwh[mi, si]})
        dup = rng.random(len(df)) < 0.01
        late = dup & (rng.random(len(df)) < 0.4) & (d_i < n_days - 1)
        same_day = df[dup & ~late]
        next_day = df[late]
        parts = [df, same_day] + ([carry] if carry is not None else [])
        out_df = pd.concat(parts, ignore_index=True)
        out_df = out_df.iloc[rng.permutation(len(out_df))]
        out_df.to_csv(out / "readings" / f"{day:%Y-%m-%d}.csv", index=False, float_format="%.3f", lineterminator="\n")
        carry = next_day


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--seed", type=int, default=2026)
    ap.add_argument("--meters", type=int, default=60)
    ap.add_argument("--days", type=int, default=7)
    a = ap.parse_args()
    write(Path(a.out), a.seed, a.meters, a.days)


if __name__ == "__main__":
    main()
