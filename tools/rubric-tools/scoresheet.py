#!/usr/bin/env python3
"""Generate an assessor score sheet (Markdown or CSV) from an assessment's rubric.md,
or compute a total and outcome band from a completed CSV.

Usage:
  python tools/rubric-tools/scoresheet.py DS-T1-001                 # print a Markdown score sheet
  python tools/rubric-tools/scoresheet.py DS-T1-001 --csv > s.csv   # a blank CSV for assessors
  python tools/rubric-tools/scoresheet.py --score s.csv             # total plus the provisional band

The band printed here is PROVISIONAL. The final outcome also depends on the
technical defence and the gating conditions in docs/placement-framework.md.
"""
from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))
import clbgtools as ct  # noqa: E402

BANDS = [
    (80, "Meets requirements (provisional)"),
    (65, "Meets requirements with minor deficiencies (provisional)"),
    (50, "Requires revision"),
    (0, "Does not yet demonstrate competence"),
]


def find(aid: str) -> ct.Assessment:
    for a in ct.load_assessments():
        if a.id == aid:
            return a
    sys.exit(f"assessment {aid} not found")


def band(total: float) -> str:
    for cut, label in BANDS:
        if total >= cut:
            return label
    return BANDS[-1][1]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("id", nargs="?")
    ap.add_argument("--csv", action="store_true")
    ap.add_argument("--score")
    args = ap.parse_args(argv)
    if args.score:
        rows = list(csv.DictReader(open(args.score, encoding="utf-8")))
        total = sum(float(r["awarded"] or 0) for r in rows)
        maxp = sum(float(r["max"]) for r in rows)
        over = [r["dimension"] for r in rows if float(r["awarded"] or 0) > float(r["max"])]
        if over:
            sys.exit(f"awarded exceeds max for: {', '.join(over)}")
        print(f"Total: {total:g}/{maxp:g}\nProvisional band: {band(100 * total / maxp)}")
        print("Remember to apply the gating conditions (integrity, defence, reproducibility) from docs/placement-framework.md.")
        return 0
    if not args.id:
        ap.error("an assessment id is required")
    a = find(args.id)
    rows = ct.parse_rubric_weights((a.path / "rubric.md").read_text(encoding="utf-8"))
    if args.csv:
        w = csv.writer(sys.stdout)
        w.writerow(["assessment", "dimension", "max", "awarded", "evidence_and_comments"])
        for dim, pts in rows:
            w.writerow([a.id, dim, pts, "", ""])
        return 0
    print(f"# Score sheet: {a.id}: {a.meta['title']}\n")
    print("Assessor: ________  Member: ________  Date: ________  Submission commit: ________\n")
    print("| # | Dimension | Max | Awarded | Evidence / comments |\n|---|---|---|---|---|")
    for i, (dim, pts) in enumerate(rows, 1):
        print(f"| {i} | {dim} | {pts} | | |")
    print(f"| | **Total** | **{sum(p for _, p in rows)}** | | |\n")
    print("Gates (all must be YES for a passing outcome): integrity declaration present ☐ · results reproduced ☐ · defence satisfactory ☐")
    return 0


if __name__ == "__main__":
    sys.exit(main())
