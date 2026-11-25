#!/usr/bin/env python3
"""Check whether the Rakuten Automate widget on the site actually affiliates a link.

The widget rewrites outbound links on click. When it works, the click goes
through automate.linksynergy.com and then to a deep link carrying the
publisher id and the advertiser mid, so the sale is attributed. When it
does not work, the reader is redirected to the plain URL and nothing is
attributed - and nothing on the site complains.

That failure is silent, which is why it needs a probe. This script loads a
throwaway page carrying the real widget snippet, clicks one link per
candidate domain, and reports what the widget did with each one.

Usage:
    python3 scripts/check-rakuten-widget.py                 # default probe set
    python3 scripts/check-rakuten-widget.py --url https://www.taobao.com/x
    python3 scripts/check-rakuten-widget.py --widget-key ABC123...

Needs playwright:
    pip install playwright && playwright install chromium

Exit code is 0 when at least one probed domain affiliates, 1 when none do.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import tempfile
import threading
import time
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXTEND_HEAD = ROOT / "layouts" / "partials" / "extend_head.html"

WIDGET_KEY_RE = re.compile(r'widgetKey:\s*"([^"]+)"')

DEFAULT_PROBES = [
    ("taobao", "https://www.taobao.com/"),
    ("taobao-global", "https://intl.taobao.com/"),
    ("aliexpress", "https://www.aliexpress.com/item/1005012318553820.html"),
    ("newegg", "https://www.newegg.com/p/2E3-010D-00308"),
    ("amazon", "https://www.amazon.com/dp/B0D1XD1ZV3"),
]

PAGE = """<!doctype html><html><head><meta charset="utf-8">
<style>body{{font:14px system-ui;padding:20px}} a{{display:block;margin:6px 0}}</style>
<script type="text/javascript">
{widget}
</script></head><body><div id="links"></div>
<script>
const urls = {urls};
document.getElementById('links').innerHTML =
  urls.map((u,i)=>`<a id="L${{i}}" href="${{u[1]}}" target="_blank">${{u[0]}}</a>`).join('');
window.__probe = urls;
</script></body></html>"""


def read_widget_key() -> str:
    """Pull the live widget key out of the site's own template."""
    if not EXTEND_HEAD.exists():
        raise SystemExit(f"cannot find {EXTEND_HEAD}")
    m = WIDGET_KEY_RE.search(EXTEND_HEAD.read_text(encoding="utf-8"))
    if not m:
        raise SystemExit(f"no widgetKey found in {EXTEND_HEAD}")
    return m.group(1)


def build_page(widget_key: str, probes: list[tuple[str, str]]) -> str:
    widget = (
        "var _rakuten_automate={u1:'',"
        "snippetURL:'https://automate-frontend.linksynergy.com/minified_logic.js',"
        "automateURL:'https://automate.linksynergy.com',"
        f"widgetKey:'{widget_key}',aelJS:null,useDefaultAEL:false,loaded:false,events:[]}};"
        "var ael=window.addEventListener;window.addEventListener=function(a,b,c,d){"
        "'click'!==a&&_rakuten_automate.useDefaultAEL?ael(a,b,c):"
        "_rakuten_automate.events.push({type:a,handler:b,capture:c,rakuten:d})};"
        "_rakuten_automate.links={};var httpRequest=new XMLHttpRequest;"
        "httpRequest.open('GET',_rakuten_automate.snippetURL,!0);httpRequest.timeout=5E3;"
        "httpRequest.ontimeout=function(){if(!_rakuten_automate.loaded){"
        "for(i=0;i<_rakuten_automate.events.length;i++){var a=_rakuten_automate.events[i];"
        "ael(a.type,a.handler,a.capture)}_rakuten_automate.useDefaultAEL=!0}};"
        "httpRequest.onreadystatechange=function(){httpRequest.readyState===XMLHttpRequest.DONE"
        "&&200===httpRequest.status&&(eval(httpRequest.responseText),_rakuten_automate.run(ael))};"
        "httpRequest.send(null);"
    )
    return PAGE.format(widget=widget, urls=json.dumps(probes))


def serve(directory: str):
    class Quiet(SimpleHTTPRequestHandler):
        def log_message(self, *args):  # noqa: D102 - silence the access log
            pass

    handler = partial(Quiet, directory=directory)
    httpd = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    return httpd, httpd.server_address[1]


def probe(widget_key: str, probes: list[tuple[str, str]]) -> list[dict]:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        raise SystemExit("playwright is not installed - pip install playwright")

    tmp = tempfile.mkdtemp(prefix="rakuten-probe-")
    Path(tmp, "index.html").write_text(build_page(widget_key, probes), encoding="utf-8")
    httpd, port = serve(tmp)

    results = []
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(args=["--no-sandbox"])
            page = browser.new_page()
            console: list[str] = []
            page.on("console", lambda m: console.append(m.text))
            page.goto(f"http://127.0.0.1:{port}/index.html", wait_until="networkidle")
            time.sleep(3)

            for i, (name, _url) in enumerate(probes):
                console.clear()
                seen: list[str] = []
                page.on(
                    "request",
                    lambda r: seen.append(r.url) if "linksynergy" in r.url else None,
                )
                try:
                    page.locator(f"#L{i}").click(no_wait_after=True, timeout=8000)
                except Exception as exc:  # noqa: BLE001 - report, do not abort the run
                    results.append({"name": name, "state": "click-failed", "detail": str(exc)[:120]})
                    continue
                time.sleep(1.2)

                if not seen:
                    results.append({"name": name, "state": "not-affiliated", "detail": "no widget request"})
                    continue
                req = seen[0]
                state = "not-affiliated" if "err_code=" in req else "affiliated"
                detail = "; ".join(c for c in console if c.strip())[:200]
                results.append({"name": name, "state": state, "detail": detail or req[:160]})
            browser.close()
    finally:
        httpd.shutdown()
    return results


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", action="append", help="probe a URL (repeatable)")
    ap.add_argument("--widget-key", help="override the widget key read from the template")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    args = ap.parse_args()

    widget_key = args.widget_key or read_widget_key()
    probes = [(u, u) for u in args.url] if args.url else DEFAULT_PROBES

    results = probe(widget_key, probes)
    affiliated = [r for r in results if r["state"] == "affiliated"]

    if args.json:
        print(json.dumps({"widgetKey": widget_key, "results": results}, indent=2))
    else:
        print("Rakuten Automate widget probe")
        print("-" * 60)
        print(f"  widget key {widget_key}")
        for r in results:
            print(f"  {r['name']:<16} {r['state']:<16} {r['detail'][:80]}")
        print("-" * 60)
        if affiliated:
            print(f"  OK - {len(affiliated)}/{len(results)} probed domains affiliate.")
        else:
            print("  NOTHING AFFILIATES. The widget is on the page but earns nothing.")
            print("  Rakuten: 'If a link is not being affiliated, first check that you are")
            print("  partnered with that advertiser. Automate may take up to 24 hours to")
            print("  reflect relationship changes' - if it is still failing after that,")
            print("  contact Rakuten publisher support.")

    return 0 if affiliated else 1


if __name__ == "__main__":
    sys.exit(main())
