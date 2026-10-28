"""The topic backlog — what to write next, and why.

Follows the repo's existing convention that ``catalog/`` holds the single source
of truth (like ``catalog/products.yaml`` for products). ``catalog/topics.yaml``
is human-editable; ``blogforge ideas`` re-ranks it, and ``blogforge generate
--topic-id`` uses the entry (including its ``facts``) as the brief.

The ranking is deliberately opinionated: it rewards verified facts and section
gaps, and it punishes topics that would duplicate something already published.
"""

from __future__ import annotations

from typing import Any, Iterable

from . import corpus, retrieve, site, yamlmini
from .corpus import Post

STATUSES = ("idea", "drafted", "published", "rejected")

#: Things built in this repo that a post could be written about, if none exists.
ARTIFACT_GLOBS: tuple[str, ...] = (
    "bashbuddy",
    "static/tools/*.html",
    "static/buddy",
    "static/cluster-panic",
    "static/*.html",
    "content/kids/*.md",
)


def load(path=None) -> dict[str, Any]:
    target = site.resolve(path or site.DEFAULTS["topics"])
    if not target.exists():
        return {"topics": []}
    data = yamlmini.loads(target.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        return {"topics": []}
    data.setdefault("topics", [])
    return data


def save(data: dict[str, Any], path=None):
    target = site.resolve(path or site.DEFAULTS["topics"])
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(yamlmini.dumps(data), encoding="utf-8")
    return target


def find(data: dict[str, Any], topic_id: str) -> dict[str, Any] | None:
    for topic in data.get("topics") or []:
        if str(topic.get("id")) == topic_id:
            return topic
    return None


def open_topics(data: dict[str, Any]) -> list[dict[str, Any]]:
    return [t for t in data.get("topics") or [] if str(t.get("status", "idea")) == "idea"]


def set_status(data: dict[str, Any], topic_id: str, status: str) -> bool:
    topic = find(data, topic_id)
    if not topic:
        return False
    topic["status"] = status
    return True


def gaps(posts: Iterable[Post]) -> dict[str, Any]:
    """Where the site is thin: sections, and which tags are already covered."""
    posts = list(posts)
    sections: dict[str, int] = {}
    for post in posts:
        sections[post.section] = sections.get(post.section, 0) + 1
    return {
        "sections": dict(sorted(sections.items(), key=lambda kv: kv[1])),
        "tags": retrieve.covered_tags(posts),
    }


def _score(
    topic: dict[str, Any],
    posts: list[Post],
    covered: dict[str, int],
    section_counts: dict[str, int],
) -> tuple[float, list[str]]:
    reasons: list[str] = []
    score = 10.0 * float(topic.get("priority", 2) or 0)

    section = str(topic.get("section", ""))
    total = max(1, sum(section_counts.values()))
    share = section_counts.get(section, 0) / total
    need = max(0.0, 0.35 - share) * 100
    if need:
        score += need
        reasons.append(f"{section} is {share * 100:.0f}% of the corpus, so it needs posts")

    tags = [str(t) for t in (topic.get("tags") or [])]
    fresh = [t for t in tags if t not in covered]
    if fresh:
        score += min(18.0, 6.0 * len(fresh))
        reasons.append(f"tags the site has not covered: {', '.join(fresh)}")

    if topic.get("facts"):
        score += 8.0
        reasons.append("has verified facts in the brief")

    topic_terms = retrieve.keywords(
        " ".join(
            [
                str(topic.get("title", "")),
                str(topic.get("angle", "")),
                " ".join(tags),
                " ".join(str(k) for k in (topic.get("keywords") or [])),
            ]
        )
    )
    worst = 0.0
    for post in posts:
        overlap = corpus.jaccard(topic_terms, retrieve.keywords(f"{post.title} {post.description}"))
        worst = max(worst, overlap)
    if worst >= 0.35:
        score -= 40.0
        reasons.append(f"overlaps an existing post by {worst * 100:.0f}% — pick a different angle")
    elif worst >= 0.2:
        score -= 12.0
        reasons.append(f"some overlap ({worst * 100:.0f}%) with existing posts")
    return (round(score, 2), reasons)


def rank(
    data: dict[str, Any],
    posts: list[Post],
    limit: int = 10,
    include_all: bool = False,
) -> list[dict[str, Any]]:
    """Rank backlog topics, attaching a score and human-readable reasons."""
    posts = list(posts)
    counts: dict[str, int] = {}
    for post in posts:
        counts[post.section] = counts.get(post.section, 0) + 1
    covered = retrieve.covered_tags(posts)
    candidates = (data.get("topics") or []) if include_all else open_topics(data)
    ranked: list[dict[str, Any]] = []
    for topic in candidates:
        score, reasons = _score(topic, posts, covered, counts)
        entry = dict(topic)
        entry["score"] = score
        entry["reasons"] = reasons
        ranked.append(entry)
    ranked.sort(key=lambda t: (-t["score"], str(t.get("id", ""))))
    return ranked[:limit]


_ARTIFACT_TITLES: dict[str, tuple[str, str]] = {
    "bashbuddy": ("sysadmin", "Inside bashbuddy: how the 300-line bash AI companion actually works"),
    "buddy": ("senior-tech", "How Buddy works: the free senior-companion app, one screen at a time"),
    "cluster-panic": ("meta", "Building Cluster Panic: a browser game about breaking production"),
    "melody-mixer": ("kids", "Melody Mixer: teaching music to kids with a few hundred lines of JavaScript"),
}


def artifact_topics(posts: Iterable[Post], limit: int = 8) -> list[dict[str, Any]]:
    """Suggest posts about things built in this repo that nobody wrote up yet.

    Each suggestion carries the artifact's path so the generator can read the
    real file and quote real facts instead of inventing them.
    """
    posts = list(posts)
    haystack = " ".join(
        f"{p.slug} {p.title} {p.description} {' '.join(p.tags)} {p.body[:4000]}" for p in posts
    ).lower()
    suggestions: list[dict[str, Any]] = []
    seen: set[str] = set()
    for pattern in ARTIFACT_GLOBS:
        for path in sorted(site.ROOT.glob(pattern)):
            name = path.stem if path.is_file() else path.name
            key = name.lower()
            if key in seen or key in haystack:
                continue
            seen.add(key)
            section, title = _ARTIFACT_TITLES.get(key, ("sysadmin", f"What I learned building {name}"))
            suggestions.append(
                {
                    "id": key,
                    "title": title,
                    "section": section,
                    "angle": f"Read {path.relative_to(site.ROOT).as_posix()} and write the honest build log.",
                    "artifact": path.relative_to(site.ROOT).as_posix(),
                    "status": "idea",
                    "priority": 2,
                    "tags": [],
                }
            )
    return suggestions[:limit]


def merge_new(data: dict[str, Any], suggestions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Append suggestions whose ids are not already in the backlog."""
    existing = {str(t.get("id")) for t in data.get("topics") or []}
    added = []
    for suggestion in suggestions:
        if str(suggestion.get("id")) in existing:
            continue
        data.setdefault("topics", []).append(suggestion)
        existing.add(str(suggestion.get("id")))
        added.append(suggestion)
    return added

