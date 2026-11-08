"""HTTP transport (provided plumbing).

A Transport has one method, get(url, headers, timeout) -> Response. It must:
  * return a Response for ANY HTTP status, including 4xx and 5xx;
  * raise TransportError when no HTTP response was obtained at all.

The client never imports urllib directly, so tests can swap in a fake transport.
"""
from __future__ import annotations

import http.client
import socket
import urllib.error
import urllib.request
from typing import Protocol

from .types import Response, TransportError

USER_AGENT = "clbg-wbclient/1.0 (+mailto:member@example.ng)"


class Transport(Protocol):
    def get(self, url: str, headers: dict, timeout: float) -> Response: ...


class UrllibTransport:
    """Standard-library transport. Works against the real API and the local fake server."""

    def get(self, url: str, headers: dict, timeout: float) -> Response:
        hdrs = {"User-Agent": USER_AGENT, "Accept": "application/json"}
        hdrs.update(headers or {})
        req = urllib.request.Request(url, headers=hdrs, method="GET")
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return Response(resp.status, {k.lower(): v for k, v in resp.headers.items()}, resp.read())
        except urllib.error.HTTPError as e:  # an HTTP response with an error status
            body = e.read() if hasattr(e, "read") else b""
            return Response(e.code, {k.lower(): v for k, v in (e.headers or {}).items()}, body)
        except (urllib.error.URLError, socket.timeout, TimeoutError, ConnectionError,
                http.client.HTTPException) as e:
            raise TransportError(f"{type(e).__name__}: {e}") from e


class OfflineTransport:
    """A transport that refuses every request. Used by the CLI's --offline mode."""

    def get(self, url: str, headers: dict, timeout: float) -> Response:
        raise TransportError(f"offline mode: {url} is not in the cache")
