#!/usr/bin/env python3
"""Modrinth metadata resolver for the Sborka RPG pack.

Reads `pack/candidates.json` (list of mod slugs) and writes `build/report/candidates.json`
with: project metadata + every 1.20.1 Fabric version (newest first, max 4 per mod),
including its dependency list, so compatibility / version pinning can be reviewed
before the pack is built.
"""
from __future__ import annotations

import json
import os
import sys
import time
import urllib.parse
import urllib.request

API = "https://api.modrinth.com/v2"
UA = {"User-Agent": "sborka-pack-builder/1.1 (github.com/gerr8785-arch/Sborka)"}
MC = os.environ.get("MC_VERSION", "1.20.1")
LOADER = os.environ.get("LOADER", "fabric")
RAW = os.environ.get("RAW_API", "")  # optional plain-http proxy for hosts w/o egress


def sanitize(obj):
    return obj


def download(url: str) -> bytes:
    if RAW:
        url = RAW + url
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=40) as r:
        return r.read()


def get_json(url: str, attempts: int = 5):
    last = None
    for i in range(attempts):
        try:
            return json.loads(download(url).decode())
        except Exception as exc:  # noqa: BLE001
            last = exc
            time.sleep(1.5 * (i + 1))
    raise RuntimeError(f"GET {url} failed: {last}")


def versions_for(project_id: str):
    # newest first; Modrinth returns newest first by default
    q = urllib.parse.urlencode(
        {
            "game_versions": json.dumps([MC]),
            "loaders": json.dumps([LOADER]),
        }
    )
    data = get_json(f"{API}/project/{project_id}/version?{q}")
    return data


def main() -> int:
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    cand_path = os.path.join(root, "pack", "candidates.json")
    out_dir = os.path.join(root, "build", "report")
    os.makedirs(out_dir, exist_ok=True)
    with open(cand_path, encoding="utf-8") as fh:
        candidates = json.load(fh)

    cache_path = os.path.join(root, "build", "report", "api-cache.json")
    cache = {}
    if os.path.exists(cache_path):
        cache = json.load(open(cache_path, encoding="utf-8"))

    report = {}
    problems = []
    for i, entry in enumerate(candidates["mods"], 1):
        slug = entry["slug"] if isinstance(entry, dict) else entry
        print(f"[{i}/{len(candidates['mods'])}] {slug}", file=sys.stderr, flush=True)
        try:
            if slug in cache:
                proj, vers = cache[slug]["project"], cache[slug]["versions"]
            else:
                proj = get_json(f"{API}/project/{slug}")
                vers = versions_for(proj["id"])
                cache[slug] = {"project": proj, "versions": vers}
                json.dump(cache, open(cache_path, "w", encoding="utf-8"))
            slim = []
            for v in vers[:4]:
                slim.append(
                    {
                        "id": v["id"],
                        "ver": v["version_number"],
                        "type": v["version_type"],
                        "published": v["date_published"][:10],
                        "downloads": v["downloads"],
                        "files": [
                            {
                                "name": f["filename"],
                                "size": f["size"],
                                "sha1": f["hashes"].get("sha1"),
                                "url": f["url"],
                                "primary": f.get("primary", False),
                            }
                            for f in v["files"]
                            if f.get("primary") or len(v["files"]) == 1
                        ],
                        "deps": [
                            {
                                "pid": d["project_id"],
                                "type": d["dependency_type"],
                                "vid": d.get("version_id"),
                            }
                            for d in v.get("dependencies", [])
                        ],
                    }
                )
            report[slug] = {
                "id": proj["id"],
                "title": proj["title"],
                "side": (proj.get("client_side"), proj.get("server_side")),
                "categories": proj.get("categories", []),
                "loaders": proj.get("loaders", []),
                "downloads": proj.get("downloads"),
                "versions_count_1_20_1": len(vers),
                "versions": slim,
                "note": entry.get("note") if isinstance(entry, dict) else None,
            }
            if not vers:
                problems.append(f"{slug}: NO {MC}/{LOADER} version")
        except Exception as exc:  # noqa: BLE001
            problems.append(f"{slug}: ERROR {exc}")
            report[slug] = {"error": str(exc)}

    json.dump(report, open(os.path.join(out_dir, "candidates.json"), "w", encoding="utf-8"), indent=1)

    # compact human/machine readable summary
    lines = []
    for slug, info in report.items():
        if "error" in info:
            lines.append(f"## {slug}  !! {info['error']}")
            continue
        cs, ss = info["side"]
        lines.append(f"## {slug} | {info['title']} | client={cs} server={ss} | {info['downloads']//1000}k")
        for v in info["versions"]:
            deps = ",".join(f"{d['pid'][:8]}:{d['type'][:4]}" for d in v["deps"]) or "-"
            f = v["files"][0] if v["files"] else {"name": "?", "size": 0}
            lines.append(
                f"   {v['ver']:<44} {v['type']:<8} {v['published']} "
                f"{f['size']//1024:>6}KB  deps[{deps}]  {f['name']}"
            )
    open(os.path.join(out_dir, "candidates.txt"), "w", encoding="utf-8").write("\n".join(lines) + "\n")
    open(os.path.join(out_dir, "problems.txt"), "w", encoding="utf-8").write("\n".join(problems) + "\n")
    print("problems:", problems)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
