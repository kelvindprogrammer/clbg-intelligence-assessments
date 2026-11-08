"""Locate the submission under test.

Search order:
  1. $CLBG_SUBMISSION_DIR (used by assessors to point at a submission or a reference)
  2. the repository root (your submission layout: model/, usability/, specs/, explorable/ at the top level)
  3. starter/ (the layout inside the CLBG assessments repository)
"""
import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
CANDIDATES = [os.environ.get("CLBG_SUBMISSION_DIR"), str(ROOT), str(ROOT / "starter")]
SUBMISSION = None
for cand in CANDIDATES:
    if cand and (Path(cand) / "model" / "tariff_model.py").is_file():
        sys.path.insert(0, cand)
        SUBMISSION = Path(cand)
        break

SCHEMA = ROOT / "resources" / "view_spec.schema.json"


def pytest_configure(config):
    config.addinivalue_line("markers", "contract: scaffold and data-contract checks that must pass on the unmodified starter")


@pytest.fixture(scope="session")
def sub():
    return SUBMISSION
