"""CLI (provided): python -m feedguard <inbox_dir> --out <dir> [--contract contract/contract.yaml]"""
from __future__ import annotations

import argparse
import sys

from . import process_inbox


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="feedguard")
    ap.add_argument("inbox")
    ap.add_argument("--out", required=True)
    ap.add_argument("--contract", default=None)
    a = ap.parse_args(argv)
    ledger = process_inbox(a.inbox, a.out, a.contract)
    print(ledger.to_string(index=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
