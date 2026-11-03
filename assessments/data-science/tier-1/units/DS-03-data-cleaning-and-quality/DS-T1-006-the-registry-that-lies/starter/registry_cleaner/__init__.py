"""registry_cleaner: forensic cleaning for the DS-T1-006 student registry export.

The public API is fixed because the tests import it. Implement each function in its module.
"""
from .types import CleanResult, ParsedDate
from .normalize import (
    is_missing,
    normalize_department,
    normalize_phone,
    normalize_state,
    parse_date,
    parse_name,
    parse_score,
)
from .dedupe import find_duplicate_groups
from .pipeline import clean_registry, load_export

__all__ = [
    "CleanResult", "ParsedDate", "is_missing", "normalize_department", "normalize_phone",
    "normalize_state", "parse_date", "parse_name", "parse_score", "find_duplicate_groups",
    "clean_registry", "load_export",
]
