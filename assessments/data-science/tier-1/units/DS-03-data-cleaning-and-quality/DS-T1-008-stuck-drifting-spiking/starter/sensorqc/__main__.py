"""CLI entry point (R9): python -m sensorqc <readings.csv> --out <dir> [--config qc_config.json]

Provided plumbing. The work happens in run_qc() and hourly_means().
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .pipeline import (CLOCK_COLUMNS, GAP_COLUMNS, HOURLY_COLUMNS, READING_COLUMNS, hourly_means, load_config,
                       load_readings, run_qc)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="sensorqc")
    ap.add_argument("input")
    ap.add_argument("--out", required=True)
    ap.add_argument("--config", default=None)
    args = ap.parse_args(argv)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    cfg = load_config(args.config)
    res = run_qc(load_readings(args.input), cfg)
    hourly = hourly_means(res.readings, cfg["hourly_min_coverage"], cfg["expected_interval_s"])
    for df, cols, name in [(res.readings, READING_COLUMNS, "readings_qc.csv"), (res.gaps, GAP_COLUMNS, "gaps.csv"),
                           (res.clocks, CLOCK_COLUMNS, "clocks.csv"), (hourly, HOURLY_COLUMNS, "hourly.csv")]:
        if list(df.columns) != cols:
            print(f"error: {name} has unexpected columns", file=sys.stderr)
            return 2
        df.to_csv(out / name, index=False, lineterminator="\n")
    print(f"wrote {len(res.readings)} flagged readings, {len(res.gaps)} gaps and {len(hourly)} hourly rows to {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
