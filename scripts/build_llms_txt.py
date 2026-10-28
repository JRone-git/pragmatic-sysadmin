#!/usr/bin/env python3
"""Generate static/llms.txt and static/llms-full.txt following the llmstxt.org standard.

Enables AI search engines (Perplexity, ChatGPT, Claude) to index and cite
our tools and articles accurately.

The tool list is read from catalog/tools.yaml (the single source of truth shared
with layouts/sitemap.xml, layouts/partials/related-tools.html and
scripts/inject-tool-cta.py) rather than being repeated here, so the tools
advertised to AI engines can never drift from the ones the site actually ships.
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONTENT_DIR = ROOT / "content"
STATIC_DIR = ROOT / "static"
BASE_URL = "https://pragmaticsysadmin.help"


def load_tools() -> list[dict]:
    """Read catalog/tools.yaml into the {name, url, desc} shape used below."""
    catalog = ROOT / "catalog" / "tools.yaml"
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    from blogforge import yamlmini

    data = yamlmini.loads(catalog.read_text(encoding="utf-8"))
    return [
        {
            "name": entry["title"],
            "url": f"{BASE_URL}{entry['path']}",
            "desc": entry["description"],
        }
        for entry in data.get("tools", [])
    ]


TOOLS = load_tools()


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
