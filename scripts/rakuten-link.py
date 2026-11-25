#!/usr/bin/env python3
"""Build and verify tracked Rakuten / Taobao affiliate links.

Background, all verified on 2026-11-24 against the live account:

  * The publisher id is 9bfb/6Q9Df4 and the Taobao advertiser is MID 54014.
  * A tracked link looks like

        https://click.linksynergy.com/fs-bin/click?id=9bfb%2f6Q9Df4
            &offerid=2095036.<linkid>&type=3&subid=0

    and redirects to the registered Taobao product with a unid= token added.

  * The offerid link id is NOT the Taobao product. It is a Rakuten-side
    record. Link ids 18-49 are registered and resolve to their own product;
    an unknown id silently falls back to the Taobao Global storefront. That
    fallback is still attributed, but it lands on the shop, not the item.

  * Rakuten's deep link form (click.linksynergy.com/deeplink?id=..&mid=..)
    ignores murl. Taobao does not allow deep linking to an arbitrary product
    through Rakuten, so mid=54014 always lands on the storefront.

  * Taobao's own short links (https://intl.taobao.com/sk/_b.XXXX) already
    carry Taobao-side affiliate tracking: they redirect to
    world.taobao.com/.../ovs-affiliate-pdp?itemId=..&pid=..&relationId=..
    with the pid intact.

  * The Automate widget on the site matches no merchant at all - every link
    logs "Failure. No merchant." and is rewritten with err_code=2. It must
    not be relied on. See scripts/check-rakuten-widget.py.

Usage:
    rakuten-link.py build 49                 # tracked link for a registered link id
    rakuten-link.py resolve "<url>"          # follow the chain, show pid/itemId
    rakuten-link.py check <file> [<file>..]  # resolve every URL found in the files
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

PUBLISHER_ID = "9bfb/6Q9Df4"
PUBLISHER_ID_ENC = "9bfb%2f6Q9Df4"
TAOBAO_MID = "54014"
TAOBAO_OFFER = "2095036"
LINK_TYPE = "3"

UA = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)

URL_RE = re.compile(r'https?://[^\s"\'<>)\]]+')
ITEM_RE = re.compile(r"[?&]itemId=(\d+)")
PID_RE = re.compile(r"[?&]pid=([^&]+)")
REL_RE = re.compile(r"[?&]relationId=(\d+)")


def build(link_id: str | int) -> str:
    """The tracked Rakuten link for a registered Taobao link id."""
    return (
        "https://click.linksynergy.com/fs-bin/click"
        f"?id={PUBLISHER_ID_ENC}&offerid={TAOBAO_OFFER}.{link_id}"
        f"&type={LINK_TYPE}&subid=0"
    )


def shortcode(link_id: str | int, text: str = "buy on Taobao") -> str:
    """The Hugo shortcode call that renders the same link."""
    return (
        '{{< aff merchant="taobao" link="'
        f'{link_id}" text="{text}" >}}'
    )


def fetch(url: str, timeout: int = 25) -> tuple[str, str]:
    """Follow redirects, returning (final_url, chain)."""
    chain: list[str] = []
    current = url
    for _ in range(6):
        req = urllib.request.Request(
            current,
            headers={"User-Agent": UA, "Accept": "*/*"},
        )
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                body = resp.read(4000).decode("utf-8", "replace")
                final = resp.geturl()
        except urllib.error.HTTPError as exc:
            return f"HTTP {exc.code}", " -> ".join(chain + [current])
        except Exception as exc:  # noqa: BLE001
            return f"error: {exc}", " -> ".join(chain + [current])
        chain.append(current)
        if final == current:
            return body, " -> ".join(chain)
        current = final
    return "", " -> ".join(chain)


def describe(url: str) -> dict:
    """Resolve a link and say where it lands and whether it is attributed."""
    body, chain = fetch(url)
    final = chain.split(" -> ")[-1]
    # The tracking parameters live on the final hop, not the one we started
    # from - Rakuten redirects to intl.taobao.com, which then redirects to
    # the affiliate product page carrying the pid.
    haystack = final + " " + url
    item = ITEM_RE.search(haystack)
    pid = PID_RE.search(haystack)
    rel = REL_RE.search(haystack)
    out = {
        "url": url,
        "final": final,
        "chain": chain,
        "item_id": item.group(1) if item else "",
        "pid": pid.group(1) if pid else "",
        "relation_id": rel.group(1) if rel else "",
        "status": body if body.startswith(("HTTP", "error")) else "",
    }
    if out["item_id"] and out["pid"]:
        out["tracked"] = True
        out["kind"] = "taobao product"
    elif "ai.world.taobao.com" in final or "ovs-cpa" in final:
        out["tracked"] = True
        out["kind"] = "taobao global storefront (no product)"
    else:
        out["tracked"] = False
        out["kind"] = "not attributed"
    return out


def cmd_build(args: argparse.Namespace) -> int:
    link = build(args.link_id)
    print(link)
    print()
    print(shortcode(args.link_id, args.text))
    return 0


def cmd_resolve(args: argparse.Namespace) -> int:
    res = describe(args.url)
    print(f"url      {res['url']}")
    print(f"lands on {res['final'][:160]}")
    print(f"kind     {res['kind']}")
    if res["item_id"]:
        print(f"itemId   {res['item_id']}")
    if res["pid"]:
        print(f"pid      {res['pid']}")
    if res["relation_id"]:
        print(f"relation {res['relation_id']}")
    if res["status"]:
        print(f"status   {res['status']}")
    return 0


def cmd_check(args: argparse.Namespace) -> int:
    urls: list[str] = []
    for path in args.files:
        text = Path(path).read_text(encoding="utf-8", errors="replace")
        urls.extend(URL_RE.findall(text))
    seen: list[str] = []
    for u in urls:
        if u not in seen:
            seen.append(u)

    with ThreadPoolExecutor(max_workers=8) as pool:
        results = list(pool.map(describe, seen))

    tracked = [r for r in results if r["tracked"]]
    dead = [r for r in results if not r["tracked"]]
    print(f"Resolved {len(results)} unique URLs")
    print("-" * 72)
    for r in tracked:
        print(f"  OK    {r['kind']:<38} {r['url'][:80]}")
    for r in dead:
        print(f"  DEAD  {r['url'][:80]}  {r['status'][:40]}")
    print("-" * 72)
    print(f"  {len(tracked)} attributed, {len(dead)} not attributed")
    return 0 if not dead else 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)

    b = sub.add_parser("build", help="build a tracked link for a link id")
    b.add_argument("link_id", help="the registered Taobao link id, e.g. 49")
    b.add_argument("--text", default="buy on Taobao")
    b.set_defaults(func=cmd_build)

    r = sub.add_parser("resolve", help="resolve one URL and report attribution")
    r.add_argument("url")
    r.set_defaults(func=cmd_resolve)

    c = sub.add_parser("check", help="resolve every URL found in the given files")
    c.add_argument("files", nargs="+")
    c.set_defaults(func=cmd_check)

    args = ap.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
