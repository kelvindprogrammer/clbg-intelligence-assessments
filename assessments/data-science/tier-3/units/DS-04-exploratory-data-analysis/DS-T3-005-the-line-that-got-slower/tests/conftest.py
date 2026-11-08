"""Locate the package under test: $CLBG_SUBMISSION_DIR, repo root, then starter/."""
import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
for cand in [os.environ.get("CLBG_SUBMISSION_DIR"), str(ROOT), str(ROOT / "starter")]:
    if cand and (Path(cand) / "eda_lab" / "__init__.py").is_file():
        sys.path.insert(0, cand)
        break

DATA = ROOT / "resources" / "data" / "route_day.csv"


def pytest_configure(config):
    config.addinivalue_line("markers", "contract: scaffold and data-contract checks that must pass on the unmodified starter")


@pytest.fixture(scope="session")
def df():
    import pandas as pd
    out = pd.read_csv(DATA)
    out["date"] = pd.to_datetime(out["date"])
    return out
