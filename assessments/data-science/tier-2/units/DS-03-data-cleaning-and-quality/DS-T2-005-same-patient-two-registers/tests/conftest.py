"""Locate the package under test.

Search order:
  1. $CLBG_SUBMISSION_DIR (used by assessors to point at a submission or a reference)
  2. the repository root (your submission layout: linkage/ at the top level)
  3. starter/ (the layout inside the CLBG assessments repository)
"""
import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
CANDIDATES = [os.environ.get("CLBG_SUBMISSION_DIR"), str(ROOT), str(ROOT / "starter")]
for cand in CANDIDATES:
    if cand and (Path(cand) / "linkage" / "__init__.py").is_file():
        sys.path.insert(0, cand)
        break

DATA = ROOT / "resources" / "data"


def pytest_configure(config):
    config.addinivalue_line("markers", "contract: scaffold and data-contract checks that must pass on the unmodified starter")


@pytest.fixture(scope="session")
def registers():
    from linkage import load_clerical_sample, load_register
    return (load_register(DATA / "phc_register.csv"), load_register(DATA / "gh_register.csv"),
            load_clerical_sample(DATA / "clerical_sample.csv"))
