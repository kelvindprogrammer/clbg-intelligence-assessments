"""feedguard: contract validation, quarantine and alerting for the DS-T2-006 partner feed.

Only process_inbox, its arguments and its outputs are fixed (the tests use them; see README
section D). How you represent the contract, structure the checks, keep history and raise
alerts is your design. Split the work into as many modules as you like.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

LEDGER_COLUMNS = ["business_date", "status", "n_rows", "n_accepted", "n_quarantined", "findings"]


def process_inbox(inbox, out, contract_path=None, agents_path=None, holidays_path=None) -> pd.DataFrame:
    """R1-R7: validate every delivery in `inbox` in business-date order and write the outputs to `out`.

    inbox:          a directory with one sub-directory per business date (YYYY-MM-DD), each holding
                    transactions.csv and manifest.json
    out:            output directory (see README D.2 for the required layout)
    contract_path:  your contract file; default contract/contract.yaml found from the package location
    agents_path:    default resources/reference/agents.csv
    holidays_path:  default resources/reference/public_holidays.csv

    Returns the ledger as a DataFrame with LEDGER_COLUMNS (also written to out/ledger.csv).
    """
    raise NotImplementedError("R1-R7: implement process_inbox")


__all__ = ["LEDGER_COLUMNS", "process_inbox"]
