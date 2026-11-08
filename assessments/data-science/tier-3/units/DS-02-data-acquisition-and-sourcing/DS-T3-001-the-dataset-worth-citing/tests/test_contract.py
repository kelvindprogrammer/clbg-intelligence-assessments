"""Contract tests: pass on the unmodified starter."""
import hashlib
import inspect

import pytest

from conftest import CATALOGUE

pytestmark = pytest.mark.contract
CATALOGUE_SHA256 = "ab23dc636edb04eef93fcdb876e5c1915c285484e28d67d4b79e4583df515cab"


def test_catalogue_unmodified():
    assert hashlib.sha256((CATALOGUE / "catalogue.json").read_bytes()).hexdigest() == CATALOGUE_SHA256, "catalogue.json was modified"


def test_catalogue_files_present():
    import json
    entries = json.loads((CATALOGUE / "catalogue.json").read_text(encoding="utf-8"))["datasets"]
    assert len(entries) == 24
    assert all((CATALOGUE / e["file"]).is_file() for e in entries)


def test_public_api_signatures():
    import provenance_audit as pa
    assert list(inspect.signature(pa.can_use).parameters) == ["cat", "dataset_id", "purpose"]
    for name in ["load_catalogue", "effective_license", "audit", "required_attribution"]:
        assert callable(getattr(pa, name)), name


def test_finding_type():
    from provenance_audit import Finding
    assert Finding("DS101", "X") < Finding("DS101", "Y")
