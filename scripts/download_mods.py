#!/usr/bin/env python3
"""Download every jar of the resolved manifest (sha1 + size verified)."""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUILD = os.path.join(ROOT, "build")


def sha1_file(path: str) -> str:
    h = hashlib.sha1()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def fetch(item, dest_dir: str):
    dest = os.path.join(dest_dir, item["filename"])
    if os.path.exists(dest) and sha1_file(dest) == item["sha1"]:
        return "cached", item["slug"]
    tmp = dest + ".part"
    for attempt in range(4):
        r = subprocess.run(
            ["curl", "-sSL", "--retry", "3", "--retry-delay", "2", "--max-time", "300", "-o", tmp, item["url"]]
        )
        if r.returncode == 0 and os.path.exists(tmp) and os.path.getsize(tmp) == item["size"]:
            if sha1_file(tmp) == item["sha1"]:
                os.replace(tmp, dest)
                return "downloaded", item["slug"]
        print(f"  retry {attempt + 1} {item['slug']} (rc={r.returncode})", flush=True)
    raise SystemExit(f"!! cannot download {item['slug']} from {item['url']}")


def main() -> int:
    side = sys.argv[1] if len(sys.argv) > 1 else "client"
    manifest = json.load(open(os.path.join(BUILD, "manifest.json"), encoding="utf-8"))
    if manifest.get("errors"):
        print("manifest errors:", manifest["errors"])
        return 1
    if side == "server":
        items = [m for m in manifest["mods"] if m["server_side"] in ("required", "optional")]
    else:
        items = [m for m in manifest["mods"] if m["client_side"] in ("required", "optional")]
    dest_dir = os.path.join(BUILD, "run", side, "mods")
    os.makedirs(dest_dir, exist_ok=True)
    stats = {"cached": 0, "downloaded": 0}
    with ThreadPoolExecutor(max_workers=6) as pool:
        for status, slug in pool.map(lambda it: fetch(it, dest_dir), items):
            stats[status] += 1
    print(f"{side}: {len(items)} jars -> {dest_dir}  {stats}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
