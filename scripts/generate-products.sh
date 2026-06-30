#!/usr/bin/env bash
# =============================================================================
# generate-products.sh — Generate everything from catalog/products.yaml
# =============================================================================
# Reads the single source of truth in catalog/products.yaml and generates:
#   - Hugo sales pages for paid products at content/products/<id>.md
#   - Free tools pages at content/tools/free/<id>.md
#   - Ko-fi description copy at content/products/<id>-kofi.md
#   - Social media copy at content/products/<id>-social.md
#   - Cover image prompts at content/products/<id>-image-prompt.md
#   - Updated shop listing at content/shop/_index.md
#
# Usage:
#   ./scripts/generate-products.sh              # generate everything
#   ./scripts/generate-products.sh --only shop  # just regenerate the shop page
#   ./scripts/generate-products.sh --only free  # just the free tools
#   ./scripts/generate-products.sh --only paid  # just the paid products
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
      sed -n '2,16p' "$0"
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
free_tools = catalog.get("free_tools", [])
products = catalog.get("products", [])

# Filter to single product if requested
if single_id:
    free_tools = [t for t in free_tools if t["id"] == single_id]
    products = [p for p in products if p["id"] == single_id]
    if not free_tools and not products:
        print(f"No product with id '{single_id}'")
        sys.exit(1)

# Skip drafts
free_tools = [t for t in free_tools if t.get("status") == "live"]
products = [p for p in products if p.get("status") == "live"]

def replace_placeholders(text, product):
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

def generate_free_tool_page(t):
    pid = t["id"]
    title = t["title"]
    tagline = t["tagline"]
    icon = t.get("icon", "🛠️")
    description = t.get("description", "").strip()
    features = t.get("features", [])
    usage = t.get("usage", "")
    file_path = t.get("file_path", "")

    features_md = "\n".join(f"- ✅ {f}" for f in features)

    md = f"""---
title: "{title}"
date: 2026-06-30T10:00:00.000Z
description: "{tagline} — Free bash script from Pragmatic Sysadmin"
author: "{site.get('name', 'Pragmatic Sysadmin')}"
---

<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "SoftwareApplication",
  "name": "{title}",
  "description": "{tagline}",
  "applicationCategory": "UtilitiesApplication",
  "operatingSystem": "Linux",
  "offers": {{
    "@type": "Offer",
    "price": "0",
    "priceCurrency": "USD"
  }},
  "author": {{
    "@type": "Person",
    "name": "{site.get('name', 'Pragmatic Sysadmin')}"
  }}
}}
</script>

# {icon} {title}

**{tagline}**

{description}

## Features

{features_md}

## Usage

```bash
{usage}
```

## Download

Get the script from the [Free Tools Pack](/shop/#free-tools), or grab it directly:

```bash
# Clone from the repo (scripts are in /products/free/)
curl -O https://pragmaticsysadmin.help/downloads/{pid}.sh
chmod +x {pid}.sh
./{pid}.sh --help
```

## License

{site.get('license', 'MIT')} — use, modify, redistribute.

## Support

Bugs or questions: [{site.get('email', '')}](mailto:{site.get('email', '')})

## More tools

See [/shop/](/shop/) for the full catalog, including paid toolkits:

- **[The 5-Minute Server Health Check Toolkit](/products/health-check-toolkit/)** (${products[0]['price'] if products else '9'}) — the "do everything" Monday morning ritual

---

Made with care by [Pragmatic Sysadmin]({site.get('url', '')}).
"""
    return md

def generate_sales_page(p):
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
    short = p.get("kofi_description", "").strip()
    long = p.get("kofi_long_description", "").strip()
    return f"""# Ko-fi product copy for: {p['title']}

## Short description (~200 chars)

{short}

---

## Long description (~1000 chars)

{long}

---

## Listing metadata

- **Title**: {p['title']}
- **Price**: ${p['price']}.00 {p.get('currency', 'USD')}
- **Type**: Digital download
- **File**: {p.get('file_path', '')}
- **File size**: {p.get('file_size_kb', 0)} KB

## Tags

{', '.join(p.get('tags', []))}
"""

def generate_social_copy(p):
    social = p.get("social_copy", {})
    return f"""# Social media copy for: {p['title']}

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
"""

def generate_image_prompt(p):
    prompt = p.get("cover_image_prompt", "")
    return f"""# Cover image prompt for: {p['title']}

```
image_synthesize \\
  --prompt "{prompt}" \\
  --output static/images/{p.get('cover_image', '')} \\
  --aspect-ratio 16:9 \\
  --resolution 2K
```

Save to `static/images/{p.get('cover_image', '')}`.
"""

def generate_shop_page(all_free, all_products):
    site_name = site.get("name", "Pragmatic Sysadmin")
    kofi_shop = site.get("kofi_shop_url", "#")
    kofi_page = site.get("kofi_page", "#")

    live_free = [t for t in all_free if t.get("status") == "live"]
    live_paid = [p for p in all_products if p.get("status") == "live"]

    md = f"""---
title: "Shop — Sysadmin Tools & Scripts"
date: 2026-06-30T10:00:00.000Z
description: "Free scripts and paid toolkits for sysadmins. All MIT licensed, all owned by you forever. Tools for server monitoring, SSL checking, backup verification, home labs, and more."
author: "{site_name}"
---

# Shop

**Production-ready tools for sysadmins.** All MIT licensed, all owned by you forever. No subscriptions, no SaaS, no telemetry. Just scripts and guides you can actually use.

<div style="background:linear-gradient(135deg, #FBF6EE 0%, #FDFAF4 100%);border:2px solid #B7D4BE;border-radius:18px;padding:1.5rem;margin:1.5rem 0;text-align:center;">

<p style="margin:0 0 1rem 0;font-family:'Lora',serif;font-size:1.125rem;color:#2A2520;font-weight:600;">
  ☕ <strong>All paid products sold via Ko-fi</strong> — instant download, no account needed
</p>

<a href="{kofi_shop}" style="display:inline-block;background:#FF5E5B;color:white;padding:0.875rem 2rem;border-radius:999px;font-weight:700;font-size:1rem;text-decoration:none;margin:0.25rem;">🛒 Visit Ko-fi Shop</a>
<a href="{kofi_page}" style="display:inline-block;background:transparent;color:#FF5E5B;border:2px solid #FF5E5B;padding:0.75rem 1.75rem;border-radius:999px;font-weight:700;font-size:1rem;text-decoration:none;margin:0.25rem;">☕ Tip Jar</a>

</div>

---

<a id="free-tools"></a>
## 🆓 Free Tools — Start Here

**Grab these first. No email required. No signup. Just scripts.**

These solve one specific problem each. Use them forever, modify them freely. When you outgrow them, the paid toolkits below go deeper.

"""

    for t in live_free:
        pid = t["id"]
        title = t["title"]
        tagline = t["tagline"]
        icon = t.get("icon", "🛠️")
        description = t.get("description", "").strip()
        usage = t.get("usage", "").split('\n')[1] if t.get("usage", "").count('\n') > 1 else ""

        md += f"""### {icon} [{title}](/tools/free/{pid}/)

**{tagline}**

{description}

```bash
{usage.strip()}
```

[Get the script →](/tools/free/{pid}/) · [Download the whole pack]({site.get('url', '')}/downloads/free-tools-pack.zip)

---

"""

    if live_paid:
        md += """
<a id="paid-toolkits"></a>
## 💎 Paid Toolkits — The Full Solutions

**For when you need more than one script.** Each toolkit bundles multiple scripts + documentation + decision trees, all from a real-world-tested workflow.

"""
        for p in live_paid:
            pid = p["id"]
            title = p["title"]
            tagline = p["tagline"]
            price = p["price"]
            cover_image = p.get("cover_image", "")
            kofi_url = p.get("kofi_url", "#")
            tags = p.get("tags", [])

            md += f"""### [{title}](/products/{pid}/) — **${price}**

<img src="/images/{cover_image}" alt="{title}" style="width:100%;max-width:320px;border-radius:12px;margin:0.75rem 0;box-shadow:0 4px 14px rgba(95,60,30,0.12);" />

**{tagline}**

{', '.join(tags[:4])}

[Read full description →](/products/{pid}/) · [Buy on Ko-fi →]({kofi_url})

---

"""

    md += f"""
## How it works

**Free tools:**
1. Click any free tool → read the description
2. Copy the script (or download the pack)
3. Use forever — {site.get('license', 'MIT')} licensed

**Paid toolkits:**
1. Click any paid toolkit → read the full description
2. Click "Buy on Ko-fi" → instant payment, no account needed
3. Receive the download link immediately
4. Use forever — {site.get('license', 'MIT')} licensed
5. {site.get('refund_days', 60)}-day no-questions refund

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

Or tip what you want at [{kofi_page}]({kofi_page}) if you find the free content useful.
"""

    return md

# MAIN
generated = []

# Free tools pages
if not only_mode or only_mode in ("all", "free"):
    for t in free_tools:
        pid = t["id"]
        md = generate_free_tool_page(t)
        out = root / "content" / "tools" / "free" / f"{pid}.md"
        out.parent.mkdir(parents=True, exist_ok=True)
        with open(out, "w") as f:
            f.write(md)
        generated.append(str(out.relative_to(root)))

# Paid products
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

# Shop page
if not only_mode or only_mode == "shop":
    all_free = catalog.get("free_tools", [])
    all_paid = catalog.get("products", [])
    md = generate_shop_page(all_free, all_paid)
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
echo "Done."