"""Corpus loading: read the real posts, and the text maths BlogForge needs.

Everything here is read-only. The corpus is what gives BlogForge its voice:
the style profile, the few-shot examples and the duplicate detector are all
derived from these files, so no API key or cloud service is involved in
learning how Jonne writes.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

from . import site, yamlmini

__all__ = [
    "Post",
    "load_post",
    "iter_posts",
    "split_front_matter",
    "strip_markdown",
    "sentences",
    "paragraphs",
    "shingles",
    "jaccard",
    "word_count",
    "count_matches",
]

_FRONT_MATTER_RE = re.compile(
    r"\A(?P<fence>---|\+\+\+)\s*\n(?P<front>.*?)\n(?P=fence)\s*\n?", re.DOTALL
)
_SCRIPT_RE = re.compile(r"<script\b.*?</script>", re.DOTALL | re.IGNORECASE)
_STYLE_RE = re.compile(r"<style\b.*?</style>", re.DOTALL | re.IGNORECASE)
_HTML_TAG_RE = re.compile(r"<[^>]+>")
_FENCE_RE = re.compile(r"```.*?```|~~~.*?~~~", re.DOTALL)
_INLINE_CODE_RE = re.compile(r"`[^`]*`")
_IMAGE_RE = re.compile(r"!\[[^\]]*\]\([^)]*\)")
_LINK_RE = re.compile(r"\[([^\]]*)\]\([^)]*\)")
_HTML_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)
_SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])[\"')\]]*\s+")
_WORD_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9'’-]*")


def count_matches(pattern: str, text: str) -> int:
    """Number of occurrences of a case-insensitive regex in ``text``."""
    return len(re.findall(pattern, text, re.IGNORECASE))


# --- front matter -------------------------------------------------------------


def _parse_toml_front(front: str) -> dict:
    """Crude ``key = value`` reader for Hugo TOML front matter (+++)."""
    data: dict = {}
    for line in front.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        data[key.strip()] = yamlmini._parse_scalar(value)  # shared scalar rules
    return data


def split_front_matter(text: str) -> tuple[dict, str, str]:
    """Return ``(front_matter, body, raw_front_matter)``.

    YAML (``---``) and TOML (``+++``) fences are both supported because the
    repo's archetype writes TOML while every existing post is YAML.
    """
    text = text.replace("\r\n", "\n")
    match = _FRONT_MATTER_RE.match(text)
    if not match:
        return {}, text, ""
    raw_front = match.group("front")
    body = text[match.end():]
    if match.group("fence") == "+++":
        data = _parse_toml_front(raw_front)
    else:
        try:
            data = yamlmini.loads(raw_front)
        except yamlmini.YamlError:
            data = {}
    return (data if isinstance(data, dict) else {}), body, raw_front


# --- markdown helpers ---------------------------------------------------------


def strip_markdown(markdown: str) -> str:
    """Reduce markdown/HTML to prose so style metrics measure actual writing."""
    text = _SCRIPT_RE.sub(" ", markdown)
    text = _STYLE_RE.sub(" ", text)
    text = _FENCE_RE.sub(" ", text)
    text = _HTML_COMMENT_RE.sub(" ", text)
    text = _IMAGE_RE.sub(" ", text)
    text = _LINK_RE.sub(r"\1", text)
    text = _INLINE_CODE_RE.sub(" ", text)
    text = re.sub(r"^\s{0,3}#{1,6}\s*", "", text, flags=re.MULTILINE)
    text = re.sub(r"^\s*[-*+]\s+", "", text, flags=re.MULTILINE)
    text = re.sub(r"^\s*\d+[.)]\s+", "", text, flags=re.MULTILINE)
    text = re.sub(r"^\s*>\s?", "", text, flags=re.MULTILINE)
    text = re.sub(r"^\s*\|.*\|\s*$", " ", text, flags=re.MULTILINE)
    text = re.sub(r"^\s*[-:| ]{4,}\s*$", " ", text, flags=re.MULTILINE)
    text = text.replace("*", "").replace("_", "")
    return _HTML_TAG_RE.sub(" ", text)


def paragraphs(markdown: str) -> list[str]:
    """Prose paragraphs (code fences, tables, headings and lists removed)."""
    body = strip_markdown(markdown)
    blocks = [b.strip() for b in re.split(r"\n\s*\n", body)]
    return [b for b in blocks if len(_WORD_RE.findall(b)) >= 5]


def sentences(text: str) -> list[str]:
    """Rough sentence split; good enough for length statistics."""
    parts = [p.strip() for p in _SENTENCE_SPLIT_RE.split(text)]
    return [p for p in parts if len(_WORD_RE.findall(p)) >= 2]


def word_count(text: str) -> int:
    return len(_WORD_RE.findall(text))


def shingles(text: str, size: int = 5) -> set[str]:
    """Word n-grams used for duplicate detection."""
    words = [w.lower() for w in _WORD_RE.findall(strip_markdown(text))]
    if len(words) < size:
        return {" ".join(words)} if words else set()
    return {" ".join(words[i:i + size]) for i in range(len(words) - size + 1)}


def jaccard(left: Iterable[str], right: Iterable[str]) -> float:
    a, b = set(left), set(right)
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


# --- posts --------------------------------------------------------------------


@dataclass
class Post:
    """A single markdown file in one of the blog sections."""

    path: Path
    front: dict
    body: str
    raw_front: str = ""
    section: str = ""
    shingle_set: set[str] = field(default_factory=set, repr=False)

    @property
    def title(self) -> str:
        return str(self.front.get("title") or self.slug.replace("-", " ").title())

    @property
    def description(self) -> str:
        return str(self.front.get("description") or self.front.get("summary") or "")

    @property
    def slug(self) -> str:
        return self.path.stem

    @property
    def date_str(self) -> str:
        parsed = site.parse_date(self.front.get("date"))
        return parsed.isoformat() if parsed else ""

    @property
    def draft(self) -> bool:
        return bool(self.front.get("draft", False))

    @property
    def reviewed(self) -> bool:
        return bool(self.front.get("reviewed", False))

    @property
    def ai_assisted(self) -> bool:
        return bool(self.front.get("aiAssisted", False))

    @property
    def tags(self) -> list[str]:
        raw = self.front.get("tags") or []
        return [str(t) for t in raw] if isinstance(raw, list) else [str(raw)]

    @property
    def categories(self) -> list[str]:
        raw = self.front.get("categories") or []
        return [str(t) for t in raw] if isinstance(raw, list) else [str(raw)]

    @property
    def words(self) -> int:
        return word_count(strip_markdown(self.body))

    @property
    def reading_minutes(self) -> int:
        return max(1, round(self.words / 200))

    @property
    def url(self) -> str:
        return f"/{self.section}/{self.slug}/"

    @property
    def permalink(self) -> str:
        return site.site_meta()["base_url"].rstrip("/") + self.url

    def prose(self) -> str:
        return strip_markdown(self.body)

    def intro(self) -> str:
        """Text before ``<!--more-->`` (Hugo's summary), or the first paragraph.

        Leading paragraphs that merely repeat the H1/title are skipped, because
        those are heading restatements rather than hooks.
        """
        head = self.body.split(site.MORE_TAG)[0]
        title_norm = re.sub(r"[^a-z0-9]+", " ", self.title.lower()).strip()
        for paragraph in paragraphs(head):
            norm = re.sub(r"[^a-z0-9]+", " ", paragraph.lower()).strip()
            if not norm:
                continue
            if norm == title_norm:
                continue
            if len(norm) < 110 and (title_norm.startswith(norm) or norm.startswith(title_norm)):
                continue
            return paragraph
        return ""

    def closer(self) -> str:
        """Last line of prose — skips link lists, headings, tables and code."""
        skip_label = re.compile(
            r"^[*_]{0,2}(related reads|read next|further reading|sources|references|"
            r"disclosure|affiliate disclosure)[:*_ ]*$",
            re.IGNORECASE,
        )
        lines = [l.strip() for l in self.body.strip().splitlines()]
        for line in reversed(lines):
            if not line or line.startswith(("#", "|", "-", ">", "```", "<")):
                continue
            if "](" in line or skip_label.match(line):
                continue
            if line.endswith(":") and len(line.split()) <= 6:
                continue
            return line
        return ""

    def headings(self, level: int = 2) -> list[str]:
        pattern = re.compile(rf"^\s{{0,3}}{'#' * level}\s+(.*)$", re.MULTILINE)
        return [m.group(1).strip() for m in pattern.finditer(self.body)]

    def rel_path(self) -> str:
        return str(self.path.relative_to(site.ROOT)).replace("\\", "/")


def load_post(path: Path) -> Post:
    text = path.read_text(encoding="utf-8", errors="replace")
    front, body, raw_front = split_front_matter(text)
    post = Post(path=path, front=front, body=body, raw_front=raw_front, section=path.parent.name)
    post.shingle_set = shingles(body)
    return post


def post_from_text(text: str, section: str = "sysadmin", path: Path | None = None) -> Post:
    """Build a :class:`Post` from a string (a draft that is not on disk yet)."""
    front, body, raw_front = split_front_matter(text)
    post = Post(
        path=path or Path(f"draft-{section}.md"),
        front=front,
        body=body,
        raw_front=raw_front,
        section=section,
    )
    post.shingle_set = shingles(body)
    return post



def iter_posts(sections: Iterable[str] | None = None, include_drafts: bool = True) -> list[Post]:
    """Load every post in the requested sections, newest first."""
    wanted = list(sections) if sections else site.known_sections()
    posts: list[Post] = []
    for section in wanted:
        directory = site.CONTENT_DIR / section
        if not directory.is_dir():
            continue
        for path in sorted(directory.glob("*.md")):
            if path.name.startswith("_"):
                continue
            post = load_post(path)
            if not include_drafts and post.draft:
                continue
            if not post.body.strip():
                continue
            posts.append(post)
    posts.sort(key=lambda p: (p.date_str or "", p.slug), reverse=True)
    return posts

