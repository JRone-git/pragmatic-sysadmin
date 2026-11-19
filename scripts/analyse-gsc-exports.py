#!/usr/bin/env python3
"""
Analyse the Search Console "Performance on Search" exports in
analytics/inbox/ and print the numbers used in
analytics/findings-2026-08-17.md.

Standard library only, no network, no credentials. Drop a new export into
analytics/inbox/ under a folder named after its export date and run this
again.

    python3 scripts/analyse-gsc-exports.py

Every figure in the findings file comes from here. If a number in the
prose disagrees with this script, this script is right.
"""

from __future__ import annotations

import csv
import pathlib
import re
import sys
from collections import defaultdict

ROOT = pathlib.Path(__file__).resolve().parent.parent
INBOX = ROOT / "analytics" / "inbox"

# Query themes, in priority order. Each query lands in the first bucket
# whose pattern matches, so the buckets partition the whole query list.
#
# The cloud bucket needs two conditions, not one. "cloud" alone catches
# "cloud computing" queries with no spending intent; the theme word alone
# catches the machine-generated "i'm 66+ and i spend around $124/month on
# technology" queries, which are about personal spending, not cloud.
THEMES: list[tuple[str, re.Pattern[str]]] = [
    ("cloud cost / spend", re.compile(r"cloud|azure", re.I)),
    ("password managers", re.compile(r"password|vaultwarden|bitwarden|passkey", re.I)),
    ("phones / iphone", re.compile(r"iphone|phone|android|galaxy|smartphone", re.I)),
    ("network security", re.compile(r"firewall|vpn|router|network|wi-?fi|dns", re.I)),
    ("ai troubleshooting", re.compile(r"\bai\b|chatgpt|llm|openrouter|prompt", re.I)),
    ("senior tech", re.compile(r"elderly|senior|parent|aged|accessib", re.I)),
    ("sysadmin / linux", re.compile(r"linux|systemd|kernel|shell|bash|sysadmin|server|bashbuddy", re.I)),
]

# A query only reaches the cloud bucket if it also has spending intent.
SPENDING = re.compile(
    r"cost|spend|optim|budget|waste|saving|manage|pricing|reduc|decreas|strateg", re.I
)


def read_csv(path: pathlib.Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def _num(row: dict[str, str], *keys: str) -> float:
    for key in keys:
        raw = (row.get(key) or "").strip().replace("%", "")
        try:
            return float(raw)
        except ValueError:
            continue
    return 0.0


def read_queries(folder: pathlib.Path) -> list[tuple[str, float, float, float]]:
    out = []
    for row in read_csv(folder / "Queries.csv"):
        text = (row.get("Top queries") or row.get("Query") or "").strip()
        if not text:
            continue
        impressions = _num(row, "Impressions")
        if not impressions:
            continue
        out.append(
            (
                text,
                _num(row, "Clicks"),
                impressions,
                _num(row, "Position"),
            )
        )
    return out


def read_pages(folder: pathlib.Path) -> list[tuple[str, float, float, float]]:
    out = []
    for row in read_csv(folder / "Pages.csv"):
        url = (row.get("Top pages") or row.get("Page") or "").strip()
        if not url:
            continue
        impressions = _num(row, "Impressions")
        if not impressions:
            continue
        out.append((url, _num(row, "Clicks"), impressions, _num(row, "Position")))
    return out


def read_chart(folder: pathlib.Path) -> dict[str, tuple[float, float]]:
    out = {}
    for row in read_csv(folder / "Chart.csv"):
        date = (row.get("Date") or "").strip()
        if not date:
            continue
        out[date] = (_num(row, "Clicks"), _num(row, "Impressions"))
    return out


def theme_for(query: str) -> str:
    for name, pattern in THEMES:
        if not pattern.search(query):
            continue
        if name == "cloud cost / spend" and not SPENDING.search(query):
            continue
        return name
    return "other"


def export_folders() -> list[pathlib.Path]:
    if not INBOX.exists():
        return []
    return sorted(p for p in INBOX.iterdir() if p.is_dir())


def main() -> int:
    folders = export_folders()
    if not folders:
        print(f"No exports found in {INBOX}", file=sys.stderr)
        return 1

    print(f"Exports found: {len(folders)}")
    for folder in folders:
        chart = read_chart(folder)
        span = f"{min(chart)} -> {max(chart)}" if chart else "no chart"
        print(f"  {folder.name:<28} {span}")

    latest = folders[-1]
    print(f"\n=== Query themes (from {latest.name}) ===")

    queries = read_queries(latest)
    total_impressions = sum(q[2] for q in queries)
    buckets: dict[str, list[tuple[str, float, float, float]]] = defaultdict(list)
    for q in queries:
        buckets[theme_for(q[0])].append(q)

    print(
        f"{'theme':<24}{'impr':>7}{'share':>9}{'clicks':>8}{'avg pos':>10}"
    )
    ordered = sorted(
        buckets.items(), key=lambda kv: -sum(q[2] for q in kv[1])
    )
    for name, rows in ordered:
        imps = sum(q[2] for q in rows)
        clicks = sum(q[1] for q in rows)
        pos = sum(q[3] * q[2] for q in rows) / imps if imps else 0
        share = imps / total_impressions * 100 if total_impressions else 0
        print(f"{name:<24}{imps:>7.0f}{share:>8.1f}%{clicks:>8.0f}{pos:>10.1f}")
    print(f"{'TOTAL':<24}{total_impressions:>7.0f}")

    print(f"\n=== Pages with the most impressions ({latest.name}) ===")
    for url, clicks, imps, pos in sorted(read_pages(latest), key=lambda r: -r[2])[:8]:
        print(f"  {imps:>6.0f} impr  {clicks:>3.0f} clicks  pos {pos:>6.2f}  {url[:72]}")

    print("\n=== Every click in the export ===")
    # The "Top queries" table in these exports carries no click
    # attribution - the clicks are in the Pages table. Attribute them
    # there, or the export looks like a site that never earned anything.
    clickers = [p for p in read_pages(latest) if p[1] > 0]
    for url, clicks, imps, pos in sorted(clickers, key=lambda r: -r[1]):
        print(
            f"  {clicks:>3.0f} clicks  {imps:>5.0f} impr  pos {pos:>6.2f}  {url[:64]}"
        )
    if not clickers:
        print("  (none)")
    else:
        print(
            f"  {len(clickers)} page(s), "
            f"{sum(p[1] for p in clickers):.0f} clicks in total"
        )

    print("\n=== Merged daily timeline (all exports) ===")
    merged: dict[str, tuple[float, float]] = {}
    for folder in folders:
        for date, (clicks, imps) in read_chart(folder).items():
            cur = merged.get(date, (0.0, 0.0))
            merged[date] = (max(cur[0], clicks), max(cur[1], imps))
    if merged:
        days = sorted(merged)
        print(
            f"  {days[0]} -> {days[-1]}  ({len(days)} days)  "
            f"{sum(v[0] for v in merged.values()):.0f} clicks  "
            f"{sum(v[1] for v in merged.values()):.0f} impressions"
        )
        best = max(days, key=lambda d: merged[d][1])
        print(f"  best day: {best} with {merged[best][1]:.0f} impressions")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
