"""Requirement tests on the public dataset. They fail on the starter and pass on a correct toolkit."""
import json
from datetime import date

import pandas as pd
import pytest

from conftest import DATA, ROOT

EXP = json.loads((ROOT / "tests" / "expected_public.json").read_text())
SPLIT = "2025-04-30"


def test_load_route_day_parses_dates_and_validates(tmp_path):
    import eda_lab
    d = eda_lab.load_route_day(DATA)
    assert pd.api.types.is_datetime64_any_dtype(d["date"])
    bad = tmp_path / "bad.csv"
    bad.write_text("date,route\n2025-01-01,R1\n")
    with pytest.raises(ValueError):
        eda_lab.load_route_day(bad)


def test_headline_change(df):
    import eda_lab
    assert eda_lab.headline_change(df, SPLIT) == pytest.approx(EXP["headline"], abs=1e-9)
    assert eda_lab.headline_change(df, SPLIT) > 0.03  # the naive story: delays got worse


def test_kitagawa_exact_additivity(df):
    import eda_lab
    k = eda_lab.kitagawa(df, SPLIT, "route")
    assert set(k) == {"total", "within", "mix"}
    assert k["within"] + k["mix"] == pytest.approx(k["total"], abs=1e-9)


def test_kitagawa_values(df):
    import eda_lab
    k = eda_lab.kitagawa(df, SPLIT, "route")
    for key in ("total", "within", "mix"):
        assert k[key] == pytest.approx(EXP["kitagawa"][key], abs=1e-6), key


def test_kitagawa_other_segmentation(df):
    """Segmenting by operator must also add up (and gives a very different mix term)."""
    import eda_lab
    k = eda_lab.kitagawa(df, SPLIT, "operator")
    assert k["within"] + k["mix"] == pytest.approx(k["total"], abs=1e-9)
    assert abs(k["mix"]) < 0.1


def test_reversal_segments_finds_the_paradox(df):
    import eda_lab
    assert eda_lab.reversal_segments(df, SPLIT, "route") == EXP["reversal"]


def test_instrument_break_located_from_data(df):
    import eda_lab
    op, d = eda_lab.locate_instrument_break(df)
    assert op == EXP["operator"]
    assert abs((date.fromisoformat(d) - date.fromisoformat(EXP["break_date"])).days) <= 2


def test_adjusted_headline_removes_the_artefact(df):
    import eda_lab
    adj = eda_lab.adjusted_headline_change(df, SPLIT, EXP["operator"], EXP["break_date"])
    # Tolerance 0.004 (0.4 percentage points): the reference error is at most 0.0008; sampling noise in the shift estimate
    # is well below this, while ignoring the artefact would leave an error of about 0.05.
    assert abs(adj - EXP["clean_headline"]) <= 0.004
    assert adj < eda_lab.headline_change(df, SPLIT) - 0.03


def test_adjusted_headline_with_wrong_operator_is_not_clean(df):
    import eda_lab
    other = next(o for o in df["operator"].unique() if o != EXP["operator"])
    assert abs(eda_lab.adjusted_headline_change(df, SPLIT, other, EXP["break_date"]) - EXP["clean_headline"]) > 0.004


def test_ledger_validation(tmp_path):
    import eda_lab
    cols = "id,hypothesis,test,evidence,verdict,confidence\n"
    good = cols + "".join(f"H{i},h{i},t{i},e{i},{'refuted' if i < 2 else 'supported'},medium\n" for i in range(8))
    p = tmp_path / "good.csv"
    p.write_text(good)
    assert eda_lab.validate_ledger(p) == []
    q = tmp_path / "short.csv"
    q.write_text(cols + "H1,h,t,e,supported,high\n")
    problems = eda_lab.validate_ledger(q)
    assert any("8" in x for x in problems) and any("refuted" in x for x in problems)
    r = tmp_path / "badverdict.csv"
    r.write_text(good.replace("supported", "proved", 1))
    assert eda_lab.validate_ledger(r)
