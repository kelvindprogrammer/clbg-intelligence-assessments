"""Loader and fixtures. The package `analytics_model` is searched in $CLBG_SUBMISSION_DIR, the repo root, then starter/."""
import csv
import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "resources" / "data"
for cand in [os.environ.get("CLBG_SUBMISSION_DIR"), str(ROOT), str(ROOT / "starter")]:
    if cand and (Path(cand) / "analytics_model" / "__init__.py").is_file():
        sys.path.insert(0, cand)
        break

DDL = {
    "raw_agent_history": "agent_id INTEGER, effective_from DATE, tier VARCHAR, region VARCHAR, recorded_at TIMESTAMP",
    "raw_txn_events": "event_id VARCHAR, txn_id VARCHAR, version INTEGER, event_type VARCHAR, agent_id INTEGER, txn_ts TIMESTAMP, "
                      "amount DECIMAL(18,2), fee DECIMAL(18,2), currency VARCHAR, recorded_at TIMESTAMP",
    "raw_fx_rates": "rate_date DATE, currency VARCHAR, ngn_per_unit DECIMAL(18,4)",
}
FILES = {"raw_agent_history": "agent_history.csv", "raw_txn_events": "txn_events.csv", "raw_fx_rates": "fx_rates.csv"}


def load_raw(con, data_dir=DATA):
    for table, ddl in DDL.items():
        con.execute(f"CREATE OR REPLACE TABLE {table} ({ddl})")
        con.execute(f"INSERT INTO {table} SELECT * FROM read_csv('{Path(data_dir, FILES[table]).as_posix()}', header=true, columns="
                    + "{" + ", ".join(f"'{c.split()[0]}': '{c.split(None, 1)[1]}'" for c in ddl.split(", ")) + "})")


def pytest_configure(config):
    config.addinivalue_line("markers", "contract: scaffold and data-contract checks that must pass on the unmodified starter")
