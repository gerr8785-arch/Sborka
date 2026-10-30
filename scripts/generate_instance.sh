#!/usr/bin/env bash
# =============================================================================
#  generate_instance.sh — создаёт готовый инстанс в Prism Launcher (Forge 1.20.1).
#  Prism не имеет CLI для создания инстансов → скрипт создаёт структуру файлов,
#  которую Prism подхватывает при старте (portable-инстанс).
#
#  Использование:
#    bash scripts/generate_instance.sh --name Aetherfall --mem 12G
#    bash scripts/generate_instance.sh --name Test --mem 10G --dir /tmp
#    bash scripts/generate_instance.sh --name Aetherfall --mem 12G --skip-mods   # без скачивания
#
#  Структура, которую создаёт скрипт:
#    <instances>/<name>/instance.cfg        — настройки (RAM, JVM args)
#    <instances>/<name>/mmc-pack.json       — Forge 47.2.20 + LWJGL
#    <instances>/<name>/minecraft/mods/     — сюда скачиваются моды
#    <instances>/<name>/minecraft/config/   — конфиги пака (opts)
#    <instances>/<name>/minecraft/kubejs/   — скрипты пака
# =============================================================================
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
NAME="Aetherfall"
MEM="12G"
SKIP_MODS=0
MC="1.20.1"
FORGE="47.2.20"

if [[ "$(uname -s)" == "Darwin" ]]; then
  DEFAULT_DIR="$HOME/Library/Application Support/PrismLauncher/instances"
elif [[ "$(uname -s)" == MINGW* || "$(uname -s)" == MSYS* || "$(uname -s)" == CYGWIN* ]]; then
  DEFAULT_DIR="$APPDATA/PrismLauncher/instances"
else
  DEFAULT_DIR="$HOME/.local/share/PrismLauncher/instances"
fi
DEST_PARENT="$DEFAULT_DIR"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --name) NAME="$2"; shift 2 ;;
    --mem) MEM="$2"; shift 2 ;;
    --dir) DEST_PARENT="$2"; shift 2 ;;
    --skip-mods) SKIP_MODS=1; shift ;;
    -h|--help) sed -n '2,22p' "$0"; exit 0 ;;
    *) echo "Неизвестный аргумент: $1" >&2; exit 1 ;;
  esac
done

INST="$DEST_PARENT/$NAME"
MC_DIR="$INST/minecraft"
[[ -d "$INST" ]] && { echo "!! Инстанс уже существует: $INST"; echo "   Удали его или укажи --name другое."; exit 1; }

echo "→ Создаю инстанс «$NAME» ($MC / Forge $FORGE, RAM $MEM)"
mkdir -p "$MC_DIR"/{mods,config,config/opts,kubejs/server_scripts,kubejs/client_scripts,kubejs/startup_scripts,resourcepacks,shaderpacks,saves,logs}

# ── instance.cfg ─────────────────────────────────────────────────────────────
XMX=$(( ${MEM%G} * 1024 ))
[[ "$MEM" == *G* ]] && XMX=$(( ${MEM%G} * 1024 )) || XMX="$MEM"
JVM="-Xms$((XMX/2))M -Xmx${XMX}M -XX:+UseG1GC -XX:+ParallelRefProcEnabled -XX:MaxGCPauseMillis=130 -XX:+UnlockExperimentalVMOptions -XX:+DisableExplicitGC -XX:+AlwaysPreTouch -XX:G1NewSizePercent=28 -XX:G1MaxNewSizePercent=45 -XX:G1HeapRegionSize=16M -XX:G1ReservePercent=20 -XX:G1HeapWastePercent=5 -XX:G1MixedGCCountTarget=4 -XX:InitiatingHeapOccupancyPercent=15 -XX:G1MixedGCLiveThresholdPercent=90 -XX:G1RSetUpdatingPauseTimePercent=5 -XX:SurvivorRatio=32 -XX:+PerfDisableSharedMem -XX:MaxTenuringThreshold=1 -Dfile.encoding=UTF-8"
cat > "$INST/instance.cfg" <<CFG
InstanceType=OneSix
name=$NAME
iconKey=default
notes=Aetherfall: Chronicles of the Shattered Vale · MC $MC · Forge $FORGE · 238 mods
OverrideMemory=true
MinMemAlloc=$((XMX/2))
MaxMemAlloc=$XMX
PermGen=0
OverrideJavaArgs=true
JvmArgs=$JVM
OverrideCommands=false
PreLaunchCommand=
PostExitCommand=
OverrideConsole=false
ShowConsole=false
ShowGameTime=true
ShowGameLog=true
JoinServerOnLaunch=false
CFG
echo "  ✓ instance.cfg"

# ── mmc-pack.json ────────────────────────────────────────────────────────────
cat > "$INST/mmc-pack.json" <<JSON
{
    "formatVersion": 1,
    "components": [
        { "uid": "net.minecraft", "version": "$MC", "important": true },
        { "uid": "net.minecraftforge", "version": "$FORGE", "cachedName": "Forge", "cachedVersion": "$FORGE" },
        { "uid": "org.lwjgl3", "version": "3.3.1", "cachedName": "LWJGL 3" },
        { "uid": "org.lwjgl", "version": "3.3.1" },
        { "uid": "com.mojang.java", "version": "17.0.9" }
    ]
}
JSON
echo "  ✓ mmc-pack.json"

# ── конфиги пака ────────────────────────────────────────────────────────────
if [[ -d "$ROOT/config/opts" ]]; then
  cp -r "$ROOT/config/opts/." "$MC_DIR/config/opts/"
  echo "  ✓ config/opts (59 конфигов пака)"
fi
[[ -d "$ROOT/config/kubejs" ]] && cp -r "$ROOT/config/kubejs/." "$MC_DIR/kubejs/" && echo "  ✓ kubejs"

# ── options.txt (раскладка клавиш, язык, графика) ────────────────────────────
cat > "$MC_DIR/options.txt" <<OPT
version:3465
lang:ru_ru
renderDistance:10
simulationDistance:6
graphicsMode:1
fancyGraphics:true
ao:true
guiScale:3
maxFps:120
enableVsync:false
particles:1
mipmapLevels:4
entityShadows:true
soundCategory_master:0.8
soundCategory_music:0.35
soundCategory_ambient:0.7
fullscreen:false
key_key.journeymap.map:key.keyboard.m
key_key.combat_roll.roll:key.keyboard.c
key_key.irons_spellbooks.cast_first:key.keyboard.r
key_key.puffish_skills.open:key.keyboard.j
key_key.pmmo.open:key.keyboard.k
key_key.ftbquests.open_quests:key.keyboard.l
key_key.sophisticatedbackpacks.open:key.keyboard.b
key_key.jei.show.recipes:key.keyboard.u
key_key.jade.show_overlay:key.keyboard.numpad0
OPT
echo "  ✓ options.txt (клавиши/графика)"

# ── моды ─────────────────────────────────────────────────────────────────────
if [[ $SKIP_MODS -eq 0 ]]; then
  echo "→ Скачиваю моды…"
  if bash "$ROOT/scripts/download_mods.sh" --target "$MC_DIR/mods"; then
    echo "  ✓ моды загружены: $(find "$MC_DIR/mods" -name '*.jar' | wc -l) файлов"
  else
    echo "  ! Часть модов не скачалась — повтори 'bash scripts/download_mods.sh --target $MC_DIR/mods'"
  fi
else
  echo "  ~ моды пропущены (--skip-mods)"
fi

echo "──────────────────────────────────────────────────────────────"
echo "Готово: $INST"
echo "Дальше:"
echo "  1) Открой Prism Launcher → инстанс появится в списке (обнови, если не видно)"
echo "  2) Проверь Java: Settings → Java → путь к JDK 17"
echo "  3) bash scripts/validate_dependencies.sh --instance \"$INST\""
echo "  4) Запусти пак → выбери расу, класс, 3 таланта → мир «Тихий Брод»"
echo "  5) /chunky radius 3500 && /chunky start  (прогрев, обязательно)"
