"""Contract tests: pass on the unmodified starter."""
import sqlite3

import pytest

from conftest import DB, NAMES, QUERIES, ROOT, sha256

pytestmark = pytest.mark.contract
EXPECTED_SHA256 = "0047b474418b1b951b0cd95f17405b06d856c76b77d4856a1efe42eb38a132db"


def test_database_is_unmodified():
    assert sha256(DB) == EXPECTED_SHA256, "thrift.db was modified; restore the original file"


def test_schema_tables():
    con = sqlite3.connect(DB)
    tables = {r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    assert tables == {"groups", "members", "contributions", "loans", "repayments"}
    assert con.execute("SELECT COUNT(*) FROM members").fetchone()[0] == 110


def test_query_files_exist():
    for n in NAMES:
        assert (QUERIES / f"{n}.sql").is_file(), n


def test_expected_answers_file_present():
    assert (ROOT / "tests" / "expected_public.json").is_file()
