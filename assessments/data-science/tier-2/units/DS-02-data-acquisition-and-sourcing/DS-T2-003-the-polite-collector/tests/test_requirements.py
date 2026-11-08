"""Public requirement tests. These FAIL on the starter until you implement the collector.

They are a sample. The hidden suite runs your collector against a portal scenario you have not seen
(different seed, sizes, faults and a different kind of template drift), so tune nothing to this one.
"""
import json
import re
from collections import Counter
from pathlib import Path

import pytest

import collector as c

ROBOTS = """User-agent: *
Crawl-delay: 5
Disallow: /private/
Disallow: /*.pdf$

User-agent: clbg-collector
Crawl-delay: 2
Allow: /docs/public/
Disallow: /docs/
Disallow: /items/*/edit
"""


# ---------------------------------------------------------------- robots (RFC 9309)
@pytest.mark.parametrize("path,allowed", [
    ("/docs/x", False), ("/docs/public/x", True), ("/items/7/edit", False), ("/items/7/edit/now", False),
    ("/items/7", True), ("/private/a", True),  # the specific group replaces '*': its rules don't apply
    ("/robots.txt", True),
])
def test_robots_specific_group_and_longest_match(path, allowed):
    assert c.Robots(ROBOTS).allowed("clbg-collector", path) is allowed


@pytest.mark.parametrize("path,allowed", [("/a.pdf", False), ("/a.pdf?x=1", True), ("/private/", False), ("/docs/x", True)])
def test_robots_wildcards_for_other_agents(path, allowed):
    assert c.Robots(ROBOTS).allowed("otherbot", path) is allowed


def test_robots_crawl_delay():
    r = c.Robots(ROBOTS)
    assert r.crawl_delay("clbg-collector") == 2 and r.crawl_delay("otherbot") == 5


def test_canonical_url_drops_session_noise():
    a = c.canonical_url("http://H:1/tenders?page=2&session=ab12#top")
    b = c.canonical_url("http://h:1/tenders?session=ffff&page=2")
    assert a == b and "session" not in a


# ---------------------------------------------------------------- one polite run
def _cfg(portal, tmp_path, **kw):
    return c.CollectorConfig(portal.base_url, tmp_path / "state", clock=portal.clock_obj.now,
                             sleep=portal.clock_obj.sleep, **kw)


def test_day1_complete_correct_and_polite(portal, tmp_path):
    rep = c.run_once(_cfg(portal, tmp_path))
    truth = portal.truth()
    assert sorted(rep.new) == sorted(truth)
    recs = {r["reference"]: r for r in c.load_records(tmp_path / "state")}
    for ref, t in truth.items():
        for k, v in t.items():
            assert recs[ref][k] == v, (ref, k)
        assert set(c.RECORD_FIELDS) <= set(recs[ref])
    v = portal.violations()
    assert v["disallowed"] == [] and v["too_fast"] == [] and v["missing_contact_in_ua"] == 0
    log = portal.day_log()
    assert log[0]["path"] == "/robots.txt", "robots.txt must be the first request"
    paths = [e["path"] for e in log]
    assert not [p for p in paths if "/archive" in p or p.startswith("/search")], "stay inside the crawl scope"
    ok = Counter((e["path"], e["query"].get("page")) for e in log if e["status"] == 200)
    assert max(ok.values()) == 1, "no page fetched twice in one run (session parameters!)"
    assert rep.requests == len(log)


def test_no_personal_data_stored(portal, tmp_path):
    c.run_once(_cfg(portal, tmp_path))
    blob = "\n".join(p.read_text(encoding="utf-8") for p in (tmp_path / "state").rglob("*") if p.is_file())
    assert "@example.ng" not in blob
    assert not re.search(r"0[789]0\d[ -]?\d{3}[ -]?\d{4}", blob), "contact phone numbers must not be stored"


def test_day2_change_detection_with_conditional_requests(portal, tmp_path):
    cfg = _cfg(portal, tmp_path)
    r1 = c.run_once(cfg)
    before = portal.truth()
    portal.set_day(2)
    r2 = c.run_once(cfg)
    after = portal.truth()
    changed = {k for k in before.keys() & after.keys() if before[k] != after[k]}
    assert sorted(r2.new) == sorted(set(after) - set(before))
    assert sorted(r2.withdrawn) == sorted(set(before) - set(after))
    assert set(r2.updated) == changed, "every amendment, including ones the sitemap does not advertise"
    assert r2.not_modified >= 30
    assert r2.bytes < 0.6 * r1.bytes, "conditional requests should make a quiet day cheap"
    recs = {r["reference"]: r for r in c.load_records(cfg.state_dir)}
    assert all(recs[k]["withdrawn"] for k in r2.withdrawn)
    assert portal.violations()["too_fast"] == []


def test_day3_schema_drift_raises_alarm_and_keeps_good_data(portal, tmp_path):
    cfg = _cfg(portal, tmp_path)
    c.run_once(cfg)
    portal.set_day(2)
    c.run_once(cfg)
    snapshot = {r["reference"]: r for r in c.load_records(cfg.state_dir)}
    portal.set_day(3)
    r3 = c.run_once(cfg)
    assert r3.drift_alarms, "a template change must raise an alarm"
    assert all(a["kind"] in c.ALARM_KINDS and a["count"] >= 1 for a in r3.drift_alarms)
    assert any(a["field"] in ("estimated_value_ngn", "Contract value (NGN)") for a in r3.drift_alarms)
    after = {r["reference"]: r for r in c.load_records(cfg.state_dir)}
    for ref, old in snapshot.items():
        if not old["withdrawn"]:
            assert after[ref]["estimated_value_ngn"] == old["estimated_value_ngn"] or ref in r3.updated, \
                "never overwrite a good value with a null or a guess"
            assert after[ref]["estimated_value_ngn"] is not None


def test_request_budget_is_a_hard_limit(portal, tmp_path):
    rep = c.run_once(_cfg(portal, tmp_path, max_requests=10))
    assert len(portal.day_log()) <= 10
    assert rep.errors, "running out of budget must be reported"
