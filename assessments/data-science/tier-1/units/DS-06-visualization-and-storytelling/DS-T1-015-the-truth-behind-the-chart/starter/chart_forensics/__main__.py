"""Provided CLI.

    python -m chart_forensics render  --gallery resources/gallery --out gallery_png
    python -m chart_forensics audit   --gallery resources/gallery
    python -m chart_forensics redraw  --gallery resources/gallery --out redrawn_png
"""
from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt

from . import audit, lie_factor, load_gallery, redraw, render


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="chart_forensics")
    ap.add_argument("command", choices=["render", "audit", "redraw"])
    ap.add_argument("--gallery", default="resources/gallery")
    ap.add_argument("--out", default="out")
    a = ap.parse_args(argv)
    gallery = load_gallery(a.gallery)
    if a.command == "audit":
        print("id\tdefects\tlie_factor")
        for spec, df in gallery:
            try:
                lf = f"{lie_factor(spec, df):.2f}"
            except ValueError:
                lf = "n/a"
            print(f"{spec['id']}\t{','.join(sorted(audit(spec, df))) or '-'}\t{lf}")
        return 0
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    fn = render if a.command == "render" else redraw
    for spec, df in gallery:
        fig = fn(spec, df)
        fig.savefig(out / f"{spec['id']}.png", dpi=110)
        plt.close(fig)
    print(f"wrote {len(gallery)} PNGs to {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
