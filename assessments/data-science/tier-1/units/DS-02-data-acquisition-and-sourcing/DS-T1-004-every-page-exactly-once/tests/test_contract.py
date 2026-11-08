"""Contract tests: these pass on the unmodified starter.

They check that the recorded fixtures are intact, that the offline fake server behaves like the
live API, and that the public API exists with the required signatures.
"""
import hashlib
import inspect
import json
import urllib.request

import pytest

from conftest import ELEC, FIXTURES

pytestmark = pytest.mark.contract

EXPECTED_SHA256 = {
    "EG.ELC.ACCS.ZS__ecowas__2000-2024.json": "55ddbd065a9c3a935cb371574757c4d65e79d31cefc0f1c29871d3f1c51293a8",
    "error_invalid_indicator.json": "f230e5b6d8f652aa544aec29624faa117c27571ce309a7a474584e1cfeb45c1b",
    "no_format_param.xml": "043de1dc6e2c432e91aa180edc8f16ccb08aeb9a194a56613942191caf7aa990",
    "raw_page2_per100.json": "a721afa0a7be98f608a172d2d73a8e13e6c0ddfd56aa036862ee2f66694b406f",
    "sources_2_string_meta.json": "26d3ed8cf01ffed2995a9997940398bf5a287a1ee595fad75983f877d2805bba",
}


@pytest.mark.parametrize("name", sorted(EXPECTED_SHA256))
def test_fixture_unmodified(name):
    assert hashlib.sha256((FIXTURES / name).read_bytes()).hexdigest() == EXPECTED_SHA256[name], \
        f"{name} has been modified. Restore the original recording."


def test_fixture_shape():
    meta, records = json.loads(ELEC.read_text(encoding="utf-8"))
    assert meta["total"] == len(records) == 375
    assert meta["lastupdated"] == "2026-10-08"
    assert sum(r["value"] is None for r in records) == 9


def _get(url):
    with urllib.request.urlopen(url, timeout=10) as r:
        return r.status, r.headers.get("Content-Type"), r.read()


def test_fake_server_pages_like_the_api(fake_wb):
    url = f"{fake_wb.base}/country/NGA;GHA/indicator/EG.ELC.ACCS.ZS?format=json&per_page=20&page=2"
    status, ctype, body = _get(url)
    meta, recs = json.loads(body)
    assert status == 200 and meta["total"] == 50 and meta["pages"] == 3 and len(recs) == 20


def test_fake_server_defaults_to_xml_like_the_api(fake_wb):
    status, ctype, body = _get(f"{fake_wb.base}/country/NGA/indicator/EG.ELC.ACCS.ZS")
    assert status == 200 and "xml" in ctype and body.startswith(b"<?xml")


def test_fake_server_error_envelope_is_http_200(fake_wb):
    status, _, body = _get(f"{fake_wb.base}/country/NGA/indicator/NOT.REAL?format=json")
    assert status == 200 and "message" in json.loads(body)[0]


def test_public_api_exists():
    import wbclient as wb
    for name in ["build_url", "canonical_key", "parse_page", "is_retryable", "parse_retry_after", "backoff_delay",
                 "ResponseCache", "ProvenanceLog", "WorldBankClient", "to_frame", "UrllibTransport", "RetryPolicy"]:
        assert hasattr(wb, name), name
    sig = inspect.signature(wb.build_url)
    for kw in ["date", "page", "per_page", "base"]:
        assert sig.parameters[kw].kind is inspect.Parameter.KEYWORD_ONLY, kw
    csig = inspect.signature(wb.WorldBankClient)
    for kw in ["cache", "provenance", "policy", "clock", "sleep", "rng", "cache_max_age", "base"]:
        assert kw in csig.parameters, kw
    assert "use_cache" in inspect.signature(wb.WorldBankClient.fetch_page).parameters


def test_types_and_exceptions():
    import wbclient as wb
    p = wb.RetryPolicy()
    assert p.max_attempts >= 2 and p.base_delay > 0 and p.max_delay >= p.base_delay
    e = wb.WorldBankAPIError("120", "Invalid value", "bad")
    assert isinstance(e, wb.WBClientError) and e.code == "120"
    assert issubclass(wb.RetryExhausted, wb.WBClientError)
