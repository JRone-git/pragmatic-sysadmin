"""Site configuration: paths, Hugo metadata and BlogForge defaults.

Everything path-shaped lives here so the rest of the package never hard-codes
assumptions about where content lives. The section list mirrors what
``scripts/generate-og-images.py`` scans, and site metadata is read from the
real ``hugo.toml`` rather than duplicated.
"""

from __future__ import annotations

import re
from datetime import date, datetime
from pathlib import Path
from typing import Any

from . import yamlmini

# --- paths --------------------------------------------------------------------

ROOT = Path(__file__).resolve().parent.parent
CONTENT_DIR = ROOT / "content"
STATIC_DIR = ROOT / "static"
OG_DIR = STATIC_DIR / "og"
CATALOG_DIR = ROOT / "catalog"
STYLE_DIR = ROOT / "style"
DOCS_DIR = ROOT / "docs"
HUGO_CONFIG = ROOT / "hugo.toml"
CONFIG_FILE = ROOT / "blogforge.yml"

#: Sections that hold blog posts, in menu order. ``posts`` is included because
#: older scripts in this repo still reference content/posts/.
BLOG_SECTIONS: tuple[str, ...] = ("sysadmin", "senior-tech", "meta", "posts")

#: Hugo's summary divider. Posts use it to control the listing excerpt.
MORE_TAG = "<!--more-->"

# --- defaults -----------------------------------------------------------------

DEFAULTS: dict[str, Any] = {
    # "auto" tries: ollama -> github (Actions token) -> gemini -> groq
    # -> openrouter -> template (no LLM).
    "provider": "auto",
    "model": None,
    "ollama_host": "http://localhost:11434",
    # Thinking models burn their token budget on reasoning and return no prose,
    # so thinking is off by default for drafting.
    "ollama_think": False,
    "attempts": 3,
    "min_style_score": 75,
    "require_review": True,
    "related_reads": 3,
    "faq": False,
    "jsonld": False,
    "target_words": {
        "sysadmin": 1600,
        "senior-tech": 1500,
        "meta": 1200,
        "_default": 1400,
    },
    "default_section": "sysadmin",
    "style_guide": "style/STYLE-GUIDE.md",
    "profile": "style/voice-profile.json",
    "topics": "catalog/topics.yaml",
    "example_posts": 3,
    "max_prompt_chars": 48000,
}

#: Free model per provider, used when ``model`` is not set. Model ids change
#: often, so override these in blogforge.yml (`model: <id>`) when a provider
#: retires one — `python -m blogforge providers` shows what is in use.
DEFAULT_MODELS: dict[str, str] = {
    "ollama": "qwen3.5:9b",
    "gemini": "gemini-3.8-flash",
    "groq": "llama-3.3-70b-versatile",
    "openrouter": "meta-llama/llama-3.3-70b-instruct:free",
    "template": "outline",
}


def site_meta() -> dict[str, str]:
    """Read the bits of hugo.toml we need (baseURL, title, author, email)."""
    meta = {
        "base_url": "https://pragmaticsysadmin.help/",
        "title": "Pragmatic Tech",
        "author": "Pragmatic Sysadmin",
        "email": "pragmatic@pragmaticsysadmin.help",
    }
    if HUGO_CONFIG.exists():
        text = HUGO_CONFIG.read_text(encoding="utf-8", errors="replace")
        for key, pattern in (
            ("base_url", r'^baseURL\s*=\s*"([^"]+)"'),
            ("title", r'^title\s*=\s*"([^"]+)"'),
        ):
            match = re.search(pattern, text, re.MULTILINE)
            if match:
                meta[key] = match.group(1)
        author_block = re.search(r"\[author\]\s*\n\s*name\s*=\s*\"([^\"]+)\"", text)
        if author_block:
            meta["author"] = author_block.group(1)
    return meta


def load_config() -> dict[str, Any]:
    """Merge ``blogforge.yml`` (if present) over :data:`DEFAULTS`."""
    config = {k: (dict(v) if isinstance(v, dict) else v) for k, v in DEFAULTS.items()}
    if CONFIG_FILE.exists():
        loaded = yamlmini.loads(CONFIG_FILE.read_text(encoding="utf-8"))
        if isinstance(loaded, dict):
            for key, value in loaded.items():
                if isinstance(value, dict) and isinstance(config.get(key), dict):
                    merged = dict(config[key])
                    merged.update(value)
                    config[key] = merged
                else:
                    config[key] = value
    return config


def resolve(path_like: str | Path) -> Path:
    """Resolve a config path relative to the repo root."""
    path = Path(path_like)
    return path if path.is_absolute() else ROOT / path


def section_dir(section: str, create: bool = False) -> Path:
    path = CONTENT_DIR / section
    if create:
        path.mkdir(parents=True, exist_ok=True)
    return path


def known_sections() -> list[str]:
    """Blog sections that exist on disk (falls back to the declared list)."""
    found = [s for s in BLOG_SECTIONS if (CONTENT_DIR / s).is_dir()]
    return found or list(BLOG_SECTIONS)


_SLUG_STRIP = re.compile(r"[^a-z0-9]+")


def slugify(text: str, max_words: int = 9) -> str:
    """Lower-case, hyphenated slug capped at ``max_words`` words."""
    cleaned = _SLUG_STRIP.sub("-", text.lower()).strip("-")
    words = [w for w in cleaned.split("-") if w]
    return "-".join(words[:max_words]) or "untitled"


def parse_date(value: Any) -> date | None:
    """Best-effort date parse for Hugo front matter in either YAML style."""
    if isinstance(value, date) and not isinstance(value, datetime):
        return value
    if isinstance(value, datetime):
        return value.date()
    text = str(value or "").strip().strip("\"'")
    if not text:
        return None
    formats = (
        "%Y-%m-%dT%H:%M:%S.%fZ",
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d",
    )
    for fmt in formats:
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue
    match = re.match(r"(\d{4})-(\d{2})-(\d{2})", text)
    if match:
        return date(int(match.group(1)), int(match.group(2)), int(match.group(3)))
    return None
