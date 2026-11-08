"""R10: command-line interface.

python -m wbclient fetch INDICATOR --countries NGA,GHA [--date 2000:2024] --out data.csv
       --cache .wbcache --provenance provenance.jsonl [--per-page 1000] [--offline] [--base-url URL]
"""
from __future__ import annotations

import argparse
import sys

from .urls import DEFAULT_BASE


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="wbclient")
    sub = ap.add_subparsers(dest="cmd", required=True)
    f = sub.add_parser("fetch")
    f.add_argument("indicator")
    f.add_argument("--countries", required=True)
    f.add_argument("--date")
    f.add_argument("--out", required=True)
    f.add_argument("--cache", required=True)
    f.add_argument("--provenance", required=True)
    f.add_argument("--per-page", type=int, default=1000)
    f.add_argument("--offline", action="store_true")
    f.add_argument("--base-url", default=DEFAULT_BASE)
    args = ap.parse_args(argv)  # noqa: F841 - the parser is provided; the behaviour is yours
    raise NotImplementedError("R10: wire the client, cache, provenance log and to_frame together")


if __name__ == "__main__":
    sys.exit(main())
