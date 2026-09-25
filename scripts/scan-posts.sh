#!/usr/bin/env bash
# =============================================================================
# scan-posts.sh — Identify blog posts with product potential
# =============================================================================
# Scans content/posts/ for posts that could be expanded into products.
# Outputs a ranked list of candidates with suggested pricing.
#
# Heuristics:
#   - Posts with code blocks → can be packaged as scripts
#   - Long posts with checklists → can be packaged as guides/PDFs
#   - Posts on topics that recur (monitoring, backup, security) → always relevant
#
# Usage:
#   ./scripts/scan-posts.sh              # show all candidates
#   ./scripts/scan-posts.sh --json      # JSON output for further processing
#   ./scripts/scan-posts.sh --ready      # only high-confidence candidates
# =============================================================================

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
POSTS_DIR="$ROOT/content/posts"

JSON=false
READY_ONLY=false
while [[ $# -gt 0 ]]; do
  case "$1" in
    --json) JSON=true ;;
    --ready) READY_ONLY=true ;;
    --help|-h)
      sed -n '2,15p' "$0"
      exit 0 ;;
    *) echo "Unknown arg: $1"; exit 1 ;;
  esac
  shift
done

if [[ ! -d "$POSTS_DIR" ]]; then
  echo "Posts directory not found: $POSTS_DIR"
  exit 1
fi

export BUDDY_ROOT="$ROOT"
export BUDDY_POSTS_DIR="$POSTS_DIR"
export BUDDY_JSON="$JSON"
export BUDDY_READY="$READY_ONLY"

python3 << 'PYEOF'
import os
import re
import json
from pathlib import Path

posts_dir = Path(os.environ["BUDDY_POSTS_DIR"])
ready_only = os.environ.get("BUDDY_READY", "false") == "true"
as_json = os.environ.get("BUDDY_JSON", "false") == "true"

TOPIC_PATTERNS = {
    r"backup|restore|raid": ("Backup verification scripts", 19),
    r"monitoring|alert|metric|prometheus|grafana": ("Monitoring toolkit", 19),
    r"home lab|homelab|self-hosted|raspberry": ("Home lab starter pack", 9),
    r"security|hardening|firewall|ssh|2fa|mfa": ("Security hardening scripts", 9),
    r"documentation|runbook|wiki|confluence": ("Documentation toolkit", 9),
    r"kubernetes|k8s|helm|pod": ("Kubernetes starter pack", 19),
    r"linux from scratch|build.*linux|custom kernel": ("Linux build scripts", 19),
    r"first 30 days|onboarding|new.*sysadmin": ("Sysadmin onboarding guide", 9),
    r"cloud cost|aws bill|gcp bill|azure cost": ("Cloud cost analyzer", 9),
    r"slow computer|hardware|ssd|ram|upgrade": ("PC upgrade advisor", 9),
    r"vpn|wireguard|tailscale|zero.?trust": ("Network security scripts", 9),
    r"script|automation|ansible|terraform": ("Automation scripts bundle", 19),
    r"interview|hiring|jobs|resume": ("Sysadmin interview kit", 9),
}

candidates = []
for md_file in sorted(posts_dir.glob("*.md")):
    content = md_file.read_text()

    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            frontmatter = parts[1]
            body = parts[2]
        else:
            frontmatter = ""
            body = content
    else:
        frontmatter = ""
        body = content

    word_count = len(body.split())
    code_blocks = body.count("```")
    lists = len(re.findall(r"^\s*[-*]\s", body, re.MULTILINE))
    headers = len(re.findall(r"^#+\s", body, re.MULTILINE))
    has_howto = bool(re.search(r"how.?to|step.?by.?step|tutorial", body, re.IGNORECASE))
    has_scripts = code_blocks >= 2
    topic_match = None
    for pattern, (suggested, price) in TOPIC_PATTERNS.items():
        if re.search(pattern, body, re.IGNORECASE) or re.search(pattern, frontmatter, re.IGNORECASE):
            topic_match = (suggested, price)
            break

    if word_count < 300:
        continue

    score = 0
    score += min(word_count / 50, 20)
    score += min(code_blocks * 3, 15)
    score += min(lists * 0.5, 10)
    score += 10 if has_howto else 0
    score += 20 if has_scripts else 0
    score += 15 if topic_match else 0

    title_match = re.search(r"^title:\s*['\"]?(.+?)['\"]?\s*$", frontmatter, re.MULTILINE)
    title = title_match.group(1).strip() if title_match else md_file.stem

    date_match = re.search(r"^date:\s*(.+)$", frontmatter, re.MULTILINE)
    date = date_match.group(1).strip() if date_match else "unknown"

    tags_match = re.search(r"^tags:\s*\n((?:\s+-\s+.+\n)+)", frontmatter, re.MULTILINE)
    tags = []
    if tags_match:
        tags = re.findall(r"^\s+-\s+(.+)$", tags_match.group(1), re.MULTILINE)

    candidates.append({
        "file": str(md_file.relative_to(posts_dir.parent.parent)),
        "title": title,
        "date": date,
        "word_count": word_count,
        "code_blocks": code_blocks // 2,
        "has_scripts": has_scripts,
        "has_howto": has_howto,
        "topic_match": topic_match[0] if topic_match else None,
        "suggested_price": topic_match[1] if topic_match else 9,
        "score": round(score, 1),
    })

candidates.sort(key=lambda c: c["score"], reverse=True)

if ready_only:
    candidates = [c for c in candidates if c["score"] >= 30]

if as_json:
    print(json.dumps(candidates, indent=2))
else:
    if not candidates:
        print("No posts with product potential found.")
    else:
        print("=" * 72)
        print(f" POSTS WITH PRODUCT POTENTIAL ({len(candidates)} found)")
        print("=" * 72)
        print()
        for i, c in enumerate(candidates, 1):
            print(f"{i}. [{c['score']:5.1f}] {c['title']}")
            print(f"     File:    {c['file']}")
            print(f"     Words:   {c['word_count']}")
            print(f"     Scripts: {'yes' if c['has_scripts'] else 'no'}")
            if c['topic_match']:
                print(f"     Match:   {c['topic_match']} (suggested ${c['suggested_price']})")
            print()

        print("=" * 72)
        print(" TOP 3 RECOMMENDATIONS")
        print("=" * 72)
        for c in candidates[:3]:
            print(f"\n-> {c['title']}")
            print(f"   Score: {c['score']}, Suggested price: ${c['suggested_price']}")
            if c['topic_match']:
                print(f"   Product idea: {c['topic_match']}")
PYEOF