"""R6: an append-only JSON Lines provenance log."""
from __future__ import annotations

import time
from pathlib import Path
from typing import Callable, Optional

REQUIRED_FIELDS = ("ts", "url", "attempt", "outcome", "status", "sha256", "bytes", "lastupdated")
OUTCOMES = frozenset({"ok", "retry", "fail", "cache_hit"})


class ProvenanceLog:
    def __init__(self, path, clock: Callable[[], float] = time.time):
        self.path = Path(path)
        self.clock = clock
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def record(self, *, url: str, attempt: int, outcome: str, status: Optional[int] = None,
               sha256: Optional[str] = None, bytes: Optional[int] = None,  # noqa: A002 - field name is fixed
               lastupdated: Optional[str] = None, **extra) -> dict:
        """Append one JSON line containing every field in REQUIRED_FIELDS plus any extras, and return the entry."""
        raise NotImplementedError("R6: ProvenanceLog.record")

    def entries(self) -> list:
        """Read the log back as a list of dicts, in order."""
        raise NotImplementedError("R6: ProvenanceLog.entries")
