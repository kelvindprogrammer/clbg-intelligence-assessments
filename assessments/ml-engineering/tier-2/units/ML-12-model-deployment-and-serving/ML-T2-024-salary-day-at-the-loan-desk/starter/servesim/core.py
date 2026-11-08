from dataclasses import dataclass


@dataclass(frozen=True)
class Policy:
    """max_batch: most requests in one model call. max_wait_ms: longest the oldest queued request waits for the
    batch to fill. queue_cap: most requests allowed to wait (arrivals beyond it are shed, not queued)."""
    max_batch: int
    max_wait_ms: float
    queue_cap: int
