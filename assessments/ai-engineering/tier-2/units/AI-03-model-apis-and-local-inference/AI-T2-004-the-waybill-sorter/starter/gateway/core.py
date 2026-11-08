"""Provider gateway for the waybill sorter. Interfaces are fixed; policy choices are yours."""
from __future__ import annotations


def normalise_key(text: str) -> str:
    """R1: cache key. Lowercase, collapse runs of whitespace, strip ' .,;:!?' from both ends."""
    raise NotImplementedError("R1: normalise_key")


def plan_batches(texts, size: int) -> list[list[str]]:
    """R2: unique normalised keys in first-seen order, chunked into lists of at most `size`."""
    raise NotImplementedError("R2: plan_batches")


class RateLimiter:
    """R3: client-side mirror of a provider's sliding 60 s window (requests and prompt tokens)."""

    def __init__(self, rpm: int, tpm: int, clock):
        self.rpm, self.tpm, self.clock = rpm, tpm, clock

    def wait_time(self, tokens: int) -> float:
        """Seconds to wait before a request of `tokens` prompt tokens is admissible (0.0 if now).
        Raise ValueError if tokens > tpm."""
        raise NotImplementedError("R3: wait_time")

    def commit(self, tokens: int, at: float | None = None) -> None:
        """Record a request sent at `at` (default: now)."""
        raise NotImplementedError("R3: commit")

    def acquire(self, tokens: int) -> None:
        """Sleep on the clock until admissible, then commit."""
        raise NotImplementedError("R3: acquire")


class BudgetExceeded(Exception):
    pass


class Gateway:
    """R4/R5: classify waybills through an ordered list of providers.

    Attributes after construction: `stats` with cost_kobo, calls (dict provider name -> accepted calls),
    cache_hits, makespan_s (virtual seconds spent inside classify_all, cumulative); `cache` (dict).
    """

    def __init__(self, providers, clock, batch_size: int = 5, cooldown: float = 30.0, budget_kobo: float | None = None):
        self.providers, self.clock = list(providers), clock
        self.batch_size, self.cooldown, self.budget = batch_size, cooldown, budget_kobo
        raise NotImplementedError("R4: construct limiters, cache and stats")

    def classify_all(self, texts) -> list[str]:
        """Return one label per input text, in order. See the README for the required behaviour."""
        raise NotImplementedError("R4: classify_all")


def choose_batch_size(make_provider, dev_texts, dev_labels, candidates=(1, 2, 4, 6, 8, 10, 12), min_accuracy=0.96) -> int:
    """R6: measure accuracy on labelled dev data with fresh providers; return the largest passing candidate."""
    raise NotImplementedError("R6: choose_batch_size")
