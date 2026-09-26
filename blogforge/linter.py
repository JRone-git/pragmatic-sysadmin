"""Style linting: score a draft against the learned voice profile.

This is the part that makes the generator useful rather than noisy. A draft is
never trusted because a model wrote it well; it is scored, and anything the
linter complains about is fed back for a rewrite. While a draft is still
``aiAssisted: true`` the linter also checks claims of first-hand experience,
because on a site whose whole promise is "tested, honest guides" an invented
"I ran this for six months" is the one unforgivable bug.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from . import corpus, site, voice
from .corpus import Post

#: Phrasings that mark text as machine-written filler. Hard failures.
AI_TELLS: tuple[tuple[str, str], ...] = (
    (r"\bit'?s not just [^.,;]{1,60}, it'?s\b", "the 'it's not just X, it's Y' construction"),
    (r"\bthis isn'?t (?:just )?about [^.,;]{1,60}\.? it'?s about\b", "the 'this isn't about X, it's about Y' construction"),
    (r"\bwhether you'?re (?:a|an) [^.,;]{1,40} or (?:a|an) [^.,;]{1,40},", "'whether you're a X or a Y'"),
    (r"\bin this (?:article|post|guide|section), (?:we|i)(?:'ll| will| am going to| are going to)\b", "the 'in this article we will' opener"),
    (r"\bby the end of this (?:article|post|guide)\b", "the 'by the end of this post' promise"),
    (r"\bin conclusion\b", "'in conclusion'"),
    (r"\bto sum(?: it)? up\b", "'to sum up'"),
    (r"\b(?:moreover|furthermore|additionally),\s", "filler transition as a sentence opener"),
    (r"\bnow you have a working\b", "the 'now you have a working X' ending"),
    (r"\bcongratulations!?\b", "'Congratulations!'"),
    (r"\bhappy (?:automating|scripting|coding|hacking|cooking)\b", "the 'Happy automating!' sign-off"),
    (r"\bready to (?:take|level up)\b", "'Ready to level up?' marketing close"),
    (r"\bremember,\s", "'Remember, ...' as advice filler"),
    (r"\blet'?s (?:dive|explore|take a look)\b", "'let's dive in'"),
    (r"\bdive (?:into|deep)\b", "'dive into' — the most over-used phrase in tech writing"),
    (r"\bin today'?s (?:fast-paced|digital|modern)\b", "'in today's fast-paced ...' opener"),
    (r"\bit'?s worth noting that\b", "'it's worth noting that'"),
    (r"\bat the end of the day\b", "'at the end of the day'"),
    (r"\bwhen it comes to\b", "'when it comes to' padding"),
    (r"\btake your [^.,;]{1,40} to the next level\b", "'take your X to the next level'"),
)

#: First-hand claims. Only checked on AI-assisted drafts, and only failed when
#: the wording is not present in the brief's verified facts.
EXPERIENCE_PATTERNS: tuple[str, ...] = (
    r"\bi (?:have )?(?:tested|tested out|benchmarked|measured|profiled|deployed|migrated|"
    r"ran|wrote|built|used) (?:this|it|that|them)\b",
    r"\bin my (?:testing|experience|lab|homelab|setup|own setup|own lab)\b",
    r"\b(?:we|i) (?:tested|measured|benchmarked|compared)\b",
    r"\bfirst[- ]hand\b",
    r"\bwe ran this for\b",
    r"\bi'?ve run this for\b",
    r"\bafter \d+ (?:days|weeks|months|years) of (?:testing|running|use|using)\b",
)

#: Generic headings the house style avoids.
GENERIC_HEADINGS = (
    "overview", "introduction", "conclusion", "summary", "background", "step 1",
    "getting started", "final thoughts", "what is", "why it matters", "key takeaways",
)

_PLACEHOLDER = re.compile(r"\b(TODO|FIXME|Lorem ipsum|\[insert|XXX|TBD)\b", re.IGNORECASE)
_EMOJI = re.compile(
    "[\U0001F300-\U0001FAFF\u2600-\u27BF\u2B00-\u2BFF\uFE0F]"
)
#: The corpus uses these as verdict markers in lists and tables (✅ Worth it,
#: ❌ Default admin passwords, ⚠️ Only if you're determined, ⭐⭐⭐⭐ ratings).
#: They are house style; anything else is decoration.
EMOJI_VERDICTS = set("✅❌⚠⭐🏆")
_INTERNAL_LINK = re.compile(r"\]\((?:/|https?://pragmaticsysadmin\.help)")
_JSONLD = re.compile(r"application/ld\+json", re.IGNORECASE)


@dataclass
class Finding:
    """A single lint observation with a concrete fix instruction."""

    rule: str
    severity: str  # "fail" | "warn"
    message: str
    fix: str = ""
    weight: float = 0.0

    def as_dict(self) -> dict:
        return {
            "rule": self.rule,
            "severity": self.severity,
            "message": self.message,
            "fix": self.fix,
        }


@dataclass
class LintResult:
    """Score plus the findings that produced it."""

    score: int
    metrics: dict = field(default_factory=dict)
    findings: list[Finding] = field(default_factory=list)
    section: str = ""
    words: int = 0

    @property
    def failures(self) -> list[Finding]:
        return [f for f in self.findings if f.severity == "fail"]

    @property
    def warnings(self) -> list[Finding]:
        return [f for f in self.findings if f.severity == "warn"]

    def passed(self, min_score: int) -> bool:
        return self.score >= min_score and not self.failures

    def verdict(self, min_score: int) -> str:
        if self.failures:
            return "NEEDS WORK"
        if self.score >= min_score:
            return "OK"
        return "MARGINAL"

    def as_dict(self) -> dict:
        return {
            "score": self.score,
            "section": self.section,
            "words": self.words,
            "metrics": self.metrics,
            "fails": len(self.failures),
            "warnings": len(self.warnings),
            "findings": [f.as_dict() for f in (self.failures + self.warnings)],
        }


    def report(self, limit: int = 12) -> str:
        lines = [f"score {self.score}/100  ({self.words} words, {len(self.failures)} fails, {len(self.warnings)} warnings)"]
        ordered = self.failures + self.warnings
        for finding in ordered[:limit]:
            marker = "FAIL" if finding.severity == "fail" else "warn"
            lines.append(f"  [{marker}] {finding.rule}: {finding.message}")
            if finding.fix:
                lines.append(f"         fix: {finding.fix}")
        if len(ordered) > limit:
            lines.append(f"  ... {len(ordered) - limit} more")
        return "\n".join(lines)

    def repair_brief(self) -> str:
        """Compact failure list used as revision instructions for the model."""
        if not self.findings:
            return ""
        parts = []
        for finding in self.failures + self.warnings:
            parts.append(f"- {finding.rule}: {finding.message}" + (f" → {finding.fix}" if finding.fix else ""))
        return "\n".join(parts)


# --- individual rule groups ----------------------------------------------------

METRIC_FIX: dict[str, str] = {
    "words": "Land near the house median. Cut padding, not substance.",
    "words_per_sentence": "Vary the rhythm: mostly short sentences, one longer qualifier per paragraph.",
    "sentences_per_paragraph": "Break up or merge paragraphs so each one carries a single idea.",
    "h2_per_1k": "Add or merge `##` sections so the post can be skimmed.",
    "code_blocks_per_1k": "Include real, copy-pasteable blocks — sysadmin posts expect them.",
    "bullets_per_1k": "Use bullets for checklists only; keep the reasoning in prose.",
    "contractions_per_1k": "Write the way you speak: don't, you're, it's, won't.",
    "first_person_per_1k": "Add the first-person view, or drop claims you cannot stand behind.",
    "second_person_per_1k": "Address the reader directly: 'your server', 'you'll see'.",
    "em_dash_per_1k": "Use the house em dash for asides — or a full stop instead.",
    "questions_per_1k": "Ask the reader a real question, or cut the rhetorical one.",
    "concrete_numbers_per_1k": "Replace adjectives with figures you can defend, or say what you would measure.",
    "tables": "One comparison table is plenty — cut the rest.",
}


def _metric_finding(name: str, label: str, value: float, stats: dict, band: list) -> Finding:
    direction = (
        f"below the accepted band ({band[0]:g}–{band[1]:g})"
        if value < band[0]
        else f"above the accepted band ({band[0]:g}–{band[1]:g})"
    )
    return Finding(
        rule=f"metric:{name}",
        severity="fail",
        message=f"{label} is {value:g}, {direction}; house median is {stats.get('median', 0):g}",
        fix=METRIC_FIX.get(name, ""),
        weight=6.0,
    )


def _check_metrics(metrics: dict, view: dict) -> list[Finding]:
    findings: list[Finding] = []
    stats_all = view.get("metrics") or {}
    bands = view.get("bands") or {}
    ideals = view.get("ideals") or {}
    for name, label in voice.BANDED:
        stats, band = stats_all.get(name), bands.get(name)
        value = metrics.get(name)
        if not stats or not band or value is None:
            continue
        if band[0] == 0 and band[1] == 0:
            continue  # the corpus has no signal for this metric
        if band[0] == 0 and value == 0:
            continue  # metric is optional for this section
        if value < band[0] or value > band[1]:
            findings.append(_metric_finding(name, label, value, stats, band))
            continue
        ideal = ideals.get(name)
        if ideal and ideal[0] != ideal[1] and (value < ideal[0] or value > ideal[1]):
            findings.append(
                Finding(
                    rule=f"metric:{name}",
                    severity="warn",
                    message=(
                        f"{label} is {value:g}, outside the typical {ideal[0]:g}–{ideal[1]:g} "
                        f"(house median {stats.get('median', 0):g})"
                    ),
                    fix=METRIC_FIX.get(name, ""),
                    weight=1.5,
                )
            )
    return findings


_WORDY = re.compile(r"[A-Za-z0-9][A-Za-z0-9'’-]{3,}")


def _sentence_around(text: str, index: int) -> str:
    start = max(text.rfind(".", 0, index), text.rfind("\n", 0, index)) + 1
    end = text.find(".", index)
    return text[start: end if end != -1 else len(text)]


def _check_phrases(post: Post, metrics: dict, allowed_facts: str | None = None) -> list[Finding]:
    findings: list[Finding] = []
    prose = post.prose()
    lowered = prose.lower()

    for pattern, label in AI_TELLS:
        match = re.search(pattern, lowered)
        if match:
            findings.append(
                Finding(
                    rule="ai-tell",
                    severity="fail",
                    message=f"uses {label}: \u201c{match.group(0).strip()[:90]}\u201d",
                    fix="Say the concrete thing directly, in the voice of the house guide.",
                    weight=7.0,
                )
            )

    hits = {w: lowered.count(w) for w in voice.BUZZWORDS if w in lowered}
    allowed = max(2, round(metrics.get("words", 1000) / 1000 * 2))
    total_hits = sum(hits.values())
    if total_hits > allowed:
        listed = ", ".join(f"{w}×{c}" for w, c in sorted(hits.items(), key=lambda kv: -kv[1])[:6])
        findings.append(
            Finding(
                rule="buzzwords",
                severity="warn" if total_hits <= allowed * 2 else "fail",
                message=f"{total_hits} hype words (about {allowed} allowed): {listed}",
                fix="Use plain words — this vocabulary does not appear in the corpus.",
                weight=2.0,
            )
        )

    if post.ai_assisted and allowed_facts is not None:
        facts = allowed_facts.lower()
        for pattern in EXPERIENCE_PATTERNS:
            match = re.search(pattern, lowered)
            if not match:
                continue
            snippet = match.group(0)
            if snippet in facts:
                continue
            sentence = _sentence_around(lowered, match.start())
            content = [w for w in _WORDY.findall(sentence)]
            if sum(1 for w in content if w in facts) >= 2:
                continue
            findings.append(
                Finding(
                    rule="fabricated-experience",
                    severity="fail",
                    message=(
                        "claims first-hand experience that is not in the verified facts: "
                        f"\u201c{snippet}\u201d"
                    ),
                    fix="Put the fact in the topic brief, attribute it ('the docs say'), or drop the claim.",
                    weight=12.0,
                )
            )
    return findings


def _check_structure(post: Post, metrics: dict, section: str) -> list[Finding]:
    findings: list[Finding] = []
    body = post.body

    if _JSONLD.search(body):
        findings.append(
            Finding(
                rule="jsonld-duplicate",
                severity="fail",
                message=(
                    "inline JSON-LD block found; layouts/partials/extend_head.html already emits "
                    "BlogPosting for this section, so search engines see two competing articles"
                ),
                fix="Delete the <script type=\"application/ld+json\"> block; only FAQPage schema belongs here.",
                weight=4.0,
            )
        )

    placeholder = _PLACEHOLDER.search(body)
    if placeholder:
        findings.append(
            Finding(
                rule="placeholder",
                severity="fail",
                message=f"unfinished placeholder text: \u201c{placeholder.group(0)}\u201d",
                fix="Replace it with real content or delete the line.",
                weight=10.0,
            )
        )

    if body.count("```") % 2:
        findings.append(
            Finding(
                rule="code-fence",
                severity="fail",
                message="unbalanced ``` fences — a code block never closes",
                fix="Close the code block.",
                weight=6.0,
            )
        )

    h2_count = len(post.headings(2))
    if h2_count < 3:
        findings.append(
            Finding(
                rule="too-few-sections",
                severity="fail",
                message=f"only {h2_count} `##` sections",
                fix="Break the post into 6-14 skimmable sections.",
                weight=5.0,
            )
        )

    if site.MORE_TAG not in body:
        findings.append(
            Finding(
                rule="missing-more-tag",
                severity="warn",
                message="no <!--more--> divider, so listings show the whole first section",
                fix="Add <!--more--> after the hook paragraphs (optional, but it keeps the listing excerpt punchy).",
                weight=1.0,
            )
        )

    description = post.description
    if not description:
        findings.append(
            Finding("frontmatter", "warn", "no description in front matter", "Write a 120-170 character promise.", 3.0)
        )
    elif not 90 <= len(description) <= 210:
        findings.append(
            Finding(
                rule="frontmatter",
                severity="warn",
                message=f"description is {len(description)} characters; aim for 120-170",
                fix="Tighten it into one sentence that makes a clear promise.",
                weight=2.0,
            )
        )

    if len(post.title) > 70:
        findings.append(
            Finding(
                rule="frontmatter",
                severity="warn",
                message=f"title is {len(post.title)} characters and will be truncated in search results",
                fix="Shorten it below 65 characters without losing the specific claim.",
                weight=2.0,
            )
        )

    if not 3 <= len(post.tags) <= 7:
        findings.append(
            Finding(
                rule="frontmatter",
                severity="warn",
                message=f"{len(post.tags)} tags; house style is 3-7",
                fix="Reuse existing tags where they fit.",
                weight=1.0,
            )
        )

    if len(_INTERNAL_LINK.findall(body)) < 2:
        findings.append(
            Finding(
                rule="few-internal-links",
                severity="warn",
                message="fewer than two links to existing posts",
                fix="Link 2-4 existing posts inline with real anchor text (it also helps them rank).",
                weight=2.0,
            )
        )

    decorative = [m.group(0) for m in _EMOJI.finditer(body) if m.group(0) not in EMOJI_VERDICTS]
    if decorative:
        unique = "".join(dict.fromkeys(decorative))
        findings.append(
            Finding(
                rule="emoji",
                severity="warn",
                message=(
                    f"decorative emoji in the body ({unique}); house style uses ✅ ❌ ⚠️ ⭐ only, "
                    "as verdict markers in lists and tables"
                ),
                fix="Delete it, or turn it into a verdict marker on a list line.",
                weight=1.0,
            )
        )

    heading_emoji = [
        m.group(0)
        for heading in post.headings(2) + post.headings(3)
        for m in _EMOJI.finditer(heading)
    ]
    if heading_emoji:
        findings.append(
            Finding(
                rule="emoji-heading",
                severity="warn",
                message=f"emoji in a heading ({''.join(heading_emoji)})",
                fix="Headings are plain text on this site.",
                weight=2.0,
            )
        )
    for heading in post.headings(2):
        cleaned = heading.strip().lower().rstrip(":.")
        if cleaned in GENERIC_HEADINGS or re.match(r"^step \d+$", cleaned):
            findings.append(
                Finding(
                    rule="generic-heading",
                    severity="warn",
                    message=f"generic heading: \u201c{heading.strip()}\u201d",
                    fix=(
                        "Make the heading a claim or a specific problem, e.g. "
                        "'The ~/.bashrc trap: commands that run every shell'."
                    ),
                    weight=2.0,
                )
            )
        elif heading.strip().endswith("."):
            findings.append(
                Finding(
                    rule="heading-punctuation",
                    severity="warn",
                    message=f"heading ends with a full stop: \u201c{heading.strip()}\u201d",
                    fix="Drop the trailing period.",
                    weight=1.0,
                )
            )

    intro = post.intro()
    if intro and len(corpus.sentences(intro)) > 5:
        findings.append(
            Finding(
                rule="intro-length",
                severity="warn",
                message=f"the opening paragraph runs {len(corpus.sentences(intro))} sentences",
                fix="Hook in 2-4 short sentences.",
                weight=2.0,
            )
        )

    if post.ai_assisted and not post.reviewed and post.front.get("draft") is not True:
        findings.append(
            Finding(
                rule="unreviewed-publish",
                severity="fail",
                message="AI-assisted post is not marked as a draft",
                fix="Set draft: true and reviewed: false until a human has edited it.",
                weight=8.0,
            )
        )
    return findings


# --- scoring and public API ----------------------------------------------------

_RULE_CAP = 12.0


def score_findings(findings: list[Finding]) -> int:
    """100 minus weighted penalties, capped per rule so one metric cannot sink a draft."""
    per_rule: dict[str, float] = {}
    for finding in findings:
        cost = finding.weight if finding.severity == "fail" else finding.weight * 0.5
        per_rule[finding.rule] = per_rule.get(finding.rule, 0.0) + cost
    penalty = sum(min(total, _RULE_CAP) for total in per_rule.values())
    return max(0, min(100, round(100 - penalty)))


def lint_post(
    post: Post,
    profile: dict,
    section: str | None = None,
    allowed_facts: str | None = None,
) -> LintResult:
    """Score a post object against the learned profile for its section."""
    section = section or post.section
    view = voice.section_profile(profile, section)
    metrics = voice.measure(post)
    findings = (
        _check_metrics(metrics, view)
        + _check_phrases(post, metrics, allowed_facts)
        + _check_structure(post, metrics, section)
    )
    findings.sort(key=lambda f: (f.severity != "fail", -f.weight))
    return LintResult(
        score=score_findings(findings),
        metrics=metrics,
        findings=findings,
        section=section,
        words=metrics.get("words", 0),
    )


def lint_text(
    text: str,
    profile: dict,
    section: str = "sysadmin",
    allowed_facts: str | None = None,
) -> LintResult:
    """Lint a draft that is still in memory."""
    return lint_post(corpus.post_from_text(text, section), profile, section, allowed_facts)


def lint_file(
    path: str | Path,
    profile: dict,
    section: str | None = None,
    allowed_facts: str | None = None,
) -> LintResult:
    target = Path(path)
    if not target.is_absolute():
        target = site.ROOT / target
    return lint_post(corpus.load_post(target), profile, section, allowed_facts)

