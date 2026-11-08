"""Contract tests: these pass on the unmodified starter.

They check that the gallery is intact, the specs are well formed, the provided
renderer works, and the public API exists with the required signatures.
"""
import hashlib
import inspect
import json

import pytest

from conftest import GALLERY

pytestmark = pytest.mark.contract

EXPECTED_TREE_SHA256 = "89e4cdeaa6f14fd1e5543951b5f1bba3082bac26c9e7f4aee6eb1610670f6869"
MARKS = {"bar", "area", "line", "bubble", "heatmap"}


def _tree_hash(d):
    h = hashlib.sha256()
    for f in sorted(p for p in d.rglob("*") if p.is_file()):
        h.update(f.relative_to(d).as_posix().encode())
        h.update(f.read_bytes())
    return h.hexdigest()


def test_gallery_is_unmodified():
    assert _tree_hash(GALLERY) == EXPECTED_TREE_SHA256, "resources/gallery has been modified. Restore it."


def test_specs_are_well_formed():
    specs = sorted(GALLERY.glob("*.json"))
    assert len(specs) == 10
    for p in specs:
        s = json.loads(p.read_text(encoding="utf-8"))
        assert s["mark"] in MARKS, p.name
        assert (GALLERY / s["data"]).is_file(), p.name
        assert {"id", "title", "claim", "x", "source"} <= set(s), p.name


def test_provided_renderer_draws_every_chart(gallery):
    from matplotlib.figure import Figure
    from chart_forensics import render
    for spec, df in gallery.values():
        assert isinstance(render(spec, df), Figure)


def test_public_api():
    import chart_forensics as cf
    assert cf.CODES == ("TRUNCATED_AXIS", "DUAL_AXIS", "CHERRY_PICKED_WINDOW", "AREA_DISTORTION",
                        "MISLEADING_COLORMAP", "INVERTED_AXIS", "MISSING_SOURCE")
    for name, params in {"audit": ["spec", "df"], "lie_factor": ["spec", "df"], "displayed_rows": ["spec", "df"],
                         "redraw": ["spec", "df"], "trend_slope": ["values"], "srgb_to_lab": ["rgb"],
                         "colormap_ok": ["cmap", "scale"]}.items():
        assert list(inspect.signature(getattr(cf, name)).parameters) == params, name
