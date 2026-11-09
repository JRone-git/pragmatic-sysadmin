#!/usr/bin/env python3
"""Tests for the promotion pipeline's channel-specific formatting.

Run:  python3 scripts/test_promote.py

Kept deliberately small and dependency-free (stdlib unittest only) so it can
run in CI, in a cron job, or on a laptop without installing anything.

The dev.to tag rules are the reason this file exists. dev.to's API rejects
any tag that is not purely alphanumeric, and it rejects it with a 422 that
reads like a server error rather than a validation message:

    422 {"error":"Tag \\"local-llm\\" contains non-alphanumeric or prohibited
    unicode characters and Tag \\"senior-tech\\" contains non-alphanumeric or
    prohibited unicode characters","status":422}

Every dev.to cross-post in promotion/state.json failed with exactly that
before scripts/promote.py learned to strip separators instead of
hyphenating them.
"""

from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SPEC = importlib.util.spec_from_file_location("promote", ROOT / "scripts" / "promote.py")
promote = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(promote)


class DevtoTags(unittest.TestCase):
    """dev.to tags must be alphanumeric-only, at most four, never empty."""

    def test_hyphens_are_stripped_not_preserved(self):
        # The bug: re.sub(r"[^a-z0-9]", "-", ...) produced "senior-tech",
        # which dev.to rejects with a 422.
        self.assertEqual(promote.devto_tags(["senior-tech"]), ["seniortech"])
        self.assertEqual(promote.devto_tags(["local-llm"]), ["localllm"])
        self.assertEqual(promote.devto_tags(["home-lab"]), ["homelab"])

    def test_every_tag_is_alphanumeric(self):
        tags = promote.devto_tags(
            ["senior-tech", "local-llm", "home-lab", "C++", "café", "e-paper"]
        )
        for tag in tags:
            with self.subTest(tag=tag):
                self.assertTrue(tag.isalnum(), f"{tag!r} is not alphanumeric")
                self.assertTrue(tag.islower() or tag.isdigit() or tag.isalpha())

    def test_at_most_four_tags(self):
        self.assertEqual(len(promote.devto_tags(["a", "b", "c", "d", "e", "f"])), 4)

    def test_duplicates_collapse(self):
        # home-lab and homelab both sanitise to "homelab"; sending both would
        # be a duplicate tag.
        self.assertEqual(promote.devto_tags(["home-lab", "homelab"]), ["homelab"])

    def test_empty_and_punctuation_only_fall_back(self):
        self.assertEqual(promote.devto_tags([]), ["sysadmin"])
        self.assertEqual(promote.devto_tags(["---", "..."]), ["sysadmin"])

    def test_tag_length_is_capped(self):
        long_tag = "x" * 80
        self.assertLessEqual(len(promote.devto_tags([long_tag])[0]), 24)

    def test_site_vocabulary_round_trips(self):
        """Every tag used on the site must produce a valid dev.to tag."""
        import re

        allowed = re.compile(r"^[a-z0-9]+$")
        seen = 0
        for section in ("sysadmin", "senior-tech", "meta", "posts"):
            directory = ROOT / "content" / section
            if not directory.is_dir():
                continue
            for path in directory.glob("*.md"):
                if path.name.startswith("_"):
                    continue
                text = path.read_text(encoding="utf-8")
                match = re.search(r"^tags:\s*\[(.*?)\]", text, re.MULTILINE)
                if not match:
                    continue
                raw = [t.strip().strip("\"'") for t in match.group(1).split(",")]
                raw = [t for t in raw if t]
                if not raw:
                    continue
                seen += 1
                for tag in promote.devto_tags(raw):
                    with self.subTest(post=path.name, tag=tag):
                        self.assertRegex(tag, allowed)
        self.assertGreater(seen, 10, "expected to find posts with tags")


class PackageGeneration(unittest.TestCase):
    """The generated devto.md front matter must be parseable by post_devto."""

    def setUp(self):
        # write_package() writes into the live promotion/queue tree. Point it at
        # a temp dir for the duration of the test, or the test stages and then
        # deletes a real promotion package.
        import tempfile

        self._tmp = tempfile.TemporaryDirectory()
        self._orig_queue = promote.QUEUE_DIR
        promote.QUEUE_DIR = Path(self._tmp.name)

    def tearDown(self):
        promote.QUEUE_DIR = self._orig_queue
        self._tmp.cleanup()

    def _real_post(self):
        """Use a real post from the repo so the dict shape is the real one."""
        for section in ("meta", "senior-tech", "sysadmin"):
            directory = ROOT / "content" / section
            if not directory.is_dir():
                continue
            for path in sorted(directory.glob("*.md")):
                if path.name.startswith("_"):
                    continue
                post = promote.parse_post(path)
                if post and post.get("tags"):
                    return post
        self.skipTest("no posts with tags found")

    def test_devto_frontmatter_round_trip(self):
        import re

        post = self._real_post()
        pkg = promote.write_package(post)
        try:
            front = (pkg / "devto.md").read_text(encoding="utf-8")
        finally:
            for child in sorted(pkg.iterdir()):
                child.unlink()
            pkg.rmdir()

        match = re.match(r"^---\n(.*?)\n---\n(.*)$", front, re.DOTALL)
        self.assertIsNotNone(match, "devto.md must have front matter")
        fm = {}
        for line in match.group(1).splitlines():
            if ":" in line:
                key, value = line.split(":", 1)
                fm[key.strip()] = value.strip()

        tags = [t.strip() for t in fm["tags"].split(",") if t.strip()]
        self.assertTrue(tags, "devto.md must carry at least one tag")
        self.assertLessEqual(len(tags), 4)
        for tag in tags:
            with self.subTest(tag=tag):
                self.assertRegex(tag, r"^[a-z0-9]+$")
        self.assertEqual(fm["canonical_url"], post["url"])
        # the same tags the helper produces, in the same order
        self.assertEqual(tags, promote.devto_tags(post["tags"]))

    def test_relative_links_are_absolutised(self):
        import re

        post = self._real_post()
        post = dict(post)
        post["slug"] = "test-relative-links"
        post["body"] = "Body with a [link](/buddy/) and an ![img](/og/x.png)."
        pkg = promote.write_package(post)
        try:
            front = (pkg / "devto.md").read_text(encoding="utf-8")
        finally:
            for child in sorted(pkg.iterdir()):
                child.unlink()
            pkg.rmdir()
        body = re.match(r"^---\n(.*?)\n---\n(.*)$", front, re.DOTALL).group(2)
        self.assertIn("https://pragmaticsysadmin.help/buddy/", body)
        self.assertIn("https://pragmaticsysadmin.help/og/x.png", body)


class PostingPath(unittest.TestCase):
    """The tags must be clean on the way OUT too, not just on the way in.

    The promotion queue already holds packages whose devto.md was written by
    the old hyphenating code. Cleaning only at write time leaves those
    packages failing forever, because post_devto() reads the tags straight
    out of the file. This is the test that would have caught that.
    """

    def setUp(self):
        import tempfile

        self._tmp = tempfile.TemporaryDirectory()
        self.pkg = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def _package_with_tags(self, tags: str):
        (self.pkg / "devto.md").write_text(
            f'---\ntitle: "A title"\ncanonical_url: https://example.com/p/\n'
            f"tags: {tags}\n---\n\nBody text.\n",
            encoding="utf-8",
        )
        return self.pkg

    def _posted_tags(self, tags: str):
        import contextlib
        import io
        import json

        pkg = self._package_with_tags(tags)
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            promote.post_devto(pkg, dry_run=True)
        line = buffer.getvalue().strip()
        payload = json.loads(line.split(": ", 1)[1].rstrip("…"))
        return payload["article"]["tags"]

    def test_hyphenated_tags_from_an_old_package_are_cleaned_on_post(self):
        posted = self._posted_tags("senior-tech, local-llm, family-tech")
        # separators are removed, not replaced: "local-llm" -> "localllm"
        self.assertEqual(posted, ["seniortech", "localllm", "familytech"])
        for tag in posted:
            self.assertTrue(tag.isalnum(), f"{tag!r} is not alphanumeric")

    def test_clean_tags_are_left_alone(self):
        self.assertEqual(self._posted_tags("sysadmin, bash"), ["sysadmin", "bash"])

    def test_posted_tags_are_never_empty(self):
        posted = self._posted_tags("---, !!!")
        self.assertTrue(posted)
        for tag in posted:
            self.assertTrue(tag.isalnum(), f"{tag!r} is not alphanumeric")


class PostUrls(unittest.TestCase):
    """The promotion URL must be the URL Hugo actually publishes.

    Hugo uses the front matter `slug:` when there is one and falls back to
    the file name when there is not. Building the URL from the file name
    alone therefore produces a 404 for every post that sets a slug - and on
    dev.to that URL is the canonical_url, so the cross-post would point
    readers at a dead link.
    """

    def setUp(self):
        import tempfile

        self._tmp = tempfile.TemporaryDirectory()
        self.content = Path(self._tmp.name) / "content"
        (self.content / "meta").mkdir(parents=True)
        self._orig_content = promote.CONTENT_DIR
        promote.CONTENT_DIR = self.content

    def tearDown(self):
        promote.CONTENT_DIR = self._orig_content
        self._tmp.cleanup()

    def _write(self, name: str, frontmatter: str):
        path = self.content / "meta" / name
        path.write_text(f"---\n{frontmatter}\n---\n\nBody.\n", encoding="utf-8")
        return path

    def test_slug_in_frontmatter_decides_the_url(self):
        path = self._write(
            "2026-11-02-hallway-display-for-my-parents-the-idea.md",
            'title: "A title"\ndate: 2026-11-02\nslug: hallway-display-for-my-parents-the-idea',
        )
        post = promote.parse_post(path)
        self.assertEqual(
            post["url"],
            "https://pragmaticsysadmin.help/meta/hallway-display-for-my-parents-the-idea/",
        )

    def test_without_a_slug_the_file_name_is_used(self):
        path = self._write(
            "2026-08-04-plain-english-explain-any-command-error-concept.md",
            'title: "A title"\ndate: 2026-08-04',
        )
        post = promote.parse_post(path)
        self.assertEqual(
            post["url"],
            "https://pragmaticsysadmin.help/meta/2026-08-04-plain-english-explain-any-command-error-concept/",
        )

    def test_refresh_urls_rewrites_a_stale_package(self):
        import json

        pkg = Path(self._tmp.name) / "queue" / "a-slug"
        pkg.mkdir(parents=True)
        old = "https://pragmaticsysadmin.help/meta/2026-11-02-a-slug/"
        new = "https://pragmaticsysadmin.help/meta/a-slug/"
        (pkg / "package.json").write_text(
            json.dumps({"slug": "a-slug", "url": old}), encoding="utf-8"
        )
        (pkg / "devto.md").write_text(f"canonical_url: {old}\n", encoding="utf-8")

        # a post whose slug is a-slug, living in the temp content dir
        self._write("2026-11-02-a-slug.md", 'title: "T"\nslug: a-slug')

        import contextlib
        import io as _io

        orig_queue = promote.QUEUE_DIR
        promote.QUEUE_DIR = Path(self._tmp.name) / "queue"
        try:
            with contextlib.redirect_stdout(_io.StringIO()):
                promote.cmd_refresh_urls(None)
        finally:
            promote.QUEUE_DIR = orig_queue

        self.assertEqual(
            json.loads((pkg / "package.json").read_text())["url"], new
        )
        self.assertIn(new, (pkg / "devto.md").read_text())
        self.assertNotIn(old, (pkg / "devto.md").read_text())


class ShortPostEligibility(unittest.TestCase):
    """A post published on dev.to owes the social channels a short post.

    "seeded" held 42 old articles back from Bluesky and Mastodon so they
    would not be blasted out at once. But the dev.to release published
    seven of them, and their short posts could never go out: the auto
    poster refused anything marked seeded, so the articles reached the
    world with no amplification at all.
    """

    def _post(self, devto_status, bluesky_status):
        return {"channels": {"devto": {"status": devto_status},
                              "bluesky": {"status": bluesky_status}}}

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self._queue = Path(self._tmp.name)
        pkg = self._queue / "a-slug"
        pkg.mkdir(parents=True)
        (pkg / "package.json").write_text("{}", encoding="utf-8")
        self._orig_queue = promote.QUEUE_DIR
        promote.QUEUE_DIR = self._queue

    def tearDown(self):
        promote.QUEUE_DIR = self._orig_queue
        self._tmp.cleanup()

    def _eligible(self, ps):
        state = {"posts": {"a-slug": ps}}
        found = [s for s, _, _ in promote._pending_posts(state, "bluesky")]
        return found == ["a-slug"]

    def test_a_seeded_post_is_not_social_posted_by_itself(self):
        self.assertFalse(self._eligible(self._post("seeded", "seeded")))

    def test_a_post_published_on_devto_owes_a_short_post(self):
        self.assertTrue(self._eligible(self._post("posted", "seeded")))

    def test_an_already_posted_post_is_not_posted_twice(self):
        self.assertFalse(self._eligible(self._post("posted", "posted")))

    def test_a_skipped_post_stays_skipped(self):
        self.assertFalse(self._eligible(self._post("posted", "skipped")))

    def test_devto_itself_still_accepts_seeded_posts(self):
        state = {"posts": {"a-slug": self._post("seeded", "seeded")}}
        found = [s for s, _, _ in promote._pending_posts(state, "devto")]
        self.assertEqual(found, ["a-slug"])


class UnicodeEscapes(unittest.TestCase):
    """A title with an em-dash must reach dev.to as an em-dash.

    json.dumps escapes non-ASCII by default, so writing a title with
    json.dumps produced the six characters \u2014. dev.to's front matter
    parser does not decode that, and the article went up with the escape
    visible in its title.
    """

    def test_a_literal_escape_is_decoded(self):
        self.assertEqual(
            promote.decode_unicode_escapes("Cloud \\u2014 The"),
            "Cloud \u2014 The",
        )

    def test_a_title_written_as_json_is_decoded(self):
        self.assertEqual(
            promote._front_title('"Cloud \\u2014 The"'),
            "Cloud \u2014 The",
        )

    def test_a_plain_title_is_left_alone(self):
        self.assertEqual(promote._front_title("Plain Title"), "Plain Title")

    def test_a_quoted_title_keeps_its_inner_quotes(self):
        self.assertEqual(
            promote._front_title('"The \"good\" guide"'),
            'The "good" guide',
        )

    def test_a_written_package_keeps_the_character(self):
        # The whole point: the file on disk must hold a real em-dash,
        # not the six characters that broke two published titles.
        tmp = tempfile.TemporaryDirectory()
        orig = promote.QUEUE_DIR
        promote.QUEUE_DIR = Path(tmp.name)
        try:
            pkg = promote.write_package({
                "slug": "cloud-guide",
                "title": "Build Your Own Cloud \u2014 The Honest Guide",
                "description": "Self-hosting without the monthly bill.",
                "url": "https://pragmaticsysadmin.help/meta/cloud-guide/",
                "tags": ["sysadmin", "self-hosting"],
                "subreddits": ["selfhosted"],
                "body": "Some body text.",
                "published_at": "2026-08-23",
            })
            front = (pkg / "devto.md").read_text(encoding="utf-8")
        finally:
            promote.QUEUE_DIR = orig
            tmp.cleanup()

        self.assertIn("\u2014", front)
        self.assertNotIn("\\u2014", front)


class TagParsing(unittest.TestCase):
    """Tags come in three YAML shapes and all three have to work.

    The parser only understood the list form, so a post written with the
    inline `tags: [a, b]` form was queued with no tags at all. That
    article then went up on dev.to with the generic "sysadmin" fallback
    tag instead of its own topic - ten of the sixteen live articles.
    """

    def _tags(self, front_matter):
        post = {
            "title": "T",
            "url": "https://example.com/x/",
            "body": "b",
            "tags": [],
            "subreddits": [],
        }
        text = f"---\n{front_matter}\n---\n\nbody\n"
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "2026-01-01-x.md"
            path.write_text(text, encoding="utf-8")
            orig = promote.CONTENT_DIR
            promote.CONTENT_DIR = Path(tmp)
            try:
                parsed = promote.parse_post(path)
            finally:
                promote.CONTENT_DIR = orig
        return parsed["tags"]

    def test_inline_array_tags(self):
        self.assertEqual(
            self._tags('title: "T"\ntags: ["seniors", "android", "iphone"]'),
            ["seniors", "android", "iphone"],
        )

    def test_inline_array_tags_with_quotes(self):
        self.assertEqual(
            self._tags("title: \"T\"\ntags: ['a', 'b']"), ["a", "b"]
        )

    def test_comma_string_tags(self):
        self.assertEqual(
            self._tags('title: "T"\ntags: seniors, android'), ["seniors", "android"]
        )

    def test_list_tags_still_work(self):
        self.assertEqual(
            self._tags('title: "T"\ntags:\n  - seniors\n  - android'),
            ["seniors", "android"],
        )

    def test_no_tags_at_all(self):
        self.assertEqual(self._tags('title: "T"'), [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
