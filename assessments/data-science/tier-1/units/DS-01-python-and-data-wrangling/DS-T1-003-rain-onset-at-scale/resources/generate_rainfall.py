#!/usr/bin/env python3
"""Synthetic daily rainfall generator for DS-T1-003 "Rain Onset at Scale".

Simulates daily rainfall at fictional gauge stations across a south-to-north gradient
(long wet season in the south, short wet season in the north) with a two-state Markov
chain for wet/dry days and gamma-distributed amounts. It then damages the record the way
real gauge networks are damaged:
  - isolated missing readings (rain_mm left blank)
  - whole days with no row at all (the logger did not report)
  - a block of several weeks missing at some stations
  - some stations that start part-way through their first year
  - rows written in a partly shuffled order

It writes:
  rainfall.csv  station_id,date,rain_mm   (blank rain_mm = missing reading)
  stations.csv  station_id,latitude,longitude,zone

This generator is public: it does not reveal any answer, because the answers are
defined by the legacy functions in rainfall/legacy.py.

Usage:
  python generate_rainfall.py --out DIR --seed 2026                          # the committed sample
  python generate_rainfall.py --out DIR --seed 2026 --stations 400 --years 30  # the benchmark set
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd


def build(seed: int, n_stations: int = 24, n_years: int = 6, last_year: int = 2024):
    rng = np.random.default_rng(seed)
    first_year = last_year - n_years + 1
    days = pd.date_range(f"{first_year}-01-01", f"{last_year}-12-31", freq="D")
    doy = days.day_of_year.to_numpy()
    frames, meta = [], []
    for i in range(n_stations):
        sid = f"ST{i + 1:03d}"
        lat = float(rng.uniform(4.5, 13.5))
        lon = float(rng.uniform(3.0, 13.5))
        zone = "Sahel" if lat > 11.5 else "Sudan savanna" if lat > 9.5 else "Guinea savanna" if lat > 7.5 else "Forest"
        meta.append((sid, round(lat, 3), round(lon, 3), zone))
        # season centre and half-width shrink with latitude
        centre = 205 + (lat - 4.5) * 2.0 + rng.normal(0, 4)
        half = 115 - (lat - 4.5) * 7.5
        year_shift = rng.normal(0, 9, n_years)        # onset varies from year to year
        yidx = (days.year - first_year).to_numpy()
        season = np.clip(1 - np.abs(doy - centre - year_shift[yidx]) / half, 0, 1) ** 0.8
        p_wet_after_dry = 0.03 + 0.42 * season
        p_wet_after_wet = 0.05 + 0.60 * season
        u = rng.random(len(days))
        wet = np.zeros(len(days), dtype=bool)
        for t in range(1, len(days)):
            wet[t] = u[t] < (p_wet_after_wet[t] if wet[t - 1] else p_wet_after_dry[t])
        amount = rng.gamma(0.75, 10.0 + 12.0 * season + (13.5 - lat) * 1.5)
        rain = np.where(wet, np.round(amount + 0.1, 1), np.where(rng.random(len(days)) < 0.15, 0.1 * rng.integers(0, 9, len(days)), 0.0))
        rain = np.round(rain, 1)
        df = pd.DataFrame({"station_id": sid, "date": days, "rain_mm": rain})
        # damage
        df.loc[rng.random(len(df)) < 0.02, "rain_mm"] = np.nan
        if rng.random() < 0.3:                          # a multi-week outage
            start = int(rng.integers(60, len(df) - 60))
            df.loc[start:start + int(rng.integers(14, 45)), "rain_mm"] = np.nan
        keep = rng.random(len(df)) >= 0.01               # days with no row at all
        if rng.random() < 0.25:                          # station commissioned mid-year
            keep &= df["date"] >= pd.Timestamp(f"{first_year}-{int(rng.integers(2, 9)):02d}-15")
        frames.append(df[keep])
    out = pd.concat(frames, ignore_index=True)
    # partly shuffled write order: blocks of rows arrive out of order
    block = np.arange(len(out)) // 500
    order = rng.permutation(block.max() + 1)
    out = out.iloc[np.argsort(order[block], kind="stable")].reset_index(drop=True)
    stations = pd.DataFrame(meta, columns=["station_id", "latitude", "longitude", "zone"])
    return out, stations


def write(out: Path, seed: int, n_stations: int = 24, n_years: int = 6) -> None:
    out.mkdir(parents=True, exist_ok=True)
    df, stations = build(seed, n_stations, n_years)
    df.to_csv(out / "rainfall.csv", index=False, date_format="%Y-%m-%d", float_format="%.1f", lineterminator="\n")
    stations.to_csv(out / "stations.csv", index=False, lineterminator="\n")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--seed", type=int, default=2026)
    ap.add_argument("--stations", type=int, default=24)
    ap.add_argument("--years", type=int, default=6)
    a = ap.parse_args()
    write(Path(a.out), a.seed, a.stations, a.years)


if __name__ == "__main__":
    main()
