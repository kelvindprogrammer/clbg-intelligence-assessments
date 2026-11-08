"""Contract tests: pass on the unmodified starter (data integrity, generator, public names)."""
import hashlib
import inspect
import subprocess
import sys

import pytest

from conftest import DATA, ROOT

pytestmark = pytest.mark.contract

EXPECTED_SHA256 = {
    "channel_value.csv": "5f1d839ef01d8612d5d5d6f964e9e47ea6edc57dd85bd996b45092844616cac4",
    "provider_failures.csv": "25d4c38ef6c1f0dd3a9e6fce16f4cbffd3e3849accfd7656f00676e03ae3b9e6",
    "agents_by_zone.csv": "dfe27c014ecb6bfbdd2532cc08e78e18cef29d0bbb717229498f698bb5021ec3",
    "fraud_reports.csv": "499a85baeed5fa59fc932040a4e1724a85e56b787e1fea2e72a171f1ef1d89d1",
}


def _sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


@pytest.mark.parametrize("name", sorted(EXPECTED_SHA256))
def test_data_unmodified(name):
    assert _sha(DATA / name) == EXPECTED_SHA256[name]


def test_generator_reproduces_data(tmp_path):
    subprocess.run([sys.executable, str(ROOT / "resources" / "generate_data.py"), "--out", str(tmp_path), "--seed", "2026"],
                   check=True, capture_output=True)
    for name, digest in EXPECTED_SHA256.items():
        assert _sha(tmp_path / name) == digest, name


def test_contract_names():
    import housestyle as hs
    for name in hs.__all__:
        assert hasattr(hs, name), name
    assert hs.CHARTS == ("channel_value", "provider_failures", "agents_by_zone", "fraud_reports", "channel_share")
    assert hs.MIN_CONTRAST == 3.0 and hs.MIN_DELTA_E == 10.0
    assert list(inspect.signature(hs.audit_palette).parameters)[:2] == ["colors", "background"]
    assert list(inspect.signature(hs.compare_to_baseline).parameters) == ["img", "baseline_png", "tolerance"]
    assert {"min_delta_e", "worst_pair", "min_contrast", "passes"} <= set(hs.PaletteReport.__dataclass_fields__)
