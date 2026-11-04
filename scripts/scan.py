#!/usr/bin/env python3
"""Static compatibility audit of a downloaded mod folder.

For every jar it reads fabric.mod.json / quilt.mod.json (including mods bundled
inside jars, at any depth), then verifies:

  1. every `depends` id is present (top-level jar, JiJ bundle or Fabric API module)
     and its version satisfies the predicate
  2. every `breaks` / `conflicts` target is really absent
  3. no duplicate mod ids among top-level jars (bundled copies of the same id are OK)
  4. the `minecraft` predicate of every mod includes the pack MC version
  5. mixin configs referenced by fabric.mod.json exist inside the jar
  6. every jar is a Fabric/Quilt mod (a Forge jar in a Fabric pack = crash)
  7. curated rules from pack/compat-rules.json

usage: python3 scripts/scan.py <mods-dir> [--json out.json]
exit code 1 when a blocking problem is found.
"""
from __future__ import annotations

import io
import json
import os
import re
import sys
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MC = os.environ.get("MC_VERSION", "1.20.1")

# ------------------------------------------------------------------ versions --
VER_RE = re.compile(
    r"^[vV]?(\d+)(?:\.(\d+|x|\*))?(?:\.(\d+|x|\*))?(?:-([0-9A-Za-z][0-9A-Za-z.\-]*))?(?:\+.*)?$"
)
_CHUNK = re.compile(r"\d+(?:\.\d+)*[A-Za-z]*")


def parse_ver(text: str):
    """Parse a mod / minecraft version into ((major, minor, patch), prerelease).

    Mods use many conventions; the important ones:
      "1.20.1"                 -> (1,20,1)
      "1.20.1-2.5.7+fabric"    -> (2,5,7)      (mod version follows the MC version)
      "1.20-2.16.38B"          -> (2,16,38)
      "0.3.7-beta.1"           -> (0,3,7,"beta.1")  prerelease sorts before the release
      "refabricated-1.20.1-2.1"-> (2,1,0)
    """
    t = text.strip()
    head = t.split("+", 1)[0]
    if "-" in head:
        left, right = head.split("-", 1)
        if re.match(r"\d", right.strip()):  # "1.20.1-2.5.7": the real version is on the right
            head = right.strip()
    m = VER_RE.match(head)
    if not m:
        chunks = _CHUNK.findall(head)
        if not chunks:
            return None
        head = chunks[-1]
        m = VER_RE.match(head)
        if not m:
            return None
    nums = [None if g in (None, "x", "*") else int(g) for g in (m.group(1), m.group(2), m.group(3))]
    while len(nums) < 3:
        nums.append(None)
    return tuple(nums), (m.group(4) or "")


def _key(parsed):
    nums, pre = parsed
    nums = tuple(n if n is not None else -1 for n in nums)
    return nums, (0 if pre else 1), pre


def _cmp(a, b):
    ka, kb = _key(a), _key(b)
    return (ka > kb) - (ka < kb)


def _expand(op: str, ver: str):
    wild = re.match(r"^[vV]?(\d+)(?:\.(\d+|x|\*))?(?:\.(\d+|x|\*))?$", ver)
    if wild is None:
        return [(op or "=", ver)]
    if op == "" and (wild.group(2) in ("x", "*") or wild.group(3) in ("x", "*")):
        # "1.20.x" / "1.20.*" -> >=1.20.0 <1.21.0
        nums = [int(wild.group(1))]
        for g in (wild.group(2), wild.group(3)):
            if g in (None, "x", "*"):
                break
            nums.append(int(g))
        lower = ".".join(str(n) for n in nums + [0] * (3 - len(nums)))
        idx = len(nums) - 1
        upper_nums = nums[:idx] + [nums[idx] + 1]
        upper = ".".join(str(n) for n in upper_nums + [0] * (3 - len(upper_nums)))
        return [(">=", lower), ("<", upper)]
    if op in ("^", "~"):
        parts = [int(wild.group(1))]
        for g in (wild.group(2), wild.group(3)):
            parts.append(int(g) if g and g not in ("x", "*") else None)
        op = op or "^"
        if op == "^":
            major = parts[0]
            if major > 0:
                upper = f"{major + 1}.0.0"
            elif (parts[1] or 0) > 0:
                upper = f"0.{(parts[1] or 0) + 1}.0"
            else:
                upper = f"0.0.{(parts[2] or 0) + 1}"
        else:  # ~ : patch level wildcard ("~1.20.1" -> >=1.20.1 <1.21.0), semver tilde
            upper = f"{parts[0] + 1}.0.0" if parts[1] is None else f"{parts[0]}.{(parts[1] or 0) + 1}.0"
        base = ".".join(str(p) if p is not None else "0" for p in parts[:3])
        return [(">=", base), ("<", upper)]
    return [(op or "=", ver)]


def _single(version_p, op, ver) -> bool:
    if ver.endswith("*") or ver.endswith(".x"):
        prefix = [int(p) for p in ver.rsplit(".", 1)[0].split(".") if p.isdigit()]
        vnums = tuple((version_p[0] + (None,) * 3)[:3])
        for i, p in enumerate(prefix):
            if i >= len(vnums) or vnums[i] is None or vnums[i] != p:
                return False
        return True
    target = parse_ver(ver)
    if target is None:
        return True
    c = _cmp(version_p, target)
    return {"": c == 0, "=": c == 0, ">=": c >= 0, "<=": c <= 0, ">": c > 0, "<": c < 0}.get(op, True)


def satisfies(version: str, predicate: str) -> bool:
    if not isinstance(predicate, str) or not predicate.strip() or predicate.strip() in ("*", "*.*", "any"):
        return True
    vp = parse_ver(version)
    if vp is None:
        return True  # unparsable installed version: do not raise false alarms
    pred = predicate.strip()
    if pred.startswith("~") and pred.endswith("-"):  # "~1.20-" = 1.20.x
        pred = pred[1:-1] + "x"
    dash = re.fullmatch(r"(\d+(?:\.\d+)*)\s+-\s+(\d+(?:\.\d+)*)", pred)
    if dash:
        return satisfies(version, f">={dash.group(1)} <={dash.group(2)}")
    # ">=1.20-2.5.0" style: a range glued to the operator
    m2 = re.fullmatch(r"(>=|<=|>|<|=)\s*(.+)", pred)
    if m2 and re.fullmatch(r"\d+(?:\.\d+)*\s*-\s*\d+(?:\.\d+)*", m2.group(2).strip()):
        # ">=1.20-2.5.0" -> ">=2.5.0" (same convention as parse_ver)
        return satisfies(version, f"{m2.group(1)}{m2.group(2).strip().split('-')[-1].strip()}")
    for raw in pred.replace(",", " ").split():
        m = re.match(r"^(>=|<=|>|<|=|~|\^)?\s*(.+)$", raw)
        if not m:
            continue
        op, ver = m.group(1) or "", m.group(2)
        ver = ver[:-1] if ver.endswith("*") else (ver[:-2] + "x" if ver.endswith(".x") else ver)
        for o, v in _expand(op, ver):
            if not _single(vp, o, v):
                return False
    return True


def matches_any(pred, versions) -> bool:
    if isinstance(pred, list):
        return any(matches_any(p, versions) for p in pred)
    if not isinstance(pred, str) or pred in ("*", "", "any"):
        return True
    return any(satisfies(v, pred) for v in versions)


# -------------------------------------------------------------------- reading --
FABRIC_API_MODULES = {
    "fabric-api-base", "fabric-api-lookup-api-v1", "fabric-biome-api-v1", "fabric-block-api-v1",
    "fabric-blockrenderlayer-v1", "fabric-client-tags-api-v1", "fabric-command-api-v1",
    "fabric-command-api-v2", "fabric-content-registries-v0", "fabric-convention-tags-v1",
    "fabric-crash-report-info-v1", "fabric-data-attachment-api-v1", "fabric-data-generation-api-v1",
    "fabric-dimensions-v1", "fabric-entity-events-v1", "fabric-events-interaction-v0",
    "fabric-events-lifecycle-v0", "fabric-game-rule-api-v1", "fabric-gametest-api-v1",
    "fabric-item-api-v1", "fabric-item-group-api-v1", "fabric-key-binding-api-v1",
    "fabric-lifecycle-events-v1", "fabric-loot-api-v2", "fabric-message-api-v1",
    "fabric-mining-level-api-v1", "fabric-model-loading-api-v1", "fabric-models-v0",
    "fabric-networking-api-v1", "fabric-object-builder-api-v1", "fabric-particles-v1",
    "fabric-recipe-api-v1", "fabric-registry-sync-v0", "fabric-renderer-api-v1",
    "fabric-renderer-indigo", "fabric-rendering-fluids-v1", "fabric-rendering-v0",
    "fabric-rendering-v1", "fabric-resource-conditions-api-v1", "fabric-resource-loader-v0",
    "fabric-screen-api-v1", "fabric-screen-handler-api-v1", "fabric-sound-api-v1",
    "fabric-transfer-api-v1", "fabric-transitive-access-wideners-v1", "fabric-tag-api-v1",
    "fabric-loot-tables-v1", "fabric-keybindings-v0", "fabric-biomes-v1",
    "fabric-rendering-data-attachment-v1", "fabric-rendering-registries-v1",
    "fabric-client-api-v1", "fabric-object-builder-api", "fabric",
    "fabric-loader", "minecraft", "java", "fabricloader",
}


def read_json(z: zipfile.ZipFile, name: str):
    try:
        return json.loads(z.read(name).decode("utf-8", "replace"))
    except Exception:  # noqa: BLE001
        return None


def meta_of(meta: dict, bundled: bool, depth: int = 0) -> dict:
    return {
        "id": meta.get("id"),
        "version": str(meta.get("version", "?")),
        "name": meta.get("name"),
        "environment": meta.get("environment", "*"),
        "depends": meta.get("depends", {}) or {},
        "breaks": meta.get("breaks", {}) or {},
        "conflicts": meta.get("conflicts", {}) or {},
        "recommends": meta.get("recommends", {}) or {},
        "provides": [p if isinstance(p, str) else (p or {}).get("id") for p in (meta.get("provides") or [])],
        "bundled": bundled,
        "depth": depth,
    }


def harvest_nested(outer: zipfile.ZipFile, depth: int = 0, max_depth: int = 3):
    """yield (metadata, depth) for every fabric mod jar nested inside `outer`."""
    meta = read_json(outer, "fabric.mod.json") or {}
    for sub in meta.get("jars") or []:
        if not (isinstance(sub, dict) and str(sub.get("file", "")).endswith(".jar")):
            continue
        try:
            with zipfile.ZipFile(io.BytesIO(outer.read(sub["file"]))) as inner:
                inner_meta = read_json(inner, "fabric.mod.json")
                if inner_meta and inner_meta.get("id"):
                    yield inner_meta, depth
                if depth < max_depth:
                    yield from harvest_nested(inner, depth + 1, max_depth)
        except Exception:  # noqa: BLE001
            continue


def scan_jars(mods_dir: str):
    jars = []
    for f in sorted(os.listdir(mods_dir)):
        if not f.endswith(".jar") or f.startswith("."):
            continue
        info = {"file": f, "mods": [], "mixins": [], "errors": [], "nested_ids": []}
        try:
            with zipfile.ZipFile(os.path.join(mods_dir, f)) as z:
                names = set(z.namelist())
                fabric = read_json(z, "fabric.mod.json")
                quilt = read_json(z, "quilt.mod.json")
                if fabric:
                    info["loader"] = "fabric"
                    mx = fabric.get("mixins")
                    if isinstance(mx, (list, dict)):
                        for e in (mx.values() if isinstance(mx, dict) else mx):
                            for item in (e if isinstance(e, list) else [e]):
                                if isinstance(item, str):
                                    info["mixins"].append(item)
                    info["mods"].append(meta_of(fabric, bundled=False))
                    for inner_meta, depth in harvest_nested(z):
                        info["nested_ids"].append(f"{inner_meta['id']}@{inner_meta.get('version')}")
                        info["mods"].append(meta_of(inner_meta, bundled=True, depth=depth))
                elif quilt:
                    info["loader"] = "quilt"
                    ql = quilt.get("quilt_loader", {}) or {}
                    deps = ql.get("depends") or {}
                    if isinstance(deps, list):  # quilt list form
                        deps = {d.get("id"): d.get("versions") or "*" for d in deps if isinstance(d, dict)}
                    info["mods"].append(
                        {
                            "id": ql.get("id"),
                            "version": str(ql.get("version", "?")),
                            "name": (ql.get("metadata") or {}).get("name"),
                            "environment": "*",
                            "depends": deps if isinstance(deps, dict) else {},
                            "breaks": {},
                            "conflicts": {},
                            "recommends": {},
                            "provides": [],
                            "bundled": False,
                            "depth": 0,
                        }
                    )
                else:
                    info["loader"] = "forge/other"
                    info["errors"].append("no fabric.mod.json (Forge/NeoForge jar? incompatible with Fabric)")
                for mxc in info["mixins"]:
                    if mxc not in names:
                        info["errors"].append(f"missing mixin config {mxc}")
        except zipfile.BadZipFile:
            info["errors"].append("corrupted jar (BadZipFile)")
        jars.append(info)
    return jars


# ----------------------------------------------------------------------- main --
def main() -> int:
    mods_dir = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "build", "run", "client", "mods")
    out_json = sys.argv[sys.argv.index("--json") + 1] if "--json" in sys.argv else None

    jars = scan_jars(mods_dir)

    have: dict[str, list] = {}
    top_ids: dict[str, list] = {}
    for j in jars:
        for m in j["mods"]:
            if m["id"]:
                have.setdefault(m["id"], []).append((m["version"], j["file"]))
                if not m["bundled"]:
                    top_ids.setdefault(m["id"], []).append(j["file"])
            for alias in m["provides"]:
                if alias:
                    have.setdefault(alias, []).append((m["version"], j["file"] + " (provides)"))

    problems: list[str] = []
    warnings: list[str] = []

    for j in jars:
        for e in j["errors"]:
            problems.append(f"{j['file']}: {e}")
        for m in j["mods"]:
            if m["bundled"]:
                continue  # resolved by the loader together with its host jar
            for dep, pred in m["depends"].items():
                if dep in FABRIC_API_MODULES:
                    continue
                if dep not in have:
                    problems.append(f"{m['id']}: missing required dependency '{dep}' ({pred}) — needed by {j['file']}")
                    continue
                versions = [v for v, _ in have[dep]]
                if isinstance(pred, str) and pred not in ("*", "") and not any(satisfies(v, pred) for v in versions):
                    # versions coming from JiJ bundles are allowed to be older/newer
                    problems.append(
                        f"{m['id']}: dependency '{dep}' installed as {versions[0]} does not satisfy '{pred}' ({j['file']})"
                    )
            mc_pred = m["depends"].get("minecraft")
            if isinstance(mc_pred, str) and mc_pred and not satisfies(MC, mc_pred):
                problems.append(f"{m['id']}: minecraft predicate '{mc_pred}' excludes {MC} ({j['file']})")
            for key in ("breaks", "conflicts"):
                for other, pred in (m[key] or {}).items():
                    if other not in have:
                        continue
                    if matches_any(pred, [v for v, _ in have[other]]):
                        problems.append(f"{m['id']}: declares {key.upper()} with '{other}' {pred}, and it is installed ({j['file']})")
            for other in (m["recommends"] or {}):
                if other not in have and other not in FABRIC_API_MODULES:
                    warnings.append(f"{m['id']}: recommends '{other}' which is not installed")

    for mid, files in top_ids.items():
        if len(files) > 1:
            problems.append(f"duplicate mod id '{mid}' shipped by: {', '.join(files)}")

    rules_path = os.path.join(ROOT, "pack", "compat-rules.json")
    if os.path.exists(rules_path):
        rules = json.load(open(rules_path, encoding="utf-8"))
        for r in rules.get("rules", []):
            kind = r["type"]
            if kind == "mutually_exclusive":
                present = [i for i in r["ids"] if i in top_ids]
                if len(present) > 1:
                    problems.append(f"curated rule: {' + '.join(present)} must not be installed together ({r.get('why','')})")
            elif kind == "requires":
                if r["if"] in top_ids and r["then"] not in have:
                    problems.append(f"curated rule: {r['if']} requires {r['then']} ({r.get('why','')})")
            elif kind == "forbid":
                for i in r["ids"]:
                    if i in top_ids:
                        problems.append(f"curated rule: {i} is forbidden ({r.get('why','')})")
            elif kind == "warn_if_present":
                for i in r["ids"]:
                    if i in top_ids:
                        warnings.append(f"curated rule: {i} installed — {r.get('why','')}")

    report = {
        "mc": MC,
        "jar_count": len(jars),
        "top_level_ids": sorted(top_ids),
        "all_ids": {k: v[0][0] for k, v in sorted(have.items())},
        "problems": problems,
        "warnings": warnings,
        "jars": jars,
    }
    if out_json:
        os.makedirs(os.path.dirname(out_json), exist_ok=True)
        json.dump(report, open(out_json, "w", encoding="utf-8"), indent=1, ensure_ascii=False)

    print(f"jars: {len(jars)}  top-level mod ids: {len(top_ids)}  ids incl. bundled: {len(have)}")
    print(f"problems: {len(problems)}")
    for p in problems:
        print("  !!", p)
    print(f"warnings: {len(warnings)}")
    for w in warnings:
        print("   ~", w)
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
