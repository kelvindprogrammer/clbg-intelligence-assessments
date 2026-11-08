"""Public requirement tests. These FAIL on the starter until you implement the package.

They are a sample. Assessors run a hidden suite on freshly generated galleries
(new charts, new data, new colormaps), so code that only satisfies these
examples, or that looks up chart ids, will not pass. Add your own tests in
tests/test_member_*.py.
"""
import math

import matplotlib
import numpy as np
import pandas as pd
import pytest

import chart_forensics as cf
from figcheck import common_problems, defect_problems


# ---------------------------------------------------------------- R1 / R2
def test_displayed_rows_applies_filter(gallery):
    spec, df = gallery["G03"]
    shown = cf.displayed_rows(spec, df)
    assert len(shown) == 8
    assert shown.iloc[0]["month"] == spec["filter"]["from"] and shown.iloc[-1]["month"] == spec["filter"]["to"]
    assert list(shown.index) == list(range(8))


def test_displayed_rows_without_filter_is_everything(gallery):
    spec, df = gallery["G01"]
    assert len(cf.displayed_rows(spec, df)) == len(df)


def test_displayed_rows_rejects_unknown_bound():
    spec = {"filter": {"field": "x", "from": "a", "to": "zz"}}
    with pytest.raises(ValueError):
        cf.displayed_rows(spec, pd.DataFrame({"x": ["a", "b", "c"]}))


def test_trend_slope():
    assert cf.trend_slope([1, 3, 5, 7]) == pytest.approx(2.0)
    assert cf.trend_slope([5, 4, 4, 1]) < 0
    with pytest.raises(ValueError):
        cf.trend_slope([3.0])


# ---------------------------------------------------------------- R3
def test_lie_factor_truncated_bars(gallery):
    spec, df = gallery["G01"]
    assert cf.lie_factor(spec, df) == pytest.approx(49.0, rel=1e-6)


def test_lie_factor_honest_bars_is_one():
    spec = {"mark": "bar", "y": {"field": "v", "domain": [0, 50]}}
    assert cf.lie_factor(spec, pd.DataFrame({"v": [10.0, 12.0, 30.0]})) == pytest.approx(1.0)


def test_lie_factor_undefined_for_lines(gallery):
    spec, df = gallery["G07"]
    with pytest.raises(ValueError):
        cf.lie_factor(spec, df)


# ---------------------------------------------------------------- R5 / R6
def test_srgb_to_lab_reference_values():
    lab = cf.srgb_to_lab(np.array([[1, 1, 1], [0, 0, 0], [1, 0, 0], [0.5, 0.5, 0.5]]))
    assert lab.shape == (4, 3)
    np.testing.assert_allclose(lab[0], [100, 0, 0], atol=0.05)
    np.testing.assert_allclose(lab[1], [0, 0, 0], atol=0.05)
    np.testing.assert_allclose(lab[2], [53.24, 80.09, 67.20], atol=0.1)
    assert lab[3][0] == pytest.approx(53.39, abs=0.1)


def test_srgb_to_lab_ignores_alpha():
    np.testing.assert_allclose(cf.srgb_to_lab([0.2, 0.4, 0.6, 0.3]), cf.srgb_to_lab([0.2, 0.4, 0.6]))


@pytest.mark.parametrize("name,scale,ok", [
    ("viridis", "sequential", True), ("Blues", "sequential", True), ("jet", "sequential", False),
    ("hsv", "sequential", False), ("RdBu", "diverging", True), ("coolwarm", "diverging", True),
    ("jet", "diverging", False), ("viridis", "diverging", False),
])
def test_colormap_ok(name, scale, ok):
    assert cf.colormap_ok(name, scale) is ok


def test_colormap_ok_accepts_objects_and_rejects_unknown_scale():
    assert cf.colormap_ok(matplotlib.colormaps["magma"], "sequential") is True
    with pytest.raises(ValueError):
        cf.colormap_ok("viridis", "qualitative")


# ---------------------------------------------------------------- R4 (a sample of the gallery)
def test_audit_truncated_bar(gallery):
    assert cf.audit(*gallery["G01"]) == {"TRUNCATED_AXIS"}


def test_audit_honest_line_with_nonzero_baseline_is_clean(gallery):
    """Line charts do not need a zero baseline. Flagging this is a false positive."""
    assert cf.audit(*gallery["G07"]) == set()


def test_audit_returns_only_known_codes(gallery):
    for spec, df in gallery.values():
        found = cf.audit(spec, df)
        assert isinstance(found, set) and found <= set(cf.CODES), spec["id"]


def test_audit_blank_source_counts_as_missing():
    spec = {"mark": "line", "x": {"field": "t"}, "y": {"field": "v", "type": "quantitative", "domain": None,
                                                       "reverse": False}, "source": "   "}
    assert cf.audit(spec, pd.DataFrame({"t": [1, 2], "v": [1.0, 2.0]})) == {"MISSING_SOURCE"}


def test_audit_reversed_rank_axis_is_not_inverted():
    spec = {"mark": "line", "x": {"field": "t"}, "y": {"field": "pos", "type": "rank", "domain": [1, 10],
                                                       "reverse": True}, "source": "League tables"}
    assert cf.audit(spec, pd.DataFrame({"t": [1, 2, 3], "pos": [8, 4, 1]})) == set()


# ---------------------------------------------------------------- R7
@pytest.mark.parametrize("cid", ["G01", "G02", "G05"])
def test_redraw_is_honest(gallery, cid):
    spec, df = gallery[cid]
    fig = cf.redraw(spec, df)
    probs = common_problems(fig) + defect_problems(fig, spec, df)
    assert not probs, f"{cid}: {probs}"


def test_redraw_does_not_modify_inputs(gallery):
    spec, df = gallery["G03"]
    before_spec, before_df = repr(spec), df.copy()
    cf.redraw(spec, df)
    assert repr(spec) == before_spec
    pd.testing.assert_frame_equal(df, before_df)
    assert not math.isnan(cf.trend_slope(df["supply_hours"]))
