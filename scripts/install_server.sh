#!/usr/bin/env bash
# Sets up a Fabric 1.20.1 server in build/run/server and prepares it for an
# automated smoke test (no GUI, flat world, fast ticks).
set -euo pipefail
cd "$(dirname "$0")/.."
RUN="build/run/server"
MC="${MC_VERSION:-1.20.1}"
LOADER="${FABRIC_LOADER:-0.16.9}"
INSTALLER="${FABRIC_INSTALLER:-1.0.1}"
mkdir -p "$RUN"
cd "$RUN"
if [ ! -f fabric-server-launch.jar ]; then
  echo ">> downloading fabric installer ${INSTALLER}"
  curl -sSL --retry 3 -o fabric-installer.jar \
    "https://maven.fabricmc.net/net/fabricmc/fabric-installer/${INSTALLER}/fabric-installer-${INSTALLER}.jar"
  curl -sSL --retry 3 -o fabric-server-launch.jar \
    "https://meta.fabricmc.net/v2/versions/loader/${MC}/${LOADER}/${INSTALLER}/server/jar"
fi
if [ ! -f server.properties ]; then
  cat > server.properties <<'PROPS'
level-type=minecraft\:flat
online-mode=false
max-players=4
view-distance=6
simulation-distance=6
spawn-protection=0
enable-command-block=true
sync-chunk-writes=false
motd=Sborka smoke test
PROPS
fi
echo "eula=true" > eula.txt
echo ">> server tree: $PWD"
ls -la
