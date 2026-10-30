#!/usr/bin/env bash
# =============================================================================
#  validate_dependencies.sh — проверка полноты и корректности сборки пака.
#
#  Что проверяет:
#   1. Окружение (Java 17, jq, unzip, RAM).
#   2. Каждый jar в mods/ → читает META-INF/mods.toml → modid/version.
#   3. Дубли modid (DuplicateModsFoundException) и несколько версий одной библиотеки.
#   4. ВСЕ обязательные (mandatory=true) зависимости каждого мода — по декларации
#      самого мода, а не по нашей таблице. Отсутствующая mandatory = падение на старте.
#   5. Запрещённые моды (конфликты, зафиксированные в config/conflicts.md §5.10).
#   6. Зафиксированные пары версий (Apotheosis-трио, Embeddium+Oculus, PlayerAnimator).
#   7. Количество файлов против manifest.json.
#
#  Использование:
#    bash scripts/validate_dependencies.sh --env-only
#    bash scripts/validate_dependencies.sh --instance ~/.local/share/PrismLauncher/instances/Aetherfall
#    bash scripts/validate_dependencies.sh --instance . --stage libs
#    bash scripts/validate_dependencies.sh --instance . --report out/deps.md
# =============================================================================
set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
INSTANCE=""
STAGE="all"
ENV_ONLY=0
REPORT=""
FAIL=0
WARN=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --instance) INSTANCE="$2"; shift 2 ;;
    --stage) STAGE="$2"; shift 2 ;;
    --env-only) ENV_ONLY=1; shift ;;
    --report) REPORT="$2"; shift 2 ;;
    -h|--help) sed -n '2,25p' "$0"; exit 0 ;;
    *) echo "Неизвестный аргумент: $1" >&2; exit 1 ;;
  esac
done

red(){ printf '\033[31m%s\033[0m\n' "$*"; }
grn(){ printf '\033[32m%s\033[0m\n' "$*"; }
ylw(){ printf '\033[33m%s\033[0m\n' "$*"; }
say(){ [[ -n "$REPORT" ]] && echo -e "$*" >> "$REPORT"; }

[[ -n "$REPORT" ]] && : > "$REPORT"

# ─── 1. Окружение ────────────────────────────────────────────────────────────
echo "== 1. Окружение =="
if command -v java >/dev/null; then
  JV=$(java -version 2>&1 | head -1)
  if [[ "$JV" == *'"17'* ]]; then grn "  java: $JV"; else red "  java: $JV  ← НУЖНА Java 17!"; FAIL=$((FAIL+1)); fi
else
  red "  java не найдена в PATH"; FAIL=$((FAIL+1))
fi
for t in curl jq unzip python3; do
  command -v $t >/dev/null && grn "  $t: ok" || { ylw "  $t: ОТСУТСТВУЕТ (часть проверок будет недоступна)"; WARN=$((WARN+1)); }
done

if [[ $ENV_ONLY -eq 1 ]]; then
  echo "──────────────────────────────────────────"
  [[ $FAIL -eq 0 ]] && grn "Окружение в порядке." || red "Ошибок: $FAIL"
  exit $([ $FAIL -eq 0 ] && echo 0 || echo 1)
fi

[[ -z "$INSTANCE" ]] && INSTANCE="."
MODS="$INSTANCE/mods"
[[ -d "$MODS" ]] || { red "Нет папки mods в $INSTANCE"; exit 1; }
echo "  instance: $INSTANCE | stage: $STAGE"

JARS=("$MODS"/*.jar)
COUNT=${#JARS[@]}
[[ -f "${JARS[0]}" ]] || { red "В mods/ нет jar-файлов"; exit 1; }
echo "  jar-файлов: $COUNT"
say "# Отчёт валидации Aetherfall\n\n- Инстанс: \`$INSTANCE\`\n- Jar-файлов: $COUNT"

# ─── 2. Инвентаризация mods.toml ─────────────────────────────────────────────
echo "== 2. Чтение mods.toml =="
TMP=$(mktemp -d); trap 'rm -rf "$TMP"' EXIT
: > "$TMP/mods.tsv"; : > "$TMP/deps.tsv"

for j in "${JARS[@]}"; do
  base=$(basename "$j")
  toml=$(unzip -p "$j" META-INF/mods.toml 2>/dev/null || true)
  if [[ -z "$toml" ]]; then
    ylw "  ? $base — нет META-INF/mods.toml (Fabric/старый формат?)"; WARN=$((WARN+1)); continue
  fi
  # modId + version блоков [[mods]]
  echo "$toml" | awk -v f="$base" '
    /^\[\[mods\]\]/ {inmods=1; id=""; ver=""; next}
    /^\[\[dependencies/ {inmods=0}
    inmods && /^[[:space:]]*modId[[:space:]]*=/ {gsub(/.*=[[:space:]]*"/,""); gsub(/".*/,""); id=$0}
    inmods && /^[[:space:]]*version[[:space:]]*=/ {gsub(/.*=[[:space:]]*"/,""); gsub(/".*/,""); ver=$0}
    inmods && id!="" && ver!="" {print f"\t"id"\t"ver; id=""; ver=""}
  ' >> "$TMP/mods.tsv"
  # зависимости: modId + mandatory
  echo "$toml" | awk -v f="$base" '
    /^\[\[dependencies/ {indep=1; dep=""; mand="false"; next}
    /^\[\[/ && !/^\[\[dependencies/ {indep=0}
    indep && /^[[:space:]]*modId[[:space:]]*=/ {gsub(/.*=[[:space:]]*"/,""); gsub(/".*/,""); dep=$0}
    indep && /^[[:space:]]*mandatory[[:space:]]*=/ {gsub(/.*=[[:space:]]*/,""); gsub(/[[:space:]]*$/,""); mand=$0}
    indep && dep!="" && mand!="" {print f"\t"dep"\t"mand; dep=""; mand=""}
  ' >> "$TMP/deps.tsv"
done

MODIDS=$(cut -f2 "$TMP/mods.tsv" 2>/dev/null | sort -u)
echo "  уникальных modid: $(echo "$MODIDS" | grep -c . )"

# ─── 3. Дубли ────────────────────────────────────────────────────────────────
echo "== 3. Дубли modid =="
# normalize jar-суффиксы версий: foo-1.2.3.jar, foo-forge-1.2.3.jar → foo
DUP=$(awk -F'\t' '{print $2}' "$TMP/mods.tsv" | sort | uniq -d)
if [[ -n "$DUP" ]]; then
  while read -r d; do
    red "  ДУБЛЬ modid: $d"
    awk -F'\t' -v d="$d" '$2==d {print "      "$1}' "$TMP/mods.tsv"
    FAIL=$((FAIL+1))
  done <<< "$DUP"
else
  grn "  дублей нет"
fi
# две версии одной библиотеки по имени файла
for lib in placebo apothic_attributes curios geckolib playeranimator architectury cloth-config; do
  n=$(find "$MODS" -maxdepth 1 -iname "*${lib}*" -name '*.jar' | wc -l)
  [[ "$n" -gt 1 ]] && { red "  несколько jar для '$lib': $n"; find "$MODS" -maxdepth 1 -iname "*${lib}*" -name '*.jar' -printf '      %f\n'; FAIL=$((FAIL+1)); }
done

# ─── 4. Обязательные зависимости ─────────────────────────────────────────────
echo "== 4. Mandatory-зависимости =="
MISSING=0
while IFS=$'\t' read -r from dep mand; do
  [[ "$mand" != "true" ]] && continue
  case "$dep" in minecraft|forge|java|neoforge|fml|lowcodefml|javafml) continue;; esac
  if ! grep -qx "$dep" <<< "$MODIDS"; then
    red "  ОТСУТСТВУЕТ: $dep  (требует $from)"
    say "- ❌ \`$dep\` требуется \`$from\` — отсутствует"
    MISSING=$((MISSING+1)); FAIL=$((FAIL+1))
  fi
done < <(sort -u "$TMP/deps.tsv")
[[ $MISSING -eq 0 ]] && grn "  все mandatory-зависимости на месте"

# ─── 5. Запрещённые моды ─────────────────────────────────────────────────────
echo "== 5. Запрещённые комбинации =="
declare -A FORBID=(
  ["optifine"]="конфликт с Embeddium/Oculus — удалить, шейдеры через Oculus"
  ["rubidium"]="дубль Embeddium"
  ["sodium-fabric"]="Fabric-рендерер в Forge-паке"
  ["radium"]="дубль Canary"
  ["epicfight"]="конфликт анимаций с Better Combat + Iron's Spells"
  ["zenith"]="форк Apotheosis (дубль аффиксов)"
  ["biomesoplenty"]="конфликт biome source с Terralith"
  ["byg"]="конфликт biome source с Terralith"
  ["cold_sweat"]="дубль Tough As Nails (альтернатива)"
  ["cold_sweat-"]="дубль Tough As Nails"
  ["legendarysurvivaloverhaul"]="дубль First Aid + TAN"
  ["passiveskilltree"]="дубль Pufferfish's Skills"
  ["aiimprovements"]="дубль Canary"
  ["sinytraconnector"]="источник нестабильности при 200+ модах"
)
for key in "${!FORBID[@]}"; do
  hits=$(find "$MODS" -maxdepth 1 -iname "*${key}*" -name '*.jar' -printf '%f\n')
  if [[ -n "$hits" ]]; then
    red "  ЗАПРЕЩЁН: $hits → ${FORBID[$key]}"
    say "- ❌ \`$hits\` — ${FORBID[$key]}"
    FAIL=$((FAIL+1))
  fi
done
# OptiFine — отдельно (имя OptiFine_x.y.z.jar)
if find "$MODS" -maxdepth 1 -iname 'OptiFine*' | grep -q .; then red "  НАЙДЕН OptiFine — несовместим"; FAIL=$((FAIL+1)); fi
[[ $FAIL -eq 0 ]] && grn "  запрещённых нет"

# ─── 6. Зафиксированные пары версий ──────────────────────────────────────────
echo "== 6. Пары версий =="
check_pair() { # file-glob, expected-regex, human
  local f; f=$(find "$MODS" -maxdepth 1 -iname "$1" -name '*.jar' -printf '%f\n' | head -1)
  if [[ -z "$f" ]]; then ylw "  нет $3 (пропуск)"; return; fi
  if [[ "$f" =~ $2 ]]; then grn "  $3: $f"; else red "  $3: $f НЕ соответствует $2"; FAIL=$((FAIL+1)); fi
}
check_pair 'embeddium-*'      '0\.3\.'  'Embeddium 0.3.x (для Oculus 1.7.0)'
check_pair 'oculus-*'         '1\.7\.'  'Oculus 1.7.x'
check_pair 'playeranimator*'  '1\.0\.[2-9]' 'PlayerAnimator ≥1.0.2'
check_pair 'placebo-*'        '8\.[6-9]' 'Placebo 8.6+'

# ─── 7. Сверка с манифестом ──────────────────────────────────────────────────
echo "== 7. Сверка с manifest.json =="
if command -v jq >/dev/null && [[ -f "$ROOT/manifest.json" ]]; then
  EXPECTED=$(jq '[.files[] | select(.criticality=="ядро" or .criticality=="важный")] | length' "$ROOT/manifest.json")
  echo "  в манифесте (ядро+важные): $EXPECTED | jar на диске: $COUNT"
  if [[ "$COUNT" -lt "$EXPECTED" ]]; then
    ylw "  на диске меньше файлов, чем в манифесте ($COUNT < $EXPECTED) — проверь '--stage libs' и логи download_mods.sh"
    WARN=$((WARN+1))
  else
    grn "  количество в норме"
  fi
  say "\n## Сводка\n- Jar: $COUNT · ожидается (ядро+важные): $EXPECTED · ошибок: $FAIL · предупреждений: $WARN"
else
  ylw "  jq/manifest.json недоступны — сверка пропущена"
fi

echo "──────────────────────────────────────────────"
if [[ $FAIL -eq 0 ]]; then
  grn "✅ Проверка пройдена: $COUNT модов, обязательные зависимости на месте, запрещённых нет."
  [[ $WARN -gt 0 ]] && ylw "   предупреждений: $WARN (см. выше)"
  exit 0
else
  red "❌ Ошибок: $FAIL. Пак не запустится — исправь до первого запуска."
  exit 1
fi
