#!/usr/bin/env python3
"""Resolve the curated pack (pack/modlist.json) into a pinned build manifest.

Checks performed:
  * every selected slug has a 1.20.1 + Fabric build
  * pick the newest *release* build (beta only when allowed for that mod)
  * pull in every required dependency recursively; they must also have 1.20.1 Fabric builds
  * explicit `pin` / `only_version` overrides from the modlist
  * duplicate project detection + count limit (default 150 mods)

Output: build/manifest.json (+ build/manifest.tsv for review)
"""
from __future__ import annotations

import json
import os
import sys
import time
import urllib.parse
import urllib.request

API = "https://api.modrinth.com/v2"
UA = {"User-Agent": "sborka-pack-builder/1.3 (github.com/gerr8785-arch/Sborka)"}
MC = "1.20.1"
LOADER = "fabric"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "build")
CACHE_PATH = os.path.join(OUT, "report", "api-cache.json")

cache = {}
if os.path.exists(CACHE_PATH):
    cache = json.load(open(CACHE_PATH, encoding="utf-8"))


def _get(url: str):
    for i in range(5):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=45) as r:
                return json.loads(r.read().decode())
        except Exception:  # noqa: BLE001
            if i == 4:
                raise
            time.sleep(1.5 * (i + 1))


def save_cache():
    os.makedirs(os.path.dirname(CACHE_PATH), exist_ok=True)
    json.dump(cache, open(CACHE_PATH, "w", encoding="utf-8"))


def project(slug: str):
    if (e := cache.get(slug)) and e.get("project"):
        return e["project"]
    p = _get(f"{API}/project/{slug}")
    cache.setdefault(slug, {})["project"] = p
    save_cache()
    return p


def versions(slug: str):
    if (e := cache.get(slug)) and e.get("versions") is not None:
        return e["versions"]
    pid = cache[slug]["project"]["id"] if slug in cache else project(slug)["id"]
    q = urllib.parse.urlencode({"game_versions": json.dumps([MC]), "loaders": json.dumps([LOADER])})
    v = _get(f"{API}/project/{pid}/version?{q}")
    cache.setdefault(slug, {})["versions"] = v
    save_cache()
    return v


def suggest(slug: str):
    """Modrinth search for a slug we failed to look up (typos / renames)."""
    try:
        facets = json.dumps([["project_type:mod"], [f"versions:{MC}"], [f"categories:{LOADER}"]])
        q = urllib.parse.urlencode({"query": slug.replace("-", " "), "limit": 3, "facets": facets})
        hits = _get(f"{API}/search?{q}").get("hits", [])
        return ", ".join(f"{h['slug']} ({h['title']})" for h in hits) or "no hits"
    except Exception as exc:  # noqa: BLE001
        return f"search failed: {exc}"


def choose(slug: str, allow_beta: bool = False, exact: str | None = None):
    vs = versions(slug)
    if not vs:
        return None
    if exact:
        for v in vs:
            if exact in (v["version_number"], v["id"]):
                return v
        for v in vs:  # prefix match, e.g. "2.13.2" -> "2.13.2+Fabric"
            if v["version_number"].startswith(exact) or v["version_number"].split("+")[0] == exact:
                return v
        raise SystemExit(f"!! {slug}: pinned version {exact} not found for {MC}/{LOADER}")
    for v in vs:  # newest first
        if v["version_type"] == "release":
            return v
    if allow_beta:
        return vs[0]
    return vs[0]  # fall back to newest of any type, flagged later


def main() -> int:
    modlist = json.load(open(os.path.join(ROOT, "pack", "modlist.json"), encoding="utf-8"))
    banned = set(modlist.get("never_auto", []))
    order = {m["slug"]: i for i, m in enumerate(modlist["mods"])}
    limit = modlist.get("limit", 150)
    selected: dict[str, dict] = {}
    errors: list[str] = []

    def add(slug: str, category: str, why: str, required_by: str | None, pin: str | None, allow_beta: bool):
        if slug in selected:
            if required_by:
                selected[slug]["required_by"] = (selected[slug].get("required_by") or "") + f",{required_by}"
            return
        if slug in banned and required_by:
            errors.append(f"{slug}: auto-dependency {required_by} is banned (curated alternative needed)")
            return
        try:
            proj = project(slug)
        except Exception as exc:  # noqa: BLE001
            errors.append(f"slug {slug} not found on Modrinth ({exc}) — maybe: {suggest(slug)}")
            return
        v = choose(slug, allow_beta=allow_beta, exact=pin)
        if v is None:
            errors.append(f"{slug}: no {MC}/{LOADER} build")
            return
        files = [f for f in v["files"] if f.get("primary")] or v["files"][:1]
        f = files[0]
        entry = {
            "slug": slug,
            "title": proj["title"],
            "project_id": proj["id"],
            "version_id": v["id"],
            "version": v["version_number"],
            "version_type": v["version_type"],
            "filename": f["filename"],
            "url": f["url"],
            "size": f["size"],
            "sha1": f["hashes"].get("sha1"),
            "sha512": f["hashes"].get("sha512"),
            "client_side": proj.get("client_side"),
            "server_side": proj.get("server_side"),
            "category": category,
            "why": why,
            "required_by": required_by,
            "deps": [
                {"slug": None, "pid": d.get("project_id"), "type": d["dependency_type"], "vid": d.get("version_id")}
                for d in v.get("dependencies", [])
                if d.get("project_id")
            ],
        }
        selected[slug] = entry

    for item in modlist["mods"]:
        add(
            item["slug"],
            item.get("category", "misc"),
            item.get("why", ""),
            None,
            item.get("pin"),
            item.get("allow_beta", False),
        )
    # dependency pass (repeat until stable): explicit picks above always win
    changed = True
    while changed:
        changed = False
        for slug, entry in list(selected.items()):
            for d in entry["deps"]:
                if d["type"] != "required":
                    continue
                if d["slug"] is None:
                    try:
                        dproj = _get(f"{API}/project/{d['pid']}")
                    except Exception as exc:  # noqa: BLE001
                        errors.append(f"{slug}: cannot resolve dependency {d['pid']} ({exc})")
                        continue
                    d["slug"] = dproj["slug"]
                    cache.setdefault(d["slug"], {})["project"] = dproj
                dslug = d["slug"]
                if dslug not in selected:
                    add(dslug, "library", f"required by {slug}", slug, None, False)
                    changed = True

    # dependency sanity: every 'required' dep id must be in the pack
    have_ids = {e["project_id"] for e in selected.values()}
    for slug, e in selected.items():
        for d in e["deps"]:
            if d["type"] == "required" and d["pid"] not in have_ids:
                errors.append(f"{slug}: REQUIRED dependency {d['slug'] or d['pid']} missing from pack")
            if d["type"] == "incompatible" and d["pid"] in have_ids:
                errors.append(f"{slug}: declares INCOMPATIBLE with {d['slug'] or d['pid']} which is in the pack")

    if len(selected) > limit:
        errors.append(f"mod count {len(selected)} exceeds limit {limit} — trim the list")

    manifest = {
        "minecraft": MC,
        "loader": LOADER,
        "mod_count": len(selected),
        "total_size_mb": round(sum(e["size"] for e in selected.values()) / 1048576, 1),
        "errors": errors,
        "mods": sorted(selected.values(), key=lambda e: (e["category"], e["slug"])),
    }
    os.makedirs(os.path.join(OUT, "report"), exist_ok=True)
    json.dump(manifest, open(os.path.join(OUT, "manifest.json"), "w", encoding="utf-8"), indent=1)

    lines = [f"{manifest['mod_count']} mods, {manifest['total_size_mb']} MB"]
    for e in manifest["mods"]:
        lines.append(
            f"{e['category']:<14} {e['slug']:<38} {e['version']:<38} {e['version_type']:<7} "
            f"{e['client_side'][:2]}/{e['server_side'][:2]} {e['required_by'] or ''}"
        )
    lines += ["", "ERRORS:"] + (errors or ["none"])
    open(os.path.join(OUT, "report", "manifest.txt"), "w", encoding="utf-8").write("\n".join(lines) + "\n")
    print("\n".join(lines[-40:]))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
