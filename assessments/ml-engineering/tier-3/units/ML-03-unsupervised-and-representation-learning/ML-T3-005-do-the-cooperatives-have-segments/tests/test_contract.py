"""Contract tests: pass on the unmodified starter."""
import hashlib

import pytest

from conftest import DATA

pytestmark = pytest.mark.contract
EXPECTED_SHA256 = "851bdc0670c80de2bebfb019155a28fc008c2f9e76b3f66e36ccefced394846c"


def test_dataset_is_unmodified():
    assert hashlib.sha256(DATA.read_bytes()).hexdigest() == EXPECTED_SHA256, "coop_members.csv was modified"


def test_loader_shapes():
    from segment_lab import load_members
    m = load_members(DATA)
    assert m.X.shape == (700, 8) and len(m.trade) == 700 and len(m.names) == 8


def test_public_api_and_simulator():
    import segment_lab as sl
    for name in ["prepare", "null_samples", "gap_statistic", "stability", "estimate_k"]:
        assert callable(getattr(sl, name)), name
    X, lab = sl.simulate(3, 200, 0)
    assert X.shape == (200, 8) and set(lab) <= {0, 1, 2}
    X1, lab1 = sl.simulate(1, 100, 0)
    assert set(lab1) == {0}
