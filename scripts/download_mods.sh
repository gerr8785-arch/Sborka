#!/usr/bin/env bash
# =============================================================================
#  download_mods.sh — скачивает все моды пака одной командой.
#  Источники: modrinth.json (после hydrate_manifest.py) и/или manifest.json (CurseForge).
#
#  Использование:
#    bash scripts/download_mods.sh --target ./mods                 # всё из modrinth.json
#    bash scripts/download_mods.sh --target ./mods --curseforge --key $CF_API_KEY
#    bash scripts/download_mods.sh --target ./mods --dry-run       # только список
#    bash scripts/download_mods.sh --target ./mods --only core     # только criticality=ядро
#
#  Зависимости: bash 4+, curl, jq, python3
# =============================================================================
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TARGET="./mods"
SOURCE="modrinth"
DRY=0
ONLY="all"
CF_KEY="${CF_API_KEY:-}"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --target) TARGET="$2"; shift 2 ;;
    --curseforge) SOURCE="curseforge"; shift ;;
    --key) CF_KEY="$2"; shift 2 ;;
    --dry-run) DRY=1; shift ;;
    --only) ONLY="$2"; shift 2 ;;
    -h|--help) sed -n '2,20p' "$0"; exit 0 ;;
    *) echo "Неизвестный аргумент: $1" >&2; exit 1 ;;
  esac
done

command -v curl >/dev/null || { echo "Нужен curl"; exit 1; }
command -v jq   >/dev/null || { echo "Нужен jq (apt install jq / brew install jq)"; exit 1; }

mkdir -p "$TARGET"
echo "→ Источник: $SOURCE | Цель: $TARGET | Фильтр: $ONLY"

ok=0; skip=0; fail=0
fail_list=()

if [[ "$SOURCE" == "modrinth" ]]; then
  MANIFEST="$ROOT/modrinth.json"
  # пары "url|filename"
  mapfile -t ROWS < <(jq -r '.files[] | select((.downloads|length) > 0) | "\(.downloads[0])|\(.path)"' "$MANIFEST")
  if [[ ${#ROWS[@]} -eq 0 ]]; then
    echo "!! modrinth.json не гидрирован (нет downloads)."
    echo "   Сначала: python3 scripts/hydrate_manifest.py --modrinth --mc 1.20.1 --loader forge"
    exit 2
  fi
  for row in "${ROWS[@]}"; do
    url="${row%%|*}"; path="${row##*|}"
    fname="$(basename "$path")"
    if [[ -f "$TARGET/$fname" ]]; then skip=$((skip+1)); continue; fi
    if [[ $DRY -eq 1 ]]; then echo "  [dry] $fname"; continue; fi
    if curl -fsSL --retry 3 --retry-delay 2 -A "Aetherfall-pack/1.0" -o "$TARGET/$fname.part" "$url"; then
      mv "$TARGET/$fname.part" "$TARGET/$fname"; ok=$((ok+1)); echo "  ✓ $fname"
    else
      rm -f "$TARGET/$fname.part"; fail=$((fail+1)); fail_list+=("$fname"); echo "  ✗ $fname"
    fi
  done
else
  [[ -n "$CF_KEY" ]] || { echo "Нужен --key или CF_API_KEY"; exit 1; }
  MANIFEST="$ROOT/manifest.json"
  mapfile -t ROWS < <(jq -r --arg only "$ONLY" '
     .files[]
     | select(.projectID != null and .fileID != null)
     | select($only == "all" or .criticality == $only)
     | "\(.projectID)|\(.fileID)|\(.modName)"' "$MANIFEST")
  if [[ ${#ROWS[@]} -eq 0 ]]; then
    echo "!! manifest.json не гидрирован (projectID/fileID = null)."
    echo "   Сначала: python3 scripts/hydrate_manifest.py --curseforge --key \$CF_API_KEY"
    exit 2
  fi
  for row in "${ROWS[@]}"; do
    IFS='|' read -r pid fid name <<< "$row"
    meta=$(curl -fsSL -H "x-api-key: $CF_KEY" \
      "https://api.curseforge.com/v1/mods/$pid/files/$fid" 2>/dev/null) || { fail=$((fail+1)); fail_list+=("$name"); continue; }
    url=$(jq -r '.data.downloadUrl // empty' <<<"$meta")
    fname=$(jq -r '.data.fileName' <<<"$meta")
    if [[ -z "$url" ]]; then
      echo "  ~ $name: автор запретил прямую загрузку → открыть вручную: https://www.curseforge.com/minecraft/mc-mods/$(jq -r '.data.slug // ""' <<<"$meta")"
      skip=$((skip+1)); continue
    fi
    if [[ -f "$TARGET/$fname" ]]; then skip=$((skip+1)); continue; fi
    if [[ $DRY -eq 1 ]]; then echo "  [dry] $fname"; continue; fi
    if curl -fsSL --retry 3 -A "Aetherfall-pack/1.0" -o "$TARGET/$fname.part" "$url"; then
      mv "$TARGET/$fname.part" "$TARGET/$fname"; ok=$((ok+1)); echo "  ✓ $fname"
    else
      rm -f "$TARGET/$fname.part"; fail=$((fail+1)); fail_list+=("$fname"); echo "  ✗ $fname"
    fi
    sleep 0.1
  done
fi

echo "─────────────────────────────────────────────"
echo "Скачано: $ok · уже было: $skip · ошибок: $fail"
if [[ $fail -gt 0 ]]; then
  printf '  не удалось: %s\n' "${fail_list[@]}"
  echo "  см. config/conflicts.md и повтори запуск (скрипт докачивает недостающее)"
  exit 3
fi
echo "→ Проверь целостность: bash scripts/validate_dependencies.sh --instance \"$(dirname "$TARGET")\""
