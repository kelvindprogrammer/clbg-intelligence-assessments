"""CLI entry point (R9): python -m yield_harmonizer <survey.csv> --out <dir>

Provided plumbing. The work happens in harmonise() and production_totals().
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .pipeline import ISSUE_COLUMNS, RECORD_COLUMNS, TOTALS_COLUMNS, harmonise, load_survey, production_totals


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="yield_harmonizer")
    ap.add_argument("input")
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    result = harmonise(load_survey(args.input))
    totals = production_totals(result.records)
    if (list(result.records.columns) != RECORD_COLUMNS or list(result.issues.columns) != ISSUE_COLUMNS
            or list(totals.columns) != TOTALS_COLUMNS):
        print("error: unexpected output columns", file=sys.stderr)
        return 2
    result.records.to_csv(out / "harmonised.csv", index=False, lineterminator="\n")
    result.issues.to_csv(out / "issues.csv", index=False, lineterminator="\n")
    totals.to_csv(out / "totals.csv", index=False, lineterminator="\n")
    print(f"wrote {len(result.records)} records, {len(result.issues)} issues and {len(totals)} total rows to {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
