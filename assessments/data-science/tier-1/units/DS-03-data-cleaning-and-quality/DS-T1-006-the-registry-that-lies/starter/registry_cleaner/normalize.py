"""Value-level normalisers (requirements R1–R7).

Every function here takes ONE raw string value from the export and returns
either a canonical value or None. None means "missing or not confidently
recoverable". Never guess. The README explains why that matters.

Write your rules from evidence you gathered while profiling, and pin each one
with a test in tests/test_member_*.py.
"""
from __future__ import annotations

from pathlib import Path
from typing import Optional

from .types import ParsedDate

def _find_resources() -> Path:
    """Provided helper: find resources/reference in this directory or any parent."""
    for parent in Path(__file__).resolve().parents:
        candidate = parent / "resources" / "reference"
        if candidate.is_dir():
            return candidate
    raise FileNotFoundError("resources/reference not found. Keep resources/ next to your package.")


RESOURCES = _find_resources()


def _load_reference(name: str) -> list[str]:
    """Provided helper: read a reference list such as nigerian_states.txt."""
    return [ln.strip() for ln in (RESOURCES / name).read_text(encoding="utf-8").splitlines() if ln.strip()]


CANONICAL_STATES = _load_reference("nigerian_states.txt")
CANONICAL_DEPARTMENTS = _load_reference("departments.txt")


def is_missing(value: object) -> bool:
    """R1: True if `value` is one of the export's missing-value tokens (or None/NaN)."""
    raise NotImplementedError("R1: implement is_missing")


def normalize_state(value: object) -> Optional[str]:
    """R2: map a raw state string to one of CANONICAL_STATES, or None."""
    raise NotImplementedError("R2: implement normalize_state")


def normalize_department(value: object) -> Optional[str]:
    """R3: map a raw department string to one of CANONICAL_DEPARTMENTS, or None."""
    raise NotImplementedError("R3: implement normalize_department")


def normalize_phone(value: object) -> Optional[str]:
    """R4: return '+234XXXXXXXXXX' for a valid Nigerian mobile number, else None."""
    raise NotImplementedError("R4: implement normalize_phone")


def parse_name(value: object) -> Optional[tuple[str, str]]:
    """R5: return (first_name, last_name) in title case, or None."""
    raise NotImplementedError("R5: implement parse_name")


def parse_date(value: object, *, field: str) -> ParsedDate:
    """R6: parse a raw date string.

    `field` is 'date_of_birth' or 'admission_date'. Ambiguity rules apply to
    date_of_birth only (see README R6).
    """
    raise NotImplementedError("R6: implement parse_date")


def parse_score(value: object) -> Optional[int]:
    """R7: return a valid UTME score (0–400) or None. Never clip."""
    raise NotImplementedError("R7: implement parse_score")
