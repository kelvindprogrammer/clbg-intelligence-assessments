"""The BASELINE you must beat: the desk's current script. It works, and that is the problem.

It ignores robots.txt and the crawl delay, follows every link it sees (including session-tagged
duplicates and the archive), refetches everything on every run, scrapes with regexes, and stores
the contact officer's details. Run it against the mock portal and measure what it costs, using
the same harness you use for your own strategies.

    python baseline/naive_crawler.py BASE_URL OUT.json
"""
from __future__ import annotations

import json
import re
import sys
import urllib.error
import urllib.request
from collections import deque


def crawl(base: str, max_pages: int = 200) -> dict:
    seen, queue, out = set(), deque([base + "/tenders?page=1"]), {}
    while queue and len(seen) < max_pages:
        url = queue.popleft()
        if url in seen:
            continue
        seen.add(url)
        try:
            with urllib.request.urlopen(url, timeout=10) as r:   # default Python User-Agent, no contact
                html = r.read().decode("utf-8", "replace")
        except urllib.error.HTTPError:
            continue
        for href in re.findall(r"href='([^']+)'", html):
            queue.append(base + href.replace("&amp;", "&"))
        m = re.search(r"<th>Reference</th><td>([^<]+)</td>", html)
        if m:
            rec = dict(re.findall(r"<th>([^<]+)</th><td>([^<]*)</td>", html))
            out[m.group(1)] = rec                                  # includes "Contact officer"
    return out


if __name__ == "__main__":
    data = crawl(sys.argv[1].rstrip("/"))
    with open(sys.argv[2], "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=1)
    print(f"{len(data)} notices")
