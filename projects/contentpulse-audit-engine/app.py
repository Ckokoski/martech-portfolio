"""
app.py — Main entry point for ContentPulse: Marketing Content Audit Engine.

Usage:
    python app.py --sample              # Run with generated sample data (no network required)
    python app.py --url https://example.com   # Crawl a live website
    python app.py --url https://example.com --max-pages 25  # Limit crawl depth

The tool crawls web pages (or generates sample data), analyzes each page for
SEO health, content freshness, and readability, then produces an interactive
HTML dashboard that can be opened directly in any browser.
"""

import argparse
import os
import sys
import webbrowser

from sample_data import generate_sample_data
from scraper import crawl_site
from analyzer import analyze_pages, compute_site_health
from dashboard import generate_dashboard


# ---------------------------------------------------------------------------
# CLI argument parsing
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="ContentPulse",
        description="Marketing Content Audit Engine — crawl, analyze, and visualize content health.",
    )

    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument(
        "--sample",
        action="store_true",
        help="Use generated sample data (20 pages from a fictional marketing site).",
    )
    source.add_argument(
        "--url",
        type=str,
        help="URL of the website to crawl (e.g. https://example.com).",
    )

    parser.add_argument(
        "--max-pages",
        type=int,
        default=50,
        help="Maximum number of pages to crawl (default: 50).",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Output path for the HTML dashboard (default: sample_output/dashboard.html).",
    )
    parser.add_argument(
        "--no-open",
        action="store_true",
        help="Do not automatically open the dashboard in the browser.",
    )

    return parser.parse_args()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    args = parse_args()

    print("=" * 60)
    print("  ContentPulse — Marketing Content Audit Engine")
    print("=" * 60)
    print()

    # ----- Step 1: Gather page data -----
    if args.sample:
        print("[1/3] Generating sample data (20 pages)...")
        pages = generate_sample_data()
        print(f"      Generated {len(pages)} sample pages.\n")
    else:
        print(f"[1/3] Crawling {args.url} (max {args.max_pages} pages)...")
        pages = crawl_site(args.url, max_pages=args.max_pages)
        if not pages:
            print("\nERROR: No pages could be scraped. Check the URL and try again.")
            sys.exit(1)
        print()

    # ----- Step 2: Analyze -----
    print(f"[2/3] Analyzing {len(pages)} pages...")
    df = analyze_pages(pages)
    site_health = compute_site_health(df)

    print(f"      Overall Health Score : {site_health['overall_score']}/100")
    print(f"      Average SEO Score    : {site_health['avg_seo_score']}/100")
    print(f"      Total Issues Found   : {site_health['total_issues']}")
    print()

    # ----- Step 3: Generate dashboard -----
    print("[3/3] Generating HTML dashboard...")
    output_path = generate_dashboard(df, site_health, output_path=args.output)
    print(f"      Dashboard saved to: {output_path}")
    print()

    # ----- Open in browser -----
    if not args.no_open:
        print("Opening dashboard in default browser...")
        webbrowser.open("file://" + os.path.abspath(output_path))

    print()
    print("Done! Open the dashboard HTML file in any browser to explore results.")
    print("=" * 60)


if __name__ == "__main__":
    main()
