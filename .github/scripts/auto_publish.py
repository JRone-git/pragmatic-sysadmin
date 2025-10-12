import os
import re
from datetime import datetime, timezone

POSTS_DIR = os.path.join(os.path.dirname(__file__), '../../content/posts')
DATE_PATTERN = re.compile(r'^date:\s*([0-9\-]+)', re.MULTILINE)
DRAFT_PATTERN = re.compile(r'^draft:\s*true', re.MULTILINE)

now = datetime.now(timezone.utc).date()

for filename in os.listdir(POSTS_DIR):
    if not filename.endswith('.md'):
        continue
    path = os.path.join(POSTS_DIR, filename)
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    date_match = DATE_PATTERN.search(content)
    draft_match = DRAFT_PATTERN.search(content)
    if date_match and draft_match:
        post_date = datetime.strptime(date_match.group(1), '%Y-%m-%d').date()
        if post_date <= now:
            # Update draft: true to draft: false
            new_content = DRAFT_PATTERN.sub('draft: false', content)
            with open(path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"Published: {filename}")
