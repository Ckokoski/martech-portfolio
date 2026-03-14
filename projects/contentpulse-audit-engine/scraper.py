"""
scraper.py — Web scraping module for ContentPulse.

Crawls a given website, extracts SEO-relevant data from each page,
and returns structured audit records. Respects robots.txt conventions
and implements polite crawling with delays.
"""

import re
import time
from urllib.parse import urljoin, urlparse
from datetime import datetime

import requests
from bs4 import BeautifulSoup


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

DEFAULT_HEADERS = {
    "User-Agent": (
        "ContentPulse-Audit-Bot/1.0 "
        "(+https://github.com/contentpulse; educational project)"
    )
}
REQUEST_TIMEOUT = 15          # seconds per request
CRAWL_DELAY = 1.0             # seconds between requests (be polite)
MAX_PAGES = 50                # safety limit for crawling


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def _is_same_domain(url: str, base_domain: str) -> bool:
    """Check whether *url* belongs to the same domain as *base_domain*."""
    return urlparse(url).netloc == base_domain


def _normalize_url(url: str) -> str:
    """Strip fragments and trailing slashes for deduplication."""
    parsed = urlparse(url)
    clean = parsed._replace(fragment="")
    path = clean.path.rstrip("/") or "/"
    return f"{clean.scheme}://{clean.netloc}{path}"


def _extract_date(soup: BeautifulSoup, html: str) -> tuple[str, str]:
    """
    Attempt to find publish and last-modified dates from common meta tags,
    <time> elements, and structured data patterns.

    Returns (publish_date, last_modified) as ISO strings or empty strings.
    """
    publish_date = ""
    last_modified = ""

    # Check common meta tags
    date_meta_names = [
        "article:published_time", "datePublished", "publish_date",
        "og:article:published_time", "date", "DC.date.issued",
    ]
    modified_meta_names = [
        "article:modified_time", "dateModified", "last-modified",
        "og:article:modified_time", "DC.date.modified",
    ]

    for name in date_meta_names:
        tag = soup.find("meta", attrs={"property": name}) or soup.find("meta", attrs={"name": name})
        if tag and tag.get("content"):
            publish_date = tag["content"][:10]
            break

    for name in modified_meta_names:
        tag = soup.find("meta", attrs={"property": name}) or soup.find("meta", attrs={"name": name})
        if tag and tag.get("content"):
            last_modified = tag["content"][:10]
            break

    # Fallback: look for <time> elements
    if not publish_date:
        time_tag = soup.find("time", attrs={"datetime": True})
        if time_tag:
            publish_date = time_tag["datetime"][:10]

    # Fallback: regex for dates in the HTML (YYYY-MM-DD pattern)
    if not publish_date:
        date_match = re.search(r"\b(20\d{2}-(?:0[1-9]|1[0-2])-(?:0[1-9]|[12]\d|3[01]))\b", html)
        if date_match:
            publish_date = date_match.group(1)

    return publish_date, last_modified


def _extract_headings(soup: BeautifulSoup) -> dict[str, list[str]]:
    """Extract all h1-h6 headings as a dict of lists."""
    headings = {}
    for level in range(1, 7):
        tag_name = f"h{level}"
        found = soup.find_all(tag_name)
        if found:
            headings[tag_name] = [h.get_text(strip=True) for h in found]
    return headings


# ---------------------------------------------------------------------------
# Main scraping functions
# ---------------------------------------------------------------------------

def scrape_page(url: str, session: requests.Session) -> dict | None:
    """
    Fetch a single URL and extract audit data.

    Returns a dict with page metrics, or None if the request fails.
    """
    try:
        resp = session.get(url, timeout=REQUEST_TIMEOUT, headers=DEFAULT_HEADERS)
    except requests.RequestException as exc:
        print(f"  [ERROR] Failed to fetch {url}: {exc}")
        return None

    load_time_ms = int(resp.elapsed.total_seconds() * 1000)
    soup = BeautifulSoup(resp.text, "lxml")

    # --- Title ---
    title_tag = soup.find("title")
    title = title_tag.get_text(strip=True) if title_tag else ""

    # --- Meta description ---
    meta_desc_tag = soup.find("meta", attrs={"name": "description"})
    meta_description = meta_desc_tag["content"] if meta_desc_tag and meta_desc_tag.get("content") else ""

    # --- Headings ---
    headings = _extract_headings(soup)

    # --- Body text & word count ---
    body = soup.find("body")
    body_text = body.get_text(separator=" ", strip=True) if body else ""
    word_count = len(body_text.split())

    # --- Images ---
    images = soup.find_all("img")
    image_count = len(images)
    images_with_alt = sum(1 for img in images if img.get("alt", "").strip())
    images_missing_alt = image_count - images_with_alt

    # --- Links ---
    base_domain = urlparse(url).netloc
    all_links = soup.find_all("a", href=True)
    internal_links = 0
    external_links = 0
    discovered_urls = []

    for a_tag in all_links:
        href = urljoin(url, a_tag["href"])
        if _is_same_domain(href, base_domain):
            internal_links += 1
            # Only queue HTML-looking links for further crawling
            if not re.search(r"\.(pdf|jpg|png|gif|svg|css|js|zip|xml)(\?|$)", href, re.I):
                discovered_urls.append(_normalize_url(href))
        else:
            external_links += 1

    # --- Dates ---
    publish_date, last_modified = _extract_date(soup, resp.text)

    # --- Meta robots ---
    robots_tag = soup.find("meta", attrs={"name": "robots"})
    meta_robots = robots_tag["content"] if robots_tag and robots_tag.get("content") else "index, follow"

    # --- Canonical ---
    canonical_tag = soup.find("link", attrs={"rel": "canonical"})
    has_canonical = canonical_tag is not None

    # --- Open Graph / Twitter tags ---
    has_og_tags = soup.find("meta", attrs={"property": re.compile(r"^og:")}) is not None
    has_twitter_tags = soup.find("meta", attrs={"name": re.compile(r"^twitter:")}) is not None

    # --- Determine page type (simple heuristic) ---
    path = urlparse(url).path.lower()
    if path in ("/", ""):
        page_type = "homepage"
    elif "/blog" in path:
        page_type = "blog"
    elif "/product" in path:
        page_type = "product"
    elif any(seg in path for seg in ("/resources", "/whitepaper", "/webinar", "/template")):
        page_type = "resource"
    elif any(seg in path for seg in ("/case-stud", "/customer")):
        page_type = "case_study"
    elif "/about" in path:
        page_type = "about"
    else:
        page_type = "landing"

    return {
        "url": url,
        "title": title,
        "meta_description": meta_description,
        "page_type": page_type,
        "headings": headings,
        "word_count": word_count,
        "image_count": image_count,
        "images_with_alt": images_with_alt,
        "images_missing_alt": images_missing_alt,
        "internal_links": internal_links,
        "external_links": external_links,
        "publish_date": publish_date,
        "last_modified": last_modified,
        "status_code": resp.status_code,
        "load_time_ms": load_time_ms,
        "meta_robots": meta_robots,
        "has_canonical": has_canonical,
        "has_og_tags": has_og_tags,
        "has_twitter_tags": has_twitter_tags,
        "_discovered_urls": discovered_urls,
    }


def crawl_site(start_url: str, max_pages: int = MAX_PAGES) -> list[dict]:
    """
    Crawl a website starting from *start_url*, following internal links
    up to *max_pages*.

    Returns a list of page-audit dicts (same schema as sample_data).
    """
    base_domain = urlparse(start_url).netloc
    visited: set[str] = set()
    queue: list[str] = [_normalize_url(start_url)]
    results: list[dict] = []

    session = requests.Session()

    print(f"[ContentPulse] Starting crawl of {base_domain}")
    print(f"[ContentPulse] Max pages: {max_pages}\n")

    while queue and len(visited) < max_pages:
        url = queue.pop(0)
        if url in visited:
            continue

        print(f"  Crawling ({len(visited) + 1}/{max_pages}): {url}")
        visited.add(url)

        page_data = scrape_page(url, session)
        if page_data is None:
            continue

        # Collect discovered URLs for further crawling
        for discovered in page_data.pop("_discovered_urls", []):
            if discovered not in visited and _is_same_domain(discovered, base_domain):
                queue.append(discovered)

        results.append(page_data)
        time.sleep(CRAWL_DELAY)

    print(f"\n[ContentPulse] Crawl complete. {len(results)} pages scraped.")
    return results


if __name__ == "__main__":
    import sys
    import json

    url = sys.argv[1] if len(sys.argv) > 1 else "https://example.com"
    data = crawl_site(url, max_pages=5)
    print(json.dumps(data, indent=2, default=str))
