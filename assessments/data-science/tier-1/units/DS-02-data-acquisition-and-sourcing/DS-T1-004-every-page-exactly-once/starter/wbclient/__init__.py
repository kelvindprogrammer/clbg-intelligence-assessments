"""wbclient: a resilient, cache-aware, provenance-logging client for the World Bank Indicators API v2.

The public API is fixed because the tests import it. Implement each piece in its module.
"""
from .types import (FetchResult, HTTPStatusError, InconsistentPagination, MalformedResponse, Observation, Page,
                    PageMeta, Response, RetryExhausted, RetryPolicy, TransportError, WBClientError,
                    WorldBankAPIError)
from .transport import OfflineTransport, Transport, UrllibTransport
from .urls import build_url, canonical_key
from .parse import parse_page
from .retry import RETRYABLE_STATUSES, backoff_delay, is_retryable, parse_retry_after
from .cache import ResponseCache
from .provenance import ProvenanceLog
from .client import WorldBankClient
from .frame import to_frame

__all__ = [
    "FetchResult", "HTTPStatusError", "InconsistentPagination", "MalformedResponse", "Observation", "Page",
    "PageMeta", "Response", "RetryExhausted", "RetryPolicy", "TransportError", "WBClientError",
    "WorldBankAPIError", "OfflineTransport", "Transport", "UrllibTransport", "build_url", "canonical_key",
    "parse_page", "RETRYABLE_STATUSES", "backoff_delay", "is_retryable", "parse_retry_after", "ResponseCache",
    "ProvenanceLog", "WorldBankClient", "to_frame",
]
