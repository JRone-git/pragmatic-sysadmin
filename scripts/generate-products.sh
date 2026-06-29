#!/usr/bin/env bash
# =============================================================================
# generate-products.sh — Generate everything from catalog/products.yaml
# =============================================================================
# Reads the single source of truth in catalog/products.yaml and generates:
#   - Hugo sales pages at content/products/<id>.md
#   - Ko-fi description copy at content/products/<id>-kofi.md
#   - Social media copy at content/products/<id>-social.md
#   - Cover image prompt at content/products/<id>-image-prompt.md
#   - Updated shop listing at content/shop/_index.md
#
# Usage:
#   ./scripts/generate-products.sh              # generate everything
#   ./scripts/generate-products.sh --only shop  # just regenerate the shop page
#   ./scripts/generate-products.sh --id health-check-toolkit  # one product
# =============================================================================

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CATALOG="$ROOT/catalog/products.yaml"

ONLY=""
SINGLE_ID=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --only) ONLY="$2"; shift ;;
    --id) SINGLE_ID="$2"; shift ;;
    --help|-h)
      sed -n '2,15p' "$0"
      exit 0 ;;
    *) echo "Unknown arg: $1"; exit 1 ;;
  esac
  shift
done

if [[ ! -f "$CATALOG" ]]; then
  echo "Catalog not found: $CATALOG"
  exit 1
fi

# Pass bash variables to Python via env vars (avoids heredoc expansion issues)
export BUDDY_ROOT="$ROOT"
export BUDDY_CATALOG="$CATALOG"
export BUDDY_ONLY="$ONLY"
export BUDDY_SINGLE_ID="$SINGLE_ID"

python3 << 'PYEOF'
import yaml
import os
import sys
from pathlib import Path

root = Path(os.environ["BUDDY_ROOT"])
catalog_path = Path(os.environ["BUDDY_CATALOG"])
only_mode = os.environ.get("BUDDY_ONLY", "")
single_id = os.environ.get("BUDDY_SINGLE_ID", "")

with open(catalog_path) as f:
    catalog = yaml.safe_load(f)

site = catalog.get("site", {})
products = catalog.get("products", [])

# Filter to single product if requested
if single_id:
    products = [p for p in products if p["id"] == single_id]
    if not products:
        print(f"No product with id '{single_id}'")
        sys.exit(1)

# Skip drafts unless --only draft
products = [p for p in products if p.get("status") == "live"]

def replace_placeholders(text, product):
    """Replace {kofi_url}, {source_post_url}, etc. with actual values."""
    if not text:
        return text
    base_url = site.get("url", "https://pragmaticsysadmin.help")
    replacements = {
        "{kofi_url}": product.get("kofi_url", "#"),
        "{source_post_url}": base_url + product.get("source_post", ""),
        "{title}": product.get("title", ""),
        "{tagline}": product.get("tagline", ""),
        "{price}": str(product.get("price", "")),
    }
    for k, v in replacements.items():
        text = text.replace(k, v)
    return text

def generate_sales_page(p):
    """Generate Hugo sales page markdown."""
    pid = p["id"]
    title = p["title"]
    tagline = p["tagline"]
    price = p["price"]
    description = p.get("description", "").strip()
    long_description = p.get("long_description", "").strip()
    features = p.get("features", [])
    requirements = p.get("requirements", [])
    not_for = p.get("not_for", [])
    kofi_url = p.get("kofi_url", "#")
    cover_image = p.get("cover_image", "")
    file_size = p.get("file_size_kb", 0)
    refund_days = site.get("refund_days", 60)
    license = site.get("license", "MIT")
    support_email = site.get("email", "")

    features_md = "\n".join(f"- ✅ {f}" for f in features)
    requirements_md = "\n".join(f"- {r}" for r in requirements)
    not_for_md = "\n".join(f"- {n}" for n in not_for)

    testimonials = p.get("testimonials", [])
    testimonials_md = ""
    if testimonials:
        testimonials_md = "\n## What people are saying\n\n"
        for t in testimonials:
            testimonials_md += f"> {t['quote']}\n> \n> — *{t['author']}*\n\n"

    md = f"""---
title: "{title} — ${price}"
date: {p.get('date', '2026-06-29')}
description: "{tagline}"
author: "{site.get('name', 'Pragmatic Sysadmin')}"
---

<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "Product",
  "name": "{title}",
  "description": "{tagline}",
  "brand": {{
    "@type": "Brand",
    "name": "{site.get('name', 'Pragmatic Sysadmin')}"
  }},
  "offers": {{
    "@type": "Offer",
    "price": "{price}.00",
    "priceCurrency": "{p.get('currency', 'USD')}",
    "availability": "https://schema.org/InStock"
  }}
}}
</script>

# {title}

**{tagline}. ${price}, one-time, you own it forever.**

![{title}](/images/{cover_image})

{description}

{long_description}

## What's in the box

{features_md}

## Requirements

{requirements_md}

## What it's not

{not_for_md}

## How to get it

<div style="text-align:center;margin:2rem 0;padding:2rem;background:#FDFAF4;border:2px solid #B7D4BE;border-radius:18px;">

**Price: ${price} USD, one-time.**

You'll get:
- Instant download of the toolkit ({file_size} KB zip)
- Free updates for life (same link)
- A {refund_days}-day no-questions refund if it doesn't help

<a href="{kofi_url}" style="display:inline-block;background:#FF5E5B;color:white;padding:1.125rem 2.5rem;border-radius:999px;font-weight:700;font-size:1.1875rem;text-decoration:none;box-shadow:0 4px 14px rgba(255,94,91,0.25);">☕ Buy on Ko-fi — ${price}</a>

</div>

{testimonials_md}

## License & support

{license} licensed — use, modify, redistribute.

Bug reports or questions: {support_email}

---

*Part of the [Pragmatic Sysadmin]({site.get('url', '')}) tool library — built to make sysadmins sleep better at night.*
"""
    return md

def generate_kofi_copy(p):
    pid = p["id"]
    short = p.get("kofi_description", "").strip()
    long = p.get("kofi_long_description", "").strip()
    title = p["title"]
    price = p["price"]

    return f"""# Ko-fi product copy for: {title}

## Short description (for Ko-fi product page, ~200 chars)

{short}

---

## Long description (for Ko-fi product page, ~1000 chars)

{long}

---

## Listing metadata

- **Title**: {title}
- **Price**: ${price}.00 {p.get('currency', 'USD')}
- **Type**: Digital download
- **File**: {p.get('file_path', '')}
- **File size**: {p.get('file_size_kb', 0)} KB

## Tags (for Ko-fi)

{', '.join(p.get('tags', []))}
"""

def generate_social_copy(p):
    social = p.get("social_copy", {})

    md = f"""# Social media copy for: {p['title']}

## Twitter / X

### Variant A — direct
{replace_placeholders(social.get('twitter_short', ''), p)}

### Variant B — story-led
{replace_placeholders(social.get('twitter_story', ''), p)}

## LinkedIn
{replace_placeholders(social.get('linkedin', ''), p)}

## Mastodon / Fediverse
{p['tagline']}

Get it here: {p.get('kofi_url', '#')}

## Hacker News (Show HN)
{replace_placeholders(social.get('hn', ''), p)}

## Image alt-text
Product card for the {p['title']}. Warm cream background with sage green
accents. Server health check illustration.
"""
    return md

def generate_image_prompt(p):
    pid = p["id"]
    prompt = p.get("cover_image_prompt", "")

    md = f"""# Cover image prompt for: {p['title']}

Use this prompt with an image generation tool:

```
{('image_synthesize' if False else 'image generation tool')} \\
  --prompt "{prompt}" \\
  --output static/images/{p.get('cover_image', '')} \\
  --aspect-ratio 16:9 \\
  --resolution 2K
```

## Image specs
- **Filename**: `static/images/{p.get('cover_image', '')}`
- **Dimensions**: 2752x1536 (or 1200x630 for social)
- **Format**: PNG or JPEG
- **Style**: Match the Pragmatic Sysadmin brand (warm cream + sage green)
- **Text**: No text overlay (text is added in HTML around the image)

## Where it's used
- Hero of the sales page
- Twitter/X card preview
- LinkedIn post image
- Reddit post image
- Open Graph image for shared links
"""
    return md

def generate_shop_page(all_products):
    site_name = site.get("name", "Pragmatic Sysadmin")
    live = [p for p in all_products if p.get("status") == "live"]

    if not live:
        print("WARNING: No live products. Shop page will be empty.")

    md = f"""---
title: "Shop — Sysadmin Tools & Scripts"
date: 2026-06-29T20:00:00.000Z
description: "Production-ready scripts, toolkits, and guides for sysadmins. All MIT licensed, all owned by you forever. Tools for server monitoring, backup verification, home labs, and more."
author: "{site_name}"
---

# Shop

**Production-ready tools for sysadmins.** All MIT licensed, all owned by you forever. No subscriptions, no SaaS, no telemetry. Just scripts and guides you can actually use.

<p style="text-align:center;margin:2rem 0;">
  <a href="{site.get('kofi_page', '#')}" style="display:inline-block;background:#FF5E5B;color:white;padding:0.875rem 2rem;border-radius:999px;font-weight:700;font-size:1rem;text-decoration:none;">☕ Tip jar / support the work</a>
</p>

---

"""

    for p in live:
        pid = p["id"]
        title = p["title"]
        tagline = p["tagline"]
        price = p["price"]
        cover_image = p.get("cover_image", "")
        kofi_url = p.get("kofi_url", "#")
        tags = p.get("tags", [])

        md += f"""## [{title}](/products/{pid}/)

<img src="/images/{cover_image}" alt="{title}" style="width:100%;max-width:480px;border-radius:12px;margin:1rem 0;box-shadow:0 4px 14px rgba(95,60,30,0.12);" />

**{tagline}**

**${price}** · {', '.join(tags[:3])} · [Buy on Ko-fi →]({kofi_url})

---

"""

    md += f"""
## How it works

1. Click any product → reads the full description
2. Click "Buy on Ko-fi" → instant payment, no account needed
3. Receive the download link immediately
4. Use forever — {site.get('license', 'MIT')} licensed

## Why these prices are low

- $9-19 feels right for scripts that took real time to write and test
- Low prices = impulse buys = more sales = more word-of-mouth
- You get a working tool, I get to keep making tools. Win-win.

## What you won't find here

- ❌ No monthly subscriptions
- ❌ No SaaS dashboards
- ❌ No telemetry phoning home
- ❌ No "premium" tiers gating basic features
- ❌ No accounts required

You own what you buy. Modify it. Redistribute it. Use it in your team. It's yours.

## Questions?

Email [{site.get('email', '')}](mailto:{site.get('email', '')})

Or tip what you want at [{site.get('kofi_page', '#')}]({site.get('kofi_page', '#')}) if you find the free content useful.
"""

    return md

# MAIN
generated = []

if not only_mode or only_mode in ("all", "products", "kofi", "social", "image"):
    for p in products:
        pid = p["id"]

        if not only_mode or only_mode == "products":
            md = generate_sales_page(p)
            out = root / "content" / "products" / f"{pid}.md"
            out.parent.mkdir(parents=True, exist_ok=True)
            with open(out, "w") as f:
                f.write(md)
            generated.append(str(out.relative_to(root)))

        if not only_mode or only_mode == "kofi":
            md = generate_kofi_copy(p)
            out = root / "content" / "products" / f"{pid}-kofi.md"
            with open(out, "w") as f:
                f.write(md)
            generated.append(str(out.relative_to(root)))

        if not only_mode or only_mode == "social":
            md = generate_social_copy(p)
            out = root / "content" / "products" / f"{pid}-social.md"
            with open(out, "w") as f:
                f.write(md)
            generated.append(str(out.relative_to(root)))

        if not only_mode or only_mode == "image":
            md = generate_image_prompt(p)
            out = root / "content" / "products" / f"{pid}-image-prompt.md"
            with open(out, "w") as f:
                f.write(md)
            generated.append(str(out.relative_to(root)))

if not only_mode or only_mode == "shop":
    all_products = catalog.get("products", [])
    md = generate_shop_page(all_products)
    out = root / "content" / "shop" / "_index.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w") as f:
        f.write(md)
    generated.append(str(out.relative_to(root)))

print(f"\n[OK] Generated {len(generated)} file(s):")
for g in generated:
    print(f"   - {g}")
PYEOF

echo
echo "Done. To use:"
echo "  1. Review the generated files in content/products/ and content/shop/"
echo "  2. Commit and push: git add . && git commit -m 'Add products' && git push"
echo "  3. Trigger Hugo build to publish"