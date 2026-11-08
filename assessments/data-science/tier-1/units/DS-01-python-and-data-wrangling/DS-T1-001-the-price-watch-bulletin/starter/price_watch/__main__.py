"""CLI (R10): python -m price_watch <bulletin.csv> --out <dir>

Provided plumbing. The work happens in the functions it calls.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import (PUBLISHED_COLUMNS, RECONCILE_COLUMNS, TIDY_COLUMNS, load_raw, month_on_month,
               published_averages, reconcile_averages, tidy_bulletin)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="price_watch")
    ap.add_argument("bulletin")
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    raw = load_raw(args.bulletin)
    tidy = tidy_bulletin(raw)
    published = published_averages(raw)
    recon = reconcile_averages(tidy, published)
    mom = month_on_month(tidy)
    if list(tidy.columns) != TIDY_COLUMNS or list(published.columns) != PUBLISHED_COLUMNS \
            or list(recon.columns) != RECONCILE_COLUMNS or list(mom.columns) != TIDY_COLUMNS + ["mom_pct"]:
        print("error: a function returned unexpected columns", file=sys.stderr)
        return 2
    mom.to_csv(out / "tidy_prices.csv", index=False, lineterminator="\n", float_format="%.6f")
    published.to_csv(out / "published_averages.csv", index=False, lineterminator="\n", float_format="%.2f")
    recon.to_csv(out / "reconciliation.csv", index=False, lineterminator="\n", float_format="%.6f")
    n_bad = int((recon["match"] == "neither").sum())
    print(f"wrote {len(tidy)} tidy rows, {len(published)} published averages ({n_bad} unexplained) to {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
