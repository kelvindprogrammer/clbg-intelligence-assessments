"""R2: parse one World Bank API v2 JSON page."""
from __future__ import annotations

from .types import MalformedResponse, Observation, Page, PageMeta, WorldBankAPIError  # noqa: F401


def parse_page(body: bytes) -> Page:
    """Parse a raw response body into a Page.

    Raise WorldBankAPIError for the API's error envelope and MalformedResponse for anything that is
    not a well-formed [metadata, records] page. Missing values stay None. See README R2.
    """
    raise NotImplementedError("R2: parse_page")
