"""R3 and R4: which failures are retried, and how long to wait."""
from __future__ import annotations

import datetime as dt
import random
from typing import Optional

from .types import RetryPolicy

RETRYABLE_STATUSES = frozenset()  # R3: fill in, and justify each status in your report


def is_retryable(status: Optional[int], error: Optional[BaseException] = None) -> bool:
    """True if a failed attempt (an HTTP status, or an exception raised while fetching or parsing) may be retried."""
    raise NotImplementedError("R3: is_retryable")


def parse_retry_after(value: Optional[str], now: dt.datetime) -> Optional[float]:
    """Seconds to wait according to a Retry-After header value (either form allowed by RFC 9110), or None."""
    raise NotImplementedError("R4: parse_retry_after")


def backoff_delay(attempt: int, policy: RetryPolicy, rng: random.Random,
                  retry_after: Optional[float] = None) -> float:
    """Delay before the next attempt after failed attempt number `attempt` (1-based). See README R4."""
    raise NotImplementedError("R4: backoff_delay")
