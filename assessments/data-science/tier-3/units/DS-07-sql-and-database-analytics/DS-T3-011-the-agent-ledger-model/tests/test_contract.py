"""Contract tests: pass on the unmodified starter."""
import hashlib
import inspect

import duckdb
import pytest

from conftest import DATA, load_raw

pytestmark = pytest.mark.contract
SHA = {"agent_history.csv": "eba6e48961cbdde07a8193d75749aae34af6cd007bd91a482a943234e1dfde91", "txn_events.csv": "c2d3763d7e63595e2b6e59bf7351633753a9f5827311cf6b3ef178888f412051", "fx_rates.csv": "f44d5e5d5aeb288a0684562e929713651f2f2f6038c7fb7eeededc9ddeaf04f2"}


def test_raw_files_unmodified():
    for name, sha in SHA.items():
        assert hashlib.sha256((DATA / name).read_bytes()).hexdigest() == sha, f"{name} was modified"


def test_raw_tables_load():
    con = duckdb.connect()
    load_raw(con)
    assert con.execute("SELECT COUNT(DISTINCT txn_id) FROM raw_txn_events").fetchone()[0] == 1100
    assert con.execute("SELECT COUNT(DISTINCT agent_id) FROM raw_agent_history").fetchone()[0] == 40


def test_build_signature():
    import analytics_model
    assert list(inspect.signature(analytics_model.build).parameters) == ["con"]
