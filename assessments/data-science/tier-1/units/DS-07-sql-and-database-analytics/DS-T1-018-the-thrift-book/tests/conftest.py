"""Helpers: run a member's query file against the thrift database (read-only).

Query folder search order: $CLBG_SUBMISSION_DIR/queries, <repo root>/queries, starter/queries.
"""
import hashlib
import os
import re
import sqlite3
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "resources" / "data" / "thrift.db"
QUERY_DIRS = [os.environ.get("CLBG_SUBMISSION_DIR"), str(ROOT), str(ROOT / "starter")]
QUERIES = next((Path(c) / "queries" for c in QUERY_DIRS if c and (Path(c) / "queries").is_dir()), ROOT / "starter" / "queries")
NAMES = [f"q{i:02d}" for i in range(1, 11)]


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def run_query(name, db=DB):
    """Return (column_names, rows) for queries/<name>.sql, opened read-only."""
    text = (QUERIES / f"{name}.sql").read_text(encoding="utf-8")
    body = "\n".join(l for l in text.splitlines() if not l.strip().startswith("--")).strip()
    if not body:
        raise AssertionError(f"{name}.sql contains no SQL yet")
    if body.rstrip(";").count(";"):
        raise AssertionError(f"{name}.sql must contain a single statement")
    con = sqlite3.connect(f"file:{Path(db).as_posix()}?mode=ro", uri=True)
    try:
        cur = con.execute(body)
        return [d[0] for d in cur.description], cur.fetchall()
    finally:
        con.close()


def norm(rows):
    return [tuple(round(v, 2) if isinstance(v, float) else v for v in r) for r in rows]


def pytest_configure(config):
    config.addinivalue_line("markers", "contract: scaffold and data-contract checks that must pass on the unmodified starter")
