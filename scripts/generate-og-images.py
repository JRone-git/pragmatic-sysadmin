#!/usr/bin/env python3
"""
Generate branded Open Graph images for every post in content/posts/.

For each post, reads the title and description from front-matter and
renders a 1200x630 PNG into static/og/<slug>.png.

Run this whenever you add or rename a post:
    python3 scripts/generate-og-images.py

The images are committed to the repo so GitHub Pages serves them
without any build-time dependency on Pillow.
"""

import os
import re
import sys
import html
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("ERROR: Pillow is not installed. Run: pip install Pillow", file=sys.stderr)
    sys.exit(1)

# --- Config -------------------------------------------------------------------

ROOT = Path(__file__).resolve().parent.parent
# Scan all content sections that contain posts
POSTS_DIRS = [
    ROOT / "content" / "posts",
    ROOT / "content" / "sysadmin",
    ROOT / "content" / "senior-tech",
]
OUTPUT_DIR = ROOT / "static" / "og"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Brand colours
BG_TOP = (30, 30, 35)        # near-black
BG_BOTTOM = (45, 45, 51)     # PaperMod dark tertiary
ACCENT = (255, 94, 91)       # Ko-fi red — same as site CTAs
TEXT_PRIMARY = (228, 228, 231)
TEXT_SECONDARY = (155, 156, 157)
LOGO_BG = (255, 94, 91)

# Layout
WIDTH, HEIGHT = 1200, 630
PADDING = 80
TITLE_FONT_SIZE = 64
DESC_FONT_SIZE = 26
SITE_FONT_SIZE = 24

# Fonts (Liberation Sans is installed; falls back to DejaVu)
FONT_PATHS = [
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
]
BODY_FONT_PATHS = [
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
]


def find_font(paths):
    for p in paths:
        if os.path.exists(p):
            return p
    return None


TITLE_FONT_PATH = find_font(FONT_PATHS)
BODY_FONT_PATH = find_font(BODY_FONT_PATHS)
if not TITLE_FONT_PATH or not BODY_FONT_PATH:
    print("ERROR: No suitable TTF font found.", file=sys.stderr)
    sys.exit(1)


# --- Helpers ------------------------------------------------------------------

def wrap_text(text, font, draw, max_width):
    """Greedy word-wrap to fit max_width pixels."""
    words = text.split()
    lines, current = [], ""
    for w in words:
        trial = (current + " " + w).strip()
        bbox = draw.textbbox((0, 0), trial, font=font)
        if bbox[2] - bbox[0] <= max_width or not current:
            current = trial
        else:
            lines.append(current)
            current = w
    if current:
        lines.append(current)
    return lines


def parse_front_matter(path):
    """Return (front_matter_dict, slug) from a Hugo post."""
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return {}, path.stem
    # find the closing ---
    m = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
    if not m:
        return {}, path.stem
    fm_text = m.group(1)
    fm = {}
    for line in fm_text.split("\n"):
        if ":" in line:
            key, _, val = line.partition(":")
            key = key.strip()
            val = val.strip().strip('"').strip("'")
            if val:
                fm[key] = val
    # slug from filename (Hugo default)
    slug = path.stem
    if "slug" in fm:
        slug = fm["slug"]
    return fm, slug


def render_image(title, description, slug, site_name="Pragmatic Tech"):
    """Render one OG image and save to OUTPUT_DIR/<slug>.png."""
    img = Image.new("RGB", (WIDTH, HEIGHT), BG_TOP)
    draw = ImageDraw.Draw(img)

    # Vertical gradient background
    for y in range(HEIGHT):
        t = y / HEIGHT
        r = int(BG_TOP[0] + (BG_BOTTOM[0] - BG_TOP[0]) * t)
        g = int(BG_TOP[1] + (BG_BOTTOM[1] - BG_TOP[1]) * t)
        b = int(BG_TOP[2] + (BG_BOTTOM[2] - BG_TOP[2]) * t)
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))

    # Accent bar on the left
    draw.rectangle([0, 0, 12, HEIGHT], fill=ACCENT)

    # Site name "pill" at top-left
    title_font = ImageFont.truetype(TITLE_FONT_PATH, SITE_FONT_SIZE)
    site_text = site_name
    bbox = draw.textbbox((0, 0), site_text, font=title_font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    pill_pad_x, pill_pad_y = 16, 10
    pill_x0, pill_y0 = PADDING, PADDING
    pill_x1 = pill_x0 + text_w + pill_pad_x * 2
    pill_y1 = pill_y0 + text_h + pill_pad_y * 2 + 6
    draw.rounded_rectangle([pill_x0, pill_y0, pill_x1, pill_y1],
                           radius=8, fill=LOGO_BG)
    draw.text((pill_x0 + pill_pad_x, pill_y0 + pill_pad_y),
              site_text, fill=(255, 255, 255), font=title_font)

    # Title — wrapped, multi-line
    title_font_big = ImageFont.truetype(TITLE_FONT_PATH, TITLE_FONT_SIZE)
    max_w = WIDTH - PADDING * 2 - 12  # account for accent bar
    title_clean = html.unescape(title)
    # Strip emoji-ish characters that the font can't render
    title_clean = title_clean.encode("ascii", "ignore").decode("ascii").strip()
    if not title_clean:
        title_clean = "Untitled"
    title_lines = wrap_text(title_clean, title_font_big, draw, max_w)
    # Cap at 4 lines
    if len(title_lines) > 4:
        title_lines = title_lines[:4]
        if title_lines[3][-1] not in ".…":
            title_lines[3] = title_lines[3][:max(0, len(title_lines[3]) - 1)] + "…"

    y = pill_y1 + 50
    for line in title_lines:
        draw.text((PADDING + 12, y), line, fill=TEXT_PRIMARY, font=title_font_big)
        bbox = draw.textbbox((0, 0), line, font=title_font_big)
        y += (bbox[3] - bbox[1]) + 14

    # Description (truncated to ~2 lines)
    if description:
        desc_clean = html.unescape(description)
        desc_clean = desc_clean.encode("ascii", "ignore").decode("ascii").strip()
        if desc_clean:
            desc_font = ImageFont.truetype(BODY_FONT_PATH, DESC_FONT_SIZE)
            desc_lines = wrap_text(desc_clean, desc_font, draw, max_w)
            if len(desc_lines) > 2:
                desc_lines = desc_lines[:2]
                if len(desc_lines[1]) > 70:
                    desc_lines[1] = desc_lines[1][:69] + "…"
            y += 20
            for line in desc_lines:
                draw.text((PADDING + 12, y), line, fill=TEXT_SECONDARY, font=desc_font)
                bbox = draw.textbbox((0, 0), line, font=desc_font)
                y += (bbox[3] - bbox[1]) + 8

    # Footer URL
    url_font = ImageFont.truetype(BODY_FONT_PATH, 22)
    draw.text((PADDING + 12, HEIGHT - 50),
              "pragmaticsysadmin.help",
              fill=TEXT_SECONDARY, font=url_font)

    out_path = OUTPUT_DIR / f"{slug}.png"
    img.save(out_path, "PNG", optimize=True)
    return out_path


def main():
    posts = []
    for posts_dir in POSTS_DIRS:
        if posts_dir.exists():
            posts.extend(sorted(posts_dir.glob("*.md")))
    if not posts:
        print("No posts found in any of:", [str(p) for p in POSTS_DIRS])
        return

    print(f"Generating OG images for {len(posts)} posts...")
    generated, skipped, failed = 0, 0, 0
    for p in posts:
        try:
            fm, slug = parse_front_matter(p)
            title = fm.get("title", p.stem)
            description = fm.get("description", "")
            out = render_image(title, description, slug)
            generated += 1
            print(f"  ✓ {slug}.png")
        except Exception as e:
            print(f"  ✗ {p.name}: {e}", file=sys.stderr)
            failed += 1

    print(f"\nDone. {generated} generated, {failed} failed.")
    print(f"Output: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
