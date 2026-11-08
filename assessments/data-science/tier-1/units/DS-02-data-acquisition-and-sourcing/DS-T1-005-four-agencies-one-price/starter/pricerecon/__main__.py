"""R10: python -m pricerecon DATA_DIR --reference REF_DIR --out OUT_DIR"""
from __future__ import annotations

import argparse
import sys


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="pricerecon")
    ap.add_argument("data_dir")
    ap.add_argument("--reference", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)  # noqa: F841 - the parser is provided; the behaviour is yours
    raise NotImplementedError("R10: write canonical.csv, reconciled.csv, discrepancies.csv and stale_runs.csv")


if __name__ == "__main__":
    sys.exit(main())
