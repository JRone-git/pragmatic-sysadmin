#!/usr/bin/env python3
"""Notify Google Search Console after each deploy (stdlib only).

1. Re-submits sitemap.xml via the Search Console API
   (PUT /webmasters/v3/sites/{siteUrl}/sitemaps/{feedpath}).
2. Inspects every queued post URL via the URL Inspection API and prints
   each URL's index verdict, so coverage gaps show up in the workflow log.

Auth: service-account JSON in the GSC_SA_JSON env var (GitHub secret —
NEVER commit the key file). RS256 JWT is signed with the `openssl` CLI,
which is preinstalled on ubuntu-latest runners.

Google offers no public "index this URL now" endpoint for normal pages
(the Indexing API is restricted to job postings/livestreams), so this is
sitemap submission + coverage monitoring — the maximum Google allows
programmatically. Discovery itself comes from the sitemap + the backlinks
the promotion engine earns (dev.to canonicals, Reddit/HN, socials).
"""

from __future__ import annotations

import base64
import json
import os
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
QUEUE_DIR = ROOT / "promotion" / "queue"

SITE_URL = "https://pragmaticsysadmin.help/"
SITEMAP_URL = "https://pragmaticsysadmin.help/sitemap.xml"
SCOPE = "https://www.googleapis.com/auth/webmasters"


def b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def access_token(sa: dict) -> str:
    """Exchange the service-account key for an OAuth access token."""
    now = int(time.time())
    header = b64url(json.dumps({"alg": "RS256", "typ": "JWT"}).encode())

    claims = b64url(json.dumps({
        "iss": sa["client_email"],
        "scope": SCOPE,
        "aud": "https://oauth2.googleapis.com/token",
        "iat": now,
        "exp": now + 3600,
    }).encode())
    signing_input = f"{header}.{claims}".encode()

    with tempfile.NamedTemporaryFile("w", suffix=".pem",
                                     delete=False) as fh:
        fh.write(sa["private_key"])
        key_path = fh.name
    try:
        proc = subprocess.run(
            ["openssl", "dgst", "-sha256", "-sign", key_path],
            input=signing_input, capture_output=True, timeout=30,
        )
    except FileNotFoundError:
        print("openssl CLI not found — cannot sign JWT.", file=sys.stderr)
        raise SystemExit(2)
    finally:
        try:
            os.unlink(key_path)
        except OSError:
            pass
    if proc.returncode != 0:
        print(f"openssl sign failed: {proc.stderr.decode()[:200]}",
              file=sys.stderr)
        raise SystemExit(2)

    jwt = f"{header}.{claims}.{b64url(proc.stdout)}"
    body = urllib.parse.urlencode({
        "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
        "assertion": jwt,
    }).encode()
    req = urllib.request.Request(
        "https://oauth2.googleapis.com/token", data=body,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read())
    return data["access_token"]


def api(method: str, url: str, token: str, payload: dict | None = None):
    body = None
    headers = {"Authorization": f"Bearer {token}"}
    if payload is not None:
        body = json.dumps(payload).encode()
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read()
            return resp.status, json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "ignore")[:500]


def submit_sitemap(token: str) -> bool:
    site = urllib.parse.quote(SITE_URL, safe="")
    feed = urllib.parse.quote(SITEMAP_URL, safe="")
    url = (f"https://www.googleapis.com/webmasters/v3/sites/{site}"
           f"/sitemaps/{feed}")
    status, body = api("PUT", url, token)
    if status in (200, 201, 204):
        print(f"Search Console: sitemap submitted ({status}).")
        return True
    print(f"Search Console: sitemap submit failed: {status} {body}",
          file=sys.stderr)
    return False


def queued_urls() -> list[str]:
    """URLs with pitch packages (recent posts awaiting promotion)."""
    urls = []
    if not QUEUE_DIR.is_dir():
        return urls
    for pkg in sorted(QUEUE_DIR.iterdir()):
        card = pkg / "package.json"
        if not card.exists():
            continue
        post = json.loads(card.read_text(encoding="utf-8"))
        if post.get("url"):
            urls.append(post["url"])
    return urls


def inspect_urls(token: str, urls: list[str]) -> bool:
    ok = True
    url = "https://searchconsole.googleapis.com/v1/urlInspection/index:inspect"
    for target in urls:
        status, body = api("POST", url, token, {
            "inspectionUrl": target,
            "siteUrl": SITE_URL,
        })
        if status != 200:
            print(f"inspect {target}: HTTP {status} {body}", file=sys.stderr)
            ok = False
            continue
        result = (body.get("inspectionResult") or {})
        verdict = result.get("indexStatusResult", {}).get("verdict", "?")
        coverage = result.get("indexStatusResult", {}).get("coverageState", "?")
        print(f"inspect {target}\n  verdict={verdict} coverage={coverage}")
    return ok


def main() -> int:
    raw = os.environ.get("GSC_SA_JSON", "")
    if not raw:
        print("GSC_SA_JSON not set — Search Console step skipped.")
        return 0
    try:
        sa = json.loads(raw)
        token = access_token(sa)
    except SystemExit as e:
        return int(e.code or 2)
    except Exception as e:  # bad key, network, auth refused
        print(f"Search Console auth failed: {e}", file=sys.stderr)
        return 1

    ok = submit_sitemap(token)
    urls = queued_urls()
    if urls:
        print(f"Inspecting {len(urls)} queued URL(s)…")
        ok = inspect_urls(token, urls) and ok
    else:
        print("No queued URLs to inspect.")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())

