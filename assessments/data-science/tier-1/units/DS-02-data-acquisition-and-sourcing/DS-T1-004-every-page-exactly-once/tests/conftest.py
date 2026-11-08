"""Locate the package under test.

Search order:
  1. $CLBG_SUBMISSION_DIR (used by assessors to point at a submission or a reference)
  2. the repository root (your submission layout: wbclient/ at the top level)
  3. starter/ (the layout inside the CLBG assessments repository)
"""
import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
CANDIDATES = [os.environ.get("CLBG_SUBMISSION_DIR"), str(ROOT), str(ROOT / "starter")]
for cand in CANDIDATES:
    if cand and (Path(cand) / "wbclient" / "__init__.py").is_file():
        sys.path.insert(0, cand)
        break
sys.path.insert(0, str(Path(__file__).resolve().parent))

FIXTURES = ROOT / "resources" / "fixtures"
ELEC = FIXTURES / "EG.ELC.ACCS.ZS__ecowas__2000-2024.json"
ECOWAS = ["BEN", "BFA", "CPV", "CIV", "GMB", "GHA", "GIN", "GNB", "LBR", "MLI", "NER", "NGA", "SEN", "SLE", "TGO"]


def pytest_configure(config):
    config.addinivalue_line("markers", "contract: scaffold and data-contract checks that must pass on the unmodified starter")


@pytest.fixture
def fake_wb():
    from fakes import FakeWorldBank
    with FakeWorldBank({"EG.ELC.ACCS.ZS": ELEC}) as fake:
        yield fake
