"""Shared helpers for the CLBG repository tooling.

The validator, catalogue builder, link checker, test runner and rubric tools all
import this module. Its only third-party dependency is PyYAML (and jsonschema
when the schema is validated).
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterator

import yaml

ROOT = Path(__file__).resolve().parents[2]
ASSESSMENT_ROOTS = ("assessments", "cross-disciplinary", "signature-challenges")

SUBTRACK_DIRS = {
    "data-science": "DS",
    "ml-engineering": "ML",
    "ai-engineering": "AI",
}

# Every assessment README must contain these level-2 headings, in this order.
# The lettering follows the CLBG standard specification (docs/assessment-policy.md section 4).
REQUIRED_SECTIONS = [
    ("A", "Identification"),
    ("B", "Problem Statement"),
    ("C", "Objectives"),
    ("D", "Technical Requirements"),
    ("E", "Dataset and Resources"),
    ("F", "Deliverables"),
    ("G", "Acceptance Criteria"),
    ("H", "Evaluation Rubric"),
    ("I", "Submission Instructions"),
    ("J", "Extension Challenges"),
    ("K", "Assessment Integrity"),
]
PEDAGOGY_SECTION = "Pedagogical Design"

# Minimum number of words a section needs before it counts as substantive.
SECTION_MIN_WORDS = {
    "A": 40, "B": 120, "C": 40, "D": 120, "E": 40, "F": 40,
    "G": 60, "H": 20, "I": 40, "J": 30, "K": 40,
}

HEADING_RE = re.compile(r"^##\s+(?:([A-K])\.\s+)?(.+?)\s*$", re.MULTILINE)
DIR_NAME_RE = re.compile(
    r"^((?:DS|ML|AI|XD)-T[123]-[0-9]{3}|(?:DS|ML|AI)-CAP-T[123]-[0-9]{2}|SIG-[A-Z]{2,4}-[0-9]{2})-[a-z0-9]+(?:-[a-z0-9]+)*$"
)


@dataclass
class Assessment:
    path: Path
    meta: dict
    readme: str = ""
    errors: list[str] = field(default_factory=list)

    @property
    def id(self) -> str:
        return str(self.meta.get("id", "?"))

    @property
    def rel(self) -> str:
        return self.path.relative_to(ROOT).as_posix()


def _stringify_dates(obj):
    """YAML parses bare dates as datetime.date objects. Normalise them to ISO strings for schema validation."""
    import datetime as _dt
    if isinstance(obj, dict):
        return {k: _stringify_dates(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_stringify_dates(v) for v in obj]
    if isinstance(obj, (_dt.date, _dt.datetime)):
        return obj.isoformat()
    return obj


def load_yaml(path: Path):
    with open(path, encoding="utf-8") as fh:
        return _stringify_dates(yaml.safe_load(fh))


def load_units() -> dict:
    data = load_yaml(ROOT / "shared" / "units.yaml")
    return {u["code"]: u for u in data["units"]}


def load_subtracks() -> dict:
    return load_yaml(ROOT / "shared" / "units.yaml")["subtracks"]


def iter_assessment_dirs(root: Path = ROOT) -> Iterator[Path]:
    for base in ASSESSMENT_ROOTS:
        b = root / base
        if not b.exists():
            continue
        for meta in sorted(b.rglob("metadata.yaml")):
            # metadata.yaml files inside starter/ or resources/ are not assessments.
            if any(part in {"starter", "resources", "submission-template", "tests"} for part in meta.parent.relative_to(b).parts):
                continue
            yield meta.parent


def load_assessments(root: Path = ROOT) -> list[Assessment]:
    out = []
    for d in iter_assessment_dirs(root):
        try:
            meta = load_yaml(d / "metadata.yaml") or {}
        except yaml.YAMLError as exc:  # pragma: no cover - reported by validator
            a = Assessment(d, {})
            a.errors.append(f"metadata.yaml is not valid YAML: {exc}")
            out.append(a)
            continue
        readme_path = d / "README.md"
        readme = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""
        out.append(Assessment(d, meta, readme))
    return out


def split_sections(markdown: str) -> dict[str, str]:
    """Split a README into {letter-or-title: body} using level-2 headings."""
    sections: dict[str, str] = {}
    matches = list(HEADING_RE.finditer(markdown))
    for i, m in enumerate(matches):
        letter, title = m.group(1), m.group(2)
        key = letter if letter else title.strip()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(markdown)
        sections[key] = markdown[m.end():end]
        if letter:
            sections[f"__title_{letter}"] = title.strip()
    return sections


def word_count(text: str) -> int:
    text = re.sub(r"```.*?```", " code ", text, flags=re.S)
    return len(re.findall(r"[A-Za-z0-9][A-Za-z0-9'’\-]*", text))


RUBRIC_ROW_RE = re.compile(r"^\|\s*(\d+)\s*\|\s*([^|]+?)\s*\|\s*(\d+)\s*\|", re.MULTILINE)


def parse_rubric_weights(text: str) -> list[tuple[str, int]]:
    """Return [(dimension, weight)] from the weighted rubric table.

    The rubric table's first three columns must be: `# | Dimension | Points | ...`.
    """
    return [(m.group(2), int(m.group(3))) for m in RUBRIC_ROW_RE.finditer(text)]


def expected_dir_prefix(meta: dict) -> str:
    return str(meta.get("id", ""))
