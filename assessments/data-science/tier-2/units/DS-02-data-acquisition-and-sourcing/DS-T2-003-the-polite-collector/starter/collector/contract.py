"""The public contract for DS-T2-003 (provided; the tests depend on these names and fields)."""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

RECORD_FIELDS = ["reference", "title", "ministry", "category", "estimated_value_ngn", "closing_date", "status",
                 "url", "first_seen", "last_changed", "content_hash", "withdrawn"]
ALARM_KINDS = {"missing_field", "new_field", "unparseable_value", "listing_changed"}


@dataclass
class CollectorConfig:
    base_url: str
    state_dir: Path
    user_agent: str = "clbg-collector/1.0 (+mailto:member@example.ng)"
    clock: Callable[[], float] = time.time
    sleep: Callable[[float], None] = time.sleep
    strategy: str = "conditional"     # you must support "conditional"; name your others in the README
    min_delay: float = 1.0            # a floor: the effective delay is max(min_delay, robots Crawl-delay)
    max_requests: int = 500           # hard budget per run
    max_listing_pages: int = 50       # hard bound on listing pages per run


@dataclass
class RunReport:
    new: list = field(default_factory=list)
    updated: list = field(default_factory=list)
    withdrawn: list = field(default_factory=list)
    unchanged: list = field(default_factory=list)
    quarantined: list = field(default_factory=list)
    drift_alarms: list = field(default_factory=list)  # dicts: kind, field, count, example_url
    requests: int = 0
    not_modified: int = 0
    bytes: int = 0
    errors: list = field(default_factory=list)
