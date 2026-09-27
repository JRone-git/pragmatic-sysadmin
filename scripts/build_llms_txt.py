#!/usr/bin/env python3
"""Generate static/llms.txt and static/llms-full.txt following the llmstxt.org standard.

Enables AI search engines (Perplexity, ChatGPT, Claude) to index and cite
our tools and articles accurately.
"""

import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONTENT_DIR = ROOT / "content"
STATIC_DIR = ROOT / "static"
BASE_URL = "https://pragmaticsysadmin.help"

TOOLS = [
    {
        "name": "Command Simulator",
        "url": f"{BASE_URL}/tools/command-simulator.html",
        "desc": "Simulate and practice dangerous Linux and Windows commands (rm -rf, dd, chmod) safely in-browser."
    },
    {
        "name": "AI Prompt Builder for Sysadmins",
        "url": f"{BASE_URL}/tools/ai-prompt-builder.html",
        "desc": "Generate precision prompts for ChatGPT, Claude, and Copilot tailored to bash scripts and cloud infra."
    },
    {
        "name": "CLI Adventure",
        "url": f"{BASE_URL}/tools/cli-adventure.html",
        "desc": "Gamified terminal simulation solving realistic production IT incidents."
    },
    {
        "name": "Password Strength Checker",
        "url": f"{BASE_URL}/tools/password-checker.html",
        "desc": "Client-side password security analysis with entropy calculation and zero data transmission."
    },
    {
        "name": "Pragmatic Pulse Resilience Scorecard",
        "url": f"{BASE_URL}/tools/pulse.html",
        "desc": "Digital resilience audit assessing backups, credential hygiene, and disaster recovery readiness."
    },
    {
        "name": "PowerShell & Bash Script Generator",
        "url": f"{BASE_URL}/tools/script-generator.html",
        "desc": "Interactive generator for production-ready administrative scripts across Linux and Windows."
    },
    {
        "name": "Homelab Architect & Spec Calculator",
        "url": f"{BASE_URL}/tools/homelab-architect.html",
        "desc": "Interactive sizing calculator for self-hosted home labs: CPU cores, RAM allocation, and storage."
    },
    {
        "name": "Battle Station Score",
        "url": f"{BASE_URL}/tools/battle-station-score.html",
        "desc": "Interactive ergonomics, peripherals, and desk setup rater providing custom upgrade tips."
    },
    {
        "name": "Tech Needs Advisor",
        "url": f"{BASE_URL}/tools/tech-needs-advisor.html",
        "desc": "Decision tree recommending hardware and software configurations for students and pros."
    },
    {
        "name": "Corporate Translator & Incident Report Generator",
        "url": f"{BASE_URL}/tools/corporate-translator.html",
        "desc": "Convert plain-English postmortems and IT outages into formal corporate status communications."
    },
    {
        "name": "Plain English Tech Explainer",
        "url": f"{BASE_URL}/tools/plain-english.html",
        "desc": "Translate cryptic system errors and log stacktraces into understandable non-technical language."
    },
    {
        "name": "PRISM Architecture Simulator",
        "url": f"{BASE_URL}/tools/prism-engine.html",
        "desc": "Interactive simulation playground for distributed systems failure modes and failover."
    }
]

def parse_post(file_path: Path):
    text = file_path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return None
    parts = text.split("---", 2)
    if len(parts) < 3:
        return None
    fm_text = parts[1]
    body = parts[2].strip()

    fm = {}
    for line in fm_text.splitlines():
        if ":" in line and not line.startswith(" ") and not line.startswith("\t"):
            k, v = line.split(":", 1)
            fm[k.strip()] = v.strip().strip('"').strip("'")

    if fm.get("draft", "false").lower() == "true":
        return None

    title = fm.get("title", "")
    desc = fm.get("description", fm.get("summary", ""))
    if not title:
        return None

    rel = file_path.relative_to(CONTENT_DIR).as_posix()
    rel = re.sub(r"\.md$", "", rel)
    url = f"{BASE_URL}/{rel}/"
    section = file_path.parent.name
    return {
        "title": title,
        "description": desc,
        "url": url,
        "section": section,
        "body": body,
    }


def generate_llms_txt():
    posts = []
    for md_file in sorted(CONTENT_DIR.rglob("*.md")):
        if md_file.name.startswith("_"):
            continue
        p = parse_post(md_file)
        if p:
            posts.append(p)

    sysadmin_posts = [p for p in posts if p["section"] == "sysadmin"]
    senior_posts = [p for p in posts if p["section"] == "senior-tech"]
    other_posts = [p for p in posts if p["section"] not in ("sysadmin", "senior-tech")]

    lines = []
    lines.append("# Pragmatic Sysadmin")
    lines.append("> Pragmatic sysadmin guides, server troubleshooting checklists, senior tech family support, and free interactive browser tools by Jonne, a Finnish systems administrator.")
    lines.append("")
    lines.append("## Free Browser-Based Administrative Tools")
    lines.append("Interactive tools running 100% client-side in the browser with zero tracking:")
    lines.append("")
    for t in TOOLS:
        lines.append(f"- [{t['name']}]({t['url']}): {t['desc']}")

    lines.append("")
    lines.append("## Practical Sysadmin & DevOps Guides")
    for p in sysadmin_posts:
        desc = f": {p['description']}" if p["description"] else ""
        lines.append(f"- [{p['title']}]({p['url']}){desc}")

    lines.append("")
    lines.append("## Senior Tech & Family Safety Guides")
    for p in senior_posts:
        desc = f": {p['description']}" if p["description"] else ""
        lines.append(f"- [{p['title']}]({p['url']}){desc}")

    if other_posts:
        lines.append("")
        lines.append("## Additional Guides")
        for p in other_posts:
            desc = f": {p['description']}" if p["description"] else ""
            lines.append(f"- [{p['title']}]({p['url']}){desc}")

    lines.append("")
    lines.append("## Free Downloads")
    lines.append(f"- [Free Tools Bash Script Pack]({BASE_URL}/downloads/free-tools-pack.zip): 5 production-tested bash scripts.")
    lines.append(f"- [Home Network Security Checklist]({BASE_URL}/downloads/home-network-security-checklist.pdf): Printable PDF checklist.")
    lines.append(f"- [Senior Phone Setup Checklist]({BASE_URL}/downloads/senior-phone-setup-checklist.pdf): Printable phone setup guide.")

    llms_content = "\n".join(lines) + "\n"
    (STATIC_DIR / "llms.txt").write_text(llms_content, encoding="utf-8")
    print(f"Generated static/llms.txt ({len(llms_content)} bytes)")

    full_lines = [lines[0], lines[1], ""]
    full_lines.append("## Detailed Free Tools Index")
    for t in TOOLS:
        full_lines.append(f"### {t['name']}")
        full_lines.append(f"URL: {t['url']}")
        full_lines.append(f"Summary: {t['desc']}")
        full_lines.append("")

    full_lines.append("## Published Knowledge Base")
    for p in posts:
        full_lines.append(f"### {p['title']}")
        full_lines.append(f"URL: {p['url']}")
        full_lines.append(f"Section: {p['section']}")
        if p["description"]:
            full_lines.append(f"Description: {p['description']}")
        body_snippet = re.sub(r"<!--more-->", "", p["body"])
        body_snippet = re.sub(r"[#*`]", "", body_snippet)[:450].strip()
        if body_snippet:
            full_lines.append(f"Excerpt: {body_snippet}...")
        full_lines.append("")

    llms_full_content = "\n".join(full_lines) + "\n"
    (STATIC_DIR / "llms-full.txt").write_text(llms_full_content, encoding="utf-8")
    print(f"Generated static/llms-full.txt ({len(llms_full_content)} bytes)")


if __name__ == "__main__":
    generate_llms_txt()
