"""R1: robots.txt as specified by RFC 9309 (https://www.rfc-editor.org/rfc/rfc9309).

Note: the standard library's urllib.robotparser does not implement everything this portal uses. Find
out what it lacks before deciding whether to use it.
"""
from __future__ import annotations

from typing import Optional


class Robots:
    def __init__(self, text: str):
        self.text = text

    def allowed(self, product_token: str, path: str) -> bool:
        """May a client identifying as `product_token` fetch `path`?"""
        raise NotImplementedError("R1: Robots.allowed")

    def crawl_delay(self, product_token: str) -> Optional[float]:
        """The Crawl-delay that applies to `product_token`, or None."""
        raise NotImplementedError("R1: Robots.crawl_delay")
