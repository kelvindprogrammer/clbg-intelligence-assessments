"""Requirement tests (public catalogue). They fail on the starter and pass on a correct audit."""
import json
import subprocess
import sys

import pytest

from conftest import CATALOGUE, ROOT

EXP = json.loads((ROOT / "tests" / "expected_public.json").read_text())
CODES = ["CHECKSUM_MISMATCH", "ROW_COUNT_MISMATCH", "PROVENANCE_CYCLE", "LICENSE_NC_STRIPPED", "LICENSE_SA_VIOLATION",
         "LICENSE_BY_STRIPPED", "LICENSE_CONFLICT", "UPSTREAM_UNLICENSED", "MISSING_ATTRIBUTION"]


def test_load_catalogue(cat):
    assert len(cat.datasets) == 24
    d = next(iter(cat.datasets.values()))
    assert isinstance(d.derived_from, tuple)


def test_effective_licenses(cat):
    from provenance_audit import effective_license
    got = {i: effective_license(cat, i) for i in cat.datasets}
    wrong = {i: (got[i], EXP["effective"][i]) for i in got if got[i] != EXP["effective"][i]}
    assert not wrong, f"effective licence differs for {len(wrong)} datasets, e.g. {dict(list(wrong.items())[:3])}"


@pytest.mark.parametrize("code", CODES)
def test_findings_by_code(cat, code):
    from provenance_audit import audit
    got = sorted(f.dataset_id for f in audit(cat) if f.code == code)
    exp = sorted(i for i, c in EXP["findings"] if c == code)
    assert got == exp, f"{code}: expected {exp}, got {got}"


def test_no_extra_findings_and_sorted(cat):
    from provenance_audit import audit
    got = audit(cat)
    assert [(f.dataset_id, f.code) for f in got] == [tuple(x) for x in EXP["findings"]]


def test_can_use(cat):
    from provenance_audit import can_use
    for i, e in EXP["effective"].items():
        blocked = e in ("BLOCKED", "CONFLICT", "UNRESOLVED")
        assert can_use(cat, i, "commercial") == (not blocked and e != "CC-BY-NC-4.0"), i
        assert can_use(cat, i, "closed_derivative") == (not blocked and e not in ("CC-BY-SA-4.0", "ODbL-1.0")), i
    with pytest.raises(ValueError):
        can_use(cat, next(iter(cat.datasets)), "resale")


def test_required_attribution(cat):
    from provenance_audit import required_attribution
    for i, titles in EXP["required_attribution"].items():
        assert required_attribution(cat, i) == titles, i


def test_cli_writes_findings(tmp_path):
    import os
    from pathlib import Path

    import provenance_audit
    out = tmp_path / "f.json"
    env = dict(os.environ, PYTHONPATH=str(Path(provenance_audit.__file__).resolve().parents[1]))
    subprocess.run([sys.executable, "-m", "provenance_audit", str(CATALOGUE), "--out", str(out)], check=True, env=env)
    got = [(d["dataset_id"], d["code"]) for d in json.loads(out.read_text())]
    assert got == [tuple(x) for x in EXP["findings"]]
