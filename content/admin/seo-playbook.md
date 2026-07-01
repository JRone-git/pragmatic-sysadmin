---
title: "SEO & Search Console Playbook"
date: 2026-06-30
draft: true
description: "Internal playbook for managing Google Search Console, sitemaps, and SEO for pragmaticsysadmin.help."
build:
  list: false
  render: false
---

# SEO & Search Console Playbook

> This page is **draft** and excluded from the build (`render: false`).
> It exists only as a reference for the site owner. To view it locally,
> run `hugo server -D` and visit `/admin/seo-playbook/`.

This is the internal playbook for managing search visibility on pragmaticsysadmin.help. It's a draft page so it never goes live — keep it that way.

## Current state (as of 2026-06-30)

- **Google Analytics 4** is loaded via `layouts/partials/google_analytics.html`. Property ID: `G-EKQ0LBDH9Z`.
- **Google Search Console** verification file: `static/google258c5541cd373164.html` (already verified).
- **Sitemap**: auto-generated at `https://pragmaticsysadmin.help/sitemap.xml` — currently 100+ URLs.
- **robots.txt**: auto-generated, points to sitemap. Allows all crawlers.
- **Per-post OG images**: generated into `static/og/<slug>.png` by `scripts/generate-og-images.py`. Wire-up is in `layouts/partials/extend_head.html`.
- **BlogPosting JSON-LD schema**: emitted on every post page via `layouts/partials/extend_head.html`.
- **Meta descriptions**: every post and section has a unique description.

## Submitting the sitemap to Google Search Console

One-time setup (you only do this once):

1. Go to https://search.google.com/search-console
2. Sign in with the Google account that owns `G-EKQ0LBDH9Z`
3. Select the property `pragmaticsysadmin.help` (it should already be there because the verification file exists)
4. In the left sidebar, click **Sitemaps**
5. In "Add a new sitemap", enter: `sitemap.xml` (just the filename — the domain is already known)
6. Click **Submit**
7. Status should change to "Success" within a few minutes. URL count should match the number of pages on the site.

After that, Google will re-fetch the sitemap automatically every few days. You don't need to resubmit when you publish new posts.

## Linking Search Console to GA4

This lets you see which search queries bring visitors to which pages, inside GA4.

1. In Search Console, click **Settings** (gear icon, bottom left)
2. Look for **Search Console** under "Property settings" → click it
3. You should see your GA4 property (`G-EKQ0LBDH9Z`) listed — select it and link
4. In GA4, the report appears under **Reports > Acquisition > Search Console**

## What to check monthly

1. **Search Console → Performance**:
   - Which queries are getting impressions but low CTR? Rewrite those titles/descriptions.
   - Which pages are losing position over time? Update them.
   - Are there new queries you didn't expect? Write more about them.

2. **Search Console → Coverage**:
   - Any "Excluded" URLs that should be indexed? Investigate.
   - Any 404s Google found? Fix or redirect them.

3. **Search Console → Core Web Vitals**:
   - LCP (Largest Contentful Paint): target < 2.5s
   - CLS (Cumulative Layout Shift): target < 0.1
   - INP (Interaction to Next Paint): target < 200ms
   - If any are flagged, the usual culprit on this site is the chat widget or the Father's Day popup loading too early.

## When you publish a new post

1. Run `python3 scripts/generate-og-images.py` — this regenerates all OG images and creates one for the new post.
2. Commit the new post + the new `static/og/<slug>.png`.
3. Push. GitHub Actions will deploy.
4. (Optional) In Search Console → URL Inspection, paste the new URL and click **Request indexing**. This speeds up discovery from days to hours. Don't do this more than ~10 times per day.

## SEO hygiene rules for this site

- Every post MUST have a unique `description` in front-matter. The build will still work without it, but social shares and Google results suffer.
- Every post should target one primary keyword in the title. Don't try to rank for everything in one post.
- Internal links matter: every post should link to at least 2 other posts where relevant. The Start Here page (`/start-here/`) is the hub — link to it from new posts when introducing the site's audience split.
- Image alt text: every screenshot/diagram should have descriptive alt text. The OG image generator strips non-ASCII from titles, so the post title itself is safe to use special characters in.

## Things to NOT do

- Don't pay for SEO tools (Ahrefs, SEMrush) until the site has 5,000+ monthly visitors. Until then, Search Console + GA4 is enough.
- Don't submit the sitemap more than once. Repeated submission doesn't speed anything up.
- Don't request indexing for every existing page — Google will find them via the sitemap. Save the quota for new posts.
- Don't stuff keywords into descriptions. Write for humans; Google's algorithms are smart enough to handle synonyms.

## Common issues

**"My new post isn't showing up in Google"**
- Check Search Console → URL Inspection. If "URL is not on Google", click "Request indexing".
- Make sure the post is not `draft: true`.
- Make sure the post date is not in the future (or set `buildFuture = true` in hugo.toml, but that's risky).

**"OG image isn't showing on Twitter/LinkedIn"**
- Run `python3 scripts/generate-og-images.py` and commit the new image.
- Test with https://cards-dev.twitter.com/validator (deprecated but still works) or https://www.opengraph.xyz/
- The image URL must be HTTPS and publicly accessible.

**"Search Console says 'Duplicate without user-selected canonical'"**
- This usually means two posts have very similar content. Add a `canonical` link to the preferred version in the other post's front-matter: `canonicalURL: "https://pragmaticsysadmin.help/posts/the-preferred-version/"`.

## Future improvements to consider

1. **Internal search**: add a client-side search (Pagefind is free and works with Hugo static sites). Makes the site stickier.
2. **Schema for HowTo articles**: tutorials could get `HowTo` schema for richer results. Easy to add per-post via front-matter + a partial.
3. **FAQ schema**: posts with Q&A sections could get `FAQPage` schema.
4. **Bing Webmaster Tools**: lower priority but free. Submit sitemap at https://www.bing.com/webmasters/
