"""R5: an on-disk response cache with expiry, integrity checks and atomic writes."""
from __future__ import annotations

import time
from pathlib import Path
from typing import Callable, Optional


class ResponseCache:
    def __init__(self, root, clock: Callable[[], float] = time.time):
        self.root = Path(root)
        self.clock = clock
        self.root.mkdir(parents=True, exist_ok=True)

    def put(self, key: str, body: bytes, meta: Optional[dict] = None) -> None:
        """Store `body` (and `meta`) under `key`. A crash mid-write must never leave a readable partial entry."""
        raise NotImplementedError("R5: ResponseCache.put")

    def get(self, key: str, max_age: Optional[float] = None) -> Optional[bytes]:
        """Return the stored body, or None if absent, older than max_age seconds, or failing its integrity check."""
        raise NotImplementedError("R5: ResponseCache.get")
