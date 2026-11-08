"""Locate the package under test: $CLBG_SUBMISSION_DIR, repo root, then starter/."""
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for cand in [os.environ.get("CLBG_SUBMISSION_DIR"), str(ROOT), str(ROOT / "starter")]:
    if cand and (Path(cand) / "perception_lab" / "__init__.py").is_file():
        sys.path.insert(0, cand)
        break


def pytest_configure(config):
    config.addinivalue_line("markers", "contract: scaffold and data-contract checks that must pass on the unmodified starter")
