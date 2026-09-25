"""Command line interface: ``python -m blogforge <command>``.

Commands are deliberately small and composable so they work the same locally,
in a terminal on Windows, and inside a GitHub Actions job:

    learn      rebuild style/voice-profile.json + style/STYLE-GUIDE.md
    lint       score a file, or the whole corpus, against the house style
    ideas      rank the topic backlog, plus things you built but never wrote up
    generate   write a draft (lint -> repair loop, always draft: true)
    providers  show which free backends are usable right now
    review     mark a draft as human-reviewed
    publish    flip draft -> published for posts whose date has arrived
    selftest   check the toolchain itself against the real corpus
"""

from __future__ import annotations

import argparse
import json
import sys
import traceback
from datetime import date
from pathlib import Path
from typing import Any

from . import corpus, generator, gitops, linter, providers, retrieve, scheduler, server, site, topics, voice

from . import corpus, generator, linter, providers, retrieve, site, topics, voice

EXIT_OK = 0
EXIT_FAIL = 1
EXIT_BAD_USAGE = 2


def out(message: str = "") -> None:
    print(message, flush=True)


def _widen_stdout() -> None:
    """Windows consoles default to cp1252; our guide has em dashes and emoji."""
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[union-attr]
        except Exception:  # noqa: BLE001 - not all streams support it
            pass


def load_profile(config: dict[str, Any]) -> dict[str, Any]:
    profile = voice.load_profile(config["profile"])
    if not profile:
        out("no style profile yet — building one from the corpus (run `learn` to cache it)")
        profile = voice.build_profile()
        voice.save_profile(profile, config["profile"])
    return profile


def brief_from_args(args: argparse.Namespace, config: dict[str, Any]) -> dict[str, Any]:
    """Turn CLI arguments into a topic brief, preferring the backlog entry."""
    data = topics.load(config["topics"])
    if getattr(args, "topic_id", None):
        topic = topics.find(data, args.topic_id)
        if not topic:
            raise SystemExit(f"no topic with id {args.topic_id!r} in {config['topics']}")
        brief = dict(topic)
    else:
        brief = {"title": args.topic or "", "section": args.section}

    if getattr(args, "topic", None):
        brief["title"] = args.topic
    if getattr(args, "section", None):
        brief["section"] = args.section
    if getattr(args, "artifact", None):
        brief["artifact"] = args.artifact
        brief.setdefault("title", f"What I learned building {Path(args.artifact).stem}")
    if getattr(args, "facts", None):
        facts_file = Path(args.facts)
        brief["facts"] = (
            facts_file.read_text(encoding="utf-8") if facts_file.exists() else str(args.facts)
        )
    if getattr(args, "tags", None):
        brief["tags"] = [t.strip() for t in args.tags.split(",") if t.strip()]
    if not str(brief.get("title") or "").strip():
        raise SystemExit("give me a topic: --topic \"...\" or --topic-id <id> (or use --artifact)")
    return brief


# --- commands ------------------------------------------------------------------


def cmd_learn(args: argparse.Namespace) -> int:
    config = site.load_config()
    posts = corpus.iter_posts()
    if not posts:
        out(f"no posts found under {site.CONTENT_DIR}")
        return EXIT_FAIL
    profile = voice.build_profile(posts)
    profile_path = voice.save_profile(profile, args.profile or config["profile"])
    guide_path = voice.write_style_guide(profile, args.guide or config["style_guide"], args.section)

    out(f"learned from {profile['post_count']} posts")
    for name, section in sorted(profile["sections"].items()):
        median_words = section["metrics"]["words"]["median"]
        out(f"  {name:12s} {section['posts']:>3} posts, median {median_words:g} words")
    out(f"wrote {profile_path.relative_to(site.ROOT)}")
    out(f"wrote {guide_path.relative_to(site.ROOT)}")

    if args.show:
        out("\n" + voice.render_style_guide(profile, args.section))
    return EXIT_OK


def cmd_lint(args: argparse.Namespace) -> int:
    config = site.load_config()
    profile = load_profile(config)
    min_score = args.min_score or int(config["min_style_score"])
    targets: list[Path] = []

    if args.all or not args.paths:
        targets = [post.path for post in corpus.iter_posts()]
        if not args.all and not args.paths:
            out("no paths given — linting the whole corpus (use --all to be explicit)")
    else:
        for raw in args.paths:
            path = Path(raw)
            if not path.is_absolute():
                path = site.ROOT / path
            targets.append(path)

    reports: list[dict[str, Any]] = []
    failures = 0
    for path in targets:
        if not path.exists():
            out(f"missing: {path}")
            failures += 1
            continue
        result = linter.lint_file(path, profile, args.section)
        passed = result.passed(min_score)
        failures += 0 if passed else 1
        reports.append(
            {
                "path": str(path.relative_to(site.ROOT)).replace("\\", "/"),
                "section": result.section,
                "score": result.score,
                "verdict": result.verdict(min_score),
                "words": result.words,
                "findings": [f.as_dict() for f in result.findings],
            }
        )
        if not args.json:
            marker = "ok  " if passed else "FAIL"
            out(f"[{marker}] {result.score:>3}/100  {path.relative_to(site.ROOT)}")
            if not passed or args.verbose:
                out(result.report(limit=args.limit))

    if args.json:
        out(json.dumps(reports, indent=2, ensure_ascii=False))
    else:
        scores = [r["score"] for r in reports]
        if len(reports) > 1:
            out(f"\n{len(reports)} files, median {sorted(scores)[len(scores) // 2]}/100, {failures} below {min_score}")
    return EXIT_OK if failures == 0 else EXIT_FAIL


def cmd_ideas(args: argparse.Namespace) -> int:
    config = site.load_config()
    posts = corpus.iter_posts()
    data = topics.load(config["topics"])
    gaps = topics.gaps(posts)

    out("corpus by section: " + ", ".join(f"{k}={v}" for k, v in gaps["sections"].items()))
    out("most-used tags: " + ", ".join(list(gaps["tags"])[:12]))

    added: list[dict[str, Any]] = []
    if args.from_artifacts or not data.get("topics"):
        added = topics.merge_new(data, topics.artifact_topics(posts))
        if added:
            topics.save(data, config["topics"])
            out(f"\nadded {len(added)} topic(s) from things built in the repo → {config['topics']}")

    ranked = topics.rank(data, posts, limit=args.count)
    if not ranked:
        out("\nno open topics. Add some to catalog/topics.yaml, or run with --from-artifacts.")
        return EXIT_OK
    out("\nranked topics:")
    for index, topic in enumerate(ranked, start=1):
        out(f"\n{index}. [{topic['score']:>5.1f}] {topic.get('title')}  ({topic.get('section')})")
        out(f"   id: {topic.get('id')}")
        for reason in topic["reasons"][:3]:
            out(f"   · {reason}")
    out("\nnext: python -m blogforge generate --topic-id <id>")
    return EXIT_OK


def cmd_providers(args: argparse.Namespace) -> int:
    config = site.load_config()
    out("provider     ready  default model                        detail")
    for entry in providers.available_providers(config):
        flag = "yes " if entry["ready"] else "no  "
        out(f"{entry['provider']:<12} {flag}  {entry['default_model']:<34} {entry['detail']}")
    auto, model = providers.resolve_provider("auto", None, config)
    out(f"\n`auto` would use: {auto}:{model}")
    out("all of these are free: Ollama runs locally, the rest are hosted free tiers.")
    return EXIT_OK


def cmd_generate(args: argparse.Namespace) -> int:
    config = site.load_config()
    posts = corpus.iter_posts()

    if args.count and args.count > 1:
        data = topics.load(config["topics"])
        ranked = topics.rank(data, posts, limit=args.count)
        if not ranked:
            out("no open topics to work from — run `python -m blogforge ideas --from-artifacts`")
            return EXIT_FAIL
        codes = [0]
        for topic in ranked:
            child = argparse.Namespace(**vars(args))
            child.topic_id = str(topic.get("id"))
            child.topic = None
            child.count = 1
            codes.append(cmd_generate(child))
        return max(codes)

    brief = brief_from_args(args, config)
    section = str(brief.get("section") or config["default_section"])
    when = date.fromisoformat(args.date) if args.date else None

    draft = generator.generate(
        brief=brief,
        section=section,
        config=config,
        provider=args.provider,
        model=args.model,
        write=not args.dry_run,
        when=when,
        posts=posts,
        progress=out,
    )

    if args.dry_run:
        out("\n--- dry run, nothing written ---\n")
        out(draft.text)
        out("--- end ---")
    out("")
    out(draft.report(int(config["min_style_score"])))

    if args.json:
        out(
            json.dumps(
                {
                    "path": str(draft.path) if draft.path else None,
                    "section": draft.section,
                    "provider": draft.provider,
                    "model": draft.model,
                    "attempts": draft.attempts,
                    "score": draft.lint.score if draft.lint else None,
                    "outline_only": draft.outline_only,
                    "duplicates": [
                        {"path": post.rel_path(), "text_overlap": shingles, "title_overlap": title}
                        for post, shingles, title in draft.duplicates
                    ],
                },
                indent=2,
                ensure_ascii=False,
            )
        )

    if draft.duplicates:
        out("\nthis overlaps existing posts — read it carefully before publishing:")
        for post, shingles, _title in draft.duplicates[:3]:
            out(f"  {post.rel_path()}  ({shingles * 100:.1f}% shared phrasing)")
        return EXIT_FAIL
    if draft.lint and not draft.lint.passed(int(config["min_style_score"])):
        return EXIT_FAIL
    return EXIT_OK


def cmd_review(args: argparse.Namespace) -> int:
    path = generator.review(args.path, approve=not args.unapprove, publish=args.publish)
    state = "reviewed" if not args.unapprove else "not reviewed"
    extra = " and published (draft: false)" if args.publish and not args.unapprove else ""
    out(f"{path.relative_to(site.ROOT)} marked {state}{extra}")
    return EXIT_OK


def cmd_publish(args: argparse.Namespace) -> int:
    config = site.load_config()
    if not args.due:
        out("nothing to do: pass --due to publish everything whose date has arrived")
        return EXIT_OK
    posts = corpus.iter_posts()
    if args.dry_run:
        for post in posts:
            if not post.draft:
                continue
            if post.ai_assisted and not post.reviewed and not args.allow_unreviewed:
                out(f"held back (awaiting review): {post.rel_path()}")
                continue
            due = site.parse_date(post.front.get("date")) or date.today()
            if due <= date.today():
                out(f"would publish: {post.rel_path()}")
        return EXIT_OK
    published = generator.publish_due(posts, allow_unreviewed=args.allow_unreviewed)
    for path in published:
        out(f"published: {path.relative_to(site.ROOT)}")
    if not published:
        out("nothing due (or everything due is still awaiting review)")
    return EXIT_OK


def cmd_selftest(args: argparse.Namespace) -> int:
    config = site.load_config()
    checks: list[tuple[str, bool, str]] = []

    def check(name: str, ok: bool, detail: str = "") -> None:
        checks.append((name, bool(ok), detail))

    posts = corpus.iter_posts()
    check("corpus loads", len(posts) > 0, f"{len(posts)} posts")

    broken = []
    for post in posts:
        reparsed, _body, _raw = corpus.split_front_matter(post.path.read_text(encoding="utf-8"))
        if not reparsed.get("title"):
            broken.append(post.rel_path())
    check("front matter parses", not broken, ", ".join(broken[:3]))

    sample_yaml = {"a": {"b": ["x", "y"], "c": "d: e"}, "l": [{"k": 1}]}
    check(
        "yaml dumps round-trips",
        corpus.yamlmini.loads(corpus.yamlmini.dumps(sample_yaml)) == sample_yaml,
    )

    profile = voice.build_profile(posts)
    check("profile builds", bool(profile.get("global", {}).get("metrics")), f"{profile['post_count']} posts")

    results = [(post, linter.lint_post(post, profile, post.section)) for post in posts]
    scores = sorted(result.score for _post, result in results)
    median = scores[len(scores) // 2] if scores else 0
    check(
        "linter calibrated to the corpus",
        median >= 70,
        f"median {median}/100 across {len(scores)} posts",
    )
    below = [post.rel_path() for post, result in results if result.score < 50]
    check("few posts score badly", len(below) <= 2, f"{len(below)} below 50")

    sample = (
        '---\ntitle: "Test Post"\ndescription: "x"\n---\n\nBody text here.\n\n'
        '<script type="application/ld+json">{"@type":"Article"}</script>\n\n'
        "[Bad link](/sysadmin/does-not-exist/) and [good](/about/).\n"
    )
    brief = {"title": "Test Post", "section": "sysadmin"}
    text, removed = generator.normalize_output(
        sample, brief, "sysadmin", "template", "outline", None, 1, posts
    )
    front, body, _raw = corpus.split_front_matter(text)
    check("duplicate JSON-LD stripped", "application/ld+json" not in body)
    check("broken internal link pruned", removed == ["/sysadmin/does-not-exist/"], str(removed))
    check("draft forced safe", front.get("draft") is True and front.get("reviewed") is False)
    check("provenance recorded", bool(front.get("blogforge")))
    check("more-tag inserted", site.MORE_TAG in body)

    updated = generator.set_frontmatter_key(text, "reviewed", "true")
    check("front matter edited in place", "reviewed: true" in updated.split("---")[1])

    outline = generator.template_outline(brief, "sysadmin", posts[:2], [("Title", "/about/")])
    check("template outline renders", "TODO(human)" in outline and site.MORE_TAG in outline)

    ready = [entry for entry in providers.available_providers(config) if entry["ready"]]
    check("a provider is available", bool(ready), ", ".join(e["provider"] for e in ready))

    out("BlogForge selftest")
    out("-" * 78)
    for name, ok, detail in checks:
        out(f"[{'PASS' if ok else 'FAIL'}] {name:34s} {detail}")
    failed = [name for name, ok, _detail in checks if not ok]
    out("-" * 78)
    out(f"{len(checks) - len(failed)}/{len(checks)} checks passed")
    return EXIT_OK if not failed else EXIT_FAIL

def cmd_ui(args: argparse.Namespace) -> int:
    server.start_server(host=args.host, port=args.port, open_browser=not args.no_browser)
    return EXIT_OK




# --- argument parsing ----------------------------------------------------------

EXAMPLES = """examples:
  python -m blogforge learn                      # learn the voice, write STYLE-GUIDE.md
  python -m blogforge lint --all                 # score every published post
  python -m blogforge ideas --from-artifacts     # what to write next
  python -m blogforge providers                  # which free backends are usable
  python -m blogforge generate --topic "The hidden cost of running Docker at home"
  python -m blogforge generate --topic-id docker-at-home --dry-run
  python -m blogforge generate --topic "Backup audit" --provider gemini --model gemini-3.8-flash
  python -m blogforge review content/sysadmin/2026-09-25-foo.md   # after you edit it
  python -m blogforge review content/sysadmin/2026-09-25-foo.md --publish
  python -m blogforge publish --due --dry-run
"""


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="blogforge",
        description="Free, style-matched blog generation for Pragmatic Tech.",
        epilog=EXAMPLES,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="command", required=True)

    learn = sub.add_parser("learn", help="learn the house voice from the corpus")
    learn.add_argument("--profile", help="where to write voice-profile.json")
    learn.add_argument("--guide", help="where to write STYLE-GUIDE.md")
    learn.add_argument("--section", help="render the guide for one section only")
    learn.add_argument("--show", action="store_true", help="print the guide as well as writing it")
    learn.set_defaults(func=cmd_learn)

    lint = sub.add_parser("lint", help="score files against the house style")
    lint.add_argument("paths", nargs="*", help="files to lint (default: the whole corpus)")
    lint.add_argument("--all", action="store_true", help="lint every post")
    lint.add_argument("--section", help="lint against another section's profile")
    lint.add_argument("--min-score", type=int, help="pass threshold (default from config)")
    lint.add_argument("--json", action="store_true", help="machine-readable output")
    lint.add_argument("--verbose", action="store_true", help="show findings for passing files too")
    lint.add_argument("--limit", type=int, default=12, help="findings to print per file")
    lint.set_defaults(func=cmd_lint)

    ideas = sub.add_parser("ideas", help="rank the topic backlog and find gaps")
    ideas.add_argument("--count", type=int, default=10)
    ideas.add_argument("--from-artifacts", action="store_true", help="also propose posts about things built here")
    ideas.set_defaults(func=cmd_ideas)

    providers_cmd = sub.add_parser("providers", help="show free backends and their state")
    providers_cmd.set_defaults(func=cmd_providers)

    gen = sub.add_parser("generate", help="write a draft (always draft: true)")
    gen.add_argument("--topic", help="the post title / brief")
    gen.add_argument("--topic-id", help="use a catalog/topics.yaml entry")
    gen.add_argument("--artifact", help="path inside the repo to read real code/facts from")
    gen.add_argument("--facts", help="file (or inline text) of verified numbers to allow")
    gen.add_argument("--tags", help="comma-separated front matter tags")
    gen.add_argument("--section", help="content section (sysadmin, senior-tech, meta)")
    gen.add_argument("--provider", help="ollama | gemini | groq | openrouter | template | auto")
    gen.add_argument("--model", help="override the provider's default model")
    gen.add_argument("--date", help="draft date (YYYY-MM-DD), defaults to today")
    gen.add_argument("--count", type=int, default=1, help="generate N drafts from the backlog")
    gen.add_argument("--dry-run", action="store_true", help="print the draft instead of writing it")
    gen.add_argument("--json", action="store_true", help="also print a JSON summary")
    gen.set_defaults(func=cmd_generate)

    review = sub.add_parser("review", help="mark a draft as human-reviewed")
    review.add_argument("path")
    review.add_argument("--unapprove", action="store_true", help="set reviewed: false again")
    review.add_argument("--publish", action="store_true", help="also set draft: false")
    review.set_defaults(func=cmd_review)

    publish = sub.add_parser("publish", help="flip draft -> published for posts that are due")
    publish.add_argument("--due", action="store_true", help="publish everything whose date has arrived")
    publish.add_argument("--dry-run", action="store_true")
    publish.add_argument("--allow-unreviewed", action="store_true", help="publish AI drafts without review (not recommended)")
    publish.set_defaults(func=cmd_publish)

    selftest = sub.add_parser("selftest", help="check the toolchain against the real corpus")
    selftest.set_defaults(func=cmd_selftest)

    ui_cmd = sub.add_parser("ui", aliases=["serve"], help="launch the BlogForge local web UI studio")
    ui_cmd.add_argument("--host", default="127.0.0.1", help="bind address (default 127.0.0.1)")
    ui_cmd.add_argument("--port", type=int, default=8000, help="port (default 8000)")
    ui_cmd.add_argument("--no-browser", action="store_true", help="do not open browser automatically")
    ui_cmd.set_defaults(func=cmd_ui)


    return parser


def main(argv: list[str] | None = None) -> int:
    _widen_stdout()
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.func(args))
    except providers.ProviderError as exc:
        out(f"\nprovider problem: {exc}")
        return EXIT_FAIL
    except KeyboardInterrupt:
        out("\ninterrupted")
        return EXIT_FAIL
    except FileNotFoundError as exc:
        out(f"\nfile not found: {exc}")
        return EXIT_FAIL
    except Exception:  # noqa: BLE001 - a crash should still explain itself
        traceback.print_exc()
        out("\nunexpected failure above — please open an issue with that trace")
        return EXIT_FAIL


