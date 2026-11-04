#!/usr/bin/env bash
# Sets up a Fabric 1.20.1 server in build/run/server for the smoke test.
# The loader version is taken from Fabric meta (latest) because several pack mods
# require >= 0.19.5.
set -euo pipefail
cd "$(dirname "$0")/.."
RUN="build/run/server"
MC="${MC_VERSION:-1.20.1}"
INSTALLER="${FABRIC_INSTALLER:-1.0.1}"
mkdir -p "$RUN"
cd "$RUN"
LOADER="${FABRIC_LOADER:-}"
if [ -z "$LOADER" ]; then
  LOADER=$(curl -sSL "https://meta.fabricmc.net/v2/versions/loader/${MC}" \
    | python3 -c 'import json,sys; d=json.load(sys.stdin); print(d[0]["loader"]["version"])')
fi
echo ">> fabric loader ${LOADER} for ${MC}"
if [ ! -f fabric-server-launch.jar ] || ! grep -q "fabric-loader-${LOADER}" .loader-version 2>/dev/null; then
  curl -sSL --retry 3 -o fabric-installer.jar \
    "https://maven.fabricmc.net/net/fabricmc/fabric-installer/${INSTALLER}/fabric-installer-${INSTALLER}.jar"
  curl -sSL --retry 3 -o fabric-server-launch.jar \
    "https://meta.fabricmc.net/v2/versions/loader/${MC}/${LOADER}/${INSTALLER}/server/jar"
  echo "fabric-loader-${LOADER}" > .loader-version
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
echo ">> server tree: $PWD (loader ${LOADER})"
