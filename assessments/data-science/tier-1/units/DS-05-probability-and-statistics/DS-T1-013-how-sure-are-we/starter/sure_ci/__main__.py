"""CLI (requirement R8): python -m sure_ci <agent_survey.csv> --out <dir> [--reps N] [--seed S]."""
from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from . import analyse_survey, run_study


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="sure_ci")
    ap.add_argument("survey")
    ap.add_argument("--out", required=True)
    ap.add_argument("--reps", type=int, default=1000)
    ap.add_argument("--B", type=int, default=1000)
    ap.add_argument("--seed", type=int, default=2026)
    args = ap.parse_args(argv)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    survey = pd.read_csv(args.survey)
    analyse_survey(survey, seed=args.seed).to_csv(out / "survey_intervals.csv", index=False, float_format="%.6f")
    run_study(reps=args.reps, B=args.B, seed=args.seed).to_csv(out / "coverage_study.csv", index=False, float_format="%.6f")
    print(f"wrote {out / 'survey_intervals.csv'} and {out / 'coverage_study.csv'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
