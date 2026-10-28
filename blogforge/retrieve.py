"""Local retrieval: pick few-shot examples, and refuse near-duplicates.

No embeddings, no vector database, no API calls — just word overlap against the
posts that already exist. That is enough for the job: given a topic, find the
two or three existing posts that sound most like what the new one should sound
like, and then check that the new draft is not a rehash of one of them.
"""

from __future__ import annotations

import re
from typing import Iterable

from . import corpus
from .corpus import Post

STOPWORDS = set(
    """a about after all also am an and any are as at be because been before being
    below between both but by can cannot could did do does doing down during each
    few for from further had has have having he her here hers him his how i if in
    into is it its itself just me more most my no nor not of off on once only or
    other our out over own same she should so some such than that the their them
    then there these they this those through to too under until up very was we
    were what when where which while who whom why will with would you your yours
    it's don't you're i'm that's there's here's """.split()
)

_WORD = re.compile(r"[a-z0-9][a-z0-9'’-]{2,}")


def keywords(text: str) -> set[str]:
    """Content words, minus stopwords."""
    return {w for w in _WORD.findall(text.lower()) if w not in STOPWORDS}


def _post_terms(post: Post) -> set[str]:
    return keywords(f"{post.title} {post.description} {' '.join(post.tags)}")


def _tag_terms(post: Post) -> set[str]:
    return {t.lower() for t in post.tags}


def rank_examples(
    topic_text: str,
    posts: Iterable[Post],
    section: str | None = None,
    limit: int = 3,
    tags: Iterable[str] | None = None,
) -> list[tuple[Post, float]]:
    """Best few-shot examples for a topic, most similar first."""
    topic_terms = keywords(topic_text)
    wanted_tags = {t.lower() for t in (tags or [])}
    scored: list[tuple[Post, float]] = []
    for post in posts:
        if post.words < 200:
            continue
        score = 0.0
        score += 4.0 * len(wanted_tags & _tag_terms(post))
        score += 1.2 * len(topic_terms & _post_terms(post))
        if section and post.section == section:
            score += 2.0
        score += 6.0 * corpus.jaccard(corpus.shingles(topic_text, 4), corpus.shingles(post.prose(), 4))
        scored.append((post, round(score, 3)))
    scored.sort(key=lambda item: (-item[1], -item[0].words))
    return scored[:limit]


def find_duplicates(
    text: str,
    posts: Iterable[Post],
    shingle_threshold: float = 0.05,
) -> list[tuple[Post, float, float]]:
    """Existing posts the draft overlaps too much with.

    Returns ``(post, shingle_overlap, title_overlap)`` for anything above the
    threshold. Shingle overlap above ~5% on five-word shingles means whole
    sentences are being reused; title overlap above 0.5 means the same promise.
    """
    draft_shingles = corpus.shingles(corpus.strip_markdown(text), 5)
    draft_title = keywords(text.splitlines()[0] if text else "")
    matches: list[tuple[Post, float, float]] = []
    for post in posts:
        shingle_overlap = corpus.jaccard(draft_shingles, post.shingle_set)
        title_overlap = corpus.jaccard(draft_title, keywords(post.title))
        if shingle_overlap >= shingle_threshold or title_overlap >= 0.6:
            matches.append((post, round(shingle_overlap, 4), round(title_overlap, 3)))
    matches.sort(key=lambda item: -item[1])
    return matches


def covered_tags(posts: Iterable[Post]) -> dict[str, int]:
    """Tag -> number of posts using it, for gap analysis."""
    counts: dict[str, int] = {}
    for post in posts:
        for tag in post.tags:
            counts[tag] = counts.get(tag, 0) + 1
    return dict(sorted(counts.items(), key=lambda kv: -kv[1]))
