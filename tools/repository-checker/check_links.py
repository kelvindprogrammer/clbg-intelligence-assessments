#!/usr/bin/env python3
"""Check that every relative link in every Markdown file resolves.

External (http/https/mailto) links are not fetched here, because network checks are
flaky in CI. They are covered by the scheduled `external-links` workflow and the
manual verification procedure in docs/contributing/maintenance.md.

It also verifies `#anchor` fragments for links to Markdown files, using
GitHub's heading-slug rules.

Usage: python tools/repository-checker/check_links.py [--root PATH]
"""
from __future__ import annotations

import argparse
import re
import sys
import unicodedata
from pathlib import Path
from urllib.parse import unquote

LINK_RE = re.compile(r"(?<!\!)\[(?:[^\]\[]|\[[^\]]*\])*\]\(\s*<?([^)\s>]+)>?(?:\s+\"[^\"]*\")?\s*\)")
IMG_RE = re.compile(r"!\[[^\]]*\]\(\s*<?([^)\s>]+)>?\s*\)")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*#*\s*$", re.M)
SKIP_DIRS = {".git", ".venv", "venv", "node_modules", "__pycache__", ".pytest_cache"}


def github_slug(text: str) -> str:
    text = re.sub(r"`([^`]*)`", r"\1", text)
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)
    text = unicodedata.normalize("NFKD", text).lower()
    text = re.sub(r"[^\w\- ]", "", text)
    return text.replace(" ", "-")


def anchors_for(path: Path, cache: dict) -> set[str]:
    if path not in cache:
        text = path.read_text(encoding="utf-8", errors="ignore")
        text = re.sub(r"```.*?```", "", text, flags=re.S)
        seen: dict[str, int] = {}
        out = set()
        for m in HEADING_RE.finditer(text):
            s = github_slug(m.group(2))
            n = seen.get(s, 0)
            out.add(s if n == 0 else f"{s}-{n}")
            seen[s] = n + 1
        out.update(re.findall(r'<a\s+(?:name|id)="([^"]+)"', text))
        cache[path] = out
    return cache[path]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=str(Path(__file__).resolve().parents[2]))
    args = ap.parse_args(argv)
    root = Path(args.root)
    broken = []
    cache: dict = {}
    n_links = 0
    for md in sorted(root.rglob("*.md")):
        if any(p in SKIP_DIRS for p in md.relative_to(root).parts):
            continue
        text = md.read_text(encoding="utf-8", errors="ignore")
        stripped = re.sub(r"```.*?```", "", text, flags=re.S)
        stripped = re.sub(r"`[^`\n]*`", "", stripped)
        for m in list(LINK_RE.finditer(stripped)) + list(IMG_RE.finditer(stripped)):
            target = m.group(1).strip()
            if re.match(r"^[a-z][a-z0-9+.-]*:", target, re.I):
                continue
            n_links += 1
            path_part, _, frag = target.partition("#")
            path_part = unquote(path_part)
            dest = md if not path_part else (md.parent / path_part).resolve()
            if not dest.exists():
                broken.append((md, target, "target does not exist"))
                continue
            if frag and dest.is_file() and dest.suffix == ".md":
                if frag.lower() not in anchors_for(dest, cache):
                    broken.append((md, target, f"anchor '#{frag}' not found"))
    for md, target, why in broken:
        print(f"{md.relative_to(root).as_posix()}: [{target}] {why}")
    print(f"Checked {n_links} relative links: {len(broken)} broken.")
    return 1 if broken else 0


if __name__ == "__main__":
    sys.exit(main())
