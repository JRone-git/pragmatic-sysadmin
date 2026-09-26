"""Auto-publish scheduled blog posts across all content sections.

Scans content/sysadmin, content/senior-tech, content/meta, content/posts, etc.
If date <= today and draft: true (and not blocked), flips draft: false.
Also runs OG image generation so social cards exist immediately.
"""

import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
CONTENT_DIR = REPO_ROOT / "content"
SECTIONS = ["sysadmin", "senior-tech", "meta", "posts"]

DATE_PATTERN = re.compile(r'^date:\s*["\']?([0-9]{4}-[0-9]{2}-[0-9]{2})', re.MULTILINE)
DRAFT_PATTERN = re.compile(r'^draft:\s*true\b', re.MULTILINE)

now = datetime.now(timezone.utc).date()
published_count = 0

for section in SECTIONS:
    dir_path = CONTENT_DIR / section
    if not dir_path.is_dir():
        continue
    for path in dir_path.glob("*.md"):
        if path.name.startswith("_"):
            continue
        try:
            content = path.read_text(encoding="utf-8")
        except Exception:
            continue

        date_match = DATE_PATTERN.search(content)
        draft_match = DRAFT_PATTERN.search(content)

        if date_match and draft_match:
            try:
                post_date = datetime.strptime(date_match.group(1), "%Y-%m-%d").date()
            except ValueError:
                continue

            if post_date <= now:
                new_content = DRAFT_PATTERN.sub("draft: false", content, count=1)
                path.write_text(new_content, encoding="utf-8")
                print(f"Published: {section}/{path.name} (date: {post_date})")
                published_count += 1

print(f"Total posts flipped to live: {published_count}")

# Generate any missing OG images if posts were published
if published_count > 0:
    og_script = REPO_ROOT / "scripts" / "generate-og-images.py"
    if og_script.exists():
        print("Regenerating OpenGraph social images...")
        subprocess.run([sys.executable, str(og_script)], check=False)

