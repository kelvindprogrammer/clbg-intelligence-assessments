"""Shared data types and exceptions for wbclient (provided; do not change the public names)."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass(frozen=True)
class Response:
    """One raw HTTP response as returned by a Transport."""
    status: int
    headers: dict  # header names are lower-case
    body: bytes


@dataclass(frozen=True)
class PageMeta:
    page: int
    pages: int
    per_page: int
    total: int
    lastupdated: Optional[str]


@dataclass(frozen=True)
class Observation:
    indicator_id: str
    country_iso3: str
    date: str
    value: Optional[float]
    obs_status: Optional[str]


@dataclass(frozen=True)
class Page:
    meta: PageMeta
    records: list


@dataclass(frozen=True)
class RetryPolicy:
    max_attempts: int = 5          # total attempts per page, including the first
    base_delay: float = 0.5        # seconds
    max_delay: float = 30.0        # cap for computed (jittered) backoff
    max_retry_after: float = 120.0  # give up rather than wait longer than this for a server-requested delay


@dataclass
class FetchResult:
    observations: list
    lastupdated: Optional[str]
    pages: int
    restarted: bool = False
    urls: list = field(default_factory=list)


class WBClientError(Exception):
    """Base class for all wbclient errors."""


class TransportError(WBClientError):
    """The request never produced an HTTP response (DNS failure, refused or reset connection, timeout)."""


class MalformedResponse(WBClientError):
    """An HTTP 200 whose body is not a World Bank JSON page (e.g. an HTML maintenance page or truncated JSON)."""


class WorldBankAPIError(WBClientError):
    """The API answered with its error envelope: [{"message": [{"id": ..., "key": ..., "value": ...}]}]."""

    def __init__(self, code: str, key: str, message: str):
        super().__init__(f"World Bank API error {code} ({key}): {message}")
        self.code, self.key, self.message = code, key, message


class HTTPStatusError(WBClientError):
    """A non-retryable HTTP status such as 400, 403 or 404."""

    def __init__(self, status: int, url: str):
        super().__init__(f"HTTP {status} for {url}")
        self.status, self.url = status, url


class RetryExhausted(WBClientError):
    """Retries were used up, or the server asked us to wait longer than policy.max_retry_after."""


class InconsistentPagination(WBClientError):
    """The pages of one query do not describe one consistent snapshot, even after one restart."""
