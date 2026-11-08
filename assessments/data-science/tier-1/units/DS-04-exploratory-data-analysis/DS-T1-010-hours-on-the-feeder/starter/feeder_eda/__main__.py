"""CLI: python -m feeder_eda <data_dir> --out <dir> (R10)."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from . import build_answers, daily_supply, feeder_summary, load_all, parse_events


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="feeder_eda")
    ap.add_argument("data_dir")
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    events, feeders, coverage = load_all(a.data_dir)
    answers = build_answers(events, feeders, coverage)
    (out / "answers.json").write_text(json.dumps(answers, indent=2, sort_keys=True), encoding="utf-8")
    clean, _ = parse_events(events)
    daily = daily_supply(clean, feeders, coverage)
    daily.to_csv(out / "daily_supply.csv", index=False, lineterminator="\n")
    feeder_summary(daily, feeders).to_csv(out / "feeder_summary.csv", index=False, lineterminator="\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
