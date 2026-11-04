#!/usr/bin/env python3
"""Download the pinned pack, verify hashes, assemble the client/server trees,
produce a Modrinth .mrpack and a RAR archive.

Usage: python3 scripts/build_pack.py [--no-rar] [--keep]
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUILD = os.path.join(ROOT, "build")
RUN = os.path.join(BUILD, "run")
PACK_NAME = "Sborka RPG"
PACK_VERSION = os.environ.get("PACK_VERSION", "1.0.0")


def sha1_file(path: str) -> str:
    h = hashlib.sha1()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def download(url: str, dest: str, expect_sha1: str | None, size: int | None):
    if os.path.exists(dest) and expect_sha1 and sha1_file(dest) == expect_sha1:
        return "cached"
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    tmp = dest + ".part"
    subprocess.run(["curl", "-sSL", "--retry", "4", "--retry-delay", "2", "-o", tmp, url], check=True)
    got = sha1_file(tmp)
    if expect_sha1 and got != expect_sha1:
        os.remove(tmp)
        raise SystemExit(f"!! hash mismatch for {os.path.basename(dest)}: {got} != {expect_sha1}")
    if size and os.path.getsize(tmp) != size:
        raise SystemExit(f"!! size mismatch for {os.path.basename(dest)}")
    os.replace(tmp, dest)
    return "downloaded"


def main() -> int:
    args = sys.argv[1:]
    manifest = json.load(open(os.path.join(BUILD, "manifest.json"), encoding="utf-8"))
    if manifest.get("errors"):
        print("manifest has errors:", *manifest["errors"], sep="\n  ")
        return 1
    mods_dir = os.path.join(RUN, "client", "mods")
    os.makedirs(mods_dir, exist_ok=True)
    stats = {"cached": 0, "downloaded": 0}
    for i, m in enumerate(manifest["mods"], 1):
        dest = os.path.join(mods_dir, m["filename"])
        print(f"[{i}/{len(manifest['mods'])}] {m['slug']:<40} {m['filename']}", flush=True)
        stats[download(m["url"], dest, m["sha1"], m["size"])] += 1
    print("downloads:", stats)

    # ---- copy hand written configs / docs into the client + server trees ----
    for side in ("client", "server"):
        tree = os.path.join(RUN, side)
        os.makedirs(tree, exist_ok=True)
        for src_rel in ("config", "defaultconfigs", "resourcepacks", "docs", "shaderpacks"):
            src = os.path.join(ROOT, "pack", src_rel)
            if os.path.isdir(src):
                shutil.copytree(src, os.path.join(tree, src_rel), dirs_exist_ok=True)
        opts = os.path.join(ROOT, "pack", "client", "options.txt")
        if side == "client" and os.path.exists(opts):
            shutil.copy2(opts, os.path.join(tree, "options.txt"))
        docs_src = os.path.join(ROOT, "pack", "docs")
        if os.path.isdir(docs_src):
            for doc in os.listdir(docs_src):
                if doc.lower().startswith("readme"):
                    shutil.copy2(os.path.join(docs_src, doc), os.path.join(tree, doc))

    # ---- MultiMC / Prism instance metadata (so client/ can be imported directly) ----
    client_tree = os.path.join(RUN, "client")
    loader_ver = os.environ.get("FABRIC_LOADER", "0.20.1")
    with open(os.path.join(client_tree, "mmc-pack.json"), "w", encoding="utf-8") as fh:
        json.dump(
            {
                "formatVersion": 1,
                "components": [
                    {"uid": "net.minecraft", "version": manifest["minecraft"], "important": True},
                    {"uid": "net.fabricmc.fabric-loader", "version": loader_ver},
                ],
            },
            fh,
            indent=2,
        )
    with open(os.path.join(client_tree, "instance.cfg"), "w", encoding="utf-8") as fh:
        fh.write(
            "InstanceType=OneSix\n"
            f"name={PACK_NAME} {PACK_VERSION}\n"
            "MaxMemAlloc=3072\nMinMemAlloc=1024\n"
            "OverrideMemory=true\nOverrideJavaArgs=true\n"
            "JvmArgs=-XX:+UseG1GC -XX:+ParallelRefProcEnabled -XX:MaxGCPauseMillis=200\n"
        )

    # ---- Modrinth pack (.mrpack): lets Prism/ATLauncher download everything themselves ----
    index = {
        "formatVersion": 1,
        "game": "minecraft",
        "versionId": PACK_VERSION,
        "name": PACK_NAME,
        "summary": "Уютная RPG-сборка: расы, рыбалка, готовка, фермы, большие деревни, квесты — оптимизирована под слабые ПК",
        "files": [
            {
                "path": f"mods/{m['filename']}",
                "hashes": {"sha1": m["sha1"], "sha512": m["sha512"]},
                "env": {"client": "required", "server": "required"}
                if m["server_side"] in ("required", "optional")
                else {"client": "required", "server": "unsupported"},
                "downloads": [m["url"]],
                "fileSize": m["size"],
            }
            for m in manifest["mods"]
        ],
        "dependencies": {"minecraft": manifest["minecraft"], "fabric-loader": os.environ.get("FABRIC_LOADER", "0.16.9")},
    }
    mrpack = os.path.join(BUILD, f"{PACK_NAME}-{PACK_VERSION}.mrpack".replace(" ", "-"))
    cfg_root = os.path.join(ROOT, "pack")
    with zipfile.ZipFile(mrpack, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("modrinth.index.json", json.dumps(index, ensure_ascii=False, indent=1))
        for extra in ("config", "defaultconfigs", "resourcepacks", "shaderpacks"):
            base = os.path.join(cfg_root, extra)
            for dirpath, _dirs, files in os.walk(base):
                for f in files:
                    full = os.path.join(dirpath, f)
                    z.write(full, os.path.relpath(full, cfg_root))
        for doc in ("README_УСТАНОВКА.txt", "README_INSTALL_EN.txt"):
            src = os.path.join(ROOT, "pack", "docs", doc)
            if os.path.exists(src):
                z.write(src, doc)
            else:  # non-UTF8 checkouts may store the Cyrillic name differently
                for cand in os.listdir(os.path.join(ROOT, "pack", "docs")):
                    if "УСТАНОВ" in cand or "INSTALL" in cand:
                        z.write(os.path.join(ROOT, "pack", "docs", cand), cand)
    print("mrpack:", mrpack, round(os.path.getsize(mrpack) / 1048576, 1), "MB")

    if "--no-rar" in args:
        return 0

    # ---- RAR archive with everything (client tree + server tree) ----
    rar = os.path.join(BUILD, f"{PACK_NAME}-{PACK_VERSION}.rar".replace(" ", "-"))
    if os.path.exists(rar):
        os.remove(rar)
    cmd = [
        "rar", "a", "-m5", "-md256m", "-ep1", "-idq", "-r", rar,
        "-x*.log", "-xlogs", "-xworld", "-xworld_nether", "-xworld_the_end",
        "client", "server",
    ]
    subprocess.run(cmd, cwd=RUN, check=True)
    print("rar:", rar, round(os.path.getsize(rar) / 1048576, 1), "MB")
    subprocess.run(["unrar", "t", rar], check=True)

    # ---- checksums + build summary ----
    lines = [f"{PACK_NAME} {PACK_VERSION}  ({manifest['minecraft']}, fabric {loader_ver})",
             f"mods: {manifest['mod_count']}  download: {manifest['total_size_mb']} MB", ""]
    for path in sorted([p for p in (mrpack, rar) if os.path.exists(p)]):
        lines.append(f"{sha1_file(path)}  {os.path.getsize(path):>12,}  {os.path.basename(path)}")
    lines += ["", "per-mod sha1 (mods/):"]
    lines += [f"{m['sha1']}  {m['filename']}" for m in manifest["mods"]]
    with open(os.path.join(BUILD, "SHA1SUMS.txt"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")
    print("checksums written")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
