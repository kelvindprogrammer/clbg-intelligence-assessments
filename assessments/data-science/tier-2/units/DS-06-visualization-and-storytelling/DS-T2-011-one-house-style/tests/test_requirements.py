"""Public requirement tests. These FAIL on the starter until you implement the contract.

They check properties that any sound implementation must have, whichever published
CVD model, colour-difference formula and signature method you choose. The hidden suite
adds an independent organisational palette check and regression checks on all five charts.
"""
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pytest

import housestyle as hs
from conftest import DATA, SUBMISSION
from perturb import noisy, rgb, shifted, shorten_last_bar

TAB10 = [matplotlib.colors.to_hex(c) for c in plt.cm.tab10.colors]


def _lab_L(c):
    c = np.asarray(c, float)
    lin = np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
    Y = lin @ np.array([0.2126729, 0.7151522, 0.0721750])
    return 116 * np.cbrt(Y) - 16 if Y > (6 / 29) ** 3 else 903.3 * Y


# ---------------------------------------------------------------- R1
def test_contrast_ratio_wcag_values():
    assert hs.contrast_ratio("#000000", "#ffffff") == pytest.approx(21.0, abs=0.01)
    assert hs.contrast_ratio("#767676", "#ffffff") == pytest.approx(4.54, abs=0.01)
    assert hs.contrast_ratio("#ffffff", "#767676") == pytest.approx(hs.contrast_ratio("#767676", "#ffffff"))
    assert hs.contrast_ratio("#336699", "#336699") == pytest.approx(1.0)


# ---------------------------------------------------------------- R2
def test_simulate_cvd_shape_range_and_greys():
    rng = np.random.default_rng(0)
    x = rng.random((4, 5, 3))
    for kind in ("protan", "deutan", "tritan"):
        y = np.asarray(hs.simulate_cvd(x, kind))
        assert y.shape == x.shape and y.min() >= -1e-9 and y.max() <= 1 + 1e-9
        for g in (0.1, 0.5, 0.9):
            s = np.asarray(hs.simulate_cvd(np.array([g, g, g]), kind))
            assert abs(_lab_L(s) - _lab_L(np.array([g, g, g]))) < 2, "greys must stay (almost) grey"
    with pytest.raises(ValueError):
        hs.simulate_cvd(x, "achromat-ish")


def _ratio(a, b, kind):
    sa, sb = hs.simulate_cvd(np.array(matplotlib.colors.to_rgb(a)), kind), hs.simulate_cvd(np.array(matplotlib.colors.to_rgb(b)), kind)
    return hs.delta_e(sa, sb) / hs.delta_e(np.array(matplotlib.colors.to_rgb(a)), np.array(matplotlib.colors.to_rgb(b)))


def test_cvd_collapses_the_right_pairs():
    red, green, blue = "#d62728", "#2ca02c", "#1f77b4"
    assert _ratio(red, green, "deutan") < 0.35, "deuteranopes confuse this red and green"
    assert _ratio(red, green, "tritan") > 0.6, "tritanopes do not"
    assert _ratio(blue, green, "tritan") < 0.5, "tritanopes confuse this blue and green"
    assert _ratio(blue, green, "protan") > 0.6


# ---------------------------------------------------------------- R3
def test_delta_e_basics():
    assert hs.DELTA_E_METHOD in {"CIE76", "CIE94", "CIEDE2000"}
    w, k = np.ones(3), np.zeros(3)
    assert hs.delta_e(w, w) == pytest.approx(0.0, abs=1e-9)
    assert hs.delta_e(w, k) == pytest.approx(100.0, abs=0.1)
    a, b = np.array([0.2, 0.4, 0.6]), np.array([0.25, 0.38, 0.55])
    if hs.DELTA_E_METHOD != "CIE94":          # CIE94 is deliberately asymmetric (reference vs sample)
        assert hs.delta_e(a, b) == pytest.approx(hs.delta_e(b, a), rel=1e-6)


# ---------------------------------------------------------------- R4 / R5
def test_audit_rejects_tab10_and_accepts_house_palette():
    tab = hs.audit_palette(TAB10)
    house = hs.audit_palette(hs.PALETTE)
    assert set(tab.min_delta_e) == {"normal", "protan", "deutan", "tritan"}
    assert tab.passes is False and house.passes is True
    assert house.min_delta_e["deutan"] > tab.min_delta_e["deutan"]
    assert house.min_delta_e["protan"] > tab.min_delta_e["protan"]
    assert tab.min_contrast < 3.0 <= house.min_contrast
    a, b = tab.worst_pair["deutan"]
    assert a in TAB10 and b in TAB10


def test_house_palette_rules():
    assert len(hs.PALETTE) >= 6 and len(set(c.lower() for c in hs.PALETTE)) == len(hs.PALETTE)
    for c in hs.PALETTE:
        assert hs.contrast_ratio(c, hs.BACKGROUND) >= hs.MIN_CONTRAST, c
    assert hs.CVD_METHOD.strip(), "name and cite the CVD simulation you implemented"


# ---------------------------------------------------------------- R6 / R7
def test_theme_applies_and_restores():
    before = matplotlib.rcParams["axes.prop_cycle"]
    with hs.theme():
        cyc = [d["color"].lower() for d in matplotlib.rcParams["axes.prop_cycle"]]
        assert cyc[:len(hs.PALETTE)] == [c.lower() for c in hs.PALETTE]
    assert matplotlib.rcParams["axes.prop_cycle"] == before


def test_annotation_api():
    fig, ax = plt.subplots()
    for i, lab in enumerate(["USSD", "App", "Agent"]):
        ax.plot([0, 1, 2], [i, i + 1, i + 2], label=lab)
    ax.legend()
    t = hs.annotate_source(ax, "Naira Ledger Research")
    assert t.get_text().startswith("Source:") and t in fig.texts
    hs.label_lines(ax)
    assert ax.get_legend() is None
    labels = {tx.get_text(): tx for tx in ax.texts}
    assert {"USSD", "App", "Agent"} <= set(labels)
    hs.highlight(ax, "App")
    cols = {ln.get_label(): matplotlib.colors.to_hex(ln.get_color()) for ln in ax.get_lines()}
    assert cols["USSD"] == cols["Agent"] != cols["App"]
    with pytest.raises(ValueError):
        hs.highlight(ax, "Carrier pigeon")


# ---------------------------------------------------------------- R8 / R9
def test_signature_separates_benign_from_meaningful():
    fig = hs.make_chart("agents_by_zone", DATA)
    base = rgb(fig)
    s0 = hs.image_signature(base)
    assert hs.signature_distance(s0, hs.image_signature(rgb(hs.make_chart("agents_by_zone", DATA)))) == 0
    assert hs.signature_distance(s0, hs.image_signature(noisy(base))) <= hs.TOLERANCE
    assert hs.signature_distance(s0, hs.image_signature(shifted(base))) <= hs.TOLERANCE
    assert hs.signature_distance(s0, hs.image_signature(rgb(shorten_last_bar(fig)))) > hs.TOLERANCE


def test_report_matches_committed_baselines(tmp_path):
    paths = hs.build_report(DATA, tmp_path)
    assert sorted(p.name for p in paths) == sorted(f"{c}.png" for c in hs.CHARTS)
    for p in paths:
        ok, d = hs.compare_to_baseline(p, SUBMISSION / "baselines" / p.name)
        assert ok, f"{p.name}: distance {d} > tolerance {hs.TOLERANCE}"
