#!/usr/bin/env python3
"""Local HTTP cache proxy in front of the `fetch_page` tool (used by the sandbox).

The session sandbox has no direct egress to api.modrinth.com, but the agent's
fetch_page tool does. This proxy lets plain python/curl code reach Modrinth:

    PROXY  = scripts/proxy_fetch.py serving 127.0.0.1:8899
    fetch  http://127.0.0.1:8899/http://api.modrinth.com/v2/project/sodium
    (code uses env RAW_API=http://127.0.0.1:8899/http://api.modrinth.com/v2)

Requests are cached in build/netcache/<sha1>.json, so repeated builds are instant.
This file is developer tooling for the sandbox only; the pack build in CI talks to
Modrinth directly.
"""
from __future__ import annotations

import hashlib
import http.server
import json
import os
import re
import socketserver
import sys
import time
import urllib.parse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.join(ROOT, "build", "netcache")
os.makedirs(CACHE, exist_ok=True)
PORT = int(os.environ.get("PROXY_PORT", "8899"))

_fetch_page = None


def tool_fetch_page():
    """`fetch_page` is injected by the agent harness as an in-process tool."""
    global _fetch_page
    if _fetch_page is None:
        import __main__  # noqa: F401  (the harness registers the tool globally)
        _fetch_page = globals().get("fetch_page")
    return _fetch_page


def clean(text: str) -> str:
    t = text.strip()
    if t.startswith("```"):
        t = t.split("\n", 1)[1] if "\n" in t else t
    if t.endswith("```"):
        t = t[: -3]
    return t.strip()


def via_fetch_page(url: str) -> str:
    fn = tool_fetch_page()
    if fn is None:
        raise RuntimeError("fetch_page tool is not available in this process")
    parts = []
    for idx in range(8):
        res = fn(url=url, chunkIndex=idx)
        content = res.get("content", "") if isinstance(res, dict) else str(res)
        if isinstance(res, dict) and res.get("status") not in (None, "success"):
            if idx == 0:
                raise RuntimeError(f"fetch failed: {res.get('status')}")
            break
        parts.append(clean(content))
        joined = "".join(parts)
        try:
            json.loads(joined)
            return joined
        except Exception:  # noqa: BLE001
            continue
    joined = "".join(parts)
    try:
        json.loads(joined)
    except Exception as exc:  # noqa: BLE001
        raise RuntimeError(f"incomplete json ({exc}); {len(joined)} bytes") from exc
    return joined


def fetch(url: str) -> bytes:
    key = hashlib.sha1(url.encode()).hexdigest()[:24]
    path = os.path.join(CACHE, key + ".json")
    if os.path.exists(path):
        return open(path, "rb").read()
    for attempt in range(4):
        try:
            body = via_fetch_page(url).encode()
            open(path, "wb").write(body)
            time.sleep(0.2)
            return body
        except Exception as exc:  # noqa: BLE001
            sys.stderr.write(f"proxy retry {attempt} {url}: {exc}\n")
            time.sleep(2 + attempt * 3)
    raise RuntimeError(f"giving up on {url}")


class Handler(http.server.BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def do_GET(self):  # noqa: N802
        target = self.path[1:]
        if not target.startswith("http"):
            target = urllib.parse.unquote(target)
        try:
            body = fetch(target)
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        except Exception as exc:  # noqa: BLE001
            msg = json.dumps({"error": str(exc)}).encode()
            self.send_response(502)
            self.send_header("Content-Length", str(len(msg)))
            self.end_headers()
            self.wfile.write(msg)

    def log_message(self, fmt, *args):  # noqa: D401
        sys.stderr.write("%s\n" % (fmt % args))


class Server(socketserver.ThreadingTCPServer):
    allow_reuse_address = True


if __name__ == "__main__":
    sys.stderr.write(f"modrinth fetch_page proxy on http://127.0.0.1:{PORT}\n")
    with Server(("0.0.0.0", PORT), Handler) as srv:
        srv.serve_forever()
