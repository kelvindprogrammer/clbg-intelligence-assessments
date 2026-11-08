"""Public requirement tests. These FAIL on the starter until you implement the package.

They are a sample of the rules, not the full set. Assessors run a larger hidden suite against a
different recorded indicator, different page sizes and different fault scripts, so code that only
satisfies these examples will not pass. Write your own tests in tests/test_member_*.py.

Every test runs offline. No test may sleep for real: the client takes an injectable `sleep`.
"""
import datetime as dt
import hashlib
import json
import random
import subprocess
import sys
from pathlib import Path

import pytest

from conftest import ECOWAS, ELEC, FIXTURES, ROOT
from fakes import ScriptedTransport

import wbclient as wb

ELEC_BODY_META = {"page": 1, "pages": 1, "per_page": 1000, "total": 375, "sourceid": "2", "lastupdated": "2026-10-08"}


def ok(body: bytes, headers=None):
    return wb.Response(200, headers or {}, body)


def page_body(page, pages, total, records, lastupdated="2026-10-08", per_page=2):
    return json.dumps([{"page": page, "pages": pages, "per_page": per_page, "total": total,
                        "sourceid": "2", "lastupdated": lastupdated}, records]).encode()


def rec(iso3, year, value=1.0):
    return {"indicator": {"id": "X.Y", "value": "x"}, "country": {"id": iso3[:2], "value": iso3},
            "countryiso3code": iso3, "date": str(year), "value": value, "obs_status": "", "decimal": 1}


class Sleeps(list):
    def __call__(self, s):
        self.append(s)


def client(transport, **kw):
    kw.setdefault("sleep", Sleeps())
    kw.setdefault("rng", random.Random(0))
    return wb.WorldBankClient(transport, **kw)


# ---------------------------------------------------------------- R1
def test_build_url_is_canonical():
    a = wb.build_url("EG.ELC.ACCS.ZS", ["nga", "GHA", "NGA"], date="2000:2024", page=2, per_page=100)
    assert a == ("https://api.worldbank.org/v2/country/GHA;NGA/indicator/EG.ELC.ACCS.ZS"
                 "?date=2000%3A2024&format=json&page=2&per_page=100")
    b = wb.build_url("EG.ELC.ACCS.ZS", ["GHA", "nga"], date="2000:2024", page=2, per_page=100)
    assert a == b


@pytest.mark.parametrize("indicator,countries", [("EG.ELC/../x", ["NGA"]), ("EG.ELC.ACCS.ZS", ["NG A"]),
                                                  ("EG.ELC.ACCS.ZS", []), ("EG.ELC.ACCS.ZS", ["NGA;GHA"])])
def test_build_url_rejects_injection(indicator, countries):
    with pytest.raises(ValueError):
        wb.build_url(indicator, countries)


def test_canonical_key_ignores_query_order():
    k1 = wb.canonical_key("https://API.worldbank.org/v2/country/NGA/indicator/X?page=1&format=json")
    k2 = wb.canonical_key("https://api.worldbank.org/v2/country/NGA/indicator/X?format=json&page=1")
    assert k1 == k2 and len(k1) == 64


# ---------------------------------------------------------------- R2
def test_parse_real_page():
    page = wb.parse_page((FIXTURES / "raw_page2_per100.json").read_bytes())
    assert (page.meta.page, page.meta.pages, page.meta.per_page, page.meta.total) == (2, 4, 100, 375)
    assert page.meta.lastupdated == "2026-10-08"
    assert len(page.records) == 100
    nulls = [o for o in page.records if o.value is None]
    assert len(nulls) == 2, "null values must stay None, never 0"
    assert all(isinstance(o.date, str) and len(o.country_iso3) == 3 for o in page.records)


def test_parse_error_envelope_raises():
    with pytest.raises(wb.WorldBankAPIError) as ei:
        wb.parse_page((FIXTURES / "error_invalid_indicator.json").read_bytes())
    assert ei.value.code == "120"


def test_parse_string_metadata_is_coerced():
    # The /sources endpoint really does send page metadata as strings ("page":"1").
    meta = json.loads((FIXTURES / "sources_2_string_meta.json").read_text(encoding="utf-8"))[0]
    assert isinstance(meta["page"], str)
    page = wb.parse_page(json.dumps([meta, []]).encode())
    assert page.meta.page == 1 and isinstance(page.meta.total, int) and page.meta.total == 1


@pytest.mark.parametrize("body", [(FIXTURES / "no_format_param.xml").read_bytes(), b"<html>maintenance</html>",
                                  b'[{"page":1,"pages":1', b"{}"])
def test_parse_malformed(body):
    with pytest.raises(wb.MalformedResponse):
        wb.parse_page(body)


def test_parse_null_records_means_empty():
    body = json.dumps([{"page": 0, "pages": 0, "per_page": 50, "total": 0, "lastupdated": "2026-10-08"}, None]).encode()
    assert wb.parse_page(body).records == []


# ---------------------------------------------------------------- R3 / R4
@pytest.mark.parametrize("status,expected", [(429, True), (503, True), (502, True), (500, True), (504, True),
                                             (400, False), (403, False), (404, False), (200, False)])
def test_is_retryable_status(status, expected):
    assert wb.is_retryable(status) is expected


def test_is_retryable_errors():
    assert wb.is_retryable(None, wb.TransportError("reset"))
    assert wb.is_retryable(200, wb.MalformedResponse("html"))
    assert not wb.is_retryable(200, wb.WorldBankAPIError("120", "Invalid value", "x"))


def test_retry_after_forms():
    now = dt.datetime(2026, 11, 3, 12, 0, 0, tzinfo=dt.timezone.utc)
    assert wb.parse_retry_after("7", now) == 7.0
    assert wb.parse_retry_after("Tue, 03 Nov 2026 12:00:30 GMT", now) == pytest.approx(30.0)
    assert wb.parse_retry_after("Tue, 03 Nov 2026 11:59:00 GMT", now) == 0.0
    assert wb.parse_retry_after("soon", now) is None
    assert wb.parse_retry_after(None, now) is None


def test_backoff_full_jitter_is_bounded_and_capped():
    pol = wb.RetryPolicy(base_delay=0.5, max_delay=4.0)
    rng = random.Random(42)
    for attempt, cap in [(1, 0.5), (2, 1.0), (3, 2.0), (4, 4.0), (9, 4.0)]:
        draws = [wb.backoff_delay(attempt, pol, rng) for _ in range(400)]
        assert all(0.0 <= d <= cap for d in draws)
        assert max(draws) > 0.9 * cap, "full jitter should use the whole [0, cap] range"
    assert wb.backoff_delay(1, pol, rng, retry_after=11.0) == 11.0
    r1, r2 = random.Random(5), random.Random(5)
    assert [wb.backoff_delay(3, pol, r1) for _ in range(5)] == [wb.backoff_delay(3, pol, r2) for _ in range(5)]


# ---------------------------------------------------------------- R5
def test_cache_roundtrip_expiry_and_integrity(tmp_path):
    now = [1000.0]
    c = wb.ResponseCache(tmp_path / "c", clock=lambda: now[0])
    key = wb.canonical_key("https://api.worldbank.org/v2/country/NGA/indicator/X?format=json")
    c.put(key, b"[1]", {"url": "u"})
    assert c.get(key, max_age=60) == b"[1]"
    now[0] += 61
    assert c.get(key, max_age=60) is None
    assert c.get(key, max_age=None) == b"[1]"
    for f in (tmp_path / "c").rglob("*.body"):
        f.write_bytes(b"[2]")  # corrupt the stored body
    assert c.get(key, max_age=None) is None, "a corrupted entry must be a miss"
    assert not [p for p in (tmp_path / "c").rglob("*") if p.name.startswith(".tmp")]


# ---------------------------------------------------------------- R6 / R7
def test_retries_then_succeeds_and_logs_every_attempt(tmp_path):
    body = page_body(1, 1, 1, [rec("NGA", 2020)])
    t = ScriptedTransport([wb.TransportError("reset"), wb.Response(503, {"retry-after": "3"}, b"busy"),
                           ok(b"<html>maintenance</html>"), ok(body)])
    prov = wb.ProvenanceLog(tmp_path / "p.jsonl")
    sleeps = Sleeps()
    c = client(t, provenance=prov, sleep=sleeps, cache=wb.ResponseCache(tmp_path / "c"))
    page = c.fetch_page("https://api.worldbank.org/v2/country/NGA/indicator/X.Y?format=json&page=1&per_page=2")
    assert page.records[0].value == 1.0
    assert len(t.calls) == 4 and len(sleeps) == 3
    assert sleeps[1] == 3.0, "Retry-After must be honoured"
    entries = prov.entries()
    assert [e["outcome"] for e in entries] == ["retry", "retry", "retry", "ok"]
    assert [e["attempt"] for e in entries] == [1, 2, 3, 4]
    assert entries[-1]["sha256"] == hashlib.sha256(body).hexdigest()
    assert entries[-1]["lastupdated"] == "2026-10-08"
    for e in entries:
        for f in ["ts", "url", "attempt", "outcome", "status", "sha256", "bytes", "lastupdated"]:
            assert f in e, f


def test_non_retryable_status_is_not_retried(tmp_path):
    t = ScriptedTransport([wb.Response(404, {}, b"nope")])
    c = client(t)
    with pytest.raises(wb.HTTPStatusError):
        c.fetch_page("https://api.worldbank.org/v2/country/NGA/indicator/X?format=json")
    assert len(t.calls) == 1


def test_error_envelope_is_not_retried_or_cached(tmp_path):
    body = (FIXTURES / "error_invalid_indicator.json").read_bytes()
    cache = wb.ResponseCache(tmp_path / "c")
    t = ScriptedTransport([ok(body), ok(body)])
    c = client(t, cache=cache)
    url = "https://api.worldbank.org/v2/country/NGA/indicator/NOT.REAL?format=json"
    for _ in range(2):
        with pytest.raises(wb.WorldBankAPIError):
            c.fetch_page(url)
    assert len(t.calls) == 2, "an error must never be served from the cache"


def test_gives_up_after_max_attempts():
    t = ScriptedTransport([wb.Response(502, {}, b"")] * 3)
    c = client(t, policy=wb.RetryPolicy(max_attempts=3))
    with pytest.raises(wb.RetryExhausted):
        c.fetch_page("https://api.worldbank.org/v2/country/NGA/indicator/X?format=json")
    assert len(t.calls) == 3


def test_refuses_absurd_retry_after():
    t = ScriptedTransport([wb.Response(429, {"retry-after": "86400"}, b"")])
    sleeps = Sleeps()
    c = client(t, sleep=sleeps, policy=wb.RetryPolicy(max_retry_after=120))
    with pytest.raises(wb.RetryExhausted):
        c.fetch_page("https://api.worldbank.org/v2/country/NGA/indicator/X?format=json")
    assert sleeps == [], "never sleep for a day inside a client"


def test_cache_hit_avoids_network(tmp_path):
    body = page_body(1, 1, 1, [rec("NGA", 2020)])
    t = ScriptedTransport([ok(body)])
    prov = wb.ProvenanceLog(tmp_path / "p.jsonl")
    c = client(t, cache=wb.ResponseCache(tmp_path / "c"), provenance=prov)
    url = "https://api.worldbank.org/v2/country/NGA/indicator/X.Y?format=json&page=1&per_page=2"
    c.fetch_page(url)
    c.fetch_page(url)
    assert len(t.calls) == 1
    assert [e["outcome"] for e in prov.entries()] == ["ok", "cache_hit"]


# ---------------------------------------------------------------- R8 (through a real local HTTP server)
def test_fetch_indicator_every_page_exactly_once(fake_wb, tmp_path):
    c = client(wb.UrllibTransport(), base=fake_wb.base, cache=wb.ResponseCache(tmp_path / "c"))
    res = c.fetch_indicator("EG.ELC.ACCS.ZS", ECOWAS, date="2000:2024", per_page=40)
    assert res.pages == 10 and len(res.observations) == 375 and not res.restarted
    keys = {(o.country_iso3, o.date) for o in res.observations}
    assert len(keys) == 375
    assert all(r["query"].get("format") == "json" for r in fake_wb.data_requests())
    assert len(fake_wb.data_requests()) == 10


def test_transient_fault_mid_pagination(fake_wb, tmp_path):
    fake_wb.faults += [("ok",), ("ok",), ("status", 503, {"Retry-After": "1"}, b"busy"), ("drop",)]
    sleeps = Sleeps()
    c = client(wb.UrllibTransport(), base=fake_wb.base, sleep=sleeps)
    res = c.fetch_indicator("EG.ELC.ACCS.ZS", ECOWAS, date="2000:2024", per_page=100)
    assert len(res.observations) == 375 and len(sleeps) == 2


def test_snapshot_change_mid_pagination_restarts_once(fake_wb, tmp_path):
    fake_wb.bump_lastupdated_after = 2  # the dataset is republished after page 2 is served
    c = client(wb.UrllibTransport(), base=fake_wb.base, cache=wb.ResponseCache(tmp_path / "c"))
    res = c.fetch_indicator("EG.ELC.ACCS.ZS", ECOWAS, date="2000:2024", per_page=100)
    assert res.restarted and len(res.observations) == 375
    assert res.lastupdated != "2026-10-08"


def test_snapshot_keeps_changing_raises(fake_wb):
    fake_wb.bump_every = 2
    c = client(wb.UrllibTransport(), base=fake_wb.base)
    with pytest.raises(wb.InconsistentPagination):
        c.fetch_indicator("EG.ELC.ACCS.ZS", ECOWAS, date="2000:2024", per_page=100)


# ---------------------------------------------------------------- R9
def test_to_frame_keeps_nulls_as_nan():
    obs = wb.parse_page(ELEC.read_bytes()).records
    df = wb.to_frame(obs)
    assert list(df.columns) == ["indicator_id", "country_iso3", "year", "value", "obs_status"]
    assert len(df) == 375 and df["value"].isna().sum() == 9
    assert str(df["year"].dtype) == "int64"
    assert df.iloc[0]["country_iso3"] == "BEN" and df.iloc[0]["year"] == 2000


# ---------------------------------------------------------------- R10
def _cli(args, cwd):
    import os
    env = dict(os.environ)
    pkg_parent = str(Path(wb.__file__).resolve().parents[1])
    env["PYTHONPATH"] = pkg_parent + os.pathsep + env.get("PYTHONPATH", "")
    return subprocess.run([sys.executable, "-m", "wbclient", *args], cwd=cwd, env=env, capture_output=True,
                          text=True, timeout=60)


def test_cli_online_then_offline_rebuild_is_identical(fake_wb, tmp_path):
    common = ["fetch", "EG.ELC.ACCS.ZS", "--countries", ",".join(ECOWAS), "--date", "2000:2024",
              "--cache", str(tmp_path / "cache"), "--provenance", str(tmp_path / "prov.jsonl"), "--per-page", "100"]
    r1 = _cli(common + ["--out", str(tmp_path / "a.csv"), "--base-url", fake_wb.base], tmp_path)
    assert r1.returncode == 0, r1.stderr
    n_live = len(fake_wb.data_requests())
    r2 = _cli(common + ["--out", str(tmp_path / "b.csv"), "--offline", "--base-url", fake_wb.base], tmp_path)
    assert r2.returncode == 0, r2.stderr
    assert len(fake_wb.data_requests()) == n_live, "offline mode must not touch the network"
    assert (tmp_path / "a.csv").read_bytes() == (tmp_path / "b.csv").read_bytes()
    r3 = _cli(["fetch", "EG.ELC.ACCS.ZS", "--countries", "NGA", "--out", str(tmp_path / "c.csv"), "--cache",
               str(tmp_path / "cache"), "--provenance", str(tmp_path / "prov.jsonl"), "--offline"], tmp_path)
    assert r3.returncode != 0, "offline mode must fail loudly when a page is not cached"
