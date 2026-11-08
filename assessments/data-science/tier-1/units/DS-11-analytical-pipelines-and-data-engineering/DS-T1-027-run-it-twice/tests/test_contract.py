"""Contract tests: these pass on the unmodified starter."""
import hashlib

import pytest

from conftest import DROPS

pytestmark = pytest.mark.contract
EXPECTED_SHA256 = "9ff126720a6c44755ab6131f04c13b380ade96cf40b72bb29acfbe490ff08ae9"   # of all drop files, in name order


def test_drops_are_unmodified():
    h = hashlib.sha256()
    for p in sorted(DROPS.glob("*.csv")):
        h.update(p.read_bytes())
    assert h.hexdigest() == EXPECTED_SHA256, "files in resources/data/drops were modified; restore them"


def test_six_drops_and_collectors():
    import levyload as ll
    assert len(list(DROPS.glob("*.csv"))) == 6
    assert len(ll.load_collectors(DROPS.parent / "collectors.csv")) == 12


def test_public_api():
    import levyload as ll
    for n in ["parse_amount", "parse_date", "validate_row", "read_drop", "init_db", "load_file", "load_all", "check_invariants"]:
        assert callable(getattr(ll, n)), n
    assert ll.REASONS[0] == "missing_field"
