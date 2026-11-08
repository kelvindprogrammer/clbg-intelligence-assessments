"""Helpers. Member files are searched in $CLBG_SUBMISSION_DIR, then the repo root, then starter/.

Work is measured deterministically: SQLite's progress handler fires every 100 virtual-machine
instructions, and we count the calls ("steps"). Unlike wall-clock time this does not depend on the laptop.
"""
import hashlib
import os
import re
import sqlite3
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "resources" / "data" / "vends.db"
BASELINE = ROOT / "resources" / "baseline"
CANDS = [os.environ.get("CLBG_SUBMISSION_DIR"), str(ROOT), str(ROOT / "starter")]
SUB = next((Path(c) for c in CANDS if c and (Path(c) / "queries").is_dir()), ROOT / "starter")
NAMES = ["s1", "s2", "s3", "s4", "s5"]


def sha256(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def strip_comments(text):
    return "\n".join(l for l in text.splitlines() if not l.strip().startswith("--")).strip()


def indexes_sql(sub=None):
    p = Path(sub or SUB) / "indexes.sql"
    return strip_comments(p.read_text(encoding="utf-8")) if p.is_file() else ""


def connect(db=DB, indexes=""):
    """In-memory copy of the database (the original is never touched), with optional member indexes."""
    src = sqlite3.connect(f"file:{Path(db).as_posix()}?mode=ro", uri=True)
    con = sqlite3.connect(":memory:")
    src.backup(con)
    src.close()
    if indexes:
        con.executescript(indexes)
    return con


def run(con, sql):
    """Return (rows, steps)."""
    n = [0]

    def tick():
        n[0] += 1
        return 0

    con.set_progress_handler(tick, 100)
    try:
        rows = con.execute(sql).fetchall()
    finally:
        con.set_progress_handler(None, 0)
    return [tuple(round(v, 2) if isinstance(v, float) else v for v in r) for r in rows], n[0]


def member_sql(name, sub=None):
    body = strip_comments((Path(sub or SUB) / "queries" / f"{name}.sql").read_text(encoding="utf-8"))
    if not body:
        raise AssertionError(f"{name}.sql contains no SQL yet")
    return body


def pytest_configure(config):
    config.addinivalue_line("markers", "contract: scaffold and data-contract checks that must pass on the unmodified starter")
