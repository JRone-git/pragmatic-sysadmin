#!/usr/bin/env python3
"""Stamp the Buddy service worker with a cache name that matches the shell.

The service worker caches the app shell - index.html, style.css, app.js,
i18n.js - so that Buddy opens when there is no signal. The cache had a
fixed name, `buddy-v1`, that was never bumped. A browser therefore kept
serving the app.js it had cached, and only picked up a new one on the
second load, because the strategy is stale-while-revalidate: the cached
copy goes out immediately and the network copy refreshes the cache in the
background for next time.

That is how the same build behaves differently on two devices. It is also
how a parent can be running a week-old copy of Buddy with a bug in it
that was fixed days ago.

The fix is to make the cache name a function of the shell contents, and
to write that into sw.js so the file itself changes. A changed sw.js is
what makes the browser install a new service worker, and the activate
handler drops the old cache.

Runs before the Hugo build, because the build copies static/buddy/sw.js
into the site verbatim.
"""

from __future__ import annotations

import hashlib
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BUDDY = ROOT / "static" / "buddy"
SW = BUDDY / "sw.js"

# The same list the worker precaches.
SHELL = [
    "index.html",
    "style.css",
    "app.js",
    "i18n.js",
    "manifest.webmanifest",
    "icon-192.png",
    "icon-512.png",
]

CACHE_RE = re.compile(r"^const CACHE = 'buddy-[0-9a-z]+';$", re.M)


def shell_hash() -> str:
    digest = hashlib.sha256()
    for name in SHELL:
        path = BUDDY / name
        if not path.exists():
            print(f"bump-sw-cache: missing {name}", file=sys.stderr)
            continue
        digest.update(name.encode("utf-8"))
        digest.update(path.read_bytes())
    return digest.hexdigest()[:12]


def main() -> int:
    if not SW.exists():
        print(f"bump-sw-cache: {SW} not found", file=sys.stderr)
        return 1
    text = SW.read_text(encoding="utf-8")
    if not CACHE_RE.search(text):
        print("bump-sw-cache: could not find the CACHE constant", file=sys.stderr)
        return 1
    version = f"buddy-{shell_hash()}"
    updated = CACHE_RE.sub(f"const CACHE = '{version}';", text)
    if updated != text:
        SW.write_text(updated, encoding="utf-8")
        print(f"bump-sw-cache: cache name -> {version}")
    else:
        print(f"bump-sw-cache: already {version}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
