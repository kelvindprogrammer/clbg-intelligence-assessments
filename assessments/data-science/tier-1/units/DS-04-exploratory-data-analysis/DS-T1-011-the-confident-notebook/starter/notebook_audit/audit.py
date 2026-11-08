"""Validation of audit.json (provided complete in the starter)."""
from __future__ import annotations

import json
import math
from pathlib import Path

from .io import CLAIM_IDS, FLAWS, VERDICTS


def validate_audit(path: str | Path) -> list[dict]:
    """Load audit.json and check its structure. Returns the list of entries or raises ValueError."""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError("audit.json must be a JSON list")
    ids = [e.get("claim_id") for e in data]
    if sorted(ids, key=lambda s: int(s[1:])) != CLAIM_IDS:
        raise ValueError(f"audit.json must contain each of {CLAIM_IDS} exactly once")
    for e in data:
        if e.get("verdict") not in VERDICTS:
            raise ValueError(f"{e['claim_id']}: verdict must be one of {VERDICTS}")
        if e.get("flaw") not in FLAWS:
            raise ValueError(f"{e['claim_id']}: flaw must be one of {FLAWS}")
        if (e["verdict"] == "supported") != (e["flaw"] == "none"):
            raise ValueError(f"{e['claim_id']}: use flaw 'none' exactly when the verdict is 'supported'")
        v = e.get("corrected_value")
        if not isinstance(v, (int, float)) or isinstance(v, bool) or not math.isfinite(v):
            raise ValueError(f"{e['claim_id']}: corrected_value must be a finite number")
        if not isinstance(e.get("evidence"), str) or len(e["evidence"].split()) < 15:
            raise ValueError(f"{e['claim_id']}: evidence must be a sentence or more (at least 15 words)")
    return data
