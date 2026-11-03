"""Self-tests for the repository tooling."""
import importlib.util
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS / "lib"))
import clbgtools as ct  # noqa: E402


def _load(rel):
    spec = importlib.util.spec_from_file_location(Path(rel).stem, TOOLS / rel)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_rubric_parser_reads_weighted_rows_only():
    text = """
| # | Dimension | Points | Look for |
|---|---|---|---|
| 1 | Correctness | 60 | x |
| 2 | Quality | 40 | y |
| | **Total** | **100** | |
| **Exemplary** | 90–100% | z |
"""
    assert ct.parse_rubric_weights(text) == [("Correctness", 60), ("Quality", 40)]


def test_split_sections_letters_and_titles():
    md = "# T\n## A. Identification\nabc\n## B. Problem Statement\ndef\n## Pedagogical Design\nghi\n"
    s = ct.split_sections(md)
    assert s["A"].strip() == "abc" and s["B"].strip() == "def" and s["Pedagogical Design"].strip() == "ghi"
    assert s["__title_A"] == "Identification"


def test_dir_name_pattern():
    assert ct.DIR_NAME_RE.match("DS-T1-006-the-registry-that-lies")
    assert ct.DIR_NAME_RE.match("ML-CAP-T2-01-fleet-health")
    assert ct.DIR_NAME_RE.match("SIG-RES-01-replicate-this")
    assert not ct.DIR_NAME_RE.match("DS-T1-6-bad")
    assert not ct.DIR_NAME_RE.match("DS-T1-006_Bad_Case")


def test_github_slug():
    links = _load("repository-checker/check_links.py")
    assert links.github_slug("5. Multi-dimensional difficulty") == "5-multi-dimensional-difficulty"
    assert links.github_slug("A. Identification") == "a-identification"
    assert links.github_slug("`code` and [link](x)") == "code-and-link"


def test_yaml_dates_become_strings(tmp_path):
    p = tmp_path / "m.yaml"
    p.write_text("created: 2026-11-03\nnested: {d: 2027-01-01}\n", encoding="utf-8")
    assert ct.load_yaml(p) == {"created": "2026-11-03", "nested": {"d": "2027-01-01"}}


def test_units_registry_is_consistent():
    units = ct.load_units()
    subs = ct.load_subtracks()
    for code, u in units.items():
        assert u["subtrack"] in subs
        assert code.startswith(subs[u["subtrack"]]["code"] + "-")
        assert set(u["targets"]) == {1, 2, 3}
        if any(int(v) == 0 for v in u["targets"].values()):
            assert u.get("tier_notes"), f"{code} omits a tier without tier_notes"


def test_validator_passes_on_repository():
    validate = _load("assessment-validator/validate.py")
    assert validate.main(["--quiet"]) == 0
