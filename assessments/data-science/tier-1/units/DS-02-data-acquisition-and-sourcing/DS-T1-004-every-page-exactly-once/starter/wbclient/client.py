"""R7 and R8: the resilient client."""
from __future__ import annotations

import random
import time
from typing import Callable, Iterable, Optional

from .types import FetchResult, Page, RetryPolicy
from .urls import DEFAULT_BASE


class WorldBankClient:
    def __init__(self, transport, *, cache=None, provenance=None, policy: RetryPolicy = RetryPolicy(),
                 clock: Callable[[], float] = time.time, sleep: Callable[[float], None] = time.sleep,
                 rng: Optional[random.Random] = None, cache_max_age: Optional[float] = 86400.0,
                 timeout: float = 30.0, base: str = DEFAULT_BASE):
        self.transport = transport
        self.cache = cache
        self.provenance = provenance
        self.policy = policy
        self.clock = clock
        self.sleep = sleep
        self.rng = rng if rng is not None else random.Random()
        self.cache_max_age = cache_max_age
        self.timeout = timeout
        self.base = base

    def fetch_page(self, url: str, *, use_cache: bool = True) -> Page:
        """Fetch and parse one page: cache first, then the transport with retries. See README R7."""
        raise NotImplementedError("R7: WorldBankClient.fetch_page")

    def fetch_indicator(self, indicator: str, countries: Iterable[str], *, date: Optional[str] = None,
                        per_page: int = 1000) -> FetchResult:
        """Fetch every page of a query as one consistent snapshot. See README R8."""
        raise NotImplementedError("R8: WorldBankClient.fetch_indicator")
