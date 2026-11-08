"""A local mock of a (fictional) state e-procurement portal, for DS-T2-003. Provided test infrastructure.

The portal, the state ("Ajana State"), the ministries' notices and every person are fictional.
Contact e-mails use the reserved example.ng domain.

Everything runs on a VirtualClock shared by the portal and the collector under test, so politeness
(crawl delays, Retry-After) can be verified exactly without real waiting.

Usage:
    clock = VirtualClock()
    with MockPortal(clock, scenario=PUBLIC_SCENARIO) as portal:
        portal.base_url            # e.g. http://127.0.0.1:54321
        portal.set_day(2)          # apply day-2 changes (and advance the clock by a day)
        portal.log                 # every request the portal received
        portal.violations()        # robots / rate-limit violations by user agent
"""
from __future__ import annotations

import copy
import datetime as dt
import hashlib
import html
import random
import re
import threading
import urllib.parse
from email.utils import format_datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


class VirtualClock:
    def __init__(self, start: float = 1_767_225_600.0):  # 2026-01-01T00:00:00Z
        self._t = float(start)
        self._lock = threading.Lock()

    def now(self) -> float:
        with self._lock:
            return self._t

    def sleep(self, seconds: float) -> None:
        if seconds < 0:
            raise ValueError("negative sleep")
        with self._lock:
            self._t += float(seconds)

    def advance(self, seconds: float) -> None:
        self.sleep(seconds)


ROBOTS_TXT = """# Ajana State e-Procurement Portal (fictional)
# Automated access: see /terms

User-agent: *
Crawl-delay: 5
Disallow: /admin/
Disallow: /search
Disallow: /tenders/*/print$

User-agent: clbg-collector
Crawl-delay: 2
Allow: /tenders/
Disallow: /admin/
Disallow: /search
Disallow: /tenders/*/print$
Disallow: /tenders/*/bidders
"""

TERMS_HTML = """<html><head><title>Terms of use</title></head><body><h1>Terms of use for automated access</h1>
<ol>
<li>Automated collection of published tender notices is permitted for non-commercial research, journalism and civic monitoring.</li>
<li>Identify your client with a User-Agent that includes a contact address, and respect /robots.txt including Crawl-delay.</li>
<li>Do not access bidder lists, print views or administrative pages by automated means.</li>
<li>Contact-officer details are published so bidders can ask questions. They may not be harvested, republished or used for marketing.</li>
<li>Cite the portal as the source. Notices may be amended or withdrawn: re-users must reflect amendments and withdrawals.</li>
</ol></body></html>"""

MINISTRIES = ["Ministry of Health", "Ministry of Education", "Ministry of Works and Infrastructure",
              "Ministry of Agriculture", "Ministry of Water Resources", "Ministry of Environment"]
MIN_CODE = {"Ministry of Health": "MOH", "Ministry of Education": "MOE", "Ministry of Works and Infrastructure": "MWI",
            "Ministry of Agriculture": "MOA", "Ministry of Water Resources": "MWR", "Ministry of Environment": "MEN"}
CATEGORIES = ["Works", "Goods", "Consultancy"]
SUBJECTS = {
    "Works": ["Rehabilitation of {n} km rural feeder road", "Construction of {n}-classroom block", "Drilling of {n} motorised boreholes",
              "Renovation of {n} primary health centres"],
    "Goods": ["Supply of {n} hospital beds", "Supply of {n} solar street lights", "Supply of {n} tonnes of improved maize seed",
              "Supply of {n} desktop computers"],
    "Consultancy": ["Feasibility study for {n} irrigation schemes", "Supervision of {n} water projects",
                    "Environmental impact assessment of {n} sites", "Design review for {n} school buildings"],
}
FIRST = ["Adaeze", "Bola", "Chinedu", "Damilola", "Emeka", "Fatima", "Garba", "Halima", "Ifeoma", "Kunle", "Ngozi", "Usman"]
LAST = ["Okafor", "Adeyemi", "Bello", "Eze", "Abubakar", "Ogunleye", "Nwosu", "Danjuma", "Ibrahim", "Okon"]
MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
          "November", "December"]

# A scenario describes the portal's behaviour over successive days. Template v2 = schema drift.
PUBLIC_SCENARIO = {
    "seed": 2026,
    "n_initial": 40,
    "page_size": 10,
    "transient_503_at": [7],            # request numbers (1-based, per day) answered 503 + Retry-After
    "days": {
        2: {"new": 5, "amend": 3, "withdraw": 2, "silent_amend": 1},  # silent = sitemap lastmod not updated
        3: {"template": 2, "amend": 2},
    },
    "template_v2": {
        "rename": {"Estimated value (₦)": "Contract value (NGN)"},
        "value_format": "NGN {v:d}",
        "date_format": "iso",
        "extra_rows": {"Lot": "1 of 1"},
    },
}


def _fmt_date(d: dt.date, style: str) -> str:
    if style == "iso":
        return d.isoformat()
    return f"{d.day} {MONTHS[d.month - 1]} {d.year}"


class MockPortal:
    def __init__(self, clock: VirtualClock, scenario: dict = PUBLIC_SCENARIO, enforce: bool = True):
        """enforce=False still LOGS rate violations but serves the request anyway (for measuring baselines)."""
        self.clock = clock
        self.enforce = enforce
        self.sc = copy.deepcopy(scenario)
        self.rng = random.Random(self.sc["seed"])
        self.day = 1
        self.template = 1
        self.listing_class = "tender"
        self.notices: dict = {}
        self.withdrawn: set = set()
        self.log: list = []
        self._day_requests = 0
        self._last_by_group: dict = {}
        self._lock = threading.Lock()
        self._seq = 0
        for _ in range(self.sc["n_initial"]):
            self._new_notice()

    # ------------------------------------------------------------------ data
    def _new_notice(self):
        self._seq += 1
        ministry = self.rng.choice(MINISTRIES)
        cat = self.rng.choice(CATEGORIES)
        ref = f"AJ-{MIN_CODE[ministry]}-2026-{self._seq:04d}"
        title = self.rng.choice(SUBJECTS[cat]).format(n=self.rng.randint(2, 40))
        first, last = self.rng.choice(FIRST), self.rng.choice(LAST)
        phone = f"080{self.rng.randint(3, 9)}{self.rng.randint(1000000, 9999999)}"
        n = {"reference": ref, "title": title, "ministry": ministry, "category": cat,
             "value": self.rng.randint(20, 900) * 250_000,
             "closing": dt.date(2026, 1, 1) + dt.timedelta(days=self.rng.randint(20, 90)),
             "status": "Open", "contact": f"{first} {last}, {phone[:4]} {phone[4:7]} {phone[7:]}, {first[0].lower()}.{last.lower()}@example.ng",
             "modified": self.clock.now(), "sitemap_modified": self.clock.now()}
        self.notices[ref] = n
        return ref

    def _amend(self, ref, silent=False):
        n = self.notices[ref]
        choice = self.rng.choice(["extend", "value", "cancel"])
        if choice == "extend":
            n["closing"] = n["closing"] + dt.timedelta(days=14)
        elif choice == "value":
            n["value"] = int(n["value"] * 1.1) // 1000 * 1000
        else:
            n["status"] = "Cancelled"
        n["modified"] = self.clock.now()
        if not silent:
            n["sitemap_modified"] = self.clock.now()

    def set_day(self, day: int):
        if day <= self.day:
            raise ValueError("days only move forward")
        while self.day < day:
            self.day += 1
            self.clock.advance(86400)
            ev = self.sc["days"].get(self.day, {})
            live = [r for r in sorted(self.notices) if r not in self.withdrawn]
            if ev.get("template"):
                self.template = ev["template"]
            if ev.get("listing_class"):
                self.listing_class = ev["listing_class"]
            k_amend, k_silent = ev.get("amend", 0), ev.get("silent_amend", 0)
            picks = self.rng.sample(live, k_amend + k_silent + ev.get("withdraw", 0))
            for r in picks[:k_amend]:
                self._amend(r)
            for r in picks[k_amend:k_amend + k_silent]:
                self._amend(r, silent=True)
            for r in picks[k_amend + k_silent:]:
                self.withdrawn.add(r)
                self.notices[r]["modified"] = self.clock.now()
                self.notices[r]["sitemap_modified"] = self.clock.now()
            for _ in range(ev.get("new", 0)):
                self._new_notice()
        self._day_requests = 0

    def truth(self) -> dict:
        """Ground truth of live notices (for tests): reference -> canonical fields."""
        out = {}
        for r, n in self.notices.items():
            if r in self.withdrawn:
                continue
            out[r] = {"reference": r, "title": n["title"], "ministry": n["ministry"], "category": n["category"],
                      "estimated_value_ngn": n["value"], "closing_date": n["closing"].isoformat(), "status": n["status"]}
        return out

    # ------------------------------------------------------------------ robots model (used to audit clients)
    def _group(self, ua: str) -> str:
        return "clbg-collector" if "clbg-collector" in (ua or "").lower() else "*"

    def _disallowed(self, path: str, group: str) -> bool:
        if path.startswith("/admin/") or path.startswith("/search"):
            return True
        if re.fullmatch(r"/tenders/[^/]+/print", path):
            return True
        if group == "clbg-collector" and re.match(r"^/tenders/[^/]+/bidders", path):
            return True
        return False

    def crawl_delay(self, group: str) -> float:
        return 2.0 if group == "clbg-collector" else 5.0

    def violations(self) -> dict:
        v = {"disallowed": [], "too_fast": [], "missing_contact_in_ua": 0}
        for e in self.log:
            if e["disallowed"]:
                v["disallowed"].append(e["path"])
            if e["too_fast"]:
                v["too_fast"].append(e["path"])
            if "@" not in e["ua"] and "http" not in e["ua"]:
                v["missing_contact_in_ua"] += 1
        return v

    # ------------------------------------------------------------------ rendering
    def _detail_html(self, n) -> str:
        v2 = self.template == 2
        t2 = self.sc.get("template_v2", {})
        rows = [("Reference", n["reference"]), ("Ministry", n["ministry"]), ("Category", n["category"])]
        vlabel = "Estimated value (₦)"
        vtext = f"{n['value']:,.2f}"
        dstyle = "long"
        if v2:
            vlabel = t2.get("rename", {}).get(vlabel, vlabel)
            vtext = t2.get("value_format", "{v:,.2f}").format(v=n["value"])
            dstyle = t2.get("date_format", "long")
        rows += [(vlabel, vtext), ("Closing date", _fmt_date(n["closing"], dstyle)), ("Status", n["status"]),
                 ("Contact officer", n["contact"])]
        if v2:
            renames = t2.get("rename", {})
            rows = [(renames.get(k, k), val) for k, val in rows]
            rows += list(t2.get("extra_rows", {}).items())
        trs = "\n".join(f"<tr><th>{html.escape(k)}</th><td>{html.escape(str(val))}</td></tr>" for k, val in rows)
        ref = n["reference"]
        return (f"<!doctype html><html><head><meta charset='utf-8'><title>Tender {ref}</title></head><body>\n"
                f"<nav><a href='/'>Home</a> | <a href='/tenders?page=1'>All tenders</a></nav>\n"
                f"<h1 class='tender-title'>{html.escape(n['title'])}</h1>\n<table class='notice'>\n{trs}\n</table>\n"
                f"<p><a href='/tenders/{ref}/print'>Print view</a> | <a href='/tenders/{ref}/bidders'>Bidders</a></p>\n"
                f"</body></html>\n")

    def _session(self):
        return "%08x" % self.rng.getrandbits(32)

    def _listing_html(self, page: int):
        live = sorted((r for r in self.notices if r not in self.withdrawn), reverse=True)
        ps = self.sc["page_size"]
        pages = max(1, -(-len(live) // ps))
        if page < 1 or page > pages:
            return None
        items = live[(page - 1) * ps: page * ps]
        lis = "\n".join(f"<li><a class='{self.listing_class}' href='/tenders/{r}?session={self._session()}'>{html.escape(self.notices[r]['title'])}</a>"
                        f" <span class='closing'>{_fmt_date(self.notices[r]['closing'], 'long')}</span></li>" for r in items)
        nxt = f"<a class='next' href='/tenders?page={page + 1}&amp;session={self._session()}'>Next</a>" if page < pages else ""
        prev_month = (dt.date(2026, 1, 1) - dt.timedelta(days=1)).strftime("%Y-%m")
        return (f"<!doctype html><html><head><meta charset='utf-8'><title>Tenders page {page}</title></head><body>\n"
                f"<h1>Open tenders</h1><ul class='tenders'>\n{lis}\n</ul>\n<p>{nxt}</p>\n"
                f"<p><a href='/tenders/archive/{prev_month}'>Archive</a> | <a href='/search?q='>Search</a> | <a href='/terms'>Terms</a></p>\n"
                f"</body></html>\n")

    def _archive_html(self, ym: str):
        y, m = map(int, ym.split("-"))
        prev = (dt.date(y, m, 1) - dt.timedelta(days=1)).strftime("%Y-%m")
        return (f"<html><body><h1>Archive {ym}</h1><p>No notices.</p>"
                f"<a href='/tenders/archive/{prev}'>Previous month</a></body></html>")

    def _sitemap(self):
        urls = []
        for r in sorted(self.notices):
            if r in self.withdrawn:
                continue
            lm = dt.datetime.fromtimestamp(self.notices[r]["sitemap_modified"], dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            urls.append(f"  <url><loc>/tenders/{r}</loc><lastmod>{lm}</lastmod></url>")
        return ('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
                + "\n".join(urls) + "\n</urlset>\n")

    # ------------------------------------------------------------------ HTTP
    def _respond(self, h, status, body: str = "", ctype="text/html; charset=utf-8", headers=None):
        data = body.encode("utf-8")
        h.send_response(status)
        h.send_header("Content-Type", ctype)
        h.send_header("Content-Length", str(len(data)))
        for k, v in (headers or {}).items():
            h.send_header(k, v)
        h.end_headers()
        if h.command != "HEAD":
            h.wfile.write(data)
        return status

    def handle(self, h):
        parts = urllib.parse.urlsplit(h.path)
        path, query = parts.path, dict(urllib.parse.parse_qsl(parts.query))
        ua = h.headers.get("User-Agent", "")
        group = self._group(ua)
        now = self.clock.now()
        with self._lock:
            self._day_requests += 1
            nreq = self._day_requests
            last = self._last_by_group.get(group)
            too_fast = last is not None and (now - last) < self.crawl_delay(group) - 1e-9 and path != "/robots.txt"
            if path != "/robots.txt":
                self._last_by_group[group] = now
            entry = {"t": now, "day": self.day, "path": path, "query": query, "ua": ua, "group": group,
                     "inm": h.headers.get("If-None-Match"), "ims": h.headers.get("If-Modified-Since"),
                     "disallowed": self._disallowed(path, group), "too_fast": too_fast, "status": None, "bytes": 0}
            self.log.append(entry)
        if too_fast and self.enforce:
            entry["status"] = self._respond(h, 429, "Too many requests", headers={"Retry-After": str(int(self.crawl_delay(group)))})
            return
        if nreq in self.sc.get("transient_503_at", []) and path != "/robots.txt":
            entry["status"] = self._respond(h, 503, "<html>Maintenance</html>", headers={"Retry-After": "4"})
            return
        status, body, ctype, headers = self._route(path, query, h)
        entry["status"] = self._respond(h, status, body, ctype, headers)
        entry["bytes"] = len(body.encode("utf-8"))

    def _route(self, path, query, h):
        if path == "/robots.txt":
            return 200, ROBOTS_TXT, "text/plain; charset=utf-8", {}
        if path == "/terms":
            return 200, TERMS_HTML, "text/html; charset=utf-8", {}
        if path == "/sitemap.xml":
            return 200, self._sitemap(), "application/xml", {}
        if path in ("/", "/tenders"):
            page = int(query.get("page", "1")) if query.get("page", "1").isdigit() else 0
            body = self._listing_html(page)
            return (200, body, "text/html; charset=utf-8", {}) if body else (404, "<html>No such page</html>", "text/html", {})
        m = re.fullmatch(r"/tenders/archive/(\d{4}-\d{2})", path)
        if m:
            return 200, self._archive_html(m.group(1)), "text/html; charset=utf-8", {}
        m = re.fullmatch(r"/tenders/([A-Z0-9-]+)(/print|/bidders)?", path)
        if m and m.group(1) in self.notices:
            ref, sub = m.group(1), m.group(2)
            if ref in self.withdrawn:
                return 410, "<html>This notice has been withdrawn.</html>", "text/html", {}
            n = self.notices[ref]
            if sub == "/bidders":
                return 200, "<html><body><h1>Bidders</h1><p>" + html.escape(n["contact"]) + "</p></body></html>", "text/html", {}
            body = self._detail_html(n)
            etag = '"' + hashlib.sha256(body.encode()).hexdigest()[:16] + '"'
            lm = format_datetime(dt.datetime.fromtimestamp(n["modified"], dt.timezone.utc), usegmt=True)
            hdrs = {"ETag": etag, "Last-Modified": lm, "Cache-Control": "max-age=0"}
            if h.headers.get("If-None-Match") == etag:
                return 304, "", "text/html", hdrs
            return 200, body, "text/html; charset=utf-8", hdrs
        return 404, "<html>Not found</html>", "text/html", {}

    def __enter__(self):
        portal = self

        class Handler(BaseHTTPRequestHandler):
            protocol_version = "HTTP/1.1"

            def log_message(self, *a):
                pass

            def do_GET(self):
                portal.handle(self)

            def do_HEAD(self):
                portal.handle(self)

        self.httpd = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.thread = threading.Thread(target=self.httpd.serve_forever, kwargs={"poll_interval": 0.05}, daemon=True)
        self.thread.start()
        self.base_url = f"http://127.0.0.1:{self.httpd.server_address[1]}"
        return self

    def __exit__(self, *exc):
        self.httpd.shutdown()
        self.httpd.server_close()

    def day_log(self, day=None):
        d = self.day if day is None else day
        return [e for e in self.log if e["day"] == d]


def _main(argv=None):
    """Generator contract: python tests/mocksite.py --out DIR --seed INT writes the scenario's truth per day."""
    import argparse
    import json
    from pathlib import Path
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--seed", type=int, default=PUBLIC_SCENARIO["seed"])
    ap.add_argument("--days", type=int, default=3)
    a = ap.parse_args(argv)
    sc = copy.deepcopy(PUBLIC_SCENARIO)
    sc["seed"] = a.seed
    portal = MockPortal(VirtualClock(), scenario=sc)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    for day in range(1, a.days + 1):
        if day > 1:
            portal.set_day(day)
        (out / f"truth_day{day}.json").write_text(json.dumps(portal.truth(), indent=1, sort_keys=True) + "\n",
                                                   encoding="utf-8")


if __name__ == "__main__":
    _main()
