#!/usr/bin/env python3
"""Inject SEO/social metadata + a monetization CTA block into the free web tools.

The interactive tools live in /static/tools/*.html and are copied verbatim by
Hugo — they get no template help, so their metadata and conversion paths have
to be injected into the files themselves. This is the same approach as
scripts/inject_tool_nav.py, and it is idempotent: re-running it never
duplicates markup (it looks for its own markers).

What each tool gets:
  1. <head>: canonical (if missing), meta description (if missing),
     Open Graph + Twitter Card tags, and WebApplication JSON-LD.
     Without these, sharing a tool on HN/Reddit/X produces a bare link with
     no card — which is the main way these pages travel.
  2. End of <body>: a "keep the momentum" block that
       - links 2-3 relevant guides (internal links = SEO + affiliate surface),
       - captures email for the newsletter (Buttondown, same list as the blog),
       - surfaces one paid product (contextual: $9 sysadmin toolkit vs $5
         senior checklist) plus the shop and Ko-fi support links.

Usage:
    python scripts/inject-tool-cta.py            # inject / refresh
    python scripts/inject-tool-cta.py --check    # report status, no writes
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TOOLS_DIR = REPO_ROOT / "static" / "tools"
SITE = "https://pragmaticsysadmin.help"

HEAD_MARKER_START = "<!-- Pragmatic Sysadmin Tool Meta (scripts/inject-tool-cta.py) -->"
HEAD_MARKER_END = "<!-- Pragmatic Sysadmin Tool Meta end (scripts/inject-tool-cta.py) -->"
CTA_MARKER_START = "<!-- Pragmatic Sysadmin Tool CTA (scripts/inject-tool-cta.py) -->"
CTA_MARKER_END = "<!-- Pragmatic Sysadmin Tool CTA end (scripts/inject-tool-cta.py) -->"

NEWSLETTER_ACTION = "https://buttondown.com/api/emails/embed-subscribe/jonne"
KOFI_SUPPORT = "https://ko-fi.com/sysadmin_dad"
SHOP_URL = f"{SITE}/shop/"
TOOLS_URL = f"{SITE}/tools/"
OG_IMAGE = f"{SITE}/og-default.png"

# Contextual paid offer shown next to the newsletter box. One per tool, chosen
# to match that tool's audience.
OFFERS = {
    "sysadmin": {
        "label": "The 5-Minute Server Health Check Toolkit — $9",
        "text": "3 production-tested bash scripts, a printable weekly checklist, and a decision tree for every warning.",
        "cta": "See what's inside →",
        "url": f"{SITE}/products/health-check-toolkit/",
    },
    "senior": {
        "label": "Senior Phone Setup & Maintenance Checklist — $5",
        "text": "All four senior-tech guides as one laminatable PDF you can leave with your parent.",
        "cta": "Get the printable →",
        "url": "https://ko-fi.com/s/a567718347",
    },
}

# Per-tool metadata. `description` is only written when the page has none;
# `guides` are canonical post URLs (verify with --check against the built site).
def _esc(value: str) -> str:
    return value.replace("&", "&amp;").replace('"', "&quot;").replace("<", "&lt;").replace(">", "&gt;")


CARD = "background:#1e293b;border:1px solid #334155;border-left:3px solid #2563eb;border-radius:8px;padding:1.15rem 1.25rem;"
LINK = "color:#93c5fd;text-decoration:none;"


def head_block(title: str, description: str, url: str, has_canonical: bool, has_description: bool) -> str:
    """Canonical + description (only when missing) + social cards + JSON-LD."""
    lines = [HEAD_MARKER_START]
    if not has_canonical:
        lines.append(f'<link rel="canonical" href="{url}">')
    if not has_description:
        lines.append(f'<meta name="description" content="{_esc(description)}">')
    lines += [
        '<meta property="og:type" content="website">',
        '<meta property="og:site_name" content="Pragmatic Sysadmin">',
        f'<meta property="og:title" content="{_esc(title)}">',
        f'<meta property="og:description" content="{_esc(description)}">',
        f'<meta property="og:url" content="{url}">',
        f'<meta property="og:image" content="{OG_IMAGE}">',
        '<meta property="og:image:width" content="1200">',
        '<meta property="og:image:height" content="630">',
        '<meta name="twitter:card" content="summary_large_image">',
        f'<meta name="twitter:title" content="{_esc(title)}">',
        f'<meta name="twitter:description" content="{_esc(description)}">',
        f'<meta name="twitter:image" content="{OG_IMAGE}">',
    ]
    schema = {
        "@context": "https://schema.org",
        "@type": "WebApplication",
        "name": title,
        "url": url,
        "description": description,
        "applicationCategory": "UtilitiesApplication",
        "operatingSystem": "Any (runs in the browser)",
        "isAccessibleForFree": True,
        "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"},
        "publisher": {"@type": "Organization", "name": "Pragmatic Sysadmin", "url": f"{SITE}/"},
    }
    lines.append('<script type="application/ld+json">')
    lines.append(json.dumps(schema, ensure_ascii=False, indent=2))
    lines.append("</script>")
    lines.append(HEAD_MARKER_END)
    return "\n".join(lines) + "\n"


def cta_block(meta: dict) -> str:
    """Guide links + newsletter capture + one contextual paid offer."""
    guide_items = "\n".join(
        f'      <li style="margin:.35rem 0;"><a href="{SITE}{path}" style="{LINK}">{_esc(anchor)}</a></li>'
        for anchor, path in meta["guides"]
    )
    offer = OFFERS[meta["offer"]]
    return f'''{CTA_MARKER_START}
<section style="background:#0f172a;border-top:1px solid #334155;color:#cbd5e1;padding:2rem 1.25rem 2.25rem;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;">
  <div style="max-width:820px;margin:0 auto;">
    <h2 style="color:#f8fafc;font-size:1.1rem;margin:0 0 .6rem;">Keep going — the guides behind this tool</h2>
    <ul style="margin:0 0 1.5rem;padding-left:1.15rem;line-height:1.6;font-size:.95rem;">
{guide_items}
    </ul>

    <div style="{CARD}">
      <h3 style="color:#f8fafc;font-size:1rem;margin:0 0 .4rem;">📬 One practical guide a week — free</h3>
      <p style="margin:0 0 .9rem;font-size:.92rem;line-height:1.5;">Sysadmin how-tos, senior-tech fixes, and new free tools. No spam, unsubscribe anytime.</p>
      <form action="{NEWSLETTER_ACTION}" method="post" target="_top" style="display:flex;gap:.5rem;flex-wrap:wrap;margin:0 0 .8rem;">
        <input type="email" name="email" required placeholder="your@email.com" autocomplete="email" aria-label="Email address" style="flex:1;min-width:220px;padding:.6rem .8rem;border:1px solid #475569;border-radius:6px;background:#0f172a;color:#f1f5f9;font-size:.95rem;font-family:inherit;">
        <button type="submit" style="background:#2563eb;color:#fff;border:0;border-radius:6px;padding:.6rem 1.15rem;font-weight:600;font-size:.95rem;cursor:pointer;font-family:inherit;white-space:nowrap;">Subscribe free →</button>
      </form>
      <p style="margin:0;font-size:.8rem;color:#94a3b8;">Subscribers also get the free Home Network Security Checklist and the 5 Bash Scripts pack.</p>
    </div>

    <div style="{CARD}border-left-color:#c97b5e;margin-top:1rem;">
      <h3 style="color:#f8fafc;font-size:1rem;margin:0 0 .4rem;">{_esc(offer["label"])}</h3>
      <p style="margin:0 0 .7rem;font-size:.92rem;line-height:1.5;">{_esc(offer["text"])}</p>
      <a href="{offer["url"]}" style="display:inline-block;background:#c97b5e;color:#fff;padding:.55rem 1.1rem;border-radius:6px;font-weight:600;font-size:.92rem;text-decoration:none;">{_esc(offer["cta"])}</a>
    </div>

    <p style="margin:1.5rem 0 0;font-size:.88rem;display:flex;gap:1.25rem;flex-wrap:wrap;">
      <a href="{TOOLS_URL}" style="{LINK}">All free tools →</a>
      <a href="{SHOP_URL}" style="{LINK}">Shop: scripts &amp; printable guides →</a>
      <a href="{KOFI_SUPPORT}" style="{LINK}">☕ Support on Ko-fi</a>
    </p>
  </div>
</section>
{CTA_MARKER_END}
'''


# Per-tool metadata. `description` is only written when the page has none;
# `guides` are canonical post URLs (verify with --check against the built site).
TOOL_META: dict[str, dict] = {
    "ai-prompt-builder.html": {
        "description": "Build better prompts for ChatGPT, Claude, or Copilot in seconds. Pick an IT task, fill in the blanks, and copy a prompt that gets useful answers instead of generic ones.",
        "guides": [
            ("Tech Survival Guide: AI Edition 2026", "/sysadmin/tech-survival-guide-ai-edition-2026/"),
            ("AI for IT Troubleshooting: Real-World Use Cases", "/sysadmin/ai-for-it-troubleshooting-2026/"),
        ],
        "offer": "sysadmin",
    },
    "battle-station-score.html": {
        "description": "Rate your desk, chair, monitors, and lighting and get a 0-100 battle station score with concrete fixes. Free, no signup.",
        "guides": [
            ("Setting Up a Home Lab: A Beginner's Guide", "/sysadmin/2025-10-29-setting-up-a-home-lab-a-beginner-s-guide/"),
            ("What IT Pros Actually Do On Their Own Machines", "/sysadmin/2026-03-18-what-it-pros-actually-do-on-their-own-machines-vs-what-they-tell-you/"),
        ],
        "offer": "sysadmin",
    },
    "cli-adventure.html": {
        "description": "Learn Linux troubleshooting by playing: a terminal adventure where you diagnose servers with real commands in a safe fake environment.",
        "guides": [
            ("A Sandbox for the Linux Commands You're Afraid to Run", "/sysadmin/2026-09-26-a-sandbox-for-the-linux-commands-youre-afraid-to-run/"),
            ("Linux Things That Are Easy to Miss", "/sysadmin/2026-07-13-linux-things-easy-to-miss/"),
        ],
        "offer": "sysadmin",
    },
    "command-simulator.html": {
        "description": "Preview what destructive Linux commands do (rm -rf, dd, mkfs, iptables -F) against a simulated filesystem before you ever type them on a real server.",
        "guides": [
            ("A Sandbox for the Linux Commands You're Afraid to Run", "/sysadmin/2026-09-26-a-sandbox-for-the-linux-commands-youre-afraid-to-run/"),
            ("Git Things That Are Easy to Mess Up", "/sysadmin/2026-07-14-git-things-easy-to-mess-up/"),
        ],
        "offer": "sysadmin",
    },
    "corporate-translator.html": {
        "description": "Turn technical incident notes into corporate-speak incident reports management will actually read — with severity, impact, and next steps.",
        "guides": [
            ("The Documentation I Wish I'd Written", "/sysadmin/2026-03-04-i-was-the-only-it-person-for-3-years-the-documentation-i-wish-id-written/"),
            ("Explain Any Command or Error in Plain English", "/meta/plain-english-explain-any-command-error-concept/"),
        ],
        "offer": "sysadmin",
    },
    "homelab-architect.html": {
        "description": "Paste your Docker Compose stack to visualize it, audit for security issues, find single points of failure, and generate a backup plan. Free homelab design tool.",
        "guides": [
            ("Homelab Architect: Plan Before You Build", "/meta/homelab-architect-plan-before-you-build/"),
            ("Setting Up a Home Lab: A Beginner's Guide", "/sysadmin/2025-10-29-setting-up-a-home-lab-a-beginner-s-guide/"),
        ],
        "offer": "sysadmin",
    },
    "password-checker.html": {
        "description": "Check how strong a password really is — length, character classes, and common-pattern weaknesses — right in your browser. Nothing is sent anywhere.",
        "guides": [
            ("Password Managers for Elderly Parents", "/senior-tech/2026-07-27-password-manager-for-elderly-parents/"),
            ("Zero Trust for Small Teams: Practical Steps", "/sysadmin/zero-trust-small-teams-2026/"),
        ],
        "offer": "senior",
    },
    "plain-english.html": {
        "description": "Paste any command, error message, or log line and get it explained in plain English — what it means, why it happened, and what to check next.",
        "guides": [
            ("Explain Any Command or Error in Plain English", "/meta/plain-english-explain-any-command-error-concept/"),
            ("The Art of Reading Logs Like a Detective", "/sysadmin/2025-12-17-the-art-of-reading-logs-like-a-detective-finding-needles-in-haystacks/"),
        ],
        "offer": "sysadmin",
    },
    "prism-engine.html": {
        "description": "Turn a Docker Compose, Kubernetes, or network config into a 3D infrastructure topology you can click through, with risk analysis per node. Free browser tool.",
        "guides": [
            ("Kubernetes Without Jargon: Pods, Processes, Services", "/sysadmin/kubernetes-without-jargon-pods-processes-services/"),
            ("Self-Hosting Isn't Free: The Honest Math", "/sysadmin/2026-09-10-self-hosting-isnt-free-honest-cost-running-own-server/"),
        ],
        "offer": "sysadmin",
    },
    "pulse.html": {
        "description": "A short digital resilience assessment: score how well your backups, updates, passwords, and recovery plan would survive a real incident.",
        "guides": [
            ("Why Your Monitoring is Broken (And How to Fix It)", "/sysadmin/2025-11-06-why-your-monitoring-is-broken-and-how-to-fix-it-before-your-boss-notices/"),
            ("The Friday Backup Audit: Because Hope Is Not a Strategy", "/sysadmin/2025-12-12-the-friday-backup-audit-because-hope-is-not-a-strategy/"),
        ],
        "offer": "sysadmin",
    },
    "script-generator.html": {
        "description": "Generate ready-to-edit bash and PowerShell scripts for common sysadmin chores — disk checks, log cleanup, service restarts, backups — without starting from a blank file.",
        "guides": [
            ("Stop Doing Things Manually: 5 Scripts That'll Make You Look Like a Genius", "/sysadmin/stop-doing-things-manually/"),
            ("The 5-Minute Server Health Check That Could Save Your Career", "/sysadmin/2025-12-09-the-5-minute-server-health-check-that-could-save-your-career/"),
        ],
        "offer": "sysadmin",
    },
    "tech-needs-advisor.html": {
        "description": "Answer a few questions about how your parent uses tech — calls, photos, video calls, reading — and get a recommendation for the right phone, tablet, or setup.",
        "guides": [
            ("Best Phones for Seniors in 2026 (Tested by Real Grandparents)", "/senior-tech/2026-07-01-best-phones-for-seniors-2026/"),
            ("Best Tablets for Seniors in 2026 (Tested by Real Grandparents)", "/senior-tech/2026-07-14-best-tablets-for-seniors-2026/"),
        ],
        "offer": "senior",
    },
}


TOOL_TITLES = {
    "ai-prompt-builder.html": "AI Prompt Builder for IT & Sysadmin Tasks",
    "battle-station-score.html": "Battle Station Score Calculator",
    "cli-adventure.html": "CLI Adventure: Learn Linux Troubleshooting",
    "command-simulator.html": "Linux Command Simulator: Test Destructive Commands Safely",
    "corporate-translator.html": "Corporate Translator: Sysadmin to Management Speak",
    "homelab-architect.html": "Homelab Architect: Docker Compose & Infrastructure Planner",
    "password-checker.html": "Password Strength Checker: In-Browser & Private",
    "plain-english.html": "Plain English: Explain Commands, Errors & Tech Jargon",
    "prism-engine.html": "PRISM Engine: 3D Infrastructure Topology Visualizer",
    "pulse.html": "Sysadmin Digital Resilience Scorecard (PULSE)",
    "script-generator.html": "Sysadmin Script Generator: Bash & PowerShell Automation",
    "tech-needs-advisor.html": "Senior Tech Needs Advisor: Find the Right Phone or Tablet",
}


def _title_from_html(html: str) -> str:
    match = re.search(r"<title>(.*?)</title>", html, flags=re.S | re.I)
    if not match:
        return ""
    title = re.sub(r"\s+", " ", match.group(1)).strip()
    return re.sub(r"\s*[|\-–—]\s*(Pragmatic Sysadmin)?\s*$", "", title).strip()


def _strip_existing_meta(html: str) -> str:
    """Strip an existing injected meta block so check functions work on original html."""
    pattern = re.compile(re.escape(HEAD_MARKER_START) + r".*?" + re.escape(HEAD_MARKER_END) + r"\n?", re.S)
    return pattern.sub("", html)


def _inject_head(html: str, meta: dict, url: str) -> tuple[str, bool]:
    title = TOOL_TITLES.get(meta["name"], "") or _title_from_html(html)
    base_html = _strip_existing_meta(html)
    description = meta.get("description", "")
    if not description:
        m = re.search(r'<meta\s+name="description"\s+content="([^"]*)"', base_html, flags=re.I)
        description = m.group(1) if m else f"Free browser tool from Pragmatic Sysadmin: {title}."
    block = head_block(
        title=title,
        description=description,
        url=url,
        has_canonical=bool(re.search(r'rel="canonical"', base_html, flags=re.I)),
        has_description=bool(re.search(r'<meta\s+name="description"', base_html, flags=re.I)),
    )
    if HEAD_MARKER_START in html:
        pattern = re.compile(re.escape(HEAD_MARKER_START) + r".*?" + re.escape(HEAD_MARKER_END) + r"\n?", re.S)
        html, count = pattern.subn(block, html)
        return html, count > 0
    if "</head>" in html:
        return html.replace("</head>", block + "</head>", 1), True
    return html, False


def _inject_cta(html: str, meta: dict) -> tuple[str, bool]:
    block = cta_block(meta)
    if CTA_MARKER_START in html:
        pattern = re.compile(re.escape(CTA_MARKER_START) + r".*?" + re.escape(CTA_MARKER_END) + r"\n?", re.S)
        html, count = pattern.subn(block, html)
        return html, count > 0
    if "</body>" in html:
        return html.replace("</body>", block + "\n</body>", 1), True
    return html, False


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="report status without writing")
    args = parser.parse_args()

    tools = sorted(TOOLS_DIR.glob("*.html"))
    if not tools:
        print(f"No tool pages found in {TOOLS_DIR}")
        return 1

    problems = 0
    changed = 0
    for path in tools:
        html = path.read_text(encoding="utf-8")
        name = path.name
        meta = dict(TOOL_META.get(name, {"guides": [], "offer": "sysadmin"}))
        meta["name"] = name
        url = f"{SITE}/tools/{name}"

        if name not in TOOL_META:
            problems += 1
            print(f"  ! {name}: no TOOL_META entry (guides/offer missing)")

        new_html, head_ok = _inject_head(html, meta, url)
        new_html, cta_ok = _inject_cta(new_html, meta)
        if not head_ok:
            problems += 1
            print(f"  ! {name}: could not find an insertion point in <head>")
        if not cta_ok:
            problems += 1
            print(f"  ! {name}: could not find </body>")

        if new_html != html:
            if args.check:
                print(f"  -> {name}: needs update")
            else:
                path.write_text(new_html, encoding="utf-8")
                print(f"  -> {name}: updated")
            changed += 1
        elif not args.check:
            print(f"  -- {name}: already up to date")

    verb = "would change" if args.check else "updated"
    print(f"\n{len(tools)} tools scanned, {changed} {verb}, {problems} problem(s).")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())

