"""CLI (requirement R9): python -m fuel_queue <station_log.csv> --out <dir> [--seed N]."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from . import load_log, recommend_pumps


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="fuel_queue")
    ap.add_argument("log")
    ap.add_argument("--out", required=True)
    ap.add_argument("--window", type=float, default=240.0, help="observation window in minutes")
    ap.add_argument("--target-wait", type=float, default=10.0)
    ap.add_argument("--max-prob", type=float, default=0.10)
    ap.add_argument("--seed", type=int, default=2026)
    args = ap.parse_args(argv)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    rec = recommend_pumps(load_log(args.log), window_min=args.window, target_wait=args.target_wait,
                          max_prob=args.max_prob, seed=args.seed)
    rec.table.to_csv(out / "pump_table.csv", index=False, float_format="%.6f")
    summary = {"c_recommended": rec.c_recommended, "c_mmc": rec.c_mmc, "lam": rec.lam,
               "mean_service": rec.mean_service, "cv_service": rec.cv_service,
               "target_wait": args.target_wait, "max_prob": args.max_prob, "seed": args.seed}
    (out / "recommendation.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
