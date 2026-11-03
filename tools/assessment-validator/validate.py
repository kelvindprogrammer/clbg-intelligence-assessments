#!/usr/bin/env python3
"""CLBG assessment validator.

Checks every assessment directory against the repository standard:
metadata schema, ID/location/naming consistency, required README sections and
their substance, rubric weights, declared resources, dataset references and
forbidden placeholder text.

Usage:
    python tools/assessment-validator/validate.py            # validate all
    python tools/assessment-validator/validate.py --strict   # warnings fail too
    python tools/assessment-validator/validate.py --only DS-T1-001 ML-T2-003

The exit code is 0 when there are no errors (and no warnings under --strict), otherwise 1.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))
import clbgtools as ct  # noqa: E402

try:
    import jsonschema
except ImportError:  # pragma: no cover
    jsonschema = None

FORBIDDEN_PATTERNS = [
    (re.compile(r"lorem ipsum", re.I), "placeholder text 'lorem ipsum'"),
    (re.compile(r"\bTBD\b"), "unresolved 'TBD'"),
    (re.compile(r"\[insert[^\]]*\]", re.I), "unresolved '[insert ...]' placeholder"),
    (re.compile(r"co-authored-by", re.I), "attribution trailer text"),
    (re.compile(r"as an ai language model", re.I), "boilerplate model text"),
]

SIG_CATEGORIES = {
    "SIG-INT": "intelligence-challenges",
    "SIG-DATA": "data-challenges",
    "SIG-ML": "machine-learning-challenges",
    "SIG-AIE": "ai-engineering-challenges",
    "SIG-RES": "research-challenges",
    "SIG-SYS": "systems-and-optimization-challenges",
    "SIG-GRAND": "grand-integrated-challenges",
}
XD_DIRS = {"XD-FND": "foundations", "XD-INT": "integrated-challenges", "XD-ADV": "advanced-challenges"}


def load_registry_ids() -> set[str]:
    reg = ct.ROOT / "shared" / "datasets" / "registry.yaml"
    if not reg.exists():
        reg = None
    if reg is None:
        return set()
    data = ct.load_yaml(reg) or []
    if isinstance(data, dict):
        data = data.get("datasets", [])
    # Proposals from in-flight units (shared/datasets/proposals/*.yaml) count too, until merged.
    for prop in sorted((ct.ROOT / "shared" / "datasets" / "proposals").glob("*.yaml")):
        extra = ct.load_yaml(prop) or []
        data = list(data) + (extra if isinstance(extra, list) else extra.get("datasets", []))
    return {str(d.get("id")) for d in data if isinstance(d, dict)}


def check_location(a: ct.Assessment, units: dict) -> list[str]:
    errs = []
    m = a.meta
    parts = Path(a.rel).parts
    dirname = a.path.name
    if not ct.DIR_NAME_RE.match(dirname):
        errs.append(f"directory name '{dirname}' must be '<ID>-<kebab-case-slug>'")
    if not dirname.startswith(f"{m.get('id')}-"):
        errs.append(f"directory name '{dirname}' does not start with id '{m.get('id')}-'")

    coll, sub, tier, unit, aid = m.get("collection"), m.get("subtrack"), m.get("tier"), m.get("unit"), str(m.get("id"))
    if coll == "unit":
        code = ct.SUBTRACK_DIRS.get(sub)
        if not code:
            return errs + [f"collection 'unit' requires a specialist subtrack, got '{sub}'"]
        if not aid.startswith(f"{code}-T{tier}-"):
            errs.append(f"id '{aid}' inconsistent with subtrack '{sub}' / tier {tier}")
        u = units.get(unit)
        if not u:
            errs.append(f"unit '{unit}' not found in shared/units.yaml")
        else:
            if u["subtrack"] != sub:
                errs.append(f"unit '{unit}' belongs to '{u['subtrack']}', not '{sub}'")
            if int(u["targets"].get(tier, 0)) == 0:
                errs.append(f"unit '{unit}' is not offered at tier {tier} (targets=0)")
            expected = ("assessments", sub, f"tier-{tier}", "units", f"{unit}-{u['slug']}", dirname)
            if parts != expected:
                errs.append(f"expected location {'/'.join(expected)}")
    elif coll == "capstone":
        code = ct.SUBTRACK_DIRS.get(sub)
        if unit != "CAP" or not code or not aid.startswith(f"{code}-CAP-T{tier}-"):
            errs.append("capstone must have unit 'CAP' and id '<DS|ML|AI>-CAP-T<tier>-NN'")
        expected = ("assessments", sub, "capstones", dirname)
        if parts != expected:
            errs.append(f"expected location {'/'.join(expected)}")
    elif coll == "cross-disciplinary":
        if sub != "cross-disciplinary" or not aid.startswith(f"XD-T{tier}-") or unit not in XD_DIRS:
            errs.append("cross-disciplinary assessment must have subtrack 'cross-disciplinary', unit XD-FND/INT/ADV and id 'XD-T<tier>-NNN'")
        else:
            expected = ("cross-disciplinary", XD_DIRS[unit], dirname)
            if parts != expected:
                errs.append(f"expected location {'/'.join(expected)}")
    elif coll == "signature":
        cat = SIG_CATEGORIES.get(unit)
        if not cat:
            errs.append(f"signature unit '{unit}' unknown")
        else:
            expected = ("signature-challenges", cat, dirname)
            if parts != expected:
                errs.append(f"expected location {'/'.join(expected)}")
    return errs


def check_readme(a: ct.Assessment) -> tuple[list[str], list[str]]:
    errs, warns = [], []
    if not a.readme:
        return ["README.md missing or empty"], warns
    if not a.readme.lstrip().startswith("# "):
        errs.append("README must start with a level-1 title")
    secs = ct.split_sections(a.readme)
    order = []
    for letter, title in ct.REQUIRED_SECTIONS:
        if letter not in secs:
            errs.append(f"missing section '## {letter}. {title}'")
            continue
        order.append(letter)
        got_title = secs.get(f"__title_{letter}", "")
        if title.lower() not in got_title.lower():
            warns.append(f"section {letter} titled '{got_title}', expected '{title}'")
        wc = ct.word_count(secs[letter])
        if wc < ct.SECTION_MIN_WORDS[letter]:
            errs.append(f"section {letter} ({title}) too thin: {wc} words < {ct.SECTION_MIN_WORDS[letter]}")
    letters_in_doc = [m.group(1) for m in ct.HEADING_RE.finditer(a.readme) if m.group(1)]
    if letters_in_doc != sorted(letters_in_doc):
        errs.append(f"sections out of order: {letters_in_doc}")
    if ct.PEDAGOGY_SECTION not in secs:
        errs.append(f"missing section '## {ct.PEDAGOGY_SECTION}'")
    elif ct.word_count(secs[ct.PEDAGOGY_SECTION]) < 80:
        errs.append("Pedagogical Design section too thin (< 80 words)")
    # Objectives must be a list of at least 3 items.
    if "C" in secs and len(re.findall(r"^\s*(?:[-*]|\d+\.)\s+", secs["C"], re.M)) < 3:
        errs.append("Objectives must list at least 3 items")
    # Acceptance criteria must be enumerated (checkbox or numbered list).
    if "G" in secs and len(re.findall(r"^\s*(?:[-*]\s+\[ \]|\d+\.|[-*]\s+\*\*AC)", secs["G"], re.M)) < 3:
        errs.append("Acceptance Criteria must enumerate at least 3 testable criteria")
    if "H" in secs and "rubric.md" not in secs["H"]:
        warns.append("section H should link to rubric.md")
    if "D" in secs and not re.search(r"mandatory|required|must", secs["D"], re.I):
        warns.append("section D should separate mandatory requirements explicitly")
    if "E" in secs and not re.search(r"licen[cs]e|synthetic|generated|member-sourced", secs["E"], re.I):
        errs.append("section E must state dataset licensing or synthetic provenance")
    total = ct.word_count(a.readme)
    if total < 1200:
        warns.append(f"README is short ({total} words); check the specification is complete")
    return errs, warns


def check_rubric(a: ct.Assessment) -> list[str]:
    p = a.path / "rubric.md"
    if not p.exists():
        return ["rubric.md missing"]
    rows = ct.parse_rubric_weights(p.read_text(encoding="utf-8"))
    if len(rows) < 5:
        return [f"rubric.md must contain a weighted table with >= 5 dimensions (found {len(rows)})"]
    total = sum(w for _, w in rows)
    if total != 100:
        return [f"rubric weights sum to {total}, expected 100"]
    return []


def check_resources(a: ct.Assessment) -> list[str]:
    errs = []
    r = a.meta.get("resources", {}) or {}
    d = a.path
    if r.get("starter"):
        s = d / "starter"
        if not s.is_dir() or not any(s.rglob("*.*")):
            errs.append("resources.starter is true but starter/ is missing or empty")
    if r.get("tests"):
        t = d / "tests"
        if not t.is_dir() or not list(t.glob("test_*.py")):
            errs.append("resources.tests is true but tests/test_*.py not found")
    if r.get("submission_template"):
        st = d / "submission-template"
        if not st.is_dir() or not any(st.iterdir()):
            errs.append("resources.submission_template is true but submission-template/ missing or empty")
    gen = r.get("data_generator")
    if gen and not (d / gen).is_file():
        errs.append(f"data_generator '{gen}' not found")
    # Empty directories are not allowed (rule: do not imitate structure).
    for sub in d.rglob("*"):
        if sub.is_dir() and not any(sub.iterdir()):
            errs.append(f"empty directory {sub.relative_to(d).as_posix()}")
    return errs


def check_meta_semantics(a: ct.Assessment, registry: set[str], all_ids: set[str]) -> tuple[list[str], list[str]]:
    errs, warns = [], []
    m = a.meta
    eh = m.get("estimated_hours") or {}
    if eh and eh.get("min", 0) > eh.get("max", 0):
        errs.append("estimated_hours.min > max")
    try:
        lr = dt.date.fromisoformat(str(m.get("last_reviewed")))
        nr = dt.date.fromisoformat(str(m.get("next_review")))
        cr = dt.date.fromisoformat(str(m.get("created")))
        if nr <= lr:
            errs.append("next_review must be after last_reviewed")
        if lr < cr:
            errs.append("last_reviewed precedes created")
    except ValueError:
        errs.append("created/last_reviewed/next_review must be ISO dates")
    if m.get("status") == "approved" and not m.get("reviewers"):
        errs.append("status 'approved' requires at least one reviewer")
    for ds in m.get("datasets", []) or []:
        if ds.startswith("DSET-") and registry and ds not in registry:
            errs.append(f"dataset '{ds}' not in shared/datasets/registry.yaml")
    res = m.get("resources") or {}
    if "synthetic" in (m.get("datasets") or []) and not (res.get("data_generator") or res.get("generator_in_assessor_kit")):
        warns.append("synthetic dataset declared without resources.data_generator")
    for pre in (m.get("prerequisites") or {}).get("recommended_assessments", []) or []:
        if pre not in all_ids:
            warns.append(f"recommended prerequisite '{pre}' does not exist (yet)")
    c = m.get("compute") or {}
    if c.get("paid_api") in {"optional", "required"} and not c.get("free_alternative"):
        errs.append("compute.paid_api set but no compute.free_alternative given")
    if c.get("gpu") == "required" and not c.get("free_alternative"):
        errs.append("compute.gpu 'required' needs a compute.free_alternative (e.g. Colab/Kaggle free tier or CPU variant)")
    return errs, warns


def check_forbidden(a: ct.Assessment) -> list[str]:
    errs = []
    for f in a.path.rglob("*"):
        if f.suffix.lower() not in {".md", ".yaml", ".yml", ".py", ".txt", ".json", ".sql", ".toml", ".ipynb"} or not f.is_file():
            continue
        text = f.read_text(encoding="utf-8", errors="ignore")
        for pat, label in FORBIDDEN_PATTERNS:
            if pat.search(text):
                errs.append(f"{f.relative_to(a.path).as_posix()}: {label}")
    return errs


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--strict", action="store_true", help="treat warnings as errors")
    ap.add_argument("--only", nargs="*", help="validate only these IDs")
    ap.add_argument("--json", action="store_true", help="emit a JSON report")
    ap.add_argument("--quiet", action="store_true", help="only print the summary and failures")
    args = ap.parse_args(argv)

    schema = json.loads((ct.ROOT / "shared" / "schemas" / "assessment.schema.json").read_text(encoding="utf-8"))
    units = ct.load_units()
    registry = load_registry_ids()
    assessments = ct.load_assessments()
    all_ids = {a.id for a in assessments}
    id_counts = Counter(a.id for a in assessments)

    report = defaultdict(lambda: {"errors": [], "warnings": []})
    for a in assessments:
        if args.only and a.id not in args.only:
            continue
        rec = report[a.rel]
        rec["errors"].extend(a.errors)
        if not a.meta:
            continue
        if jsonschema is not None:
            v = jsonschema.Draft202012Validator(schema, format_checker=jsonschema.FormatChecker())
            for e in sorted(v.iter_errors(a.meta), key=lambda e: list(e.path)):
                loc = "/".join(str(p) for p in e.path) or "<root>"
                rec["errors"].append(f"metadata {loc}: {e.message}")
        else:
            rec["warnings"].append("jsonschema not installed; schema validation skipped")
        if id_counts[a.id] > 1:
            rec["errors"].append(f"duplicate id '{a.id}'")
        rec["errors"].extend(check_location(a, units))
        e, w = check_readme(a)
        rec["errors"].extend(e)
        rec["warnings"].extend(w)
        rec["errors"].extend(check_rubric(a))
        rec["errors"].extend(check_resources(a))
        e, w = check_meta_semantics(a, registry, all_ids)
        rec["errors"].extend(e)
        rec["warnings"].extend(w)
        rec["errors"].extend(check_forbidden(a))

    # Unit directories must match the registry slug.
    for sub in ct.SUBTRACK_DIRS:
        for unit_dir in (ct.ROOT / "assessments" / sub).glob("tier-*/units/*"):
            code = "-".join(unit_dir.name.split("-")[:2])
            u = units.get(code)
            if not u or unit_dir.name != f"{code}-{u['slug']}":
                report[unit_dir.relative_to(ct.ROOT).as_posix()]["errors"].append("unit directory does not match shared/units.yaml slug")

    n_err = sum(len(r["errors"]) for r in report.values())
    n_warn = sum(len(r["warnings"]) for r in report.values())
    if args.json:
        print(json.dumps({"assessments": len(assessments), "errors": n_err, "warnings": n_warn, "report": report}, indent=2))
    else:
        for path, r in sorted(report.items()):
            if not r["errors"] and (args.quiet or not r["warnings"]):
                continue
            print(f"\n{path}")
            for e in r["errors"]:
                print(f"  ERROR   {e}")
            if not args.quiet:
                for w in r["warnings"]:
                    print(f"  warning {w}")
        print(f"\nValidated {len(assessments)} assessments: {n_err} error(s), {n_warn} warning(s).")
    if n_err or (args.strict and n_warn):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
