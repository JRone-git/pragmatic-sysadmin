#!/usr/bin/env python3
"""Autonomous promotion engine for pragmaticsysadmin.help.

Turns every newly published post into platform-ready promotion:

  generate        Find published posts not yet promoted, write pitch packages
                  to promotion/queue/<slug>/ (HN, Reddit, Bluesky, Mastodon,
                  dev.to cross-post) and register them in promotion/state.json.
  auto-post       Post queued content to the safe auto channels (Bluesky,
                  Mastodon, dev.to) - cadence-enforced, dry-run capable.
  issue-body      Print the GitHub issue body (HN/Reddit drafts + prefill
                  links) for one queued post.
  open-issues     Create/update the tracking issue labelled `promotion` for
                  every post that still needs manual HN/Reddit submission.
  handle-comment  Process a "/submit" or "/skip" command from an issue comment
                  (reads $GITHUB_EVENT_PATH). Posts to Reddit via API when
                  secrets are present, otherwise replies with copy-paste
                  blocks and pre-filled submit links.
  evergreen       Resurface an older post on the auto channels so traffic
                  doesn't die after week one.

Zero third-party dependencies (repo rule): stdlib only.
Cadence rule from hacker-news-pitches.md: at most one post per platform per
48 hours - enforced via promotion/state.json.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONTENT_DIR = ROOT / "content"
PROMO_DIR = ROOT / "promotion"
QUEUE_DIR = PROMO_DIR / "queue"
STATE_PATH = PROMO_DIR / "state.json"
RELEASE_PATH = PROMO_DIR / "release.yaml"

BASE_URL = "https://pragmaticsysadmin.help"
SECTIONS = ("sysadmin", "senior-tech", "meta", "posts")
AUTO_CHANNELS = ("bluesky", "mastodon", "devto")
CADENCE_HOURS = 48  # default: "once per platform per 48 hours" - see hacker-news-pitches.md
MAX_PER_RUN = 1  # default: max posts per auto channel per run
EVERGREEN_MIN_AGE_DAYS = 30
EVERGREEN_RESHARE_DAYS = 60

# The 48 hour rule exists so followers on Bluesky and Mastodon are not
# buried. dev.to is not a feed - it is an article library. Every post
# there is a permanent, separately browsable page, and nothing gets
# interrupted. One article a day keeps the same courtesy while giving the
# queue a way to drain.
#
# The social channels stay at one post per run. That is deliberate: 42
# queued posts dumped on a follower timeline at once is spam, and a
# suspended account earns nothing at all.
CHANNEL_CADENCE_HOURS = {"bluesky": 48, "mastodon": 48, "devto": 24}
CHANNEL_MAX_PER_RUN = {"bluesky": 1, "mastodon": 1, "devto": 5}
# dev.to's API allows 30 write requests per 30 seconds. Six seconds is
# well inside that and still leaves the run readable in the log.
DEVTO_POST_PAUSE_SECONDS = 35
# dev.to's article endpoint rate-limits well below the published
# 30-requests-per-30-seconds figure for general API traffic: two articles
# in twelve seconds came back 429. One article every 35 seconds is
# comfortably inside it.
DEVTO_RETRY_ATTEMPTS = 3
DEVTO_RETRY_WAIT_SECONDS = 40


def _post_devto_with_retry(pkg: Path, *, dry_run: bool) -> str:
    """Post to dev.to, waiting out a rate limit instead of giving up.

    The first version treated a 429 like a broken configuration: it marked
    the post failed and abandoned the whole batch. Two articles went out,
    the third hit the limit, and the two behind it were never tried.
    """
    last = ""
    for attempt in range(1, DEVTO_RETRY_ATTEMPTS + 1):
        try:
            return post_devto(pkg, dry_run=dry_run)
        except RateLimited as e:
            last = str(e)
            if attempt == DEVTO_RETRY_ATTEMPTS:
                break
            wait = DEVTO_RETRY_WAIT_SECONDS
            print(f"dev.to/{pkg.parent.name}: rate limited, waiting {wait}s "
                  f"(attempt {attempt}/{DEVTO_RETRY_ATTEMPTS})")
            time.sleep(wait)
    raise RuntimeError(last or "dev.to post failed")

# Fallback subreddits per section (first match wins; overridable per-post
# with a `promotion_subreddits:` line in front matter).
SUBREDDITS = {
    "sysadmin": ["r/sysadmin", "r/selfhosted", "r/homelab"],
    "senior-tech": ["r/techsupport", "r/eldercare"],
    "meta": ["r/selfhosted"],
    "posts": ["r/sysadmin"],
}


# ---------------------------------------------------------------------------
# Channel-specific formatting helpers
# ---------------------------------------------------------------------------


def devto_tags(tags, limit: int = 4) -> list[str]:
    """Sanitise site tags into dev.to's tag format.

    dev.to's API rejects any tag that is not purely alphanumeric. A hyphen is
    a hard 422, not a warning:

        422 {"error":"Tag \"local-llm\" contains non-alphanumeric or
        prohibited unicode characters and Tag \"senior-tech\" contains
        non-alphanumeric or prohibited unicode characters","status":422}

    So `senior-tech` has to go out as `seniortech`. Strip the separators
    rather than hyphenating them, because a hyphen is exactly what the API
    is refusing. Articles also cap at four tags, and a tag made entirely of
    punctuation would sanitise to an empty string and be rejected too.

    Tags are taken from the site's own front matter, whose vocabulary is
    hyphenated by design (`senior-tech`, `home-lab`, `local-llm`). This is
    the single conversion point between the two vocabularies.
    """
    out: list[str] = []
    for raw in tags or []:
        clean = re.sub(r"[^a-z0-9]", "", str(raw).lower())[:24]
        if clean and clean not in out:
            out.append(clean)
        if len(out) == limit:
            break
    return out or ["sysadmin"]


# ---------------------------------------------------------------------------
# Front matter + state helpers
# ---------------------------------------------------------------------------


def now() -> datetime:
    return datetime.now(timezone.utc)


def split_front_matter(text: str) -> tuple[str, str] | None:
    """Split YAML front matter from the body, or return None.

    The naive `text.split("---", 2)` breaks on any post whose front matter
    contains a --- inside a quoted string. Three of the best posts did: an
    FAQ answer ended with "Same phones, same service, new name. ---" and
    the splitter took that for the end of the front matter. The body then
    started with a stray quote and a horizontal rule, and dev.to published
    it exactly like that.

    A --- only ends the front matter when it is alone on its own line.
    Hugo's own YAML parser agrees, so this matches what the site renders.
    """
    lines = text.splitlines(keepends=True)
    if not lines or lines[0].strip() != "---":
        return None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            return "".join(lines[1:i]), "".join(lines[i + 1:])
    return None


def parse_post(path: Path):
    """Return dict with title/description/tags/section/url/body or None."""
    text = path.read_text(encoding="utf-8")
    split = split_front_matter(text)
    if split is None:
        return None
    fm_text, body = split
    body = body.strip()

    fm = {}
    tags: list[str] = []
    in_tags = False
    for line in fm_text.splitlines():
        if re.match(r"^tags\s*:", line):
            in_tags = True
            continue
        if in_tags:
            m = re.match(r"^\s*-\s*(.+)$", line)
            if m:
                tags.append(m.group(1).strip().strip('"').strip("'"))
                continue
            in_tags = False
        if ":" in line and not line[:1].isspace():
            k, v = line.split(":", 1)
            fm[k.strip()] = v.strip().strip('"').strip("'")

    if fm.get("draft", "false").lower() == "true":
        return None
    # `no_publish: true` is an explicit hold — the post stays down even if
    # something else flips draft to false (e.g. the auto-publish cron).
    if fm.get("no_publish", "false").lower() == "true":
        return None
    title = fm.get("title", "")
    if not title:
        return None

    date_str = fm.get("date", "")
    post_date = None
    if date_str:
        try:
            post_date = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
            if post_date.tzinfo is None:
                post_date = post_date.replace(tzinfo=timezone.utc)
        except ValueError:
            try:
                post_date = datetime.strptime(date_str[:10], "%Y-%m-%d").replace(
                    tzinfo=timezone.utc
                )
            except ValueError:
                post_date = None

    rel = path.relative_to(CONTENT_DIR).as_posix()
    rel_no_ext = re.sub(r"\.md$", "", rel)
    slug = fm.get("slug") or re.sub(r"^\d{4}-\d{2}-\d{2}-", "", path.stem)

    # The public URL has to match what Hugo actually publishes. Hugo uses
    # the front matter `slug:` when there is one and falls back to the file
    # name when there is not - so building the URL from the file name
    # produces a 404 for every post that sets a slug.
    #
    #   content/meta/2026-11-02-hallway-display-for-my-parents-the-idea.md
    #     slug: hallway-display-for-my-parents-the-idea
    #     -> /meta/hallway-display-for-my-parents-the-idea/
    #     not /meta/2026-11-02-hallway-display-for-my-parents-the-idea/
    if fm.get("slug"):
        url = f"{BASE_URL}/{path.parent.name}/{fm['slug']}/"
    else:
        url = f"{BASE_URL}/{rel_no_ext}/"

    return {
        "slug": slug,
        "title": title,
        "description": fm.get("description", fm.get("summary", "")),
        "tags": tags,
        "section": path.parent.name,
        "url": url,
        "date": post_date.isoformat() if post_date else None,
        "body": body,
        "subreddits": [
            s.strip()
            for s in fm.get("promotion_subreddits", "").split(",")
            if s.strip()
        ] or SUBREDDITS.get(path.parent.name, ["r/sysadmin"]),
    }



def load_state() -> dict:
    if STATE_PATH.exists():
        return json.loads(STATE_PATH.read_text(encoding="utf-8"))
    return {"posts": {}, "last_posted": {}}


def save_state(state: dict) -> None:
    PROMO_DIR.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(
        json.dumps(state, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def channel_status(post_state: dict, channel: str) -> str:
    return (post_state.get("channels") or {}).get(channel, {}).get("status", "none")


def set_channel(post_state: dict, channel: str, status: str, **extra) -> None:
    post_state.setdefault("channels", {})[channel] = {
        "status": status,
        "at": now().isoformat(timespec="seconds"),
        **extra,
    }


def hours_since(state: dict, channel: str) -> float:
    last = state.get("last_posted", {}).get(channel)
    if not last:
        return float("inf")
    try:
        return (now() - datetime.fromisoformat(last)).total_seconds() / 3600
    except ValueError:
        return float("inf")


# ---------------------------------------------------------------------------
# Pitch package generation
# ---------------------------------------------------------------------------


def _clip(text: str, limit: int) -> str:
    text = " ".join(text.split())
    if len(text) <= limit:
        return text
    cut = text[: max(limit - 1, 1)]
    if " " in cut:
        cut = cut[: cut.rfind(" ")]
    return cut.rstrip(" ,.;:-—") + "…"



def strip_scripts(body: str) -> str:
    """Remove real <script> blocks from a cross-post body.

    Two reasons. JSON-LD belongs on the canonical site - the canonical_url
    points dev.to at the original anyway, so repeating the structured data
    helps nobody, and Forem renders a <script> block as visible text. One
    post had two of them.

    And one post carried the site's own Google Analytics snippet. On
    dev.to that would have re-instrumented a third-party site with our
    property. Forem strips scripts anyway, but leaving it in the source
    is asking for trouble.

    Only blocks that start a line are removed. `bash <script>` inside
    inline code is not a tag and must survive - the closing </script> it
    might otherwise pair with could be a long way away.
    """
    body = re.sub(
        r'^[ \t]*<script\b[^>]*>.*?</script>[ \t]*\n?',
        "",
        body,
        flags=re.DOTALL | re.MULTILINE | re.IGNORECASE,
    )
    # A self-closing external script, e.g. <script async src="..."></script>
    body = re.sub(
        r'^[ \t]*<script\b[^>]*/>[ \t]*\n?',
        "",
        body,
        flags=re.MULTILINE | re.IGNORECASE,
    )
    return body.strip()


def write_package(post: dict) -> Path:
    """Write channel-ready pitch files for one post. Returns package dir."""
    pkg = QUEUE_DIR / post["slug"]
    pkg.mkdir(parents=True, exist_ok=True)

    title = post["title"]
    desc = post["description"] or ""
    url = post["url"]
    hashtags = " ".join(
        "#" + re.sub(r"[^a-z0-9]", "", t.lower()) for t in post["tags"][:3]
    )

    # Hacker News - link submission (HN has no write API; the tracking issue
    # provides a pre-filled submit link plus this copy-paste body).
    hn_title = _clip(title, 100)
    hn_body = (
        f"{desc}\n\nFull write-up with the commands and checklists:\n{url}\n\n"
        "Happy to answer questions about the approach."
    )
    (pkg / "hn.md").write_text(
        f"# Hacker News pitch\n\n**Title:**\n> {hn_title}\n\n**Body:**\n\n{hn_body}\n",
        encoding="utf-8",
    )

    # Reddit - one file per candidate subreddit.
    for sub in post["subreddits"][:2]:
        reddit_title = _clip(title, 300)
        reddit_body = (
            f"{desc}\n\nFull write-up (no paywall, no tracking): {url}\n\n"
            "What I'd like your take on: does this match your experience, "
            "and what did I get wrong?"
        )
        safe = sub.replace("/", "-").replace("r-", "")
        (pkg / f"reddit-{safe}.md").write_text(
            f"# Reddit pitch — {sub}\n\n**Subreddit:** {sub}\n\n"
            f"**Title:**\n> {reddit_title}\n\n**Body:**\n\n{reddit_body}\n",
            encoding="utf-8",
        )

    # Bluesky - 300 char hard limit (URL counts toward it).
    hook_src = desc.split(". ")[0] if desc else title
    hook = _clip(hook_src, max(240 - len(url), 60))
    (pkg / "bluesky.txt").write_text(
        f"{hook}\n\n{url}" + (f"\n\n{hashtags}" if hashtags else ""),
        encoding="utf-8",
    )

    # Mastodon - 500 char limit.
    masto = _clip(desc if desc else title, max(400 - len(url), 60))
    (pkg / "mastodon.txt").write_text(
        f"{masto}\n\n{url}" + (f"\n\n{hashtags}" if hashtags else ""),
        encoding="utf-8",
    )


    # dev.to cross-post: front matter with canonical_url + absolute image URLs.
    body = re.sub(r"\]\(/", f"]({BASE_URL}/", post["body"])
    body = re.sub(r'src="/', f'src="{BASE_URL}/', body)
    body = strip_scripts(body)
    dev_tags = devto_tags(post["tags"])
    (pkg / "devto.md").write_text(
        f"---\ntitle: {json.dumps(title)}\n"
        f"canonical_url: {url}\ntags: {', '.join(dev_tags)}\n---\n\n{body}\n",
        encoding="utf-8",
    )

    # Index card consumed by issue-body/handle-comment.
    (pkg / "package.json").write_text(
        json.dumps(post, indent=2, ensure_ascii=False, default=str) + "\n",
        encoding="utf-8",
    )
    return pkg



# ---------------------------------------------------------------------------
# HTTP helpers (stdlib urllib only)
# ---------------------------------------------------------------------------


def _req(url: str, *, method: str = "GET", data: dict | None = None,
         headers: dict | None = None, token: str | None = None) -> tuple[int, bytes]:
    body = None
    hdrs = {"User-Agent": "pragmatic-sysadmin-promote/1.0"}
    if headers:
        hdrs.update(headers)
    if token:
        hdrs["Authorization"] = f"Bearer {token}"
    if data is not None:
        body = json.dumps(data).encode("utf-8")
        hdrs["Content-Type"] = "application/json"
    request = urllib.request.Request(url, data=body, headers=hdrs, method=method)
    try:
        with urllib.request.urlopen(request, timeout=30) as resp:
            return resp.status, resp.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read()


def post_bluesky(text: str, *, dry_run: bool) -> str:
    """Post to Bluesky via ATProto (handle + app password). Returns ref."""
    if dry_run:
        print(f"[dry-run] bluesky:\n{text}\n")
        return "dry-run"
    handle = os.environ.get("BLUESKY_HANDLE", "")
    app_pw = os.environ.get("BLUESKY_APP_PASSWORD", "")
    if not handle or not app_pw:
        raise RuntimeError("BLUESKY_HANDLE / BLUESKY_APP_PASSWORD not set")

    status, raw = _req(
        "https://bsky.social/xrpc/com.atproto.server.createSession",
        method="POST",
        data={"identifier": handle, "password": app_pw},
    )
    if status != 200:
        raise RuntimeError(f"bluesky login failed: {status} {raw[:200]!r}")
    sess = json.loads(raw)

    # Link facet so the URL is tappable (byte offsets per ATProto spec).
    facets = []
    url_pos = text.find(BASE_URL)
    if url_pos >= 0:
        link = text[url_pos:].split("\n")[0]
        start_b = len(text[:url_pos].encode("utf-8"))
        end_b = start_b + len(link.encode("utf-8"))
        facets.append({
            "index": {"byteStart": start_b, "byteEnd": end_b},
            "features": [{"$type": "app.bsky.facet#link", "uri": link}],
        })

    record = {
        "$type": "app.bsky.feed.post",
        "text": text,
        "createdAt": now().isoformat(timespec="seconds").replace("+00:00", "Z"),
    }
    if facets:
        record["facets"] = facets

    status, raw = _req(
        "https://bsky.social/xrpc/com.atproto.repo.createRecord",
        method="POST",
        token=sess["accessJwt"],
        data={"repo": sess["did"], "collection": "app.bsky.feed.post",
              "record": record},
    )
    if status != 200:
        raise RuntimeError(f"bluesky post failed: {status} {raw[:200]!r}")
    ref = json.loads(raw).get("uri", "")
    print(f"bluesky OK: {ref}")
    return ref



def post_mastodon(text: str, *, dry_run: bool) -> str:
    """Post to Mastodon via access token. Returns status URL."""
    if dry_run:
        print(f"[dry-run] mastodon:\n{text}\n")
        return "dry-run"
    instance = os.environ.get("MASTODON_INSTANCE", "mastodon.social").strip("/")
    token = os.environ.get("MASTODON_ACCESS_TOKEN", "")
    if not token:
        raise RuntimeError("MASTODON_ACCESS_TOKEN not set")

    status, raw = _req(
        f"https://{instance}/api/v1/statuses",
        method="POST",
        token=token,
        data={"status": text, "visibility": "public"},
    )
    if status != 200:
        raise RuntimeError(f"mastodon post failed: {status} {raw[:200]!r}")
    ref = json.loads(raw).get("url", "")
    print(f"mastodon OK: {ref}")
    return ref


class RateLimited(RuntimeError):
    """dev.to said "try again in 30 seconds". Transient, not fatal."""


class ConfigError(RuntimeError):
    """Something is wrong with the setup, so every post would fail."""


def post_devto(pkg: Path, *, dry_run: bool) -> str:
    """Cross-post to dev.to with canonical_url pointing back at the site."""
    front = (pkg / "devto.md").read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", front, re.DOTALL)
    if not m:
        raise RuntimeError(f"devto.md front matter malformed in {pkg}")
    fm_text, body = m.group(1), m.group(2).strip()
    fm = {}
    for line in fm_text.splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            fm[k.strip()] = v.strip()
    payload = {
        "article": {
            "title": fm.get("title", "").strip('"'),
            "body_markdown": body,
            "published": True,
            "canonical_url": fm.get("canonical_url", ""),
            # Sanitise here as well as at write time. The queue already holds
            # packages written by the old hyphenating code, and dev.to's API
            # rejects a hyphenated tag outright - so a package staged before
            # the fix would keep failing forever unless the tags are cleaned
            # on the way out.
            "tags": devto_tags(
                [t.strip() for t in fm.get("tags", "").split(",") if t.strip()]
            ),
        }
    }
    if dry_run:
        print(f"[dry-run] dev.to: {json.dumps(payload)[:400]}…")
        return "dry-run"

    api_key = os.environ.get("DEVTO_API_KEY", "")
    if not api_key:
        raise ConfigError("DEVTO_API_KEY not set")
    status, raw = _req(
        "https://dev.to/api/articles",
        method="POST",
        # NOTE: Forem authenticates with an `api-key` header, NOT
        # `Authorization: Bearer` (that 401s even with a valid key).
        headers={"Content-Type": "application/json", "api-key": api_key},
        data=payload,
    )
    if status == 429:
        # "Rate limit reached, try again in 30 seconds". The article itself
        # is fine - the account posted too many too fast. This is not a
        # reason to mark the post failed and abandon the batch.
        raise RateLimited("dev.to rate limit reached")
    if status not in (200, 201):
        raise RuntimeError(f"dev.to post failed: {status} {raw[:300]!r}")
    ref = json.loads(raw).get("url", "")
    print(f"dev.to OK: {ref}")
    return ref



# ---------------------------------------------------------------------------
# Subcommands
# ---------------------------------------------------------------------------


def iter_posts():
    for section in SECTIONS:
        d = CONTENT_DIR / section
        if not d.is_dir():
            continue
        for path in sorted(d.glob("*.md")):
            if path.name.startswith("_"):
                continue
            post = parse_post(path)
            if post:
                yield post


def cmd_refresh_urls(args) -> int:
    """Rewrite stale URLs in already-queued promotion packages.

    `generate` skips posts that are already in the queue, so a package written
    with the wrong URL keeps that wrong URL forever. The URL used to be built
    from the post's file name, which is only right for posts that do not set
    a `slug:` in their front matter. Hugo uses the slug when there is one, so
    every such post pointed at a 404 - as the canonical_url on dev.to, which
    is exactly the link that has to work.

    This walks the queue, recomputes the URL from the source post and
    rewrites it everywhere it appears in the package.
    """
    by_slug = {post["slug"]: post for post in iter_posts()}
    changed = 0
    for pkg in sorted(QUEUE_DIR.iterdir()) if QUEUE_DIR.is_dir() else []:
        if not pkg.is_dir():
            continue
        pj = pkg / "package.json"
        if not pj.exists():
            continue
        try:
            meta = json.loads(pj.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        old_url = meta.get("url", "")
        post = by_slug.get(meta.get("slug", ""))
        if not post or not old_url or post["url"] == old_url:
            continue
        new_url = post["url"]
        touched = 0
        for child in sorted(pkg.iterdir()):
            if not child.is_file():
                continue
            try:
                text = child.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue
            if old_url not in text:
                continue
            child.write_text(text.replace(old_url, new_url), encoding="utf-8")
            touched += 1
        print(f"refresh: {meta['slug']} -> {new_url}  ({touched} file(s))")
        changed += 1

    # state.json keeps its own copy of the URL for every queued post.
    state = load_state()
    state_changed = 0
    for slug, entry in (state.get("posts") or {}).items():
        post = by_slug.get(slug)
        if not post or not isinstance(entry, dict):
            continue
        if entry.get("url") and entry["url"] != post["url"]:
            print(f"refresh: state.json {slug} -> {post['url']}")
            entry["url"] = post["url"]
            state_changed += 1
    if state_changed:
        save_state(state)

    print(f"refresh: {changed} package(s) and {state_changed} state entry/entries updated.")
    return 0


def cmd_generate(args) -> int:
    """Queue pitch packages for published posts not yet in state.

    Posts newer than --promo-days (default 14) get the full promotion
    treatment: pitch package + pending auto/manual channels. Older posts are
    registered as historical seeds (channels pre-marked done) so the backlog
    doesn't flood the queue — they remain eligible for evergreen resharing.
    """
    state = load_state()
    promo_cutoff = now() - timedelta(days=args.promo_days)
    new, seeded = [], []
    for post in iter_posts():
        if post["slug"] in state["posts"]:
            continue
        # Only promote posts that are actually live (date <= now).
        if post["date"] and post["date"] > now().isoformat():
            continue
        try:
            post_dt = datetime.fromisoformat(post["date"]) if post["date"] else None
        except ValueError:
            post_dt = None
        is_fresh = post_dt is None or post_dt >= promo_cutoff

        if is_fresh:
            pkg = write_package(post)
            channels = {}
            new.append((post["slug"], pkg))
        else:
            # Historical post: seed state only, no pitch package, no issues.
            channels = {ch: {"status": "seeded",
                             "at": now().isoformat(timespec="seconds")}
                        for ch in AUTO_CHANNELS + ("hn", "reddit")}
            seeded.append(post["slug"])

        state["posts"][post["slug"]] = {
            "title": post["title"],
            "url": post["url"],
            "section": post["section"],
            "queued_at": now().isoformat(timespec="seconds"),
            "published_at": post["date"],
            "channels": channels,
        }
    save_state(state)
    if not new and not seeded:
        print("generate: nothing new to queue.")
    for slug, pkg in new:
        print(f"generate: queued {slug} -> {pkg.relative_to(ROOT).as_posix()}")
    if seeded:
        print(f"generate: seeded {len(seeded)} historical posts "
              "(evergreen-eligible only).")
    # Machine-readable list for the workflow's issue-creation step.
    (PROMO_DIR / "new-slugs.txt").write_text(
        "\n".join(slug for slug, _ in new) + ("\n" if new else ""),
        encoding="utf-8",
    )
    return 0


def _pending_posts(state: dict, channel: str):
    """Posts whose package exists and this channel hasn't succeeded yet.

    "seeded" means the post was judged historical when the queue was
    generated, so it is held back from the social channels and left for
    evergreen resharing. dev.to is different: it is an article library,
    not a feed, and a cross-post there interrupts nobody. A seeded post
    that already has a package is therefore eligible for dev.to.
    """
    for slug, ps in sorted(
        state["posts"].items(), key=lambda kv: kv[1].get("queued_at", "")
    ):
        pkg = QUEUE_DIR / slug
        if not (pkg / "package.json").exists():
            continue
        status = channel_status(ps, channel)
        if status in ("posted", "skipped"):
            continue
        if status == "seeded" and channel != "devto":
            continue
        yield slug, ps, pkg


def load_release() -> dict:
    """Optional release control read from promotion/release.yaml.

    A tiny key: value file, because the repo has no YAML parser available
    to a stdlib-only script and this does not need to be YAML.

        devto_batch: 8
        devto_ignore_cadence: true

    The file is a one-shot ticket: it is deleted once a run has actually
    published something, so a release does not repeat on every later push.
    """
    out: dict = {}
    if not RELEASE_PATH.exists():
        return out
    for raw in RELEASE_PATH.read_text(encoding="utf-8").splitlines():
        line = raw.split("#", 1)[0].strip()
        if not line or ":" not in line:
            continue
        key, value = line.split(":", 1)
        value = value.strip().strip('"').strip("'")
        if value.lower() in ("true", "yes", "on"):
            out[key.strip()] = True
        elif value.lower() in ("false", "no", "off"):
            out[key.strip()] = False
        else:
            try:
                out[key.strip()] = int(value)
            except ValueError:
                out[key.strip()] = value
    return out


def cmd_rebuild(args) -> int:
    """Regenerate the pitch packages from the source posts.

    The packages are derived data. A change to the front matter splitter,
    the tag cleaning or the URL rule should not need the queue to be
    emptied and refilled by hand - and a package written by a buggy
    splitter stays wrong forever otherwise.

    Only posts that already have a package are rebuilt, so this never
    pulls a historical post into the queue behind the operator's back.
    """
    state = load_state()
    count = 0
    for post in iter_posts():
        pkg = QUEUE_DIR / post["slug"]
        if not (pkg / "package.json").exists():
            continue
        write_package(post)
        count += 1
    print(f"rebuild: regenerated {count} package(s).")
    return 0


def cmd_auto_post(args) -> int:
    """Post queued content to the safe auto channels, cadence-enforced."""
    state = load_state()
    poster = {"bluesky": post_bluesky, "mastodon": post_mastodon, "devto": post_devto}
    exit_code = 0
    force = getattr(args, "force", False)
    release = load_release()
    devto_published = 0
    for channel in AUTO_CHANNELS:
        if args.channels and channel not in args.channels.split(","):
            continue
        cadence = CHANNEL_CADENCE_HOURS.get(channel, CADENCE_HOURS)
        # A release ticket can wave the dev.to cooldown through. It cannot
        # wave through the social channels - those stay on their cadence
        # whatever the file says.
        skip_cadence = force or (
            channel == "devto" and release.get("devto_ignore_cadence")
        )
        if not skip_cadence:
            wait = cadence - hours_since(state, channel)
            if wait > 0:
                print(f"{channel}: cadence cooldown, {wait:.1f}h remaining. "
                      "Skipping.")
                continue
        else:
            print(f"{channel}: release override, cadence bypassed.")
        # --batch only ever applies to dev.to. The social channels stay at
        # one post per run no matter what, so a batch can never turn into
        # a follower-timeline dump.
        limit = CHANNEL_MAX_PER_RUN.get(channel, MAX_PER_RUN)
        if channel == "devto":
            if getattr(args, "batch", 0):
                limit = args.batch
            elif release.get("devto_batch"):
                limit = int(release["devto_batch"])
        posted = 0
        for slug, ps, pkg in _pending_posts(state, channel):
            if posted >= limit:
                break
            if channel == "devto":
                text = (pkg / "devto.md").read_text(encoding="utf-8")
            else:
                text = (pkg / f"{channel}.txt").read_text(encoding="utf-8")
            try:
                if channel == "devto":
                    ref = _post_devto_with_retry(pkg, dry_run=args.dry_run)
                else:
                    ref = poster[channel](text, dry_run=args.dry_run)
            except ConfigError as e:
                # A setup problem will fail every post. Stop rather than
                # spamming failures, and say what is actually wrong.
                print(f"{channel}/{slug}: FAILED - {e}")
                set_channel(ps, channel, "failed", error=str(e))
                exit_code = 1
                break
            except RuntimeError as e:
                # One bad article should not cost us the rest of the batch.
                # Leave it eligible so the next run tries it again.
                print(f"{channel}/{slug}: FAILED - {e}")
                set_channel(ps, channel, "failed", error=str(e))
                exit_code = 1
                continue
            if not args.dry_run:
                set_channel(ps, channel, "posted", ref=ref)
                state["last_posted"][channel] = now().isoformat(timespec="seconds")
            posted += 1
            if channel == "devto":
                devto_published += 1
                if posted < limit and not args.dry_run:
                    time.sleep(DEVTO_POST_PAUSE_SECONDS)
    if not args.dry_run:
        save_state(state)
        # A release ticket is spent once it has published something. If the
        # run published nothing, it stays on disk so the next run can try
        # again rather than silently dropping the intent.
        if devto_published and RELEASE_PATH.exists():
            RELEASE_PATH.unlink()
            print(f"promotion: release ticket consumed after "
                  f"{devto_published} dev.to article(s).")
    else:
        print("(dry-run: state not saved)")
    return exit_code



# ---------------------------------------------------------------------------
# Approval flow: tracking issues with HN/Reddit drafts
# ---------------------------------------------------------------------------


def _read_pkg(slug: str) -> dict:
    return json.loads((QUEUE_DIR / slug / "package.json").read_text(encoding="utf-8"))


def _prefill_hn_link(title: str, url: str) -> str:
    import urllib.parse
    return (
        "https://news.ycombinator.com/submit?title="
        + urllib.parse.quote(_clip(title, 100))
        + "&url=" + urllib.parse.quote(url, safe="")
    )


def _prefill_reddit_link(sub: str, title: str, url: str) -> str:
    import urllib.parse
    sub = sub if sub.startswith("r/") else "r/" + sub
    return (
        f"https://www.reddit.com/{sub}/submit?title="
        + urllib.parse.quote(title)
        + "&url=" + urllib.parse.quote(url, safe="")
    )


def cmd_issue_body(args) -> int:
    """Print the tracking-issue body for one queued post."""
    pkg = QUEUE_DIR / args.slug
    if not (pkg / "package.json").exists():
        print(f"unknown or unqueued slug: {args.slug}", file=sys.stderr)
        return 1
    post = _read_pkg(args.slug)
    hn = (pkg / "hn.md").read_text(encoding="utf-8")
    reddit_files = sorted(pkg.glob("reddit-*.md"))

    out = []
    out.append(f"## Promotion queue — {post['title']}")
    out.append("")
    out.append(f"URL: {post['url']}  ")
    out.append(f"Section: `{post['section']}`  ")
    out.append(f"<!-- promote-slug: {post['slug']} -->")
    out.append("")
    out.append("### Auto channels (handled by the `promote` workflow)")
    out.append("Bluesky / Mastodon / dev.to are posted automatically with")
    out.append("48-hour cadence. Status lives in `promotion/state.json`.")
    out.append("")
    out.append("---")
    out.append("")
    out.append("### 1. Hacker News (manual — HN has no write API)")
    out.append(f"[**Pre-filled submit link →**]({_prefill_hn_link(post['title'], post['url'])})")
    out.append("")
    out.append("<details><summary>HN title + body (copy-paste)</summary>")
    out.append("")
    out.append(hn)
    out.append("</details>")
    out.append("")
    out.append("**Tip:** reply to the first comments within 30 minutes — it")
    out.append("decides the ranking (see `hacker-news-pitches.md`).")
    out.append("")
    out.append("### 2. Reddit")
    for rf in reddit_files:
        text = rf.read_text(encoding="utf-8")
        m = re.search(r"\*\*Subreddit:\*\* (\S+)", text)
        sub = m.group(1) if m else "r/sysadmin"
        m = re.search(r"\*\*Title:\*\*\n> (.+)", text)
        rtitle = m.group(1) if m else post["title"]
        out.append(f"**{sub}** — [pre-filled submit link →]"
                   f"({_prefill_reddit_link(sub, rtitle, post['url'])})")
        out.append("")
        out.append("<details><summary>Reddit title + body (copy-paste)</summary>")
        out.append("")
        out.append(text)
        out.append("</details>")
        out.append("")
    out.append("---")
    out.append("")
    out.append("### Approve from this issue")
    out.append("Comment one of:")
    out.append("")
    out.append("```")
    out.append("/submit hn")
    out.append("/submit reddit r/sysadmin")
    out.append("/skip hn")
    out.append("/skip reddit")
    out.append("```")
    out.append("")
    out.append("`/submit hn` replies with the pre-filled link + body.")
    out.append("`/submit reddit <sub>` posts via the Reddit API when")
    out.append("`REDDIT_CLIENT_ID/SECRET/USERNAME/PASSWORD` secrets are set;")
    out.append("otherwise it replies with the copy-paste block.")
    out.append("`/skip` marks the channel done so it stops nagging.")
    print("\n".join(out))
    return 0



def cmd_open_issues(args) -> int:
    """Create (or skip if existing) a promotion issue for each pending post.

    Uses `gh` CLI (present on GitHub runners, auth via GH_TOKEN).
    Prints issue URLs to stdout; sets GITHUB_OUTPUT if available.
    """
    state = load_state()
    pending = []
    for slug, ps in sorted(state["posts"].items(),
                           key=lambda kv: kv[1].get("queued_at", "")):
        hn_done = channel_status(ps, "hn") in ("posted", "skipped", "seeded")
        reddit_done = channel_status(ps, "reddit") in ("posted", "skipped", "seeded")
        if hn_done and reddit_done:
            continue
        if not (QUEUE_DIR / slug / "package.json").exists():
            continue
        pending.append((slug, ps))

    if not pending:
        print("open-issues: nothing pending.")
        return 0

    import subprocess
    import shutil
    if not shutil.which("gh"):
        print("open-issues: gh CLI not found; skipping.", file=sys.stderr)
        return 0

    # Prefer GITHUB_TOKEN but never clobber an existing GH_TOKEN.
    gh_env = {**os.environ,
              "GH_TOKEN": os.environ.get("GITHUB_TOKEN")
              or os.environ.get("GH_TOKEN", "")}
    created = []
    # Existing open promotion issues (label = promotion).
    res = subprocess.run(
        ["gh", "issue", "list", "--label", "promotion", "--state", "open",
         "--json", "number,title,body"],
        capture_output=True, text=True,
        env=gh_env,
    )
    existing = []
    if res.returncode == 0 and res.stdout.strip():
        existing = json.loads(res.stdout)

    for slug, ps in pending:
        match = None
        for issue in existing:
            if f"promote-slug: {slug}" in (issue.get("body") or ""):
                match = issue
                break
        if match:
            print(f"open-issues: issue #{match['number']} already covers {slug}")
            continue
        body_res = subprocess.run(
            [sys.executable, str(Path(__file__)), "issue-body", "--slug", slug],
            capture_output=True, text=True,
        )
        if body_res.returncode != 0:
            print(f"open-issues: issue-body failed for {slug}: {body_res.stderr}")
            continue
        title = f"📣 Promote: {_clip(ps['title'], 70)}"
        res = subprocess.run(
            ["gh", "issue", "create", "--label", "promotion",
             "--title", title, "--body-file", "-"],
            input=body_res.stdout, capture_output=True, text=True,
            env=gh_env,
        )
        if res.returncode == 0:
            url = res.stdout.strip()
            print(f"open-issues: created {url}")
            created.append(url)
        else:
            print(f"open-issues: create failed for {slug}: {res.stderr}")

    if created and os.environ.get("GITHUB_OUTPUT"):
        with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as fh:
            fh.write("created=" + ",".join(created) + "\n")
    return 0



# ---------------------------------------------------------------------------
# Reddit posting (OAuth script-app flow, stdlib only)
# ---------------------------------------------------------------------------


def reddit_access_token() -> str:
    cid = os.environ.get("REDDIT_CLIENT_ID", "")
    secret = os.environ.get("REDDIT_CLIENT_SECRET", "")
    user = os.environ.get("REDDIT_USERNAME", "")
    pw = os.environ.get("REDDIT_PASSWORD", "")
    if not (cid and secret and user and pw):
        raise RuntimeError(
            "REDDIT_CLIENT_ID / REDDIT_CLIENT_SECRET / REDDIT_USERNAME / "
            "REDDIT_PASSWORD not all set"
        )
    import base64
    basic = base64.b64encode(f"{cid}:{secret}".encode()).decode()
    body = urllib.parse.urlencode({
        "grant_type": "password", "username": user, "password": pw,
    }).encode()
    req = urllib.request.Request(
        "https://www.reddit.com/api/v1/access_token",
        data=body,
        headers={
            "Authorization": f"Basic {basic}",
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "pragmatic-sysadmin-promote/1.0",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read())
    if "access_token" not in data:
        raise RuntimeError(f"reddit token failed: {data}")
    return data["access_token"]


def reddit_submit(sub: str, title: str, url: str, text: str = "") -> str:
    """Submit a link (or crosspost text) to a subreddit. Returns permalink."""
    token = reddit_access_token()
    sub = sub.replace("r/", "").strip("/")
    payload = urllib.parse.urlencode({
        "sr": sub, "kind": "link" if url else "self",
        "title": title, "url": url, "text": text, "api_type": "json",
    }).encode()
    req = urllib.request.Request(
        "https://oauth.reddit.com/api/submit",
        data=payload,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "pragmatic-sysadmin-promote/1.0",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read())
    errors = (data.get("json", {}).get("errors")) or []
    if errors:
        raise RuntimeError(f"reddit submit errors: {errors}")
    post_id = data["json"]["data"].get("id", "")
    return f"https://www.reddit.com/comments/{post_id}"



def cmd_handle_comment(_args) -> int:
    """Process a /submit or /skip comment on a promotion issue.

    Reads the GitHub issue_comment event from $GITHUB_EVENT_PATH and writes
    the reply body to $GITHUB_OUTPUT (key: reply) plus a status file so the
    workflow can commit state changes.
    """
    event_path = os.environ.get("GITHUB_EVENT_PATH", "")
    if not event_path or not Path(event_path).exists():
        print("handle-comment: GITHUB_EVENT_PATH not set", file=sys.stderr)
        return 1
    event = json.loads(Path(event_path).read_text(encoding="utf-8-sig"))
    comment = (event.get("comment") or {}).get("body", "")
    issue_body = (event.get("issue") or {}).get("body", "") or ""

    m_slug = re.search(r"promote-slug:\s*(\S+)", issue_body)
    if not m_slug:
        print("handle-comment: no promote-slug marker in issue body")
        return 0

    cmd = None
    for line in comment.splitlines():
        line = line.strip()
        if line.startswith("/submit") or line.startswith("/skip"):
            cmd = line
            break
    if not cmd:
        print("handle-comment: no /submit or /skip command; ignoring.")
        return 0

    parts = cmd.split()
    action, channel = parts[0].lstrip("/"), (parts[1].lower() if len(parts) > 1 else "")
    slug = m_slug.group(1)
    state = load_state()
    ps = state["posts"].get(slug)
    if ps is None:
        print(f"handle-comment: slug {slug} not in state")
        return 0
    pkg = QUEUE_DIR / slug
    post = _read_pkg(slug)
    reply_lines = []

    if channel == "all":
        channels = ["hn", "reddit"]
    elif channel in ("hn", "reddit"):
        channels = [channel]
    else:
        channels = []

    if not channels:
        reply_lines.append("I didn't recognize that command. Use:")
        reply_lines.append("```/submit hn```, ```/submit reddit r/sysadmin```, "
                           "```/skip hn```, ```/skip reddit```")
    for ch in channels:
        if action == "skip":
            set_channel(ps, ch, "skipped")
            reply_lines.append(f"✅ `{ch}` marked as skipped for this post.")
            continue
        if ch == "hn":
            hn = (pkg / "hn.md").read_text(encoding="utf-8")
            link = _prefill_hn_link(post["title"], post["url"])
            reply_lines.append(f"**Hacker News** — [submit here]({link}) "
                               "(pre-filled title + URL).")
            reply_lines.append("")
            reply_lines.append("Paste this as the first comment after submitting:")
            reply_lines.append("")
            reply_lines.append("```")
            reply_lines.append(hn)
            reply_lines.append("```")
            set_channel(ps, "hn", "posted", ref="manual-submit")
        else:  # reddit
            sub = parts[2] if len(parts) > 2 else (
                post["subreddits"][0] if post.get("subreddits") else "r/sysadmin")
            reddit_file = pkg / f"reddit-{sub.replace('r/', '').replace('/', '-')}.md"
            text = (reddit_file.read_text(encoding="utf-8")
                    if reddit_file.exists() else "")
            m_title = re.search(r"\*\*Title:\*\*\n> (.+)", text)
            rtitle = m_title.group(1) if m_title else post["title"]
            try:
                ref = reddit_submit(sub, rtitle, post["url"])
                set_channel(ps, "reddit", "posted", ref=ref)
                reply_lines.append(f"✅ Posted to {sub}: {ref}")
            except (RuntimeError, OSError) as e:
                # Fall back to copy-paste + prefill link.
                link = _prefill_reddit_link(sub, rtitle, post["url"])
                reply_lines.append(f"⚠️ Reddit API unavailable ({e}).")
                reply_lines.append(f"Manual submit: [open {sub} pre-filled]({link})")
                reply_lines.append("")
                reply_lines.append("<details><summary>Title + body</summary>\n\n"
                                   f"{text}\n</details>")
                set_channel(ps, "reddit", "failed", error=str(e))

    save_state(state)
    reply = "\n\n".join(reply_lines)
    out_path = os.environ.get("GITHUB_OUTPUT")
    if out_path:
        with open(out_path, "a", encoding="utf-8") as fh:
            fh.write("reply<<PROMO_EOF\n")
            fh.write(reply + "\nPROMO_EOF\n")
    else:
        print(reply)
    return 0



# ---------------------------------------------------------------------------
# Evergreen resharing
# ---------------------------------------------------------------------------


def cmd_evergreen(args) -> int:
    """Resurface an older post on the auto channels (weekly rotation)."""
    state = load_state()
    cutoff = datetime(2000, 1, 1, tzinfo=timezone.utc)
    candidates = []
    for slug, ps in state["posts"].items():
        # Skip if any auto channel recently reshared it.
        reshared = False
        for ch in AUTO_CHANNELS:
            st = (ps.get("channels") or {}).get(ch) or {}
            if st.get("kind") == "evergreen" and st.get("at"):
                try:
                    if (now() - datetime.fromisoformat(st["at"])).days \
                            < EVERGREEN_RESHARE_DAYS:
                        reshared = True
                except ValueError:
                    pass
        if reshared:
            continue
        # Age is measured from the publish date, not the queue date, so
        # freshly-seeded historical posts are eligible immediately.
        age_src = ps.get("published_at") or ps.get("queued_at")
        try:
            qdt = datetime.fromisoformat(age_src) if age_src else cutoff
        except ValueError:
            qdt = cutoff
        age_days = (now() - qdt).days
        if age_days < EVERGREEN_MIN_AGE_DAYS:
            continue
        if not (QUEUE_DIR / slug / "package.json").exists():
            # Seeded historical post: rebuild the pitch package on demand.
            for post in iter_posts():
                if post["slug"] == slug:
                    write_package(post)
                    break
            if not (QUEUE_DIR / slug / "package.json").exists():
                continue
        candidates.append((qdt, slug, ps))

    if not candidates:
        print("evergreen: no aged candidates.")
        return 0
    # Oldest-queued first = fair rotation.
    candidates.sort()
    _, slug, ps = candidates[0]
    pkg = QUEUE_DIR / slug
    print(f"evergreen: resurfacing {slug} — {ps['title']}")

    state_local = {"last_posted": state.get("last_posted", {})}
    for channel in ("bluesky", "mastodon"):
        wait = CADENCE_HOURS - hours_since(state_local, channel)
        if wait > 0:
            print(f"evergreen: {channel} cooldown {wait:.1f}h; skipping.")
            continue
        text = (pkg / f"{channel}.txt").read_text(encoding="utf-8")
        # Prefix signals it's a reshare, not a new post.
        share_text = f"Still one of the most useful things I've written:\n\n{text}"
        if channel == "bluesky" and len(share_text) > 300:
            share_text = text  # stay within the hard limit
        try:
            if channel == "bluesky":
                ref = post_bluesky(share_text, dry_run=args.dry_run)
            else:
                ref = post_mastodon(share_text, dry_run=args.dry_run)
        except RuntimeError as e:
            print(f"evergreen: {channel} failed: {e}")
            continue
        if not args.dry_run:
            st = (ps.setdefault("channels", {}).setdefault(channel, {}))
            st.update({"status": "posted", "kind": "evergreen",
                       "at": now().isoformat(timespec="seconds"), "ref": ref})
            state["last_posted"][channel] = now().isoformat(timespec="seconds")

    if not args.dry_run:
        save_state(state)
    else:
        print("(dry-run: state not saved)")
    return 0


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main(argv=None) -> int:
    # Windows consoles default to cp1252 and choke on Unicode (→, emojis).
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except (AttributeError, OSError):
            pass
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("generate", help="queue pitch packages for new posts").add_argument(
        "--promo-days", type=int, default=14,
        help="posts newer than this get full promotion; older ones are seeded "
             "as historical (default: 14)",
    )

    sub.add_parser(
        "refresh-urls",
        help="rewrite stale URLs in already-queued packages",
    )

    p = sub.add_parser("auto-post", help="post queued content to auto channels")
    p.add_argument("--channels", default="",
                   help="comma list: bluesky,mastodon,devto (default: all)")
    p.add_argument("--force", action="store_true",
                   help="bypass the 48h cadence (manual dispatch only)")
    p.add_argument("--batch", type=int, default=0,
                   help="how many dev.to articles to publish in one run "
                        "(ignored for the social channels, which stay at one "
                        "post per run so a follower timeline is never dumped)")
    p.add_argument("--dry-run", action="store_true")

    p = sub.add_parser("issue-body", help="print tracking issue body")
    p.add_argument("--slug", required=True)

    sub.add_parser("rebuild", help="regenerate pitch packages from the posts")

    sub.add_parser("open-issues", help="create promotion issues via gh CLI")

    sub.add_parser("handle-comment", help="process /submit or /skip comment")

    p = sub.add_parser("evergreen", help="reshare an older post")
    p.add_argument("--dry-run", action="store_true")

    args = parser.parse_args(argv)
    handlers = {
        "generate": cmd_generate,
        "refresh-urls": cmd_refresh_urls,
        "rebuild": cmd_rebuild,
        "auto-post": cmd_auto_post,
        "issue-body": cmd_issue_body,
        "open-issues": cmd_open_issues,
        "handle-comment": cmd_handle_comment,
        "evergreen": cmd_evergreen,
    }
    return handlers[args.command](args)


if __name__ == "__main__":
    raise SystemExit(main())

