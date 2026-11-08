"""CLI: python -m paradox_ward <admissions.csv> --out <dir> (R9)."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from . import build_findings, load_admissions, rate_table


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="paradox_ward")
    ap.add_argument("input")
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    df = load_admissions(a.input)
    f = build_findings(df)
    (out / "findings.json").write_text(json.dumps(f, indent=2, sort_keys=True), encoding="utf-8")
    rate_table(df, ["hospital", f["primary_confounder"]]).to_csv(out / "stratified_rates.csv", index=False,
                                                                 lineterminator="\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
