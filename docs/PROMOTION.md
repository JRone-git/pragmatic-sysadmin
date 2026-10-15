# Promotion System (Autonomous Traffic Engine)

`scripts/promote.py` turns every newly published post into platform-ready
promotion and keeps the back catalogue in rotation. Zero third-party Python
dependencies (stdlib only), matching the repo rule.

## How it flows

```
new post lands on main (content/**/*.md)
        │
        ▼  promote.yml (push + daily 08:30 UTC retry)
┌──────────────────────────────────────────────────────────┐
│ generate     → pitch package in promotion/queue/<slug>/  │
│                + state in promotion/state.json           │
│ auto-post    → Bluesky + Mastodon + dev.to (canonical)   │
│                48h cadence, 1 post/channel/run           │
│ open-issues  → GitHub issue "📣 Promote: <title>"        │
│                (label: promotion) with HN/Reddit drafts  │
└──────────────────────────────────────────────────────────┘
        │
        ▼  you comment on the issue
/promote commands (promote-approve.yml)
  /submit hn                  → replies with pre-filled HN link + body
  /submit reddit r/sysadmin   → posts via Reddit API (if secrets set),
                                 else replies with copy-paste block
  /skip hn | /skip reddit     → marks channel done, stops nagging
        │
        ▼  evergreen.yml (Wednesdays 09:00 UTC)
reshares one post older than 30 days to Bluesky/Mastodon
(oldest-first rotation, max once per post per 60 days)
```

## Why this split (hybrid design)

| Channel | Mode | Reason |
|---|---|---|
| Bluesky, Mastodon | **automatic** | Your own accounts; self-promo is expected |
| dev.to | **automatic** | Cross-post with `canonical_url` → no SEO duplicate penalty, dev.to's audience sees it |
| IndexNow (Bing/Yandex) | **automatic** | Wired into `hugo.yml` deploy (`--live` mode) |
| Hacker News | **approval** | No write API; also the highest ban-risk if auto-posted |
| Reddit | **approval** | Auto-posting self-promo gets accounts shadowbanned; approval keeps you in control of *which* subreddit and *when* |

Cadence rule (from `hacker-news-pitches.md`) is enforced in code: **at most
one post per platform per 48 hours**, tracked in `promotion/state.json`
(committed back by the workflow so it persists between runs).

## Required setup (GitHub repo → Settings → Secrets and variables → Actions)

**Automatic channels** (all optional — missing secret = that channel is
skipped with a logged reason, nothing fails):

| Secret | How to get it |
|---|---|
| `BLUESKY_HANDLE` | Your handle, e.g. `you.bsky.social` |
| `BLUESKY_APP_PASSWORD` | bsky.app → Settings → App passwords → create |
| `MASTODON_INSTANCE` | e.g. `mastodon.social` (default if unset) |
| `MASTODON_ACCESS_TOKEN` | Your instance → Settings → Development → New application → `write:statuses` scope |
| `DEVTO_API_KEY` | dev.to → Settings → Extensions → generate API key |

**Reddit API posting** (optional — without these, `/submit reddit` replies
with a copy-paste block + pre-filled link instead):

| Secret | How to get it |
|---|---|
| `REDDIT_CLIENT_ID` | old.reddit.com/prefs/apps → create app → type **script** |
| `REDDIT_CLIENT_SECRET` | shown next to the client id |
| `REDDIT_USERNAME` | your Reddit username |
| `REDDIT_PASSWORD` | your Reddit password (use a dedicated account!) |

> **Strongly recommended:** use a dedicated Reddit account for promotions,
> and read each subreddit's self-promo rules (the 10:1 rule) before your
> first `/submit`. r/sysadmin allows it if you participate beyond links.

## Local usage

```bash
python scripts/promote.py generate                # queue new posts (14-day window)
python scripts/promote.py generate --promo-days 30 # wider window
python scripts/promote.py auto-post --dry-run      # preview auto channels
python scripts/promote.py auto-post                # post for real (needs secrets)
python scripts/promote.py issue-body --slug <slug> # preview the tracking issue
python scripts/promote.py evergreen --dry-run      # preview weekly reshare
```

## Tuning knobs (top of `scripts/promote.py`)

- `CADENCE_HOURS = 48` — minimum gap per platform
- `MAX_PER_RUN = 1` — posts per auto channel per workflow run
- `SUBREDDITS` — default candidate subreddits per section; override a single
  post with `promotion_subreddits: r/foo, r/bar` in its front matter
- `EVERGREEN_MIN_AGE_DAYS` / `EVERGREEN_RESHARE_DAYS` — reshare rotation
- `--promo-days` — how fresh a post must be for full promotion on first run

## Files

- `scripts/promote.py` — the engine (all subcommands listed in `--help`)
- `.github/workflows/promote.yml` — generate + auto-post + issues
- `.github/workflows/promote-approve.yml` — `/submit` and `/skip` commands
- `.github/workflows/evergreen.yml` — weekly reshare
- `promotion/state.json` — cadence ledger (auto-committed; don't edit by hand)
- `promotion/queue/<slug>/` — generated pitches (`hn.md`, `reddit-*.md`,
  `bluesky.txt`, `mastodon.txt`, `devto.md`)

## Relationship to the existing pitch files

`hacker-news-pitches.md` and `reddit-pitches.md` are the manual playbook for
*tools* (Buddy, bashbuddy, Prism Engine). The promotion engine covers *blog
posts*. Same cadence philosophy, same tone — different pipeline.
