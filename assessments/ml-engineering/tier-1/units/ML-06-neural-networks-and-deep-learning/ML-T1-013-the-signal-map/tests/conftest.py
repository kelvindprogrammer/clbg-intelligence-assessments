import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
for cand in [os.environ.get("CLBG_SUBMISSION_DIR"), str(ROOT), str(ROOT / "starter")]:
    if cand and (Path(cand) / "tinynet" / "__init__.py").is_file():
        sys.path.insert(0, cand)
        break

DATA = ROOT / "resources" / "data" / "coverage.csv"


def pytest_configure(config):
    config.addinivalue_line("markers", "contract: scaffold and data-contract checks that must pass on the unmodified starter")


@pytest.fixture(scope="session")
def coverage():
    import pandas as pd
    d = pd.read_csv(DATA)
    tr, te = d[d.split == "train"], d[d.split == "test"]
    f = lambda x: x[["x_km", "y_km"]].to_numpy() / 10.0
    return f(tr), tr.covered_4g.to_numpy(), f(te), te.covered_4g.to_numpy()
