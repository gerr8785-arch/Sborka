#!/usr/bin/env python3
"""Compact Modrinth search helper (Fabric, 1.20.1 only).

usage: python3 scripts/search.py "query one" "query two" ...
prints one line per hit:  slug | title | 1234k | categories | versions_1.20.1_count
"""
from __future__ import annotations

import json
import sys
import time
import urllib.parse
import urllib.request

API = "https://api.modrinth.com/v2"
UA = {"User-Agent": "sborka-pack-builder/1.2 (github.com/gerr8785-arch/Sborka)"}
MC = "1.20.1"
LOADER = "fabric"


def get(url: str):
    for i in range(4):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.loads(r.read().decode())
        except Exception:  # noqa: BLE001
            if i == 3:
                raise
            time.sleep(1 + i)


def main() -> int:
    queries = sys.argv[1:]
    facets = json.dumps([["project_type:mod"], [f"versions:{MC}"], [f"categories:{LOADER}"]])
    for q in queries:
        url = (
            f"{API}/search?query={urllib.parse.quote(q)}&limit=6"
            f"&facets={urllib.parse.quote(facets)}&index=relevance"
        )
        print(f"\n### {q}")
        try:
            res = get(url)
        except Exception as exc:  # noqa: BLE001
            print(f"  ERROR {exc}")
            continue
        for h in res.get("hits", []):
            dl = h["downloads"] // 1000
            cats = ",".join(c for c in h["display_categories"] if c not in ("fabric", "forge", "neoforge", "quilt"))
            side = f"{h['client_side'][:2]}/{h['server_side'][:2]}"
            print(f"  {h['slug']:<42} {h['title'][:34]:<34} {dl:>6}k {side} [{cats[:46]}]")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
