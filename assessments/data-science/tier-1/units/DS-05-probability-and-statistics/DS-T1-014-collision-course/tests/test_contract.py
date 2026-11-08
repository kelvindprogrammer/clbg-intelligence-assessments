"""Contract tests: these pass on the unmodified starter."""
import hashlib
import inspect

import pytest

from conftest import DATA

pytestmark = pytest.mark.contract

EXPECTED_SHA256 = "51b8638d6dbaa057294878c548feac91b809c1c3bde42582e9d63437d875aed7"


def test_dataset_is_unmodified():
    assert hashlib.sha256(DATA.read_bytes()).hexdigest() == EXPECTED_SHA256, "booking_refs.csv was modified"


def test_refs_schema(refs):
    import ref_collisions as rc
    assert list(refs.columns) == ["date", "ref"]
    assert len(refs) == 50_000
    assert sorted(refs["date"].unique()) == ["2026-10-12", "2026-10-13"]
    assert refs["ref"].str.len().eq(6).all()
    assert set("".join(refs["ref"].head(2000))) <= set(rc.ALPHABET)
    assert len(rc.ALPHABET) == 31 and not set("01ILO") & set(rc.ALPHABET)


def test_public_api():
    import ref_collisions as rc
    for name in ["p_collision_exact", "p_collision_approx", "expected_colliding_pairs", "p_collision_nonuniform",
                 "max_n_for_risk", "min_code_length", "guess_success_prob", "simulate_collision_prob",
                 "count_colliding_pairs", "estimate_space_size", "char_uniformity_pvalue", "excess_collision_pvalue"]:
        assert callable(getattr(rc, name)), name
    assert list(inspect.signature(rc.min_code_length).parameters) == [
        "alphabet_size", "n_per_window", "collision_risk", "guesses", "guess_risk"]
