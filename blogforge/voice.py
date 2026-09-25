"""Voice learning: turn the existing corpus into a measurable style profile.

Two outputs, both derived from the real posts only:

* ``style/voice-profile.json`` — per-section numbers (sentence length, block
  density, contraction rate, "you"/"I" rates, em-dash rate, buzzword hits, ...)
  plus real example openers / closers / headings for few-shot prompting.
* ``style/STYLE-GUIDE.md`` — a human-readable contract containing the curated
  house rules *and* the measured numbers, so a writer (or a model) can check its
  work against reality instead of vibes.

The linter in :mod:`blogforge.linter` scores drafts against exactly these
numbers, which means generated drafts can be graded objectively and for free.
"""

from __future__ import annotations

import json
import re
import statistics
from datetime import datetime, timezone
from typing import Any

from . import corpus, site
from .corpus import Post

# --- regexes for the things we count ------------------------------------------

_CONTRACTIONS = (
    r"\b(?:isn|aren|wasn|weren|don|doesn|didn|won|can|couldn|shouldn|wouldn|hasn|haven|hadn)t\b"
    r"|\b(?:it|that|there|here|what|who|let|I|you|we|they|he|she)'(?:s|re|ve|ll|d|m)\b"
)
_FIRST_PERSON = r"\b(?:I|I've|I'm|I'd|I'll|my|mine|me)\b"
_SECOND_PERSON = r"\b(?:you|you're|you've|you'll|you'd|your|yours)\b"
_CONCRETE = (
    r"[$€]\d|\b\d+(?:[.,]\d+)?\s*"
    r"(?:%|GB|MB|TB|KB|kWh|W|hours?|minutes?|days?|weeks?|months?|years?|requests?|lines?|users?|days?)\b"
)
_QUESTION_LINE = r"(?m)^[^|\n]*\?\s*$"
_CODE_FENCE = r"```"
_BULLET = r"(?m)^\s{0,3}[-*+]\s+\S"
_TABLE_ROW = r"(?m)^\s*\|.+\|\s*$"
_TABLE_RULE = r"(?m)^\s*\|[-: |]+\|\s*$"
_CLOSING_CTA = r"^\*[^*].*\*$"

#: Consultant-speak and the phrasings language models reach for by default.
#: Almost none of these appear in the existing corpus, which is the point.
BUZZWORDS: tuple[str, ...] = (
    "leverage", "synergy", "seamless", "seamlessly", "cutting-edge", "game-changer",
    "game changer", "revolutionize", "revolutionise", "unlock the power", "empower",
    "elevate your", "delve", "fast-paced", "landscape of", "realm of", "tapestry",
    "testament to", "navigate the complexities", "dive into", "dive deep",
    "let's explore", "let's dive", "in conclusion", "to sum up", "moreover",
    "furthermore", "utilize", "utilise", "plethora", "myriad", "paradigm shift",
    "holistic", "best-in-class", "state-of-the-art", "supercharge", "turbocharge",
    "effortless", "effortlessly", "unparalleled", "pivotal", "it is important to note",
    "it's important to note", "ever-evolving", "transformative", "in the world of",
    "rest assured", "look no further", "in this article, we", "in today's",
    "the fact of the matter",
)

#: Slack applied around the measured p10/p90 range when turning it into a band.
_BAND_SLACK = 0.25


def rate(count: int, words: int, per: int = 1000) -> float:
    return round(count * per / words, 2) if words else 0.0


def measure(post: Post) -> dict[str, Any]:
    """Per-post style metrics (mostly normalised per 1000 words)."""
    prose = post.prose()
    words = max(1, corpus.word_count(prose))
    sentence_list = corpus.sentences(prose)
    paragraphs = corpus.paragraphs(post.body)
    code_blocks = len(re.findall(_CODE_FENCE, post.body)) // 2
    bullet_lines = len(re.findall(_BULLET, post.body))
    prose_lines = len([l for l in prose.splitlines() if corpus.word_count(l) >= 5])
    h2 = len(post.headings(2))
    h3 = len(post.headings(3))
    lowered = prose.lower()
    buzz_hits = {w: lowered.count(w) for w in BUZZWORDS if w in lowered}
    lengths = [corpus.word_count(s) for s in sentence_list]
    last_line = post.body.strip().splitlines()[-1].strip() if post.body.strip() else ""
    return {
        "words": words,
        "reading_minutes": post.reading_minutes,
        "words_per_sentence": round(statistics.fmean(lengths), 2) if lengths else 0.0,
        "sentences_per_paragraph": round(len(sentence_list) / len(paragraphs), 2) if paragraphs else 0.0,
        "sentences": len(sentence_list),
        "paragraphs": len(paragraphs),
        "h2": h2,
        "h3": h3,
        "h2_per_1k": rate(h2, words),
        "code_blocks": code_blocks,
        "code_blocks_per_1k": rate(code_blocks, words),
        "tables": len(re.findall(_TABLE_RULE, post.body)),
        "bullets_per_1k": rate(bullet_lines, words),
        "bullet_ratio": round(bullet_lines / (bullet_lines + prose_lines), 3) if (bullet_lines + prose_lines) else 0.0,
        "contractions_per_1k": rate(corpus.count_matches(_CONTRACTIONS, prose), words),
        "first_person_per_1k": rate(corpus.count_matches(_FIRST_PERSON, prose), words),
        "second_person_per_1k": rate(corpus.count_matches(_SECOND_PERSON, prose), words),
        "em_dash_per_1k": rate(prose.count("—"), words),
        "questions_per_1k": rate(corpus.count_matches(_QUESTION_LINE, post.body), words),
        "concrete_numbers_per_1k": rate(corpus.count_matches(_CONCRETE, prose), words),
        "buzzwords_per_1k": rate(sum(buzz_hits.values()), words),
        "has_more_tag": site.MORE_TAG in post.body,
        "has_related_reads": "related reads" in lowered,
        "has_closing_cta": bool(re.match(_CLOSING_CTA, last_line)),
        "has_jsonld": "application/ld+json" in post.body,
        "has_faq": "FAQPage" in post.body,
        "has_toc": bool(post.front.get("ShowToc")),
        "_buzz_hits": buzz_hits,
    }


#: Metrics aggregated into target bands, with the label used in the guide.
BANDED: tuple[tuple[str, str], ...] = (
    ("words", "Words per post"),
    ("reading_minutes", "Reading time (min)"),
    ("words_per_sentence", "Words per sentence"),
    ("sentences_per_paragraph", "Sentences per paragraph"),
    ("h2_per_1k", "H2 sections per 1000 words"),
    ("code_blocks_per_1k", "Code blocks per 1000 words"),
    ("bullets_per_1k", "Bullet lines per 1000 words"),
    ("tables", "Tables per post"),
    ("contractions_per_1k", "Contractions per 1000 words"),
    ("first_person_per_1k", "'I' / my per 1000 words"),
    ("second_person_per_1k", "'you' / your per 1000 words"),
    ("em_dash_per_1k", "Em dashes per 1000 words"),
    ("questions_per_1k", "Standalone questions per 1000 words"),
    ("concrete_numbers_per_1k", "Concrete figures per 1000 words"),
)

CONVENTIONS: tuple[tuple[str, str], ...] = (
    ("has_more_tag", "Uses <!--more--> summary divider"),
    ("has_related_reads", "Ends with a 'Related reads' block"),
    ("has_closing_cta", "Ends with an italic one-line closer"),
    ("has_faq", "Includes FAQPage JSON-LD"),
    ("has_jsonld", "Includes an inline JSON-LD block"),
    ("has_toc", "Sets ShowToc in front matter"),
)


def _stats(values: list[float]) -> dict[str, float]:
    if not values:
        return {}
    ordered = sorted(float(v) for v in values)

    def percentile(pct: float) -> float:
        if len(ordered) == 1:
            return ordered[0]
        index = min(len(ordered) - 1, max(0, round((len(ordered) - 1) * pct)))
        return ordered[index]

    return {
        "median": round(statistics.median(ordered), 2),
        "mean": round(statistics.fmean(ordered), 2),
        "min": round(ordered[0], 2),
        "max": round(ordered[-1], 2),
        "p10": round(percentile(0.10), 2),
        "p25": round(percentile(0.25), 2),
        "p75": round(percentile(0.75), 2),
        "p90": round(percentile(0.90), 2),
    }


def _scale(stats: dict[str, float], key: str, slack: float) -> float:
    value = stats[key]
    return 0.0 if value <= 0 else round(value * (1 + slack), 2)


def band(stats: dict[str, float]) -> list[float]:
    """Outer band (p10/p90 with slack): outside this is a style violation."""
    if not stats:
        return [0.0, 0.0]
    return [_scale(stats, "p10", -_BAND_SLACK), _scale(stats, "p90", _BAND_SLACK)]


def ideal_band(stats: dict[str, float]) -> list[float]:
    """Inner band (p25/p75): outside this is a gentle warning, not a failure."""
    if not stats:
        return [0.0, 0.0]
    return [_scale(stats, "p25", -_BAND_SLACK), _scale(stats, "p75", _BAND_SLACK)]


def _plain(line: str) -> str:
    """Strip markdown emphasis/links so examples stay readable in the guide."""
    return re.sub(r"\s+", " ", line.replace("*", "").replace("`", "")).strip()


def _summarise(posts: list[Post]) -> dict[str, Any]:
    """Aggregate one set of posts into bands, conventions and examples."""
    metrics = [measure(p) for p in posts]
    stats = {name: _stats([m[name] for m in metrics]) for name, _ in BANDED}
    bands = {name: band(stats[name]) for name, _ in BANDED}
    ideals = {name: ideal_band(stats[name]) for name, _ in BANDED}
    conventions = {
        key: round(sum(1 for m in metrics if m[key]) / len(metrics), 2) for key, _ in CONVENTIONS
    }
    buzz_hits: dict[str, int] = {}
    for metric in metrics:
        for word, count in metric["_buzz_hits"].items():
            buzz_hits[word] = buzz_hits.get(word, 0) + count

    openers, closers, headings, tags = [], [], [], {}
    for post in sorted(posts, key=lambda p: (-p.words, p.date_str)):
        if post.intro():
            openers.append({"post": post.slug, "text": _plain(post.intro())[:420]})
        closer = _plain(post.closer())
        if closer:
            closers.append({"post": post.slug, "text": closer[:280]})
        for heading in post.headings(2):
            cleaned = _plain(heading)
            if cleaned and cleaned not in headings:
                headings.append(cleaned)
        for tag in post.tags:
            tags[tag] = tags.get(tag, 0) + 1

    return {
        "posts": len(posts),
        "metrics": stats,
        "bands": bands,
        "ideals": ideals,
        "conventions": conventions,
        "buzzword_hits": dict(sorted(buzz_hits.items(), key=lambda kv: -kv[1])),
        "examples": {
            "openers": openers[:6],
            "closers": closers[:6],
            "h2": headings[:30],
        },
        "top_tags": dict(sorted(tags.items(), key=lambda kv: -kv[1])[:25]),
    }


def build_profile(posts: list[Post] | None = None) -> dict[str, Any]:
    """Build the full voice profile: global + per-section."""
    posts = posts if posts is not None else corpus.iter_posts()
    by_section: dict[str, list[Post]] = {}
    for post in posts:
        by_section.setdefault(post.section, []).append(post)
    return {
        "version": 1,
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "post_count": len(posts),
        "sections": {name: _summarise(group) for name, group in sorted(by_section.items())},
        "global": _summarise(posts),
        "buzzwords": list(BUZZWORDS),
    }


def save_profile(profile: dict[str, Any], path=None):
    target = site.resolve(path or site.STYLE_DIR / "voice-profile.json")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(profile, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return target


def load_profile(path=None) -> dict[str, Any]:
    target = site.resolve(path or site.STYLE_DIR / "voice-profile.json")
    if not target.exists():
        return {}
    return json.loads(target.read_text(encoding="utf-8"))


def section_profile(profile: dict[str, Any], section: str) -> dict[str, Any]:
    """Section profile, with global values filling any gaps."""
    global_profile = profile.get("global") or {}
    merged = dict(global_profile)
    specific = (profile.get("sections") or {}).get(section)
    if specific:
        merged.update(specific)
        for key in ("metrics", "bands", "ideals", "conventions"):
            merged[key] = {**(global_profile.get(key) or {}), **(specific.get(key) or {})}
    return merged


# --- the curated contract ------------------------------------------------------

HOUSE_RULES = """## 1. Who is writing, and for whom

The author is Jonne, a Finnish sysadmin. The brand is *Pragmatic Tech*; the
byline stays *Pragmatic Sysadmin*. Three audiences, one voice:

- **Sysadmin / IT pro** — was paged at 3 AM, wants the fix and the reasoning.
- **Adult child of an aging parent** — got voluntold into being the family IT
  department, has ten minutes and no patience for jargon.
- **Curious tinkerer** — reads the build logs, wants the honest version.

Write to one of them. Never write to "everyone".

## 2. Non-negotiables

1. **Open with a scene, a number, or a claim you are about to argue with.**
   Good: *"Every self-hosting guide starts the same way: 'Forget Dropbox, run it
   yourself and save money.' I'm going to tell you something different."*
   Good: *"The other day I spent 20 minutes debugging a cron job that worked
   perfectly when I ran it from the shell."*
   Banned opener: *"In this article, we will explore ..."*
2. **Second person, present tense.** "Your server", "you'll notice". Use first
   person for your own experience only.
3. **Short paragraphs.** Two to four sentences, one idea each. Break often.
4. **Sentence rhythm.** Mostly short and declarative, with an occasional longer
   qualifying sentence. Prefer a full stop over a comma splice.
5. **Contractions, always.** *don't, you're, it's, won't*. The only formality
   allowed is when you quote a product or an error message verbatim.
6. **Numbers beat adjectives.** "$150–250", "175.2 kWh/year", "one drive every
   3–4 years", "20W idle". If you do not have the real number, say what you would
   measure and how — do not invent one.
7. **Say the tradeoff out loud**, including when the honest answer is "just pay
   for the cloud service". Honesty is the brand: the site has no sponsored
   posts and no vendor pitches.
8. **Code blocks are real.** Copy-pasteable, commented with *why*, not *what*.
   Never invent a flag or a package name.
9. **Tables for comparisons, bullets for checklists, prose for reasoning.**
   Never bullet-point a story.
10. **H2 headings are claims or specific problems, not labels.**
    Good: *"The `~/.bashrc` trap: commands that run every shell"*, *"The Hidden
    Cost Nobody Talks About"*. Bad: *"Step 1"*, *"Overview"*.
11. **Close with a specific next action, or one direct question to the reader.**
    A short italic one-liner is the house closer. Never summarise the post back
    to the reader, and never end on *"In conclusion"* or *"Happy automating!"*.
12. **Admit uncertainty.** *"I don't have a benchmark for this"*, *"Your mileage
    will vary"*, *"I'd check this first"*. Never bluff about other people's
    environments.
13. **Never invent experience.** No "I tested this for six months" unless the
    brief's verified facts say so. Attribute anything second-hand: *"The docs
    say"*, *"community reports suggest"*.
14. **Emoji only as verdict markers.** ✅ ❌ ⚠️ and ⭐ ratings inside lists and
    tables are house style (see the tablet and network posts). Nothing
    decorative, and never in a heading.
15. **One offer, no pressure.** At most one soft funnel mention (newsletter,
    free scripts pack, Ko-fi) and only where it is genuinely relevant.
"""

HOUSE_RULES_BANNED = """
## 3. Banned: the tells of average-at-best writing

**Consultant-speak and hype** (none of these appear in the existing corpus):
leverage, synergy, seamless, cutting-edge, game-changer, revolutionize, unlock
the power of, empower, elevate, delve, tapestry, landscape of, realm of,
testament to, plethora, myriad, holistic, best-in-class, state-of-the-art,
unparalleled, pivotal, supercharge, effortless, transformative, fast-paced.

**Filler transitions**: *Moreover, Furthermore, Additionally,* as paragraph
openers. Jump to the next idea instead.

**Language-model tells**, all banned:
- *"It's not just X — it's Y"* and *"This isn't about X. It's about Y."*
- Three-adjective stacks: *"fast, reliable, and secure"*.
- *"Whether you're a beginner or an expert ..."*
- *"In this article/guide, we will ..."* and *"By the end of this post ..."*
- *"Now you have a working ..."*, *"And that's it!"*, *"Congratulations!"*
- *"Remember, ..."* as a closing paragraph.
- *"Ready to take your X to the next level?"* / *"Happy [doing thing]!"*
- Emoji-decorated bullets (🚀 💡 🎉 as decoration) — verdict markers only.
- Fake suspense: *"But here's the catch..."* used more than once per post.
- Restating the heading as the first sentence of the section.

**Vagueness instead of a number**: "generally", "usually", "quite a few",
"a lot of", "many users", "typically" — unless the claim is genuinely
unquantified, in which case say so explicitly.
"""

HOUSE_RULES_STRUCTURE = """
## 4. Structure contract

Front matter is YAML, keys in this order:

```yaml
---
title: "Plain-language title, under 65 characters, no clickbait"
date: YYYY-MM-DD
draft: true
description: "The promise of the post, 120-170 characters, written like a person
  would say it. This is the meta description and the listing snippet."
tags: ["kebab-case", "3-7 tags", "reuse existing tags where they fit"]
categories: ["System administration"]   # optional, only when it adds real value
author: "Pragmatic Sysadmin"
ShowToc: true                            # only for long procedural posts
---
```

Body:

1. **Hook** — 2-4 short paragraphs ending with `<!--more-->`. Everything above
   that marker is the summary Hugo shows in listings, so it must stand alone.
2. **Sections** — 6-14 `##` headings; use `###` only inside long procedural
   sections. Each section makes one point and stays skimmable.
3. **Internal links** — link at least two existing posts inline, with real
   anchor text (not "click here").
4. **Closer** — one short italic line, or one direct question to the reader.
5. **Related reads** — optional italic bullet list of 2-4 real posts.

Do **not** hand-write a JSON-LD block: `layouts/partials/extend_head.html`
already emits `BlogPosting` schema for the `sysadmin`, `senior-tech` and
`posts` sections, and a second block makes Google see two competing articles.
The one exception is `FAQPage` JSON-LD for senior-tech Q&A posts.

File name: `content/<section>/YYYY-MM-DD-slug.md`. Do not add a `slug:` key
unless the URL genuinely needs to differ from the file name.

## 5. Section expectations

| Section | Audience | Code blocks | Tables | FAQ schema |
|---|---|---|---|---|
| `sysadmin` | IT pros | expected — the more real code the better | common | no |
| `senior-tech` | adult children | almost none; commands only when unavoidable | common | yes, 4-6 questions |
| `meta` | followers of the build | occasional | occasional | no |

## 6. Trust rails (do not bypass)

- Drafts are written with `draft: true` and `reviewed: false`. A human edits,
  then runs `python -m blogforge review <file>` to set `reviewed: true`; only
  then may `publish --due` flip `draft: false`.
- Every generated file records which model produced it in a `blogforge:` block
  in the front matter, so provenance is never a mystery later.
- The home page currently claims *"Everything written by hand, not AI."* If
  AI-drafted posts get published, that claim has to be updated honestly — see
  `docs/BLOGFORGE.md`. Being upfront about the process is more on-brand than
  keeping the claim.
"""


def render_style_guide(profile: dict[str, Any], section: str | None = None) -> str:
    """Render STYLE-GUIDE.md: curated rules + measured fingerprint + examples."""
    view = section_profile(profile, section) if section else (profile.get("global") or {})
    metrics = view.get("metrics") or {}
    bands = view.get("bands") or {}
    conventions = view.get("conventions") or {}
    count = view.get("posts", profile.get("post_count", 0))
    where = f"the `{section}` section" if section else "the whole corpus"

    lines: list[str] = [
        "# House style — Pragmatic Tech",
        "",
        "*Generated by `python -m blogforge learn`. The curated rules live in*",
        "`blogforge/voice.py`; *the numbers below are measured from the posts and*",
        "should never be hand-edited.*",
        "",
        f"Measured from **{count} published posts** in {where}.",
        "",
        HOUSE_RULES,
        HOUSE_RULES_BANNED,
        HOUSE_RULES_STRUCTURE,
        "## 7. The measured fingerprint",
        "",
        "The linter checks drafts against these bands. Staying inside them is what",
        "makes a generated post read like the rest of the site.",
        "",
        "| Metric | Median | Accepted band | Range seen |",
        "|---|---|---|---|",
    ]
    for name, label in BANDED:
        stats = metrics.get(name) or {}
        if not stats:
            continue
        low, high = bands.get(name, [0, 0])
        lines.append(
            f"| {label} | {stats['median']:g} | {low:g} – {high:g} | {stats['min']:g} – {stats['max']:g} |"
        )
    lines += ["", "### Conventions in the published corpus", "", "| Convention | Share of posts |", "|---|---|"]
    for key, label in CONVENTIONS:
        lines.append(f"| {label} | {conventions.get(key, 0) * 100:.0f}% |")

    lines += [
        "",
        "## 8. How the existing posts actually sound",
        "",
        "Copied verbatim from the corpus. Read two of these before drafting; the",
        "rhythm is easier to match by ear than by numbers.",
        "",
    ]
    examples = view.get("examples") or {}
    if examples.get("openers"):
        lines += ["### Real opening paragraphs", ""]
        for item in examples["openers"][:4]:
            lines += [f"*{item['post']}*", "", f"> {item['text']}", ""]
    if examples.get("h2"):
        lines += ["### Real section headings", ""]
        lines += [f"- {heading}" for heading in examples["h2"][:16]]
        lines.append("")
    if examples.get("closers"):
        lines += ["### Real closers", ""]
        for item in examples["closers"][:4]:
            lines += [f"*{item['post']}*", "", f"> {item['text']}", ""]
    return "\n".join(lines) + "\n"


def write_style_guide(profile: dict[str, Any], path=None, section: str | None = None):
    target = site.resolve(path or site.STYLE_DIR / "STYLE-GUIDE.md")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(render_style_guide(profile, section), encoding="utf-8")
    return target



