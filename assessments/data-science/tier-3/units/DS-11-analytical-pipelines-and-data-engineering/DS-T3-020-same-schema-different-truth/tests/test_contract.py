"""Contract tests: these pass on the unmodified starter."""
import hashlib

import pytest

from conftest import BATCHES, CONTRACT

pytestmark = pytest.mark.contract
EXPECTED_SHA256 = "d767fa1a0e2008cebdd7c63d75a0f03db096270ec4aa3d9d5ce28f06a12daa56"   # all batches in name order


def test_batches_are_unmodified():
    h = hashlib.sha256()
    for p in sorted(BATCHES.glob("batch_*.csv")):
        h.update(p.read_bytes())
    assert h.hexdigest() == EXPECTED_SHA256, "resources/data/batches was modified; restore it"


def test_stream_and_contract_load():
    import contractgate as cg
    b = cg.load_batches(BATCHES)
    c = cg.load_contract(CONTRACT)
    assert len(b) == 30 and 80 <= len(b[0]) <= 100 and set(c["columns"]) <= set(b[0].columns)
    assert c["key"] == ["market_id", "commodity", "observed_on"]


def test_public_api_and_provided_decide():
    import contractgate as cg
    for n in ["infer_schema", "diff_schema", "validate_batch", "fit_baseline", "detect_drift", "gate",
              "run_stream", "inject_fault", "operating_characteristics"]:
        assert callable(getattr(cg, n)), n
    assert cg.decide(["schema:new_column:x"]).action == "accept"
    assert cg.decide(["rule:null:state", "schema:new_column:x"]).action == "quarantine"
    assert cg.decide(["rule:null:state", "drift:scale_shift:p"]).action == "block"
