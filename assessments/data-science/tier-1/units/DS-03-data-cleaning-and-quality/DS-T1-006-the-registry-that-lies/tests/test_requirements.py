"""Public requirement tests. These FAIL on the starter until you implement the package.

They're a sample of the rules, not the full set. Assessors run a larger hidden
suite, including on a re-generated export, so code that only satisfies these
examples will not pass. Write your own tests in tests/test_member_*.py.
"""
import datetime as dt
import os
import re
import subprocess
import sys

import pytest

from conftest import DATA

import registry_cleaner as rc


# ---------------------------------------------------------------- R1
@pytest.mark.parametrize("token", ["", "   ", "NA", "n/a", "-", "NULL", "nil"])
def test_missing_tokens(token):
    assert rc.is_missing(token)


@pytest.mark.parametrize("value", ["0", "Lagos", "2004-01-01", "none of the above"])
def test_not_missing(value):
    assert not rc.is_missing(value)


# ---------------------------------------------------------------- R2/R3
@pytest.mark.parametrize("raw,expected", [
    ("Lagos", "Lagos"), (" lagos", "Lagos"), ("Lagos State", "Lagos"), ("Lag.", "Lagos"),
    ("Akwa-Ibom", "Akwa Ibom"), ("C/River", "Cross River"), ("Abuja", "FCT"), ("F.C.T", "FCT"),
    ("Nassarawa", "Nasarawa"), ("NA", None), ("Atlantis", None),
])
def test_normalize_state(raw, expected):
    assert rc.normalize_state(raw) == expected


@pytest.mark.parametrize("raw,expected", [
    ("CSC", "Computer Science"), ("Comp. Sci.", "Computer Science"), ("MECH ENG", "Mechanical Engineering"),
    ("Accountancy", "Accounting"), ("law ", "Law"),
])
def test_normalize_department(raw, expected):
    assert rc.normalize_department(raw) == expected


# ---------------------------------------------------------------- R4
@pytest.mark.parametrize("raw,expected", [
    ("08031234567", "+2348031234567"), ("+2348031234567", "+2348031234567"),
    ("2348031234567", "+2348031234567"), ("0803 123 4567", "+2348031234567"),
    ("+234 (803) 123-4567", "+2348031234567"),
    ("080312345", None),          # truncated: must NOT be repaired
    ("", None), ("12345678901", None),
])
def test_normalize_phone(raw, expected):
    assert rc.normalize_phone(raw) == expected


# ---------------------------------------------------------------- R5
def test_parse_name_formats():
    assert rc.parse_name("Chidi Okafor") == ("Chidi", "Okafor")
    assert rc.parse_name("OKAFOR, Chidi") == ("Chidi", "Okafor")
    assert rc.parse_name("  chidi okafor ") == ("Chidi", "Okafor")


# ---------------------------------------------------------------- R6
def test_parse_date_unambiguous_formats():
    d = dt.date(2004, 3, 25)
    for raw in ["2004-03-25", "25/03/2004", "25-03-2004", "25 Mar 2004", "03/25/2004"]:
        p = rc.parse_date(raw, field="date_of_birth")
        assert (p.value, p.status) == (d, "ok"), raw


def test_parse_date_ambiguous_dob_is_flagged_not_guessed():
    p = rc.parse_date("04/07/2004", field="date_of_birth")
    assert p.status == "ambiguous" and p.value == dt.date(2004, 7, 4)


def test_parse_date_same_day_month_is_not_ambiguous():
    p = rc.parse_date("05/05/2004", field="date_of_birth")
    assert p.status == "ok" and p.value == dt.date(2004, 5, 5)


def test_parse_date_missing_and_invalid():
    assert rc.parse_date("N/A", field="date_of_birth").status == "missing"
    assert rc.parse_date("31/02/2004", field="date_of_birth").status == "invalid"


# ---------------------------------------------------------------- R7
@pytest.mark.parametrize("raw,expected", [("250", 250), ("400", 400), ("639", None), ("-226", None), ("N/A", None)])
def test_parse_score(raw, expected):
    assert rc.parse_score(raw) == expected


# ---------------------------------------------------------------- R8
def test_duplicate_groups_partition(raw):
    groups = rc.find_duplicate_groups(raw)
    flat = [rid for g in groups for rid in g]
    assert sorted(flat) == sorted(raw["record_id"]), "groups must partition every record_id exactly once"


def test_namesakes_are_not_merged(raw):
    """Two different students called Zainab Bello (different matric numbers, emails and DOBs)."""
    groups = rc.find_duplicate_groups(raw)
    owner = {rid: i for i, g in enumerate(groups) for rid in g}
    assert owner["R00001"] != owner["R00005"]


# ---------------------------------------------------------------- R9–R12 (end-to-end)
@pytest.fixture(scope="module")
def result(raw):
    return rc.clean_registry(raw)


def test_traceability(result, raw):
    ids = [x for cell in result.clean["source_record_ids"] for x in cell.split(";")]
    assert sorted(ids) == sorted(raw["record_id"])


def test_canonical_outputs(result):
    c = result.clean
    phones = c["phone_e164"].dropna().astype(str)
    phones = phones[phones != ""]
    assert phones.map(lambda p: bool(re.fullmatch(r"\+234[789][01]\d{8}", p))).all()
    assert set(c["dob_status"]) <= {"ok", "ambiguous", "missing", "invalid"}
    cg = c["cgpa_5pt"].dropna().astype(str)
    assert cg[cg != ""].astype(float).between(0, 5).all()


def test_systemic_scale_issue_detected(result):
    issues = result.issues
    assert (issues["issue_type"] == "rescaled").sum() > 50
    assert result.clean["cgpa_rescaled"].astype(str).isin(["True", "False"]).all()


def test_cli_runs(tmp_path):
    proc = subprocess.run([sys.executable, "-m", "registry_cleaner", str(DATA), "--out", str(tmp_path)],
                          capture_output=True, text=True, timeout=120,
                          env={**os.environ, "PYTHONPATH": os.pathsep.join(p for p in sys.path if p)})
    assert proc.returncode == 0, proc.stderr
    assert (tmp_path / "clean_registry.csv").exists() and (tmp_path / "issues.csv").exists()
