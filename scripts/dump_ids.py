#!/usr/bin/env python3
"""Dump namespaced item / block / entity ids from every jar (from en_us lang keys).

Offline alternative to starting the game: mod jars ship their lang files, so
`item.<namespace>.<path>` keys give us the exact registry ids we can use in
quest requirements, datapack functions and the docs.

usage: python3 scripts/dump_ids.py <mods-dir> [out.txt]
"""
from __future__ import annotations

import json
import os
import sys
import zipfile

PREFIXES = ("item.", "block.", "entity.", "itemGroup.", "biome.")


def main() -> int:
    mods_dir = sys.argv[1] if len(sys.argv) > 1 else "build/run/client/mods"
    out = sys.argv[2] if len(sys.argv) > 2 else "report/ids.txt"
    per_namespace: dict[str, dict[str, set[str]]] = {}
    for f in sorted(os.listdir(mods_dir)):
        if not f.endswith(".jar"):
            continue
        try:
            with zipfile.ZipFile(os.path.join(mods_dir, f)) as z:
                for name in z.namelist():
                    if not (name.startswith("assets/") and name.endswith("/lang/en_us.json")):
                        continue
                    try:
                        data = json.loads(z.read(name).decode("utf-8", "replace"))
                    except Exception:  # noqa: BLE001
                        continue
                    for key in data:
                        for pref in PREFIXES:
                            if key.startswith(pref):
                                rest = key[len(pref):]
                                if "." not in rest:
                                    continue
                                ns, path = rest.split(".", 1)
                                per_namespace.setdefault(ns, {}).setdefault(pref[:-1], set()).add(path)
        except zipfile.BadZipFile:
            continue
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    lines = []
    for ns in sorted(per_namespace):
        for kind in ("item", "block", "entity", "itemGroup", "biome"):
            ids = sorted(per_namespace[ns].get(kind, ()))
            if ids:
                lines.append(f"## {ns} / {kind} ({len(ids)})")
                for i in range(0, len(ids), 6):
                    lines.append("   " + "  ".join(f"{ns}:{p}" for p in ids[i : i + 6]))
    with open(out, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")
    print(f"{sum(len(v.get('item', ())) for v in per_namespace.values())} items, "
          f"{sum(len(v.get('entity', ())) for v in per_namespace.values())} entities, "
          f"{len(per_namespace)} namespaces -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
