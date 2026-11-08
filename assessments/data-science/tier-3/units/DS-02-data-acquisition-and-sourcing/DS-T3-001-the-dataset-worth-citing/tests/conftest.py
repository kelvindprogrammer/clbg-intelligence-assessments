"""Locate the package under test.

Search order: $CLBG_SUBMISSION_DIR, the repository root (your layout), then starter/.
"""
import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
for cand in [os.environ.get("CLBG_SUBMISSION_DIR"), str(ROOT), str(ROOT / "starter")]:
    if cand and (Path(cand) / "provenance_audit" / "__init__.py").is_file():
        sys.path.insert(0, cand)
        break

CATALOGUE = ROOT / "resources" / "catalogue"


def pytest_configure(config):
    config.addinivalue_line("markers", "contract: scaffold and data-contract checks that must pass on the unmodified starter")


@pytest.fixture(scope="session")
def cat():
    from provenance_audit import load_catalogue
    return load_catalogue(CATALOGUE)
