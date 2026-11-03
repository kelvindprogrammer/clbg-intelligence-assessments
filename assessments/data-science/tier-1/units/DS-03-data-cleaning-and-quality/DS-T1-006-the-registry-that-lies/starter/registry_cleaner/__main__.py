"""CLI entry point (R10): python -m registry_cleaner <input.csv> --out <dir>

Provided plumbing. The work happens in clean_registry().
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .pipeline import ISSUE_COLUMNS, OUTPUT_COLUMNS, clean_registry, load_export


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="registry_cleaner")
    ap.add_argument("input")
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    result = clean_registry(load_export(args.input))
    if list(result.clean.columns) != OUTPUT_COLUMNS or list(result.issues.columns) != ISSUE_COLUMNS:
        print("error: clean_registry returned unexpected columns", file=sys.stderr)
        return 2
    result.clean.to_csv(out / "clean_registry.csv", index=False, lineterminator="\n")
    result.issues.to_csv(out / "issues.csv", index=False, lineterminator="\n")
    print(f"wrote {len(result.clean)} students and {len(result.issues)} issues to {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
