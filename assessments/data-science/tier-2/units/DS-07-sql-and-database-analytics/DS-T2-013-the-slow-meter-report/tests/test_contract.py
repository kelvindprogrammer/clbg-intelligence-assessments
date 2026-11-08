"""Contract tests: pass on the unmodified starter."""
import sqlite3

import pytest

from conftest import BASELINE, DB, SUB, sha256

pytestmark = pytest.mark.contract
EXPECTED_SHA256 = "eaca47ff4d4824ccb14507aa821aa9507a40cc9276b579d3859ff54125b1a385"


def test_database_unmodified():
    assert sha256(DB) == EXPECTED_SHA256, "vends.db was modified; restore the original"


def test_schema_and_size():
    con = sqlite3.connect(DB)
    assert {r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table'")} == {"feeders", "meters", "vends"}
    assert con.execute("SELECT COUNT(*) FROM vends").fetchone()[0] == 3000


def test_baseline_and_member_files_present():
    for i in range(1, 6):
        assert (BASELINE / f"b{i}.sql").is_file()
        assert (SUB / "queries" / f"s{i}.sql").is_file()
    assert (SUB / "indexes.sql").is_file()
