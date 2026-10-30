#!/usr/bin/env python3
"""
hydrate_manifest.py — разрешает ID модов и заполняет manifest.json / modrinth.json.

Зачем: из песочницы агента api.modrinth.com и api.curseforge.com недоступны.
Запусти этот скрипт на своей машине или через GitHub Actions (workflow resolve-manifest.yml) —
он подставит реальные projectID/fileID (CurseForge) и downloads/hashes (Modrinth).

Использование:
  python3 scripts/hydrate_manifest.py --modrinth --mc 1.20.1 --loader forge
  python3 scripts/hydrate_manifest.py --curseforge --key $CF_API_KEY
  python3 scripts/hydrate_manifest.py --modrinth --check-only      # только отчёт, без записи

Требования: python3.9+, интернет, (для CF) ключ API https://console.curseforge.com/
"""
import argparse, json, sys, time, urllib.parse, urllib.request, pathlib, re

ROOT = pathlib.Path(__file__).resolve().parent.parent
UA = "Aetherfall-pack/1.0 (manifest hydration; contact: gerr8785-arch)"


def get(url, headers=None, retries=3):
    h = {"User-Agent": UA, "Accept": "application/json"}
    if headers: h.update(headers)
    for i in range(retries):
        try:
            req = urllib.request.Request(url, headers=h)
            with urllib.request.urlopen(req, timeout=25) as r:
                return json.loads(r.read().decode())
        except urllib.error.HTTPError as e:
            if e.code == 429:
                time.sleep(2 ** i); continue
            if e.code == 404:
                return None
            raise
        except Exception:
            if i == retries - 1: raise
            time.sleep(1 + i)
    return None


# ---------- Modrinth ----------
def mr_project(slug):
    if not slug: return None
    return get(f"https://api.modrinth.com/v2/project/{urllib.parse.quote(slug)}")


def mr_versions(project_id, mc, loader):
    return get(f"https://api.modrinth.com/v2/project/{project_id}/version"
               f"?game_versions=%5B%22{mc}%22%5D&loaders=%5B%22{loader}%22%5D") or []


def mr_search(name, mc, loader):
    q = urllib.parse.quote(name)
    facet = urllib.parse.quote(json.dumps([[f"versions:{mc}"], [f"categories:{loader}"]]))
    res = get(f"https://api.modrinth.com/v2/search?query={q}&facets={facet}&limit=1")
    if res and res.get("hits"): return res["hits"][0].get("slug")
    return None


def hydrate_modrinth(mc, loader, check_only):
    p = ROOT / "modrinth.json"
    data = json.loads(p.read_text(encoding="utf-8"))
    ok = miss = unresolved = 0
    for f in data["files"]:
        slug = f.get("_project")
        proj = mr_project(slug) if slug else None
        if not proj and f.get("_name"):
            alt = mr_search(f["_name"], mc, loader)
            proj = mr_project(alt) if alt else None
            if proj: slug = alt
        if not proj:
            unresolved += 1
            print(f"  ✗ {f['_name']:<42} — не найден на Modrinth (проверить вручную)")
            continue
        vers = mr_versions(proj["id"], mc, loader)
        if not vers:
            miss += 1
            print(f"  ! {f['_name']:<42} — проект есть, нет версии под {mc}/{loader}")
            continue
        v = vers[0]
        file = v["files"][0]
        f["path"] = f"mods/{file['filename']}"
        f["hashes"] = file["hashes"]
        f["downloads"] = [file["url"]]
        f["fileSize"] = file["size"]
        f["_project"] = slug
        f["_version"] = v["version_number"]
        ok += 1
        print(f"  ✓ {f['_name']:<42} {v['version_number']}  ({round(file['size']/1048576,1)} МБ)")
    if not check_only:
        p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nModrinth: разрешено {ok}, без версии {miss}, не найдено {unresolved} из {len(data['files'])}")
    return unresolved


# ---------- CurseForge ----------
def cf_search(name, key, mc):
    h = {"x-api-key": key}
    q = urllib.parse.quote(name)
    res = get(f"https://api.curseforge.com/v1/mods/search?gameId=432&searchFilter={q}"
              f"&gameVersion={mc}&modLoaderType=1&pageSize=5", headers=h)
    return res["data"] if res and res.get("data") else []


def cf_files(mod_id, key, mc):
    h = {"x-api-key": key}
    res = get(f"https://api.curseforge.com/v1/mods/{mod_id}/files?gameVersion={mc}&modLoaderType=1", headers=h)
    return res["data"] if res and res.get("data") else []


def hydrate_curseforge(key, mc, check_only):
    p = ROOT / "manifest.json"
    data = json.loads(p.read_text(encoding="utf-8"))
    ok = fail = 0
    for f in data["files"]:
        cands = cf_search(f["modName"], key, mc)
        if not cands:
            fail += 1; print(f"  ✗ {f['modName']:<42} — не найден на CurseForge"); continue
        mod = cands[0]
        files = cf_files(mod["id"], key, mc)
        if not files:
            fail += 1; print(f"  ! {f['modName']:<42} — нет файла под {mc}/Forge"); continue
        best = sorted(files, key=lambda x: x.get("fileDate", ""), reverse=True)[0]
        f["projectID"] = mod["id"]
        f["fileID"] = best["id"]
        f["_fileName"] = best["fileName"]
        f["_downloadUrl"] = best.get("downloadUrl") or ""
        f["_fileDate"] = best.get("fileDate", "")
        ok += 1
        print(f"  ✓ {f['modName']:<42} {best['fileName']}")
        time.sleep(0.05)
    if not check_only:
        p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nCurseForge: разрешено {ok}, не удалось {fail} из {len(data['files'])}")
    return fail


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--modrinth", action="store_true")
    ap.add_argument("--curseforge", action="store_true")
    ap.add_argument("--key", default=None, help="CurseForge API key")
    ap.add_argument("--mc", default="1.20.1")
    ap.add_argument("--loader", default="forge")
    ap.add_argument("--check-only", action="store_true")
    a = ap.parse_args()
    if not (a.modrinth or a.curseforge):
        ap.error("укажи --modrinth и/или --curseforge")
    bad = 0
    if a.modrinth: bad += hydrate_modrinth(a.mc, a.loader, a.check_only)
    if a.curseforge:
        if not a.key: ap.error("--curseforge требует --key (или переменную CF_API_KEY)")
        bad += hydrate_curseforge(a.key, a.mc, a.check_only)
    sys.exit(1 if bad else 0)
