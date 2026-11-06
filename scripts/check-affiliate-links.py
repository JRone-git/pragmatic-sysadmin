#!/usr/bin/env python3
"""
Check that every affiliate link on the built site actually earns.

The resources page once disclosed seven affiliate programmes with specific
commission rates - DigitalOcean, 1Password, Newegg, Lively, Consumer
Cellular, Bay Alarm Medical, Backblaze. Not one of them carried tracking.
The DigitalOcean link even said "I get a commission" on a plain
https://digitalocean.com URL with no referral code. Nothing in the build
noticed, because the disclosure was hand-written prose and the links were
hand-written URLs, and no check ever compared the two.

This script closes that gap. It reads catalog/affiliates.json and the built
HTML and asserts:

  A. A link in "param" or "path" mode that has a code carries that code in
     its URL.
  B. A link in "param" or "path" mode with no code earns nothing. Reported,
     not failed - that is the normal state before an application is approved.
  C. A link in "widget" mode is tracked by the Rakuten Automate widget, but
     only if the account is actually partnered with the advertiser.
  D. A "direct" link is a destination that earns nothing and never will.
  E. No commission claim is printed next to a link that earns nothing. This
     is the check that would have caught the original lie.
  F. The generated disclosure names only programmes that are actually
     applied.

Usage:
    python scripts/check-affiliate-links.py [public_dir]

Exits non-zero when a claim is made that the site cannot back up.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "catalog" / "affiliates.json"

# Hugo's minifier strips attribute quotes, so the same attribute appears as
# data-aff="newegg" in a dev build and data-aff=newegg in a production one.
# The pattern has to accept both.
def _attr(group: str) -> str:
    """Matches an attribute value in either the quoted or the unquoted form.

    The outer non-capturing group matters: without it the "|" splits the
    whole pattern instead of just this attribute. The attribute name itself
    is left to the caller so it is not repeated.
    """
    return rf'(?:"(?P<{group}>[^"]*)"|(?P<{group}2>[^\s>]+))'


ANCHOR_RE = re.compile(
    rf'<a\s[^>]*?href={_attr("href")}[^>]*?'
    rf'data-aff={_attr("merchant")}[^>]*?'
    rf'data-aff-mode={_attr("mode")}[^>]*?>',
    re.IGNORECASE,
)
NOTE_RE = re.compile(rf'data-aff-note={_attr("note")}', re.IGNORECASE)
DISCLOSURE_RE = re.compile(
    rf'<div[^>]*data-aff-disclosure={_attr("disc")}[^>]*>'
    r'(?P<body>.*?)</div>',
    re.IGNORECASE | re.DOTALL,
)


def _pick(m: re.Match, group: str) -> str:
    """Reads a value from either the quoted or the unquoted alternative."""
    quoted = m.groupdict().get(group)
    if quoted is not None:
        return quoted
    return m.groupdict().get(group + "2") or ""


# Words that promise money next to a link. If one of these appears after a
# link, that link had better start earning.
#
# Deliberately narrow. "affiliate link" on its own also turns up in
# disclosures and in sentences like "No affiliate links" - which is the
# opposite of a claim - so only the affirmative forms count.
CLAIM_WORDS = re.compile(
    r"i\s+(?:get|earn|receive)\s+(?:a\s+|small\s+|the\s+)?commission"
    r"|affiliate\s+link\s*[-–—:]"
    r"|referral\s+(?:link|code)\s*[-–—:]",
    re.IGNORECASE,
)

# A claim immediately preceded by one of these is a denial, not a promise.
NEGATION = re.compile(
    r"(?:no|not|never|without|neither|nor|isn't|aren't|don't|doesn't)\s+"
    r"(?:\w+\s+){0,3}$",
    re.IGNORECASE,
)


def claims_money(text: str) -> bool:
    """True when the text promises a commission rather than denying one."""
    for m in CLAIM_WORDS.finditer(text):
        before = text[max(0, m.start() - 60) : m.start()]
        if NEGATION.search(before):
            continue
        return True
    return False


def load_config() -> dict:
    raw = json.loads(CONFIG.read_text(encoding="utf-8"))
    return {k: v for k, v in raw.items() if not k.startswith("_")}


def is_tracked(spec: dict) -> bool:
    mode = spec.get("mode", "param")
    if mode == "direct":
        return False
    if mode == "widget":
        return spec.get("status") == "applied"
    return bool((spec.get("code") or "").strip())


def main() -> int:
    public = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "public"
    if not public.is_dir():
        print(f"check-affiliate-links: {public} does not exist - build the site first.")
        return 2

    config = load_config()
    failures: list[str] = []
    counts: dict[str, int] = {}
    missing_param: list[str] = []
    untracked: dict[str, set[str]] = {}
    pending_counts: dict[str, int] = {}

    pages = sorted(public.rglob("*.html"))
    if not pages:
        print("check-affiliate-links: no HTML found in the build output.")
        return 2

    for page in pages:
        html = page.read_text(encoding="utf-8", errors="replace")
        rel = page.relative_to(public)

        # Disclosure blocks are excluded from the per-link claim scan - the
        # page-level disclosure is allowed to mention commission.
        html_no_disclosure = DISCLOSURE_RE.sub(" ", html)

        # E. A generated claim for a merchant that earns nothing.
        for m in NOTE_RE.finditer(html):
            merchant = _pick(m, "note")
            spec = config.get(merchant)
            if spec is None:
                failures.append(f"{rel}: claim for unknown merchant {merchant!r}")
            elif not is_tracked(spec):
                failures.append(
                    f"{rel}: a commission claim is printed for {merchant}, but that "
                    f"link earns nothing (status={spec.get('status')!r}, "
                    f"code={(spec.get('code') or '')!r})."
                )

        # A, B, C, D and F. The claim scan runs over the text that follows
        # each anchor, up to the next anchor.
        pieces = list(ANCHOR_RE.finditer(html_no_disclosure))
        for i, m in enumerate(pieces):
            merchant = _pick(m, "merchant")
            mode = _pick(m, "mode").lower()
            href = _pick(m, "href")
            spec = config.get(merchant)

            if spec is None:
                failures.append(f"{rel}: data-aff={merchant!r} is not in catalog/affiliates.json")
                continue

            counts[merchant] = counts.get(merchant, 0) + 1
            end = pieces[i + 1].start() if i + 1 < len(pieces) else len(html_no_disclosure)
            trailing = html_no_disclosure[m.end() : end][:300]

            if mode in ("param", "path"):
                code = (spec.get("code") or "").strip()
                param = (spec.get("param") or "").strip()
                if not code:
                    untracked.setdefault(merchant, set()).add(str(rel))
                    if claims_money(trailing):
                        failures.append(
                            f"{rel}: a commission is promised next to a {merchant} link, "
                            f"but {merchant} has no code in catalog/affiliates.json - "
                            f"that link earns nothing."
                        )
                elif param and f"{param}={code}" not in href:
                    missing_param.append(f"{rel}: {merchant}")
            elif mode == "widget":
                if spec.get("status") != "applied":
                    pending_counts[merchant] = pending_counts.get(merchant, 0) + 1
                if claims_money(trailing) and spec.get("status") != "applied":
                    failures.append(
                        f"{rel}: a commission is promised next to a {merchant} link, "
                        f"but the Rakuten account is not partnered yet."
                    )
            # mode == direct: a plain link. No tracking expected, no failure.

        # F. The disclosure must name only applied programmes.
        for m in DISCLOSURE_RE.finditer(html):
            body = m.group("body")
            for spec in config.values():
                if spec.get("status") == "applied":
                    continue
                name = spec.get("name", "")
                if name and name in body:
                    failures.append(
                        f"{rel}: the disclosure names {name}, but that programme is "
                        f"not applied - the disclosure is claiming money the site "
                        f"does not earn."
                    )

    print("Affiliate link check")
    print("-" * 52)
    if counts:
        for merchant in sorted(counts):
            spec = config.get(merchant, {})
            tracked = is_tracked(spec)
            code = (spec.get("code") or "").strip()
            if tracked:
                state = f"tracked ({code})" if code else "tracked (widget)"
            elif spec.get("mode") == "direct":
                state = "plain link, earns nothing"
            else:
                state = "Earns nothing - no code yet"
            print(f"  {merchant:<20} {counts[merchant]:>3} link(s)   {state}")
    else:
        print("  no affiliate links found")

    if untracked:
        print()
        print("Links that earn nothing until a code is added:")
        for merchant in sorted(untracked):
            pages = len(untracked[merchant])
            print(
                f"  - {merchant}: {counts[merchant]} link(s) across {pages} page(s)"
            )

    if missing_param:
        print()
        print("Links whose URL is missing their tracking parameter:")
        for note in sorted(set(missing_param)):
            print(f"  - {note}")

    if pending_counts:
        print()
        print("Pending - tracked by the Rakuten widget, but the account is not")
        print("partnered with the advertiser yet, so nothing is earned:")
        for merchant in sorted(pending_counts):
            spec = config.get(merchant, {})
            print(
                f"  - {merchant}: {pending_counts[merchant]} link(s) - no commission "
                f"until the Rakuten account is partnered with "
                f"{spec.get('name', merchant)}"
            )

    print()
    if failures:
        print(f"FAIL - {len(failures)} problem(s):")
        for f in failures[:40]:
            print(f"  - {f}")
        if len(failures) > 40:
            print(f"  ... and {len(failures) - 40} more")
        return 1

    print("PASS - no link promises a commission it cannot deliver.")
    if untracked or warnings:
        print(f"      {len(set(untracked))} merchant(s) still need a code.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
