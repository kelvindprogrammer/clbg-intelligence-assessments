"""Offline test doubles for the World Bank Indicators API (provided test infrastructure; do not edit).

* ScriptedTransport: an in-memory Transport that replays a script of Responses and exceptions.
* FakeWorldBank: a real HTTP server on 127.0.0.1 that serves recorded API data with the same
  paging rules, error envelope and XML default as the live API, plus scriptable faults.

The recorded data in resources/fixtures/ was fetched from https://api.worldbank.org/v2 on
2026-11-03 (WDI lastupdated 2026-10-08). World Bank data is licensed CC BY 4.0.
"""
from __future__ import annotations

import json
import math
import threading
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


class ScriptedTransport:
    """Replays `script` in order. Each item is a Response-like object or an exception instance to raise."""

    def __init__(self, script):
        self.script = list(script)
        self.calls = []

    def get(self, url, headers, timeout):
        self.calls.append(url)
        if not self.script:
            raise AssertionError(f"unexpected extra request: {url}")
        item = self.script.pop(0)
        if isinstance(item, BaseException):
            raise item
        return item


def load_fixture(path) -> tuple[dict, list]:
    doc = json.loads(Path(path).read_text(encoding="utf-8"))
    return doc[0], doc[1]


class FakeWorldBank:
    """A local stand-in for https://api.worldbank.org/v2.

    Use as a context manager. `base` is the value to pass as the client's `base`.

    Faults: append to `faults`; each request to a data path pops the next fault, if any:
        ("status", code, headers_dict, body_bytes)   respond with this status
        ("body", body_bytes)                         respond 200 with this body
        ("drop",)                                    close the connection without a response
        ("ok",)                                      serve normally
    Drift: set `bump_lastupdated_after = n` to change `lastupdated` after n normally served pages
    (once), or `bump_every = n` to change it after every n pages.
    """

    def __init__(self, fixtures: dict):
        self.data = {}
        for indicator, path in fixtures.items():
            meta, records = load_fixture(path)
            self.data[indicator] = (meta.get("lastupdated"), records)
        self.faults = []
        self.requests = []
        self.served_pages = 0
        self.bump_lastupdated_after = None
        self.bump_every = None
        self._bumps = 0
        self._lock = threading.Lock()

    # ------------------------------------------------------------ server plumbing
    def __enter__(self):
        fake = self

        class Handler(BaseHTTPRequestHandler):
            protocol_version = "HTTP/1.1"

            def log_message(self, *args):  # silence
                pass

            def do_GET(self):
                fake._handle(self)

        self.httpd = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.thread = threading.Thread(target=self.httpd.serve_forever, daemon=True)
        self.thread.start()
        self.base = f"http://127.0.0.1:{self.httpd.server_address[1]}/v2"
        return self

    def __exit__(self, *exc):
        self.httpd.shutdown()
        self.httpd.server_close()

    # ------------------------------------------------------------ behaviour
    def _lastupdated(self, original):
        if not self._bumps:
            return original
        return f"2026-12-{self._bumps:02d}"

    def _send(self, h, status, body: bytes, headers=None, ctype="application/json;charset=utf-8"):
        h.send_response(status)
        h.send_header("Content-Type", ctype)
        h.send_header("Content-Length", str(len(body)))
        for k, v in (headers or {}).items():
            h.send_header(k, v)
        h.end_headers()
        h.wfile.write(body)

    def _handle(self, h):
        parts = urllib.parse.urlsplit(h.path)
        query = dict(urllib.parse.parse_qsl(parts.query))
        with self._lock:
            self.requests.append({"path": parts.path, "query": query, "headers": dict(h.headers)})
            fault = self.faults.pop(0) if self.faults else ("ok",)
        segs = [s for s in parts.path.split("/") if s]
        if len(segs) != 5 or segs[0] != "v2" or segs[1] != "country" or segs[3] != "indicator":
            return self._send(h, 404, b"<html>not found</html>", ctype="text/html")
        kind = fault[0]
        if kind == "drop":
            h.close_connection = True
            return
        if kind == "status":
            _, code, headers, body = fault
            return self._send(h, code, body, headers, ctype="text/html")
        if kind == "body":
            return self._send(h, 200, fault[1])
        if query.get("format", "").lower() != "json":
            xml = b'<?xml version="1.0" encoding="utf-8"?><wb:data page="1" pages="1" xmlns:wb="http://www.worldbank.org"/>'
            return self._send(h, 200, xml, ctype="application/xml;charset=utf-8")
        indicator = segs[4]
        if indicator not in self.data:
            err = [{"message": [{"id": "120", "key": "Invalid value", "value": "The provided parameter value is not valid"}]}]
            return self._send(h, 200, json.dumps(err).encode())
        original, records = self.data[indicator]
        codes = {c.upper() for c in segs[2].split(";")}
        recs = [r for r in records if r["countryiso3code"].upper() in codes]
        if "date" in query:
            lo, _, hi = query["date"].partition(":")
            hi = hi or lo
            recs = [r for r in recs if lo <= r["date"] <= hi]
        per_page = int(query.get("per_page", 50))
        page = int(query.get("page", 1))
        total = len(recs)
        pages = math.ceil(total / per_page) if total else 0
        with self._lock:
            lastupdated = self._lastupdated(original)
            chunk = recs[(page - 1) * per_page: page * per_page]
            self.served_pages += 1
            if self.bump_lastupdated_after is not None and self.served_pages == self.bump_lastupdated_after:
                self._bumps += 1
            if self.bump_every and self.served_pages % self.bump_every == 0:
                self._bumps += 1
        meta = {"page": page, "pages": pages, "per_page": per_page, "total": total, "sourceid": "2",
                "lastupdated": lastupdated}
        body = json.dumps([meta, chunk if total else None]).encode()
        return self._send(h, 200, body)

    def data_requests(self):
        return [r for r in self.requests if "/indicator/" in r["path"]]
