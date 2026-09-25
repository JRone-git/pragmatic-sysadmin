"""Minimal YAML subset reader/writer used by BlogForge.

BlogForge ships with **zero third-party dependencies** on purpose: the whole
pipeline stays free, installs nothing, and runs on a bare GitHub Actions
runner (and on Windows) with nothing but CPython. That means no PyYAML, so
this module implements just enough YAML for the files we own:

    * Hugo front matter
    * catalog/topics.yaml (the topic backlog)
    * style/voice-profile.json is JSON, so ``json`` handles that one

Supported: nested mappings, block sequences, inline sequences, quoted and
plain scalars, booleans / ints / floats / null, ``#`` comments and ``|`` /
``>`` block scalars (with ``-`` chomping). Deliberately not supported:
anchors, aliases, tags, flow mappings, multiple documents.

Everything we parse is round-tripped by ``blogforge selftest`` against the
real content tree, so regressions here surface immediately.
"""

from __future__ import annotations

import re
from typing import Any

__all__ = ["loads", "dumps", "YamlError"]

_TRUE = {"true", "yes", "on"}
_FALSE = {"false", "no", "off"}
_NULL = {"null", "~", "none", ""}

_KEY_RE = re.compile(r"^(?P<key>[^:#][^:]*?):(?:\s+(?P<value>.*))?$")
_INT_RE = re.compile(r"^[-+]?\d+$")
_FLOAT_RE = re.compile(r"^[-+]?(?:\d+\.\d*|\.\d+|\d+)(?:[eE][-+]?\d+)?$")


class YamlError(ValueError):
    """Raised when a file uses YAML we deliberately do not support."""


# --- scalars ------------------------------------------------------------------


def _parse_scalar(text: str) -> Any:
    s = text.strip()
    if not s:
        return ""
    if len(s) >= 2 and s[0] == s[-1] and s[0] in "\"'":
        return s[1:-1]
    low = s.lower()
    if low in _TRUE:
        return True
    if low in _FALSE:
        return False
    if low in _NULL:
        return None
    if _INT_RE.match(s):
        return int(s)
    if _FLOAT_RE.match(s) and any(c in s for c in ".eE"):
        return float(s)
    return s


def _split_inline_items(inner: str) -> list[str]:
    """Split ``a, "b, c", d`` on top-level commas."""
    items: list[str] = []
    buf: list[str] = []
    quote: str | None = None
    for ch in inner:
        if quote:
            buf.append(ch)
            if ch == quote:
                quote = None
        elif ch in "\"'":
            quote = ch
            buf.append(ch)
        elif ch == ",":
            items.append("".join(buf))
            buf = []
        else:
            buf.append(ch)
    items.append("".join(buf))
    return [i for i in (x.strip() for x in items) if i != ""]


def _parse_value(text: str) -> Any:
    s = text.strip()
    if s.startswith("[") and s.endswith("]"):
        return [_parse_scalar(item) for item in _split_inline_items(s[1:-1])]
    if s.startswith("{") and s.endswith("}"):
        out: dict[str, Any] = {}
        for pair in _split_inline_items(s[1:-1]):
            key, _, val = pair.partition(":")
            out[key.strip()] = _parse_scalar(val)
        return out
    return _parse_scalar(s)


def _strip_comment(line: str) -> str:
    """Remove trailing ``#`` comments that are not inside quotes."""
    out: list[str] = []
    quote: str | None = None
    for i, ch in enumerate(line):
        if quote:
            out.append(ch)
            if ch == quote:
                quote = None
            continue
        if ch in "\"'":
            quote = ch
            out.append(ch)
        elif ch == "#" and (i == 0 or line[i - 1] in " \t"):
            break
        else:
            out.append(ch)
    return "".join(out).rstrip()


class _Reader:
    """Token stream of (indent, text) pairs with push-back support."""

    def __init__(self, lines: list[str]) -> None:
        self.lines = lines
        self.i = 0
        self._pushed: tuple[int, str] | None = None

    def peek(self) -> tuple[int, str] | None:
        if self._pushed is not None:
            return self._pushed
        if not self._advance_to_content():
            return None
        raw = self.lines[self.i]
        return len(raw) - len(raw.lstrip(" ")), _strip_comment(raw).strip()

    def pop(self) -> tuple[int, str]:
        tok = self.peek()
        if tok is None:
            raise YamlError("unexpected end of document")
        if self._pushed is not None:
            self._pushed = None
        else:
            self.i += 1
        return tok

    def push(self, token: tuple[int, str]) -> None:
        self._pushed = token

    def raw_line(self) -> str | None:
        """Next physically unconsumed content line (skips blanks/comments)."""
        if not self._advance_to_content():
            return None
        return self.lines[self.i]

    def _advance_to_content(self) -> bool:
        if self._pushed is not None:
            return True
        while self.i < len(self.lines):
            raw = self.lines[self.i]
            if not raw.strip() or _strip_comment(raw).strip() == "":
                self.i += 1
                continue
            return True
        return False


# --- structure ----------------------------------------------------------------


def _read_block_scalar(reader: _Reader, key_indent: int, fold: bool) -> str:
    body: list[str] = []
    while True:
        raw = reader.raw_line()
        if raw is None:
            break
        if not raw.strip():
            body.append("")
            reader.i += 1
            continue
        indent = len(raw) - len(raw.lstrip(" "))
        if indent <= key_indent:
            break
        body.append(raw)
        reader.i += 1
    if not body:
        return ""
    pad = min(len(l) - len(l.lstrip(" ")) for l in body if l.strip())
    lines = [l[pad:] if l.strip() else "" for l in body]
    if fold:
        return " ".join(l.strip() for l in lines).strip()
    return "\n".join(lines)


def _read_map(reader: _Reader, indent: int) -> dict[str, Any]:
    out: dict[str, Any] = {}
    while True:
        tok = reader.peek()
        if tok is None or tok[0] < indent:
            break
        if tok[0] > indent:
            raise YamlError(f"unexpected indentation at {tok[1]!r}")
        ind, text = reader.pop()
        if text == "-" or text.startswith("- "):
            raise YamlError(f"sequence item inside mapping: {text!r}")
        match = _KEY_RE.match(text)
        if not match:
            raise YamlError(f"not a mapping line: {text!r}")
        key = match.group("key").strip()
        raw_value = (match.group("value") or "").strip()
        value: Any
        if raw_value in ("|", "|-", "|+", ">", ">-", ">+"):
            value = _read_block_scalar(reader, ind, fold=raw_value.startswith(">"))
            if raw_value.endswith("-"):
                value = value.rstrip("\n")
        elif raw_value == "":
            nxt = reader.peek()
            if nxt is not None and nxt[0] > ind:
                value = _read_node(reader, nxt[0])
            else:
                value = None
        else:
            value = _parse_value(raw_value)
        out[key] = value
    return out


def _read_seq(reader: _Reader, indent: int) -> list[Any]:
    out: list[Any] = []
    while True:
        tok = reader.peek()
        if tok is None or tok[0] != indent:
            break
        ind, text = reader.pop()
        if not (text == "-" or text.startswith("- ")):
            reader.push(tok)
            break
        rest = text[1:].strip()
        if rest == "":
            nxt = reader.peek()
            out.append(_read_node(reader, nxt[0]) if nxt and nxt[0] > ind else None)
            continue
        if _KEY_RE.match(rest):
            # "- key: value" starts a mapping item; sibling keys follow at ind+2.
            reader.push((ind + 2, rest))
            out.append(_read_map(reader, ind + 2))
        else:
            out.append(_parse_value(rest))
    return out


def _read_node(reader: _Reader, indent: int) -> Any:
    tok = reader.peek()
    if tok is None:
        return {}
    if tok[1] == "-" or tok[1].startswith("- "):
        return _read_seq(reader, tok[0])
    return _read_map(reader, tok[0])


def loads(text: str) -> Any:
    """Parse a YAML-subset document into Python data."""
    reader = _Reader(text.replace("\r\n", "\n").split("\n"))
    tok = reader.peek()
    if tok is None:
        return {}
    return _read_node(reader, tok[0])


# --- writer -------------------------------------------------------------------


def _dump_scalar(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    s = str(value)
    needs_quotes = (
        s == ""
        or s != s.strip()
        or ":" in s
        or s[0] in "-?\"'#&*!|>%@`[]{}"
        or s.lower() in _TRUE | _FALSE | _NULL
    )
    if needs_quotes:
        return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'
    return s


def _dump_node(value: Any, indent: int, lines: list[str]) -> None:
    pad = " " * indent
    if isinstance(value, dict):
        for key, val in value.items():
            _dump_entry(key, val, indent, lines)
    elif isinstance(value, list):
        for item in value:
            if isinstance(item, dict) and item:
                col = indent + 2
                for index, (key, val) in enumerate(item.items()):
                    _dump_entry(key, val, col, lines, dash=(index == 0))
            elif isinstance(item, dict):
                lines.append(f"{pad}- {{}}")
            else:
                lines.append(f"{pad}- {_dump_scalar(item)}")


def _dump_entry(key: str, val: Any, col: int, lines: list[str], dash: bool = False) -> None:
    """Write ``key: value`` at column ``col``, expanding nested structures.

    ``col`` is the column the *key* starts at, so nested blocks indent from the
    key (``col + 2``) no matter how deep the surrounding structure is.
    """
    prefix = (" " * (col - 2) + "- " if dash else " " * col) + key
    child = col + 2
    if isinstance(val, list) and not val:
        lines.append(f"{prefix}: []")
    elif isinstance(val, dict) and not val:
        lines.append(f"{prefix}: {{}}")
    elif isinstance(val, (dict, list)):
        lines.append(f"{prefix}:")
        _dump_node(val, child, lines)
    elif isinstance(val, str) and "\n" in val:
        lines.append(f"{prefix}: |")
        lines.extend((" " * child + part) if part else "" for part in val.split("\n"))
    else:
        lines.append(f"{prefix}: {_dump_scalar(val)}")



def dumps(value: Any) -> str:
    """Serialise the subset BlogForge writes back (topic backlog, stubs)."""
    lines: list[str] = []
    _dump_node(value, 0, lines)
    return "\n".join(lines) + "\n"
