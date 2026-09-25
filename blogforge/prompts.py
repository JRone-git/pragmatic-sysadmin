"""Prompt construction.

The prompt is assembled from four things that all come from the repo, not from
judgement calls at runtime:

1. the curated style guide (``style/STYLE-GUIDE.md``),
2. the measured fingerprint for the target section,
3. two or three real posts from the corpus as voice anchors,
4. the topic brief — including its *verified facts*, which are the only figures
   the draft is allowed to state as first-hand experience.

The model is also given the exact output contract so its answer can be parsed
and linted without negotiation.
"""

from __future__ import annotations

from typing import Any, Iterable

from . import voice
from .corpus import Post

#: How much of each example post to include, and of the whole prompt.
EXAMPLE_CHARS = 5200
ARTIFACT_CHARS = 3500

OUTPUT_CONTRACT = """## The output contract (follow exactly)

Return **one markdown file and nothing else** — no commentary before or after,
and do not wrap the whole thing in a code fence.

```
---
title: "..."
date: YYYY-MM-DD
draft: true
description: "..."
tags: ["..."]
categories: ["..."]
author: "Pragmatic Sysadmin"
---

<hook paragraph 1>

<hook paragraph 2>

<!--more-->

## <claim-shaped heading>

...
```

Rules for the file:

- Front matter keys in that order. `draft: true`. No `slug:` key.
- No `<script type="application/ld+json">` block — the theme generates the
  BlogPosting schema itself and a second copy hurts the page.
- Include `<!--more-->` after two or three short hook paragraphs.
- 6-14 `##` sections. `###` only inside genuinely long procedures.
- Code blocks must be real, runnable and commented with *why*. If you are not
  sure a flag or package exists, leave the code out and describe the step.
- Run headers are plain sentences, no emoji, no trailing full stop.
- Inline links only to the pages listed in "Internal links you may use".
- End with one short italic line, or a direct question to the reader.
"""

GROUNDING = """## Grounding rules (a lint check enforces these)

- Numbers, prices, timings and "I tested / I ran / in my lab" claims may only
  come from **Verified facts** in the brief. If a figure is not there, write
  what you would measure and how, or say plainly that you do not have it.
- Never invent a benchmark, a price, a version number, a command flag, or a
  product capability. Attribute second-hand information ("the docs say",
  "community reports suggest").
- If the brief is thin, write a shorter, more honest post rather than padding
  it. Being visibly unsure is in-voice; bluffing is not.
- No vendor pitching, no affiliate framing in the body.
"""


def system_prompt(style_guide: str, section: str) -> str:
    """System message: who is writing, in what voice, under what contract."""
    return (
        "You are ghost-writing a blog post for Pragmatic Tech "
        "(https://pragmaticsysadmin.help), written by Jonne — a Finnish sysadmin. "
        f"The post belongs in the `{section}` section.\n\n"
        "Your only job is to sound exactly like the existing posts. You are not "
        "writing marketing copy, you are writing the honest, tested, slightly "
        "tired guide that this author would have written himself at the end of a "
        "long week. Copy the rhythm, the bluntness and the willingness to say "
        "'just pay for the cloud service' when that is the truth.\n\n"
        "Here is the house style, derived from the published corpus:\n\n"
        f"{style_guide}\n\n"
        f"{GROUNDING}\n"
        f"{OUTPUT_CONTRACT}"
    )


def metrics_table(profile: dict, section: str) -> str:
    """The measured targets for this section, as prompt-ready markdown."""
    view = voice.section_profile(profile, section)
    metrics = view.get("metrics") or {}
    ideals = view.get("ideals") or {}
    lines = ["| Metric | House median | Target for this draft |", "|---|---|---|"]
    for name, label in voice.BANDED:
        stats = metrics.get(name)
        ideal = ideals.get(name)
        if not stats or not ideal:
            continue
        if ideal[0] == ideal[1] == 0:
            continue
        lines.append(f"| {label} | {stats['median']:g} | {ideal[0]:g} to {ideal[1]:g} |")
    return "\n".join(lines)


def truncate(text: str, limit: int) -> str:
    if len(text) <= limit:
        return text
    return text[: limit - 40].rstrip() + "\n\n[...truncated for length...]"


def user_prompt(
    brief: dict[str, Any],
    example_posts: Iterable[Post],
    internal_links: Iterable[tuple[str, str]],
    profile: dict,
    section: str,
    target_words: int,
    repair: str = "",
    artifact_excerpt: str = "",
    budget: int = 48000,
) -> str:
    """User message: the brief, the targets, the anchors and any repair notes."""
    parts: list[str] = [
        f"## Topic\n\nTitle to work from: **{brief.get('title', '')}**",
        f"Section: `{section}`",
    ]
    if brief.get("angle"):
        parts.append(f"Angle / argument: {brief['angle']}")
    if brief.get("keywords"):
        parts.append("Search intent: " + ", ".join(str(k) for k in brief["keywords"]))
    if brief.get("tags"):
        parts.append(f"Front matter tags: {', '.join(str(t) for t in brief['tags'])}")

    parts.append(
        f"\n## Length target\n\nAbout **{target_words} words** of prose "
        "(plus code blocks). Shorter and specific beats long and padded."
    )

    facts = str(brief.get("facts") or "").strip()
    parts.append(
        "\n## Verified facts (the only numbers and experiences you may claim)\n\n"
        + (facts if facts else "_None supplied._ Do not state figures, prices, timings or first-hand testing at all; write what a careful sysadmin would check and why.")
    )

    if artifact_excerpt:
        parts.append(
            "\n## Real code from this project (quote from this only)\n\n"
            + f"```\n{truncate(artifact_excerpt, ARTIFACT_CHARS)}\n```"
        )

    parts.append("\n## Measured style targets for this section\n\n" + metrics_table(profile, section))

    examples = list(example_posts)
    if examples:
        parts.append("\n## Voice anchors — real published posts\n")
        for index, post in enumerate(examples, start=1):
            parts.append(
                f"\n### Anchor {index}: {post.title} (`{post.rel_path()}`)\n"
                + truncate(post.body.strip(), EXAMPLE_CHARS)
            )

    links = list(internal_links)
    if links:
        parts.append("\n## Internal links you may use (exact URLs)\n")
        for title, url in links:
            parts.append(f"- [{title}]({url})")

    if repair:
        parts.append(
            "\n## REVISION REQUIRED\n\n"
            "The previous attempt failed the house-style linter. Rewrite the whole "
            "post, keeping what is good and fixing every item below:\n\n"
            f"{repair}"
        )

    parts.append("\nWrite the post now. Output only the markdown file.")
    return _fit("\n".join(parts), budget)


def _fit(prompt: str, budget: int) -> str:
    """Keep the prompt inside the budget by dropping anchors before content."""
    if len(prompt) <= budget:
        return prompt
    marker = "\n## Voice anchors"
    head, _, _tail = prompt.partition(marker)
    links_marker = "\n## Internal links"
    links = prompt.partition(links_marker)[2]
    kept = head
    if links:
        kept += links_marker + links
    return kept[:budget] + "\n\n(Anchor posts omitted to fit the context budget.)"


def build_messages(
    system: str,
    user: str,
) -> list[dict[str, str]]:
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]

