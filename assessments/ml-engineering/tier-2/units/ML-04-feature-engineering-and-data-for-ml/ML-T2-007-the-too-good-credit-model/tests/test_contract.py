"""Contract tests: pass on the unmodified starter."""
import hashlib

import pytest

from conftest import DATA, DICT

pytestmark = pytest.mark.contract
EXPECTED_SHA256 = "aaffda5ed613314dc93b117d6a59a537a7a0e82cb8089e1e4550063e3263b09b"


def test_dataset_is_unmodified():
    assert hashlib.sha256(DATA.read_bytes()).hexdigest() == EXPECTED_SHA256, "loans.csv was modified"


def test_loader_and_dictionary():
    from loan_audit import load_dictionary, load_loans
    d = load_loans(DATA)
    assert len(d["default"]) == 1399 and set(d["default"]) == {0, 1}
    assert load_dictionary(DICT)["restructured_flag"] == "post_outcome"


def test_public_api():
    import loan_audit as la
    for n in ["audit_features", "honest_split", "leaky_vs_honest", "psi", "drift_check"]:
        assert callable(getattr(la, n)), n
