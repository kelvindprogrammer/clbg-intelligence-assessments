"""Contract tests: these pass on the unmodified starter."""
import hashlib
import inspect

import pandas as pd
import pytest

from conftest import DATA, ROOT

pytestmark = pytest.mark.contract

SHA256 = {
    "phc_register.csv": "3d1bd177a67957c6088f0dc0da75720bce0d5d57cc7c6a20129c0337d93e2f1a",
    "gh_register.csv": "4856bfcf83f3a8cfa994929edf0928bd4f5c98a5964b8658a268186f24c88d9f",
    "clerical_sample.csv": "aa9427ff02fe1756f7ae13888606f20a33dc5a29ba3f42946c64fe074aa0e002",
}


@pytest.mark.parametrize("name", sorted(SHA256))
def test_data_unmodified(name):
    assert hashlib.sha256((DATA / name).read_bytes()).hexdigest() == SHA256[name], f"{name} has been modified"


def test_register_schemas(registers):
    a, b, c = registers
    assert list(a.columns) == ["phc_id", "surname", "first_name", "other_name", "sex", "dob", "age_years", "phone", "lga", "settlement"]
    assert list(b.columns) == ["gh_id", "full_name", "sex", "date_of_birth", "phone", "lga", "address"]
    assert list(c.columns) == ["phc_id", "true_gh_id"]
    assert (len(a), len(b), len(c)) == (4025, 3422, 250)
    assert a["phc_id"].is_unique and b["gh_id"].is_unique
    assert set(c["phc_id"]) <= set(a["phc_id"])
    assert set(c.loc[c["true_gh_id"] != "", "true_gh_id"]) <= set(b["gh_id"])


def test_name_variants_resource():
    v = pd.read_csv(ROOT / "resources" / "reference" / "name_variants.csv")
    assert list(v.columns) == ["canonical", "variant"] and len(v) > 40


def test_evaluate_links_helper(registers):
    from linkage import evaluate_links
    _, _, c = registers
    truth = c[c["true_gh_id"] != ""].rename(columns={"phc_id": "a_id", "true_gh_id": "b_id"})
    e = evaluate_links(truth, c)
    assert e["precision"] == 1.0 and e["recall"] == 1.0


def test_public_api():
    import linkage
    assert list(inspect.signature(linkage.link).parameters) == ["a", "b", "clerical"]
    assert list(inspect.signature(linkage.candidate_pairs).parameters) == ["a", "b"]
    assert list(inspect.signature(linkage.deterministic_link).parameters) == ["a", "b"]
