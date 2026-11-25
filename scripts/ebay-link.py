#!/usr/bin/env python3
"""Build and verify eBay Partner Network tracking links.

An EPN link is the target eBay URL with six tracking parameters appended:

    [TARGET][?|&]mkevt=1&mkcid=1&mkrid=[ROTATION-ID]&campid=[CAMPAIGN-ID]
              &toolid=[TOOL-ID]&customid=[SUB-ID]

mkevt   1 = click
mkcid   1 = EPN channel
mkrid   rotation id, chosen by the marketplace the link points at
campid  the publisher's own EPN campaign id - this is the one that is
        unique to you and the one that makes the link yours
toolid  the tool that produced the link (10001 = link generator default)
customid optional sub id

The target changes per product; the tracking does not. So the account
values live once in catalog/affiliates.json and every link is built from
them. Nothing is hand-written per product.

Workflow:

    # once: paste a link from eBay's "Create a Promotable Link" tool
    python3 scripts/ebay-link.py ingest "<the generated link>"

    # every time after that
    python3 scripts/ebay-link.py build "https://www.ebay.de/itm/123456"
    python3 scripts/ebay-link.py verify "https://www.ebay.de/itm/123456?..."

Usage:
    ebay-link.py build <target-url> [--customid X]
    ebay-link.py ingest <generated-link>
    ebay-link.py verify <link>
    ebay-link.py show
"""

from __future__ import annotations

import argparse
import collections
import json
import sys
import urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "catalog" / "affiliates.json"

# Rotation ids per marketplace, lifted verbatim from eBay's own
# epn-smart-tools.js. The site id is the second half of the pair - eBay
# needs both, and guessing either one produces a link that looks right
# and attributes to nobody.
DEFAULT_ROTATION = {
    "ebay.com": ("711-53200-19255-0", "0"),
    "ebay.ca": ("706-53473-19255-0", "2"),
    "ebay.co.uk": ("710-53481-19255-0", "3"),
    "ebay.com.au": ("705-53470-19255-0", "15"),
    "ebay.at": ("5221-53469-19255-0", "16"),
    "ebay.be": ("1553-53471-19255-0", "23"),
    "ebay.fr": ("709-53476-19255-0", "71"),
    "ebay.de": ("707-53477-19255-0", "77"),
    "ebay.it": ("724-53478-19255-0", "101"),
    "ebay.nl": ("1346-53482-19255-0", "146"),
    "ebay.es": ("1185-53479-19255-0", "186"),
    "ebay.ch": ("5222-53480-19255-0", "193"),
    "ebay.ie": ("5282-53468-19255-0", "205"),
    "ebay.pl": ("4908-226936-19255-0", "212"),
}

TRACK_KEYS = ("mkevt", "mkcid", "mkrid", "campid", "toolid", "customid")


def load() -> dict:
    return json.loads(CONFIG.read_text(encoding="utf-8"))


def merchant() -> dict:
    data = load()
    if "ebay" not in data:
        raise SystemExit("no ebay merchant in catalog/affiliates.json")
    return data["ebay"]


def domain_of(url: str) -> str:
    host = urllib.parse.urlparse(url).netloc.lower()
    return host[4:] if host.startswith("www.") else host


def build(target: str, customid: str = "") -> str:
    spec = merchant()
    campid = (spec.get("code") or "").strip()
    if not campid:
        raise SystemExit(
            "catalog/affiliates.json has no eBay campaign id yet.\n"
            "Run:  python3 scripts/ebay-link.py ingest \"<a link from eBay's "
            "Create a Promotable Link tool>\""
        )
    markets = {
        k: (v.get("mkrid", ""), v.get("siteid", ""))
        for k, v in (spec.get("markets") or {}).items()
        if isinstance(v, dict)
    }
    for domain, pair in DEFAULT_ROTATION.items():
        markets.setdefault(domain, pair)
    host = domain_of(target)
    mkrid, siteid = markets.get(host, ("", ""))

    parts = {
        "mkevt": "1",
        "mkcid": "1",
        "mkrid": mkrid,
        "siteid": siteid,
        "customid": "link",
        "campid": campid,
        "toolid": (spec.get("toolid") or "20001").strip(),
    }
    if customid:
        parts["customid"] = customid
    sep = "&" if "?" in target else "?"
    return target + sep + urllib.parse.urlencode(parts)


def parse(url: str) -> dict:
    query = urllib.parse.urlparse(url).query
    return {k: v[0] for k, v in urllib.parse.parse_qs(query).items()}


def cmd_build(args: argparse.Namespace) -> int:
    print(build(args.target, args.customid))
    return 0


def cmd_ingest(args: argparse.Namespace) -> int:
    params = parse(args.link)
    missing = [k for k in ("campid", "mkrid") if not params.get(k)]
    if missing:
        raise SystemExit(
            "that link carries no " + ", ".join(missing) + ". It looks like a plain "
            "eBay URL. Generate one from the EPN portal's "
            '"Create a Promotable Link" tool first.'
        )
    spec = merchant()
    print("Account values found in that link:")
    print(f'  campid   {params["campid"]}')
    print(f'  mkrid    {params["mkrid"]}')
    if params.get("toolid"):
        print(f'  toolid   {params["toolid"]}')
    if params.get("customid"):
        print(f'  customid {params["customid"]}')
    print(f'  domain   {domain_of(args.link)}')

    if not args.write:
        print("\nRe-run with --write to store these in catalog/affiliates.json.")
        return 0

    data = load()
    entry = data["ebay"]
    entry["code"] = params["campid"]
    entry["status"] = "applied"
    if params.get("toolid"):
        entry["toolid"] = params["toolid"]
    # Keep the rotation id this link proves, for the marketplace it points at.
    host = domain_of(args.link)
    if host and host in (entry.get("markets") or {}):
        entry["markets"][host]["mkrid"] = params["mkrid"]
    if params.get("siteid") and host in (entry.get("markets") or {}):
        entry["markets"][host]["siteid"] = params["siteid"]
    CONFIG.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"\nWritten to {CONFIG.relative_to(ROOT)}. Rebuild and the links start tracking.")
    print("Then run:  python3 scripts/check-affiliate-links.py")
    return 0


def cmd_verify(args: argparse.Namespace) -> int:
    spec = merchant()
    params = parse(args.link)
    campid = (spec.get("code") or "").strip()
    print(f"link     {args.link[:120]}")
    print(f"domain   {domain_of(args.link)}")
    for key in TRACK_KEYS:
        if params.get(key):
            print(f"  {key:<9} {params[key]}")
    if not campid:
        print("\n  the catalogue has no campaign id yet - nothing to compare against")
        return 1
    if params.get("campid") == campid:
        print(f"\n  OK - carries this site's own campaign id ({campid})")
        return 0
    print(f"\n  WRONG - campid is {params.get('campid')!r}, expected {campid!r}")
    return 1


def cmd_show(args: argparse.Namespace) -> int:
    spec = merchant()
    print(json.dumps(spec, indent=2, ensure_ascii=False))
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)

    b = sub.add_parser("build", help="build a tracking link for an eBay URL")
    b.add_argument("target")
    b.add_argument("--customid", default="")
    b.set_defaults(func=cmd_build)

    i = sub.add_parser("ingest", help="read the account values out of a generated link")
    i.add_argument("link")
    i.add_argument("--write", action="store_true", help="store the values in the catalogue")
    i.set_defaults(func=cmd_ingest)

    v = sub.add_parser("verify", help="check that a link carries your campaign id")
    v.add_argument("link")
    v.set_defaults(func=cmd_verify)

    s = sub.add_parser("show", help="print the ebay entry from the catalogue")
    s.set_defaults(func=cmd_show)

    args = ap.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
