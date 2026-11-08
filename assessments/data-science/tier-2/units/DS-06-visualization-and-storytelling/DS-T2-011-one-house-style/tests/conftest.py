"""Locate the package under test.

Search order:
  1. $CLBG_SUBMISSION_DIR (used by assessors to point at a submission or a reference)
  2. the repository root (your submission layout: housestyle/ at the top level)
  3. starter/ (the layout inside the CLBG assessments repository)
SUBMISSION is the folder that was found; baselines are read from SUBMISSION/baselines/.
"""
import os
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import pytest  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
CANDIDATES = [os.environ.get("CLBG_SUBMISSION_DIR"), str(ROOT), str(ROOT / "starter")]
SUBMISSION = None
for cand in CANDIDATES:
    if cand and (Path(cand) / "housestyle" / "__init__.py").is_file():
        sys.path.insert(0, cand)
        SUBMISSION = Path(cand)
        break

DATA = ROOT / "resources" / "data"


def pytest_configure(config):
    config.addinivalue_line("markers", "contract: scaffold and data-contract checks that must pass on the unmodified starter")


@pytest.fixture(autouse=True)
def _close_figures():
    yield
    import matplotlib.pyplot as plt
    plt.close("all")
