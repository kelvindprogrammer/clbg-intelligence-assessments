"""R1: canonical request URLs and cache keys."""
from __future__ import annotations

from typing import Iterable, Optional

DEFAULT_BASE = "https://api.worldbank.org/v2"


def build_url(indicator: str, countries: Iterable[str], *, date: Optional[str] = None, page: int = 1,
              per_page: int = 1000, base: str = DEFAULT_BASE) -> str:
    """Return the canonical API URL for one page of one indicator query.

    Canonical means: two logically identical requests produce byte-identical URLs. See README R1 for
    the exact form (country order, case, duplicates, query-parameter order and encoding), and for the
    inputs that must be rejected with ValueError.
    """
    raise NotImplementedError("R1: build_url")


def canonical_key(url: str) -> str:
    """Return a 64-character hex cache key that does not depend on query-parameter order or host case."""
    raise NotImplementedError("R1: canonical_key")
