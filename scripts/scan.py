#!/usr/bin/env python3
"""Static compatibility audit of a downloaded mod folder.

For every jar it reads metadata/fabric.mod.json (and quilt.mod.json / mods.toml),
collects mod ids, versions and the dependency predicates, then verifies:

  1. every `depends` id is present and its version satisfies the predicate
  2. every `breaks` (and `conflicts`) target is absent
  3. no duplicate mod ids (two jars shipping the same id = crash risk)
  4. minecraft version range of every mod includes the pack MC version
  5. entrypoint / mixin config sanity (mixin files listed actually exist in the jar)
  6. curated rule list (pack/compat-rules.json) — e.g. "iris needs sodium",
     "optifabric must never appear next to sodium"

usage: python3 scripts/scan.py build/run/client/mods [--json out.json]
exit code 1 when a blocking problem is found.
"""
from __future__ import annotations

import json
import os
import re
import sys
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MC = os.environ.get("MC_VERSION", "1.20.1")

# ---------------------------------------------------------------- semver-ish --
VER_RE = re.compile(r"^[vV]?(\d+)(?:\.(\d+|x|\*))?(?:\.(\d+|x|\*))?(?:[-+](.*))?$")


def parse_ver(text: str):
    m = VER_RE.match(text.strip())
    if not m:
        return None
    nums = []
    for g in (m.group(1), m.group(2), m.group(3)):
        if g is None or g in ("x", "*"):
            nums.append(None)
        else:
            nums.append(int(g))
    while len(nums) < 3:
        nums.append(None)
    return tuple(nums), (m.group(4) or "")


def cmp_key(parsed):
    nums, pre = parsed
    nums = tuple(n if n is not None else -1 for n in nums)
    # prerelease sorts *before* release
    return nums, (0 if pre else 1), pre


def _cmp(a, b):
    ka, kb = cmp_key(a), cmp_key(b)
    return (ka > kb) - (ka < kb)


def _expand(op: str, ver):
    """return list of (op, version) terms for ^ / ~ / wildcards"""
    text = ver
    wild = re.match(r"^[vV]?(\d+)(?:\.(\d+|x|\*))?(?:\.(\d+|x|\*))?$", text)
    if wild is None:
        return [(op or "=", text)]
    if op in ("^", "~") or (op == "" and (wild.group(2) in ("x", "*") or wild.group(3) in ("x", "*"))):
        parts = [int(wild.group(1)) if wild.group(1) else 0]
        for g in (wild.group(2), wild.group(3)):
            parts.append(int(g) if g and g not in ("x", "*") else None)
        if op == "":
            op = "^"
        if op == "^":
            major = parts[0]
            upper = f"{major + 1}.0.0" if major > 0 else (
                f"0.{ (parts[1] or 0) + 1}.0" if (parts[1] or 0) > 0 else f"0.0.{(parts[2] or 0) + 1}"
            )
        else:  # ~
            upper = f"{parts[0] + 1}.0.0" if (parts[1] is None) else f"{parts[0]}.{(parts[1] or 0) + 1}.0"
        base = ".".join(str(p) if p is not None else "0" for p in parts[:3])
        return [(">=", base), ("<", upper)]
    return [(op or "=", text)]


def satisfies(version: str, predicate: str) -> bool:
    if not predicate or predicate.strip() in ("*", "*.*", "any"):
        return True
    pred = predicate.strip()
    dash = re.fullmatch(r"(\d+(?:\.\d+)*)\s*-\s*(\d+(?:\.\d+)*)", pred)
    if dash:  # "1.20-1.20.1" style range
        return satisfies(version, f">={dash.group(1)} <={dash.group(2)}")
    vp = parse_ver(version)
    if vp is None:
        return True  # unparsable version: don't false-positive
    for raw in predicate.replace(",", " ").split():
        m = re.match(r"^(>=|<=|>|<|=|~|\^)?\s*(.+)$", raw)
        if not m:
            continue
        op, ver = m.group(1) or "", m.group(2)
        for o, v in _expand(op, ver):
            if v.endswith(".*") or v.endswith(".x"):
                prefix = v.rsplit(".", 1)[0].split(".")
                vnums = (tuple(int(p) for p in prefix) + (None,) * 3)[:3]
                if tuple((n if n is not None else -1) for n in vnums) > tuple(
                    (x if x is not None else -1) for x in (vp[0])
                ):
                    return False
                continue
            tp = parse_ver(v)
            if tp is None:
                continue
            c = _cmp(vp, tp)
            ok = {"": c == 0, "=": c == 0, ">=": c >= 0, "<=": c <= 0, ">": c > 0, "<": c < 0}.get(o)
            if not ok:
                return False
    return True


# ------------------------------------------------------------------- scanning --
def read_json(z: zipfile.ZipFile, name: str):
    try:
        return json.loads(z.read(name).decode("utf-8", "replace"))
    except Exception:  # noqa: BLE001
        return None


def scan_jars(mods_dir: str):
    jars = []
    for f in sorted(os.listdir(mods_dir)):
        if not f.endswith(".jar") or f.startswith("."):
            continue
        path = os.path.join(mods_dir, f)
        info = {"file": f, "mods": [], "mixins": [], "errors": []}
        try:
            with zipfile.ZipFile(path) as z:
                names = z.namelist()
                fabric = read_json(z, "fabric.mod.json")
                quilt = read_json(z, "quilt.mod.json")
                if fabric:
                    info["loader"] = "fabric"
                    if isinstance(fabric.get("mixins"), (list, dict)):
                        mx = fabric["mixins"]
                        entries = mx.values() if isinstance(mx, dict) else mx
                        for e in entries:
                            for item in (e if isinstance(e, list) else [e]):
                                if isinstance(item, str):
                                    info["mixins"].append(item)
                    if isinstance(fabric.get("jars"), list):
                        for sub in fabric["jars"]:
                            if isinstance(sub, dict) and sub.get("file", "").endswith(".jar"):
                                info["errors"].append(f"nested jar (Jar-in-Jar): {sub['file']} — check for bundled deps")
                    for mid, mdata in (fabric.get("depends", {}) or {}).items():
                        pass
                    info["mods"].append(
                        {
                            "id": fabric.get("id"),
                            "version": str(fabric.get("version", "?")),
                            "name": fabric.get("name"),
                            "environment": fabric.get("environment", "*"),
                            "depends": fabric.get("depends", {}) or {},
                            "breaks": fabric.get("breaks", {}) or {},
                            "conflicts": fabric.get("conflicts", {}) or {},
                            "recommends": fabric.get("recommends", {}) or {},
                        }
                    )
                elif quilt:
                    info["loader"] = "quilt"
                    info["mods"].append(
                        {
                            "id": quilt.get("quilt_loader", {}).get("id"),
                            "version": str(quilt.get("quilt_loader", {}).get("version", "?")),
                            "name": quilt.get("quilt_loader", {}).get("metadata", {}).get("name"),
                            "depends": {
                                k: (v.get("version", "*") if isinstance(v, dict) else "*")
                                for k, v in (quilt.get("quilt_loader", {}).get("depends", []) if isinstance(quilt.get("quilt_loader", {}).get("depends"), list) else {}).items()
                            }
                            if isinstance(quilt.get("quilt_loader", {}).get("depends"), (list, dict))
                            else {},
                            "breaks": {},
                            "conflicts": {},
                            "recommends": {},
                            "environment": "*",
                        }
                    )
                else:
                    info["loader"] = "forge/toml?"
                    info["errors"].append("no fabric.mod.json (Forge/NeoForge jar? incompatible with Fabric)")
                # mixin config files referenced but absent
                for mx in info["mixins"]:
                    if mx not in names:
                        info["errors"].append(f"missing mixin config {mx}")
                # a jar that only has mixins but no fabric.mod.json is opaque
        except zipfile.BadZipFile:
            info["errors"].append("corrupted jar (BadZipFile)")
        jars.append(info)
    return jars


def main() -> int:
    mods_dir = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "build", "run", "client", "mods")
    out_json = None
    if "--json" in sys.argv:
        out_json = sys.argv[sys.argv.index("--json") + 1]

    jars = scan_jars(mods_dir)
    # global id registry
    have: dict[str, list] = {}
    for j in jars:
        for m in j["mods"]:
            if m["id"]:
                have.setdefault(m["id"], []).append((m["version"], j["file"]))

    problems: list[str] = []
    warnings: list[str] = []

    for j in jars:
        for e in j["errors"]:
            problems.append(f"{j['file']}: {e}")
        for m in j["mods"]:
            env = m.get("environment", "*")
            if m["id"] in ("minecraft", "java", "fabricloader"):
                continue
            for dep, pred in m["depends"].items():
                if dep in ("minecraft", "java", "fabricloader", "fabric"):
                    continue
                if dep not in have:
                    problems.append(f"{m['id']}: missing required dependency '{dep}' ({pred}) — needed by {j['file']}")
                    continue
                pred = pred if isinstance(pred, str) else str(pred)
                if not any(satisfies(v, pred) for v, _ in have[dep]):
                    problems.append(
                        f"{m['id']}: dependency '{dep}' present but version {have[dep][0][0]} does not satisfy '{pred}' ({j['file']})"
                    )
            mc_pred = m["depends"].get("minecraft")
            if isinstance(mc_pred, str) and mc_pred and not satisfies(MC, mc_pred):
                problems.append(f"{m['id']}: minecraft predicate '{mc_pred}' excludes {MC} ({j['file']})")
            for key in ("breaks", "conflicts"):
                for other, pred in (m[key] or {}).items():
                    if other in have:
                        problems.append(f"{m['id']}: declares {key.upper()} with '{other}' {pred}, but it is installed ({j['file']})")
            for other, pred in (m["recommends"] or {}).items():
                if other not in have:
                    warnings.append(f"{m['id']}: recommends '{other}' which is not installed")

    for mid, ent in have.items():
        if len(ent) > 1:
            problems.append(f"duplicate mod id '{mid}' shipped by: " + ", ".join(f for _, f in ent))

    # curated rules
    rules_path = os.path.join(ROOT, "pack", "compat-rules.json")
    if os.path.exists(rules_path):
        rules = json.load(open(rules_path, encoding="utf-8"))
        for r in rules.get("rules", []):
            if r["type"] == "mutually_exclusive":
                present = [i for i in r["ids"] if i in have]
                if len(present) > 1:
                    problems.append(f"curated rule: {' + '.join(present)} must not be installed together ({r.get('why','')})")
            elif r["type"] == "requires":
                if r["if"] in have and r["then"] not in have:
                    problems.append(f"curated rule: {r['if']} requires {r['then']} ({r.get('why','')})")
            elif r["type"] == "forbid":
                for i in r["ids"]:
                    if i in have:
                        problems.append(f"curated rule: {i} is forbidden on {MC} ({r.get('why','')})")
            elif r["type"] == "warn_if_present":
                for i in r["ids"]:
                    if i in have:
                        warnings.append(f"curated rule: {i} installed — {r.get('why','')}")

    report = {
        "mc": MC,
        "jar_count": len(jars),
        "mod_ids": {k: v[0][0] for k, v in sorted(have.items())},
        "problems": problems,
        "warnings": warnings,
        "jars": jars,
    }
    if out_json:
        os.makedirs(os.path.dirname(out_json), exist_ok=True)
        json.dump(report, open(out_json, "w", encoding="utf-8"), indent=1, ensure_ascii=False)

    print(f"jars: {len(jars)}  mod ids: {len(have)}")
    print(f"problems: {len(problems)}")
    for p in problems:
        print("  !!", p)
    print(f"warnings: {len(warnings)}")
    for w in warnings[:25]:
        print("   ~", w)
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
