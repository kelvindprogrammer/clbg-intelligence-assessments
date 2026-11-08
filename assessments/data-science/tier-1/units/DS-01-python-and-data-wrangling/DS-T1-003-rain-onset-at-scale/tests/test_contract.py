"""Contract tests: these pass on the unmodified starter.

They check the committed sample, the generator's determinism, and the public API.
"""
import hashlib
import inspect
import subprocess
import sys

import pytest

from conftest import DATA, GENERATOR

pytestmark = pytest.mark.contract

EXPECTED_SHA256 = {
    "rainfall.csv": "f1f5921badfd4a234ef396709ce08c74f5f3a05af132f75a196573a3fd0a986a",
    "stations.csv": "e0836c40167e96050159d98cf5b50482bf195d2517df50df75b8450af39d9580",
}


@pytest.mark.parametrize("name", sorted(EXPECTED_SHA256))
def test_sample_is_unmodified(name):
    assert hashlib.sha256((DATA / name).read_bytes()).hexdigest() == EXPECTED_SHA256[name], \
        f"{name} has been modified. Regenerate it with the command in README section E."


def test_loader(sample):
    assert list(sample.columns) == ["station_id", "date", "rain_mm"]
    assert len(sample) == 51354
    assert str(sample["date"].dtype) == "datetime64[ns]"
    assert sample["rain_mm"].isna().sum() > 0


def test_generator_is_deterministic(tmp_path):
    digests = []
    for k in range(2):
        out = tmp_path / f"g{k}"
        subprocess.run([sys.executable, str(GENERATOR), "--out", str(out), "--seed", "5", "--stations", "3",
                        "--years", "2"], check=True, capture_output=True)
        digests.append(hashlib.sha256((out / "rainfall.csv").read_bytes()).hexdigest())
    assert digests[0] == digests[1]


def test_generator_reproduces_the_sample(tmp_path):
    subprocess.run([sys.executable, str(GENERATOR), "--out", str(tmp_path), "--seed", "2026"], check=True,
                   capture_output=True)
    assert hashlib.sha256((tmp_path / "rainfall.csv").read_bytes()).hexdigest() == EXPECTED_SHA256["rainfall.csv"]


def test_legacy_and_fast_share_signatures():
    import rainfall as rf
    for name in rf.FUNCTIONS:
        assert list(inspect.signature(getattr(rf.legacy, name)).parameters) == ["df"]
        assert list(inspect.signature(getattr(rf.fast, name)).parameters) == ["df"]


def test_legacy_runs_on_a_small_slice(sample):
    import rainfall as rf
    small = sample[sample["station_id"] == "ST001"]
    out = rf.legacy.onset_dates(small)
    assert list(out.columns) == ["station_id", "year", "onset_date", "onset_doy"]
