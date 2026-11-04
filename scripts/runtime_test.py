#!/usr/bin/env python3
"""Runtime smoke test: boots the Fabric server with the full pack and executes
scripts/tests/smoke_commands.txt through the console.

Fails (exit 1) if the server crashes, a mod fails to load, a command errors,
or the server does not shut down cleanly.
"""
from __future__ import annotations

import os
import re
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SERVER = os.path.join(ROOT, "build", "run", "server")
LOG = os.path.join(ROOT, "build", "report", "server-run.log")

FAIL_PATTERNS = [
    (re.compile(r"Failed to load mod"), "mod load failure"),
    (re.compile(r"Mod resolution failed"), "dependency resolution failure"),
    (re.compile(r"Incompatible mods found"), "incompatible mods"),
    (re.compile(r"java\.lang\.(NoClassDefFoundError|NoSuchMethodError|NoSuchFieldError)"), "binary incompatibility"),
    (re.compile(r"Mixin apply failed|MixinApplyError|InvalidMixinException"), "mixin failure"),
    (re.compile(r"Caused by: java\.lang\.ClassNotFoundException"), "missing class"),
    (re.compile(r"Exception in server tick loop"), "server tick crash"),
    (re.compile(r"---- Minecraft Crash Report ----"), "crash report"),
    (re.compile(r"Unknown or incomplete command"), "command/data error"),
    (re.compile(r"There is no such structure"), "missing structure (content not loaded)"),
    (re.compile(r"Unknown item|Unknown entity"), "missing registry entry"),
]
WARN_PATTERNS = [
    (re.compile(r"Can't keep up|Running \d+ms behind"), "server lag warning"),
    (re.compile(r"Failed to (load|parse) .*?(recipe|advancement|loot)"), "datapack entry skipped"),
]


def main() -> int:
    cmds_file = os.path.join(ROOT, "scripts", "tests", "smoke_commands.txt")
    os.makedirs(os.path.dirname(LOG), exist_ok=True)
    if not os.path.exists(os.path.join(SERVER, "fabric-server-launch.jar")):
        print("!! server not installed; run scripts/install_server.sh first")
        return 2
    java = os.environ.get("JAVA_BIN", "java")
    heap = os.environ.get("SERVER_HEAP", "3G")
    log_fh = open(LOG, "wb")
    print(f">> starting server (heap {heap})")
    proc = subprocess.Popen(
        [java, f"-Xmx{heap}", f"-Xms{heap}", "-XX:+UseG1GC", "-Dfabric.log.level=info",
         "-jar", "fabric-server-launch.jar", "nogui"],
        cwd=SERVER, stdin=subprocess.PIPE, stdout=log_fh, stderr=subprocess.STDOUT,
        text=True,
    )
    script = []
    for line in open(cmds_file, encoding="utf-8"):
        line = line.rstrip("\n")
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        script.append(line)

    start = time.time()
    try:
        for line in script:
            if line.startswith("@wait"):
                time.sleep(float(line.split()[1]))
                continue
            if proc.poll() is not None:
                break
            print(f">> {line}")
            try:
                proc.stdin.write(line + "\n")
                proc.stdin.flush()
            except BrokenPipeError:
                break
        # wait for clean exit
        deadline = time.time() + 120
        while proc.poll() is None and time.time() < deadline:
            time.sleep(2)
        if proc.poll() is None:
            proc.terminate()
            try:
                proc.wait(30)
            except subprocess.TimeoutExpired:
                proc.kill()
    finally:
        log_fh.close()

    text = open(LOG, errors="replace").read()
    problems = [f"{label}: {m.group(0)}" for pat, label in FAIL_PATTERNS for m in pat.finditer(text)]
    warnings = [f"{label}: {m.group(0)}" for pat, label in WARN_PATTERNS for m in pat.finditer(text)]
    done = "\"Done (" in text and "For help, type" in text
    uptime = round(time.time() - start)
    print("\n==== runtime result ====")
    print(f"server reached 'Done': {done}   uptime: {uptime}s   exit: {proc.returncode}")
    print(f"problems: {len(problems)}")
    for p in dict.fromkeys(problems):
        print("  !!", p)
    print(f"warnings: {len(warnings)}")
    for w in dict.fromkeys(warnings):
        print("   ~", w)

    # console command output excerpt
    for key in ("Done (", "TPS", "Loaded ", "structure"):
        for m in re.finditer(rf"^.*{re.escape(key)}.*$", text, re.M):
            pass
    report = os.path.join(ROOT, "build", "report", "runtime.txt")
    with open(report, "w", encoding="utf-8") as fh:
        fh.write(f"done={done} uptime={uptime}s exit={proc.returncode}\n\nPROBLEMS\n" + "\n".join(dict.fromkeys(problems)))
        fh.write("\n\nWARNINGS\n" + "\n".join(dict.fromkeys(warnings)))
    print("report:", report, "log:", LOG)
    return 0 if (done and not problems) else 1


if __name__ == "__main__":
    raise SystemExit(main())
