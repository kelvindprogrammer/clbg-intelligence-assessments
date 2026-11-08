"""Data types (provided). Do not change the field names."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class Dataset:
    id: str
    title: str
    publisher: str
    declared_license: str
    derived_from: tuple
    file: str
    sha256: str
    rows: int
    attribution: str


@dataclass(frozen=True)
class Catalogue:
    root: Path
    datasets: dict = field(default_factory=dict)


@dataclass(frozen=True, order=True)
class Finding:
    dataset_id: str
    code: str
