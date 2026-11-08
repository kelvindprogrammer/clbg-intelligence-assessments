"""CLI: python -m settlement <data_dir> --out <dir>

<data_dir> must contain transactions.csv, agents.csv and switch_control_totals.csv.
Writes settlement.csv and reconciliation.csv. Provided plumbing.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import (RECONCILE_COLUMNS, SETTLEMENT_COLUMNS, daily_settlement, load_agents, load_control_totals,
               load_transactions, reconcile_with_switch)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="settlement")
    ap.add_argument("data_dir")
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)
    d, out = Path(args.data_dir), Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    tx = load_transactions(d / "transactions.csv")
    agents = load_agents(d / "agents.csv")
    settlement = daily_settlement(tx, agents)
    recon = reconcile_with_switch(settlement, load_control_totals(d / "switch_control_totals.csv"))
    if list(settlement.columns) != SETTLEMENT_COLUMNS or list(recon.columns) != RECONCILE_COLUMNS:
        print("error: unexpected columns", file=sys.stderr)
        return 2
    settlement.to_csv(out / "settlement.csv", index=False, lineterminator="\n", float_format="%.2f")
    recon.to_csv(out / "reconciliation.csv", index=False, lineterminator="\n", float_format="%.2f")
    bad = int((~recon["matches"]).sum())
    print(f"wrote {len(settlement)} agent-days; {bad} of {len(recon)} business days do not match the switch")
    return 0


if __name__ == "__main__":
    sys.exit(main())
