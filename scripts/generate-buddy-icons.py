#!/usr/bin/env python3
"""Generate Buddy's app icons from the same geometry as the favicon SVG.

Run:  python3 scripts/generate-buddy-icons.py

Why this exists: Buddy ships a web manifest so it can be installed to a
home screen (standalone, no browser chrome) and opened offline. A manifest
without real icon files is decorative — iOS in particular ignores SVG icons
for home-screen shortcuts and wants a PNG.

The face is drawn from the same coordinates as the inline SVG favicon in
static/buddy/index.html, so the installed icon and the browser tab icon
are the same drawing. Curves are sampled as quadratic Béziers rather than
approximated with arcs, because an arc is a poor fit for the smile.

Only Pillow is needed. It is already a dependency of scripts/generate-og-images.py.
"""

from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "static" / "buddy"

# Palette, matching the favicon SVG in static/buddy/index.html.
GREEN = (45, 106, 79, 255)     # #2D6A4F  head
CREAM = (251, 246, 238, 255)   # #FBF6EE  eyes + smile
INK = (42, 37, 32, 255)        # #2A2520  pupils
BG = (251, 246, 238, 255)      # #FBF6EE  canvas behind the head


def quad(p0, p1, p2, steps: int = 48) -> list[tuple[float, float]]:
    """Sample a quadratic Bézier into a polyline."""
    pts = []
    for i in range(steps + 1):
        t = i / steps
        u = 1 - t
        x = u * u * p0[0] + 2 * u * t * p1[0] + t * t * p2[0]
        y = u * u * p0[1] + 2 * u * t * p1[1] + t * t * p2[1]
        pts.append((x, y))
    return pts


def draw_face(size: int) -> Image.Image:
    """Draw the Buddy face at `size` px square, using the SVG's 100x100 space."""
    s = size / 100.0
    img = Image.new("RGBA", (size, size), BG)
    d = ImageDraw.Draw(img)

    def sc(pts):
        return [(x * s, y * s) for x, y in pts]

    def circle(cx, cy, r, fill):
        d.ellipse([(cx - r) * s, (cy - r) * s, (cx + r) * s, (cy + r) * s], fill=fill)

    # Head
    circle(50, 52, 42, GREEN)

    # Eyebrows. joint="curve" rounds the polyline joints; without it the
    # sampled Bézier leaves visible notches along the smile.
    d.line(sc(quad((34, 41), (40, 38), (46, 41))), fill=CREAM,
           width=max(1, int(1.5 * s)), joint="curve")
    d.line(sc(quad((54, 41), (60, 38), (66, 41))), fill=CREAM,
           width=max(1, int(1.5 * s)), joint="curve")

    # Eyes: cream sclera, dark pupil
    circle(40, 48, 4, CREAM)
    circle(60, 48, 4, CREAM)
    circle(39.5, 47, 2, INK)
    circle(59.5, 47, 2, INK)

    # Smile
    d.line(sc(quad((36, 62), (50, 75), (64, 62))), fill=CREAM,
           width=max(1, int(3.5 * s)), joint="curve")

    return img


def main() -> None:
    targets = {
        "icon-192.png": 192,
        "icon-512.png": 512,
        "apple-touch-icon.png": 180,
    }
    for name, size in targets.items():
        img = draw_face(size)
        path = OUT_DIR / name
        img.save(path, "PNG", optimize=True)
        print(f"  [OK] {path.relative_to(ROOT)} ({size}x{size}, {path.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
