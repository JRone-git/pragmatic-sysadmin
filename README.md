# Pragmatic Sysadmin — Site Repo

Hugo static site for [pragmaticsysadmin.help](https://pragmaticsysadmin.help).

## Layout

```
.
├── content/              # Hugo content (Markdown)
│   ├── posts/            # Blog posts
│   ├── products/         # Product sales pages (auto-generated)
│   ├── shop/             # Shop landing page (auto-generated)
│   ├── tools/, kids/, about/, newsletter/, thank-you/  # Other sections
│   └── buddy-setup/      # $29 setup service landing page
├── static/
│   ├── buddy/            # Buddy web app (free companion for seniors)
│   ├── images/           # Site images
│   └── (other static files)
├── themes/               # Hugo themes (PaperMod, ananke)
├── catalog/
│   └── products.yaml     # ⭐ Single source of truth for all products
├── scripts/
│   ├── generate-products.sh  # ⭐ Generate sales pages from catalog
│   └── scan-posts.sh         # ⭐ Find posts with product potential
├── products/             # Source product files (zips, scripts, guides)
└── hugo.toml             # Hugo config + main menu
```

## ⭐ The product automation system

The site has a small automation system that turns product definitions into
full sales pages, social copy, Ko-fi descriptions, and a shop listing —
all from a single YAML file.

### Add a new product in 3 steps

**Step 1** — Add the product to `catalog/products.yaml`:

```yaml
products:
  - id: my-new-product
    title: "My Awesome Product"
    tagline: "What it does in one line"
    price: 9
    status: live
    cover_image: my-product-card.png
    cover_image_prompt: |
      Description for image generation tool...
    kofi_url: "https://ko-fi.com/s/yourproductid"
    features:
      - "Feature 1"
      - "Feature 2"
    # ... see catalog/products.yaml for full schema
```

**Step 2** — Create the product files in `products/<id>/`

**Step 3** — Run:

```bash
./scripts/generate-products.sh
```

This generates:
- `content/products/<id>.md` — Hugo sales page
- `content/products/<id>-kofi.md` — Ko-fi description copy
- `content/products/<id>-social.md` — Twitter/LinkedIn/HN copy
- `content/products/<id>-image-prompt.md` — Cover image prompt
- `content/shop/_index.md` — Shop page (regenerated with all products)

### Find posts to productize

```bash
./scripts/scan-posts.sh        # show all candidates
./scripts/scan-posts.sh --ready # only high-confidence
./scripts/scan-posts.sh --json # JSON output
```

The scanner scores posts by:
- Length (longer = more material)
- Code blocks (potential scripts)
- Lists/checklists (potential guides)
- How-to style (good for kits)
- Topic match (recurring topics = reliable demand)

### Generate cover images

The generator outputs image prompts at `content/products/<id>-image-prompt.md`.
Run them through your image generation tool of choice, save the result to
`static/images/<cover_image>`, and the sales page will pick it up automatically.

## Adding a new language

1. Add `[languages.<code>]` block to `hugo.toml`
2. Create translated content files (e.g., `content/posts/<slug>.<lang>.md`)
3. Update any in-content links to point to the right language version
4. Test build locally with `hugo server`

## Deployment

The site auto-deploys on push to main (via Firebase Hosting / GitHub Actions).
Manual deploy:

```bash
hugo --minify && firebase deploy
```

## Content guidelines

- **Blog posts**: 800-2000 words, well-formatted, with Hugo frontmatter + JSON-LD schema
- **Products**: Detailed enough to stand alone, with clear "what's included" and "what it's not"
- **Tool pages**: Functional HTML/JS tools, not just static pages
- **Buddy** (`static/buddy/`): Keep the companion app self-contained — no build, vanilla JS

## Security

The `static/google*.html` files are Google Search Console verification
files. Don't delete them.

## License

Site content: All rights reserved.
Code (scripts, automation, Buddy app): MIT.
Product downloads: MIT (per individual product license).