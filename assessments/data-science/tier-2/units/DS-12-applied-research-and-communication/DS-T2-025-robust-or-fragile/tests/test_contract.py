"""Contract tests: these pass on the unmodified starter."""
import hashlib

import pytest

from conftest import DATA

pytestmark = pytest.mark.contract
EXPECTED_SHA256 = "55008aa2275559e23b2144cd6dca7184a1a1f4639bd151c6d959754cf6d381e3"


def test_dataset_is_unmodified():
    assert hashlib.sha256(DATA.read_bytes()).hexdigest() == EXPECTED_SHA256, "households.csv was modified; restore it"


def test_dataset_shape_and_space():
    import speccurve as sc
    df = sc.load_export(DATA)
    assert len(df) == 1600 and {"trained", "savings_ngn", "loan_taken", "visited_agent"} <= set(df.columns)
    assert len(sc.CONTROL_SETS) == 6 and len(sc.SPACE["outcome"]) * len(sc.SPACE["controls"]) * len(sc.SPACE["method"]) * len(sc.SPACE["trim"]) == 48


def test_public_api():
    import speccurve as sc
    for n in ["ols", "logit_fit", "estimate", "spec_curve", "summarise_curve", "defensible", "e_value"]:
        assert callable(getattr(sc, n)), n
