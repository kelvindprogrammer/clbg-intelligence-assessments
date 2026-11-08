"""Contract tests: these pass on the unmodified starter."""
import hashlib
import inspect
import subprocess
import sys
from pathlib import Path

import pandas as pd
import pytest

from conftest import EXPECTED, GENERATOR, SAMPLE

pytestmark = pytest.mark.contract

SAMPLE_TREE_SHA256 = "0a4611360813b2f027343de6e5602436aa88260a0a171f428c68bd9004a5c376"


def tree_hash(d: Path) -> str:
    h = hashlib.sha256()
    for f in sorted(p for p in d.rglob("*") if p.is_file()):
        h.update(f.relative_to(d).as_posix().encode())
        h.update(f.read_bytes())
    return h.hexdigest()


def test_sample_is_unmodified():
    assert tree_hash(SAMPLE) == SAMPLE_TREE_SHA256, "resources/sample has been modified; regenerate it (README E)"


def test_generator_reproduces_sample(tmp_path):
    subprocess.run([sys.executable, str(GENERATOR), "--out", str(tmp_path), "--seed", "2026"], check=True,
                   capture_output=True)
    assert tree_hash(tmp_path) == SAMPLE_TREE_SHA256


def test_expected_outputs_follow_contract():
    import meterflow as mf
    fd = pd.read_csv(EXPECTED / "feeder_daily.csv")
    assert list(fd.columns) == mf.FEEDER_DAILY_COLUMNS
    c = pd.read_csv(EXPECTED / "compliance.csv")
    assert list(c.columns) == mf.COMPLIANCE_COLUMNS


def test_api_contract():
    import meterflow as mf
    assert mf.ENGINES == ("pandas_inmemory", "pandas_chunked", "polars", "duckdb")
    sig = inspect.signature(mf.compute_feeder_daily)
    assert list(sig.parameters) == ["data_dir", "engine", "memory_limit_mb"]
    assert sig.parameters["memory_limit_mb"].kind is inspect.Parameter.KEYWORD_ONLY
    assert list(inspect.signature(mf.compute_compliance).parameters) == ["feeder_daily", "feeders"]
    assert mf.BAND_MIN_HOURS == {"A": 20, "B": 16, "C": 12, "D": 8, "E": 4}
