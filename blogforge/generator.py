"""Generation: brief in, safe draft out.

The loop is deliberately boring:

1. assemble the prompt from the style guide, the measured targets, real anchor
   posts and the brief's verified facts,
2. ask the provider for a markdown file,
3. normalise the answer (deterministic front matter, no duplicate JSON-LD,
   real links only, ``draft: true``/``reviewed: false`` provenance block),
4. lint it and, if it fails, send the linter's own complaints back as the
   revision brief,
5. check it against the corpus for near-duplicate text,
6. write it as a draft and print the score.

Nothing here can publish. Publishing is a separate, human-triggered step
(:func:`review` then :func:`publish_due`).
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

from . import corpus, linter, prompts, providers, retrieve, site, voice, yamlmini
from .corpus import Post

_JSONLD_BLOCK = re.compile(
    r'<script\s+type="application/ld\+json">.*?</script>\s*', re.DOTALL | re.IGNORECASE
)
_WRAPPING_FENCE = re.compile(r"\A```(?:markdown|md)?\s*\n(.*?)\n```\s*\Z", re.DOTALL)
_LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)\s]+)\)")
_FENCE_SPAN = re.compile(r"```.*?```|`[^`]*`", re.DOTALL)


@dataclass
class Draft:
    """A generated draft plus everything known about its quality."""

    text: str
    section: str
    slug: str
    provider: str
    model: str
    attempts: int
    lint: linter.LintResult | None = None
    duplicates: list[tuple[Post, float, float]] = field(default_factory=list)
    path: Path | None = None
    usage: dict = field(default_factory=dict)
    removed_links: list[str] = field(default_factory=list)
    outline_only: bool = False

    def report(self, min_score: int) -> str:
        lines = [
            f"{self.provider}/{self.model} → {self.section}/{self.slug}.md "
            f"({self.attempts} attempt{'s' if self.attempts != 1 else ''})"
        ]
        if self.outline_only:
            lines.append("outline only — no prose was generated, so style checks were skipped")
        elif self.lint:
            lines.append(f"style: {self.lint.verdict(min_score)} — {self.lint.report(limit=8)}")
        if self.removed_links:
            lines.append(f"removed {len(self.removed_links)} link(s) that do not resolve: "
                         + ", ".join(self.removed_links[:5]))
        if self.duplicates:
            lines.append("possible overlap with existing posts:")
            for post, shingles, title in self.duplicates[:3]:
                lines.append(f"  - {post.rel_path()} (text {shingles * 100:.1f}%, title {title * 100:.0f}%)")
        if self.path:
            lines.append(f"written: {self.path}")
            lines.append(
                "next: read it, edit it until it sounds like you, then "
                f"`python -m blogforge review {self.path}` (add --publish to go live)"
            )
        return "\n".join(lines)


# --- normalisation helpers ------------------------------------------------------


def strip_wrapping_fence(text: str) -> str:
    match = _WRAPPING_FENCE.match(text.strip())
    return match.group(1).strip() if match else text.strip()


def strip_jsonld(body: str) -> tuple[str, bool]:
    """Remove non-FAQ JSON-LD blocks (the theme already emits BlogPosting)."""
    removed = False
    while True:
        match = _JSONLD_BLOCK.search(body)
        if not match:
            break
        if "FAQPage" in match.group(0):
            break  # legitimate: keep Q&A schema, but do not duplicate twice
        body = body[: match.start()] + body[match.end():]
        removed = True
    return body, removed


def ensure_more_tag(body: str, after_paragraphs: int = 3) -> str:
    """Insert ``<!--more-->`` after the hook when the model forgot it."""
    if site.MORE_TAG in body:
        return body
    blocks = re.split(r"\n\s*\n", body.strip())
    text_blocks = [i for i, b in enumerate(blocks) if b.strip() and not b.lstrip().startswith("#")]
    if len(text_blocks) < 2:
        return body
    index = text_blocks[min(after_paragraphs, len(text_blocks)) - 1]
    blocks[index] = blocks[index].rstrip() + "\n\n" + site.MORE_TAG
    return "\n\n".join(blocks)


def known_targets(posts: list[Post]) -> set[str]:
    """URLs the draft may link to: real posts and real static pages."""
    targets = {post.url for post in posts}
    for extra in ("/", "/about/", "/shop/", "/tools/", "/newsletter/", "/resources/"):
        targets.add(extra)
    static = site.STATIC_DIR
    if static.is_dir():
        for path in static.rglob("*.html"):
            rel = path.relative_to(static).as_posix()
            targets.add(f"/{rel}")
    return targets


def fix_links(body: str, targets: set[str]) -> tuple[str, list[str]]:
    """Drop internal link markup that points at a page that does not exist."""
    removed: list[str] = []

    def replace(match: re.Match[str]) -> str:
        text, url = match.group(1), match.group(2)
        if url.startswith(("http://", "https://", "mailto:")):
            return match.group(0)
        if not url.startswith("/"):
            return match.group(0)
        normalised = url.rstrip("/") + "/"
        if normalised in targets or url in targets:
            return match.group(0)
        removed.append(url)
        return text

    # only touch prose, never code blocks
    pieces = _FENCE_SPAN.split(body)
    fences = _FENCE_SPAN.findall(body)
    out = []
    for index, piece in enumerate(pieces):
        out.append(_LINK_RE.sub(replace, piece))
        if index < len(fences):
            out.append(fences[index])
    return "".join(out), removed


# --- front matter -------------------------------------------------------------


def _first_prose_paragraph(body: str) -> str:
    for paragraph in corpus.paragraphs(body):
        cleaned = re.sub(r"\s+", " ", paragraph).strip()
        if len(cleaned) > 40:
            return cleaned
    return ""


def _description_from(body: str) -> str:
    paragraph = _first_prose_paragraph(body)
    if not paragraph:
        return ""
    sentences = corpus.sentences(paragraph)
    out = ""
    for sentence in sentences:
        if len(out) + len(sentence) > 190 and out:
            break
        out = (out + " " + sentence).strip()
    return out[:200]


def build_frontmatter(
    front: dict[str, Any],
    brief: dict[str, Any],
    provider: str,
    model: str,
    style_score: int | None,
    attempts: int,
    when: date | None = None,
) -> dict[str, Any]:
    """Deterministic, ordered front matter with provenance. Always a draft."""
    when = when or date.today()
    title = str(front.get("title") or brief.get("title") or "Untitled").strip().strip('"')
    description = str(front.get("description") or front.get("summary") or "").strip()
    tags = front.get("tags") or brief.get("tags") or []
    if isinstance(tags, str):
        tags = [tags]
    categories = front.get("categories") or brief.get("categories") or []
    if isinstance(categories, str):
        categories = [categories]

    data: dict[str, Any] = {
        "title": title,
        "date": when.isoformat(),
        "draft": True,
        "description": description,
        "tags": [str(t) for t in tags][:7],
        "categories": [str(c) for c in categories][:3],
        "author": site.site_meta()["author"],
    }
    if front.get("ShowToc"):
        data["ShowToc"] = bool(front["ShowToc"])
    data["reviewed"] = False
    data["aiAssisted"] = True
    data["blogforge"] = {
        "provider": provider,
        "model": model,
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "attempts": attempts,
        "style_score": style_score if style_score is not None else "not-linted",
        "topic": str(brief.get("id") or brief.get("title") or ""),
    }
    return data


def compose(front: dict[str, Any], body: str) -> str:
    """Serialise front matter + markdown body into a Hugo-ready file."""
    return f"---\n{yamlmini.dumps(front)}---\n\n{body.strip()}\n"


def normalize_output(
    raw: str,
    brief: dict[str, Any],
    section: str,
    provider: str,
    model: str,
    style_score: int | None,
    attempts: int,
    posts: list[Post],
    when: date | None = None,
) -> tuple[str, list[str]]:
    """Turn a model answer into the file BlogForge is willing to write."""
    text = strip_wrapping_fence(raw)
    front, body, _raw_front = corpus.split_front_matter(text)
    if not body.strip():
        body = text

    body, _removed_jsonld = strip_jsonld(body)
    body = ensure_more_tag(body)
    body, removed_links = fix_links(body, known_targets(posts))

    if not str(front.get("description") or "").strip():
        front["description"] = _description_from(body)
    front = build_frontmatter(front, brief, provider, model, style_score, attempts, when)
    return compose(front, body), removed_links


# --- writing ------------------------------------------------------------------


def draft_path(section: str, title: str, when: date | None = None, slug: str | None = None) -> Path:
    when = when or date.today()
    name = slug or site.slugify(title)
    directory = site.section_dir(section, create=True)
    candidate = directory / f"{when.isoformat()}-{name}.md"
    counter = 2
    while candidate.exists():
        candidate = directory / f"{when.isoformat()}-{name}-{counter}.md"
        counter += 1
    return candidate


def write_draft(text: str, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


# --- the no-model path ---------------------------------------------------------


def artifact_excerpt(rel_path: str | None, limit: int = 3500) -> str:
    """Read a real file from the repo so the post can quote real code."""
    if not rel_path:
        return ""
    path = site.ROOT / str(rel_path)
    if not path.exists():
        return ""
    if path.is_dir():
        files = sorted(p for p in path.rglob("*") if p.is_file() and p.suffix in {".js", ".sh", ".py", ".html", ".css", ".md"})
        chunks = []
        for file in files[:6]:
            chunks.append(f"# {file.relative_to(site.ROOT).as_posix()}\n" + file.read_text(encoding="utf-8", errors="replace")[:1500])
        return prompts.truncate("\n\n".join(chunks), limit)
    return prompts.truncate(path.read_text(encoding="utf-8", errors="replace"), limit)


def template_outline(
    brief: dict[str, Any],
    section: str,
    examples: list[Post],
    links: list[tuple[str, str]],
    artifact: str = "",
) -> str:
    """A structure-only draft, assembled without any model at all.

    Used by ``--provider template`` so the pipeline, the linter and the CI job
    can be exercised with zero cost and zero keys. Every line that needs a human
    is marked TODO(human) on purpose — this mode never pretends to write prose.
    """
    title = str(brief.get("title") or "Untitled")
    facts = str(brief.get("facts") or "").strip()
    headings = []
    for example in examples:
        for heading in example.headings(2)[:3]:
            headings.append(heading)
    headings = headings[:8] or [
        "The problem, stated plainly",
        "What I actually checked",
        "The setup that works",
        "What breaks it",
        "The tradeoff nobody mentions",
        "What to do on Monday",
    ]
    sections = [
        f"## {heading}\n\nTODO(human): one idea per section, 2-4 short sentences, "
        "concrete numbers from the brief only." for heading in headings
    ]
    body = "\n\n".join(
        [
            "TODO(human): open with a scene, a number, or a claim you are about to argue with.",
            "TODO(human): second short paragraph raising the stakes for the reader.",
            site.MORE_TAG,
            *sections,
        ]
    )
    if facts:
        body += "\n\n## Verified facts to work from\n\n" + facts
    if artifact:
        body += "\n\n## Real code available for this post\n\n```\n" + artifact + "\n```"
    if links:
        body += "\n\n*Related reads:*\n" + "\n".join(
            f"- *[{link_title}]({url})*" for link_title, url in links[:3]
        )
    return compose({"title": title, "date": date.today().isoformat()}, body)


# --- the main loop -------------------------------------------------------------


def generate(
    brief: dict[str, Any],
    section: str | None = None,
    config: dict[str, Any] | None = None,
    provider: str | None = None,
    model: str | None = None,
    write: bool = True,
    when: date | None = None,
    posts: list[Post] | None = None,
    progress=None,
) -> Draft:
    """Generate one draft from a brief, lint it, repair it, and save it."""

    def note(message: str) -> None:
        if progress:
            progress(message)

    config = config or site.load_config()
    posts = posts if posts is not None else corpus.iter_posts()
    section = section or str(brief.get("section") or config["default_section"])
    profile = voice.load_profile(config["profile"]) or voice.build_profile(posts)
    guide_file = site.resolve(config["style_guide"])
    style_guide = (
        guide_file.read_text(encoding="utf-8")
        if guide_file.exists()
        else voice.render_style_guide(profile, section)
    )
    provider_name, model_name = providers.resolve_provider(
        provider or config.get("provider"), model or config.get("model"), config
    )
    outline_only = provider_name == "template"

    topic_text = " ".join(
        [
            str(brief.get("title", "")),
            str(brief.get("angle", "")),
            " ".join(str(t) for t in (brief.get("tags") or [])),
            " ".join(str(k) for k in (brief.get("keywords") or [])),
            str(brief.get("facts", ""))[:2000],
        ]
    )
    ranked = retrieve.rank_examples(
        topic_text, posts, section, limit=int(config["example_posts"]), tags=brief.get("tags") or []
    )
    examples = [post for post, _score in ranked]
    links = [(post.title, post.url) for post, _score in ranked[: int(config["related_reads"]) + 2]]
    target_words = int(
        (config.get("target_words") or {}).get(section)
        or (config.get("target_words") or {}).get("_default", 1400)
    )
    facts = str(brief.get("facts") or "")
    artifact = artifact_excerpt(brief.get("artifact")) if brief.get("artifact") else ""
    system = prompts.system_prompt(style_guide, section)

    min_score = int(config["min_style_score"])
    max_attempts = 1 if outline_only else max(1, int(config["attempts"]))
    repair = ""
    best_raw = ""
    best_score: int | None = None
    attempts_used = 0

    for attempt in range(1, max_attempts + 1):
        attempts_used = attempt
        if outline_only:
            note("template mode: building an outline with no model")
            best_raw = template_outline(brief, section, examples, links, artifact)
            break

        note(
            f"attempt {attempt}/{max_attempts} via {provider_name}:{model_name} "
            f"({len(examples)} anchor posts, ~{target_words} words)"
        )
        prompt = prompts.user_prompt(
            brief=brief,
            example_posts=examples,
            internal_links=links,
            profile=profile,
            section=section,
            target_words=target_words,
            repair=repair,
            artifact_excerpt=artifact,
            budget=int(config["max_prompt_chars"]),
        )
        response = providers.chat(
            prompts.build_messages(system, prompt),
            provider=provider_name,
            model=model_name,
            max_tokens=max(4000, target_words * 3),
            overrides=config,
        )
        allowed = f"{facts}\n{brief.get('title', '')}\n{brief.get('angle', '')}"
        text, _links_removed = normalize_output(
            response.text, brief, section, provider_name, model_name, None, attempt, posts, when
        )
        result = linter.lint_text(text, profile, section, allowed_facts=allowed)
        note(f"attempt {attempt}: style score {result.score}/100")
        if best_score is None or result.score > best_score:
            best_raw, best_score = response.text, result.score
        if result.passed(min_score):
            break
        repair = result.repair_brief()

    text, removed_links = normalize_output(
        best_raw, brief, section, provider_name, model_name, best_score, attempts_used, posts, when
    )
    allowed = f"{facts}\n{brief.get('title', '')}\n{brief.get('angle', '')}"
    draft = Draft(
        text=text,
        section=section,
        slug=site.slugify(str(brief.get("title") or "untitled")),
        provider=provider_name,
        model=model_name,
        attempts=attempts_used,
        duplicates=retrieve.find_duplicates(text, posts),
        removed_links=removed_links,
        outline_only=outline_only,
    )
    if not outline_only:
        draft.lint = linter.lint_text(text, profile, section, allowed_facts=allowed)
    if write:
        draft.path = write_draft(
            text, draft_path(section, str(brief.get("title") or "untitled"), when)
        )
    return draft


# --- human-in-the-loop release --------------------------------------------------

_FRONT_RE = re.compile(r"\A(---\n)(?P<front>.*?)(\n---\n)", re.DOTALL)


def set_frontmatter_key(text: str, key: str, value: str) -> str:
    """Set one key in YAML front matter without reformatting the rest of the file."""
    match = _FRONT_RE.match(text)
    if not match:
        return text
    front = match.group("front")
    pattern = re.compile(rf"(?m)^{re.escape(key)}:\s*.*$")
    if pattern.search(front):
        front = pattern.sub(f"{key}: {value}", front, count=1)
    else:
        draft_pattern = re.compile(r"(?m)^draft:\s*.*$")
        if draft_pattern.search(front):
            front = draft_pattern.sub(lambda m: f"{m.group(0)}\n{key}: {value}", front, count=1)
        else:
            front = front.rstrip() + f"\n{key}: {value}"
    return match.group(1) + front + match.group(3) + text[match.end():]


def review(path: str | Path, approve: bool = True, publish: bool = False) -> Path:
    """Mark a draft as human-reviewed (and optionally ready to publish)."""
    target = Path(path)
    if not target.is_absolute():
        target = site.ROOT / target
    text = target.read_text(encoding="utf-8")
    text = set_frontmatter_key(text, "reviewed", "true" if approve else "false")
    if publish and approve:
        text = set_frontmatter_key(text, "draft", "false")
    target.write_text(text, encoding="utf-8")
    return target


def publish_due(
    posts: list[Post] | None = None,
    when: date | None = None,
    allow_unreviewed: bool = False,
) -> list[Path]:
    """Flip draft -> published for posts whose date has arrived.

    Hand-written posts (no ``aiAssisted`` flag) publish on their date exactly as
    the previous auto-publish script intended. AI-assisted posts additionally
    require ``reviewed: true``, so an unreviewed machine draft cannot go live by
    accident.
    """
    when = when or date.today()
    posts = posts if posts is not None else corpus.iter_posts()
    published: list[Path] = []
    for post in posts:
        if not post.draft:
            continue
        if post.ai_assisted and not post.reviewed and not allow_unreviewed:
            continue
        post_date = site.parse_date(post.front.get("date")) or site.parse_date(
            post.front.get("publishDate")
        )
        if post_date and post_date > when:
            continue
        text = post.path.read_text(encoding="utf-8")
        post.path.write_text(set_frontmatter_key(text, "draft", "false"), encoding="utf-8")
        published.append(post.path)
    return published


