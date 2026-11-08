"""Contract tests: these pass on the unmodified starter.

They check that the agency files are intact and readable with the standard tools, and that the
public API exists. They do not parse the files for you.
"""
import csv
import hashlib
import inspect
import json
import xml.etree.ElementTree as ET

import pytest

from conftest import DATA, REF

pytestmark = pytest.mark.contract

EXPECTED_SHA256 = {
    "data/apc_survey.xlsx": "8950485cd531147e149678f867579827e5150f0472d11e00f0b5944e081af015",
    "data/cmb_bulletin.xml": "3f17fd73f846d8367eb050cc3f0e95e833979fc58802a052e7b2079e7b58c877",
    "data/lsa_extract.txt": "072ea75b63809d60fee7ef05a97ace7d5210b502315d54d09bd7ba1ccf0a0dcf",
    "data/ngm_prices.json": "30d626420c6a3e728e231ce42f2cd9d697cdd01e6bbc35eb9018edad90816b84",
    "reference/commodities.csv": "9588bbb99e76011b59d3e1376e00a1d10d4c1e8a39b92d25512957ae9f410c9e",
    "reference/markets.csv": "42e3ad327062fff4f277c2125d3ab4b0151651f9bb338ffc5b31ee5c5f86099d",
    "reference/units.csv": "1072c239e1e935141245f3c23252bc939a13a54ed6446f32f4b4df30796c148f",
}


@pytest.mark.parametrize("rel", sorted(EXPECTED_SHA256))
def test_files_unmodified(rel):
    path = DATA.parent / rel
    assert hashlib.sha256(path.read_bytes()).hexdigest() == EXPECTED_SHA256[rel], f"{rel} was modified. Restore it."


def test_files_are_well_formed():
    assert "reports" in json.loads((DATA / "ngm_prices.json").read_text(encoding="utf-8"))
    assert ET.parse(DATA / "cmb_bulletin.xml").getroot().tag == "PriceBulletin"
    lines = (DATA / "lsa_extract.txt").read_text(encoding="utf-8").splitlines()
    assert lines[0].startswith("LSA ") and lines[-1].startswith("TRAILER RECORDS=")
    assert (DATA / "apc_survey.xlsx").read_bytes()[:2] == b"PK"  # xlsx is a zip container


def test_reference_tables():
    with open(REF / "markets.csv", encoding="utf-8") as fh:
        assert len(list(csv.DictReader(fh))) == 10
    with open(REF / "commodities.csv", encoding="utf-8") as fh:
        assert len(list(csv.DictReader(fh))) == 5


def test_public_api_exists():
    import pricerecon as pr
    for name in ["load_reference", "week_start", "iso_week_monday", "parse_ngm", "parse_cmb", "parse_apc",
                 "parse_lsa", "load_all", "reconcile", "discrepancies", "stale_runs", "UnmappedLabel"]:
        assert hasattr(pr, name), name
    assert pr.CANONICAL_COLUMNS == ["source", "market_id", "commodity_id", "week_start", "price_ngn_per_kg", "flag"]
    assert inspect.signature(pr.discrepancies).parameters["tol"].default == 0.15
    assert inspect.signature(pr.stale_runs).parameters["min_run"].default == 4
    assert issubclass(pr.UnmappedLabel, ValueError)
