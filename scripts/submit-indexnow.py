"""IndexNow submission helper.

Reads all published URLs from sitemap.xml or public build and notifies
IndexNow (Bing, Yandex, Seznam, Naver) for instant search indexing.
"""

import sys
import json
import urllib.request
import urllib.error
import xml.etree.ElementTree as ET
from pathlib import Path

HOST = "pragmaticsysadmin.help"
KEY = "39100d6315e3be674773e62e0ae5f859"
KEY_LOCATION = f"https://{HOST}/{KEY}.txt"
INDEXNOW_ENDPOINT = "https://api.indexnow.org/indexnow"

def get_urls_from_sitemap(sitemap_path: Path) -> list[str]:
    if not sitemap_path.exists():
        return []
    try:
        tree = ET.parse(sitemap_path)
        root = tree.getroot()
        # Handle standard sitemap namespace
        ns = {"ns": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        urls = []
        for loc in root.findall(".//ns:loc", ns):
            if loc.text:
                urls.append(loc.text.strip())
        if not urls:
            for elem in root.iter():
                if elem.tag.endswith("loc") and elem.text:
                    urls.append(elem.text.strip())
        return urls
    except Exception as e:
        print(f"Error parsing sitemap: {e}", file=sys.stderr)
        return []

def submit_indexnow(urls: list[str]) -> bool:
    if not urls:
        print("No URLs to submit.")
        return True

    # Limit to 10,000 URLs per protocol spec
    submission_urls = urls[:10000]
    payload = {
        "host": HOST,
        "key": KEY,
        "keyLocation": KEY_LOCATION,
        "urlList": submission_urls
    }
    
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        INDEXNOW_ENDPOINT,
        data=data,
        headers={"Content-Type": "application/json; charset=utf-8"}
    )
    
    try:
        print(f"Submitting {len(submission_urls)} URLs to IndexNow ({INDEXNOW_ENDPOINT})...")
        with urllib.request.urlopen(req, timeout=15) as resp:
            status = resp.status
            print(f"IndexNow response status: {status}")
            return status in (200, 202)
    except urllib.error.HTTPError as e:
        # 200: OK, 202: Accepted (queued)
        if e.code in (200, 202):
            print(f"IndexNow accepted: {e.code}")
            return True
        print(f"IndexNow HTTP Error: {e.code} - {e.read().decode('utf-8', errors='ignore')}", file=sys.stderr)
        return False
    except Exception as e:
        print(f"IndexNow submission failed: {e}", file=sys.stderr)
        return False

def main():
    repo_root = Path(__file__).resolve().parent.parent
    sitemap = repo_root / "public" / "sitemap.xml"
    if not sitemap.exists():
        # Fallback to static if built locally or search in public
        print(f"Sitemap not found at {sitemap}. Run hugo build first.")
        sys.exit(1)

    urls = get_urls_from_sitemap(sitemap)
    print(f"Discovered {len(urls)} URLs from sitemap.")
    ok = submit_indexnow(urls)
    if not ok:
        print("IndexNow submission warning (will retry on next deploy).")

if __name__ == "__main__":
    main()
