"""Locate the package under test.

Search order:
  1. $CLBG_SUBMISSION_DIR (used by assessors to point at a submission or a reference)
  2. the repository root (your submission layout: notebook_audit/ at the top level)
  3. starter/ (the layout inside the CLBG assessments repository)
"""
import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
CANDIDATES = [os.environ.get("CLBG_SUBMISSION_DIR"), str(ROOT), str(ROOT / "starter")]
for cand in CANDIDATES:
    if cand and (Path(cand) / "notebook_audit" / "__init__.py").is_file():
        sys.path.insert(0, cand)
        break

DATA_DIR = ROOT / "resources" / "data"
AUDIT_CANDIDATES = [Path(c) / "outputs" / "audit.json" for c in CANDIDATES if c]


def pytest_configure(config):
    config.addinivalue_line("markers", "contract: scaffold and data-contract checks that must pass on the unmodified starter")


@pytest.fixture(scope="session")
def data():
    from notebook_audit import load_all
    return load_all(DATA_DIR)
