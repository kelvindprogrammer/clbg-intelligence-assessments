"""Contract tests: these pass on the unmodified starter.

They check that the mock portal behaves as documented and that the public contract exists.
"""
import dataclasses
import urllib.error
import urllib.request

import pytest

pytestmark = pytest.mark.contract


def _get(url, ua="clbg-collector/1.0 (+mailto:t@example.ng)", headers=None):
    req = urllib.request.Request(url, headers={"User-Agent": ua, **(headers or {})})
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return r.status, dict(r.headers), r.read().decode()
    except urllib.error.HTTPError as e:
        return e.code, dict(e.headers), e.read().decode()


def test_portal_serves_robots_terms_listing_and_details(portal):
    s, _, robots = _get(portal.base_url + "/robots.txt")
    assert s == 200 and "Crawl-delay" in robots
    s, _, terms = _get(portal.base_url + "/terms")
    assert s == 200 and "robots.txt" in terms
    portal.clock_obj.advance(10)
    s, _, listing = _get(portal.base_url + "/tenders?page=1")
    assert s == 200 and "class='tender'" in listing
    ref = sorted(portal.truth())[0]
    portal.clock_obj.advance(10)
    s, h, body = _get(f"{portal.base_url}/tenders/{ref}")
    assert s == 200 and "ETag" in h and "Contact officer" in body
    portal.clock_obj.advance(10)
    s, _, _ = _get(f"{portal.base_url}/tenders/{ref}", headers={"If-None-Match": h["ETag"]})
    assert s == 304


def test_portal_enforces_crawl_delay_on_virtual_clock(portal):
    portal.clock_obj.advance(10)
    assert _get(portal.base_url + "/tenders?page=1")[0] == 200
    portal.clock_obj.advance(0.5)
    assert _get(portal.base_url + "/tenders?page=2")[0] == 429
    assert portal.violations()["too_fast"]


def test_portal_days_change_content(portal):
    before = portal.truth()
    portal.set_day(2)
    after = portal.truth()
    assert len(set(after) - set(before)) == 5 and len(set(before) - set(after)) == 2


def test_public_contract_exists():
    import collector as c
    names = {f.name for f in dataclasses.fields(c.CollectorConfig)}
    assert {"base_url", "state_dir", "user_agent", "clock", "sleep", "strategy", "min_delay", "max_requests",
            "max_listing_pages"} <= names
    rep = c.RunReport()
    for f in ["new", "updated", "withdrawn", "unchanged", "quarantined", "drift_alarms", "requests", "not_modified",
              "bytes", "errors"]:
        assert hasattr(rep, f), f
    assert callable(c.run_once) and callable(c.load_records) and callable(c.canonical_url)
    assert hasattr(c.Robots, "allowed") and hasattr(c.Robots, "crawl_delay")
    assert "clbg-collector" in c.CollectorConfig("http://x", "s").user_agent
