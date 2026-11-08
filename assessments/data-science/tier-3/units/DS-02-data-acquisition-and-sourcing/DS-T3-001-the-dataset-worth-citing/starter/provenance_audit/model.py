"""Implement the functions below. Signatures are fixed; the internals are yours."""
from __future__ import annotations

from pathlib import Path

from .types import Catalogue, Finding


def load_catalogue(root) -> Catalogue:
    """Read <root>/catalogue.json into a Catalogue (R1)."""
    raise NotImplementedError("R1: load catalogue.json into Dataset objects")


def effective_license(cat: Catalogue, dataset_id: str) -> str:
    """The licence a careful user must assume, or BLOCKED / CONFLICT / UNRESOLVED (R2)."""
    raise NotImplementedError("R2: propagate licence obligations through derived_from")


def audit(cat: Catalogue) -> list:
    """All Findings, sorted by (dataset_id, code) (R3-R5)."""
    raise NotImplementedError("R3: licence findings; R4: integrity findings; R5: provenance findings")


def can_use(cat: Catalogue, dataset_id: str, purpose: str) -> bool:
    """purpose is 'commercial' or 'closed_derivative' (R6)."""
    raise NotImplementedError("R6: map the effective licence to permitted purposes")


def required_attribution(cat: Catalogue, dataset_id: str) -> list:
    """Sorted titles of every upstream dataset (transitive) that must be credited (R7)."""
    raise NotImplementedError("R7: transitive credit list")
