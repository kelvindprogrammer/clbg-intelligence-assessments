"""Locate the package under test, and provide shared helpers.

Search order:
  1. $CLBG_SUBMISSION_DIR (used by assessors to point at a submission or a reference)
  2. the repository root (your submission layout: rainfall/ at the top level)
  3. starter/ (the layout inside the CLBG assessments repository)
"""
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
CANDIDATES = [os.environ.get("CLBG_SUBMISSION_DIR"), str(ROOT), str(ROOT / "starter")]
for cand in CANDIDATES:
    if cand and (Path(cand) / "rainfall" / "__init__.py").is_file():
        sys.path.insert(0, cand)
        break

DATA = ROOT / "resources" / "data"
GENERATOR = ROOT / "resources" / "generate_rainfall.py"


def pytest_configure(config):
    config.addinivalue_line("markers", "contract: scaffold and data-contract checks that must pass on the unmodified starter")


@pytest.fixture(scope="session")
def sample():
    from rainfall import load_rainfall
    return load_rainfall(DATA / "rainfall.csv")


def assert_equivalent(legacy: pd.DataFrame, fast: pd.DataFrame) -> None:
    """The equivalence rule from README section D.1."""
    assert list(fast.columns) == list(legacy.columns), "column names and order must match"
    assert len(fast) == len(legacy), "row count must match"
    for col in legacy.columns:
        assert fast[col].dtype == legacy[col].dtype, f"{col}: dtype {fast[col].dtype} != {legacy[col].dtype}"
    pd.testing.assert_frame_equal(fast.reset_index(drop=True), legacy.reset_index(drop=True),
                                  check_exact=False, rtol=0, atol=1e-9)


def random_case(seed: int, n_stations: int = 3) -> pd.DataFrame:
    """A small, deliberately awkward rainfall record: leap years, gaps, NaNs, shuffled rows,
    stations that start or stop mid-year, and non-consecutive years."""
    rng = np.random.default_rng(seed)
    frames = []
    for s in range(n_stations):
        years = sorted(rng.choice(np.arange(1999, 2006), size=int(rng.integers(1, 4)), replace=False))
        for y in years:
            days = pd.date_range(f"{y}-01-01", f"{y}-12-31", freq="D")
            if rng.random() < 0.3:
                days = days[int(rng.integers(0, 200)):]
            if rng.random() < 0.3:
                days = days[: int(rng.integers(150, len(days) + 1))]
            wet = rng.random(len(days)) < rng.uniform(0.15, 0.6)
            rain = np.where(wet, np.round(rng.gamma(0.8, 14.0, len(days)), 1), np.round(rng.random(len(days)) * 0.9, 1))
            rain[rng.random(len(days)) < rng.uniform(0, 0.08)] = np.nan
            keep = rng.random(len(days)) >= rng.uniform(0, 0.05)
            frames.append(pd.DataFrame({"station_id": f"S{s:02d}", "date": days[keep], "rain_mm": rain[keep]}))
    df = pd.concat(frames, ignore_index=True)
    df = df.sample(frac=1.0, random_state=int(rng.integers(1_000_000))).reset_index(drop=True)
    df["date"] = df["date"].astype("datetime64[ns]")
    return df
