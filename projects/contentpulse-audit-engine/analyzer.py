"""
analyzer.py — Content analysis module for ContentPulse.

Takes raw page-audit data (from the scraper or sample_data) and computes:
  - SEO score per page (0-100)
  - Readability estimate
  - Content freshness rating
  - Overall site health score
  - Flagged issues per page
"""

from datetime import datetime, timedelta

import pandas as pd


# ---------------------------------------------------------------------------
# Scoring constants
# ---------------------------------------------------------------------------

# Title length: ideal 30-60 chars
TITLE_MIN = 30
TITLE_MAX = 60

# Meta description: ideal 120-160 chars
META_DESC_MIN = 120
META_DESC_MAX = 160

# Word count thresholds by page type
WORD_COUNT_THRESHOLDS = {
    "blog": (600, 2500),
    "product": (300, 1500),
    "landing": (150, 800),
    "resource": (300, 1200),
    "case_study": (500, 1500),
    "homepage": (200, 800),
    "about": (300, 1000),
}

# Freshness: days since last modification
FRESH_DAYS = 90
STALE_DAYS = 365


# ---------------------------------------------------------------------------
# Per-page scoring functions
# ---------------------------------------------------------------------------

def score_title(title: str) -> tuple[int, list[str]]:
    """Score the page title (0-15 points). Return (score, issues)."""
    issues = []
    if not title:
        issues.append("Missing page title")
        return 0, issues

    length = len(title)
    if length < TITLE_MIN:
        issues.append(f"Title too short ({length} chars, recommended {TITLE_MIN}-{TITLE_MAX})")
        return 8, issues
    if length > TITLE_MAX:
        issues.append(f"Title too long ({length} chars, recommended {TITLE_MIN}-{TITLE_MAX})")
        return 10, issues

    return 15, issues


def score_meta_description(desc: str) -> tuple[int, list[str]]:
    """Score the meta description (0-15 points). Return (score, issues)."""
    issues = []
    if not desc:
        issues.append("Missing meta description")
        return 0, issues

    length = len(desc)
    if length < META_DESC_MIN:
        issues.append(f"Meta description too short ({length} chars, recommended {META_DESC_MIN}-{META_DESC_MAX})")
        return 8, issues
    if length > META_DESC_MAX:
        issues.append(f"Meta description too long ({length} chars, recommended {META_DESC_MIN}-{META_DESC_MAX})")
        return 10, issues

    return 15, issues


def score_headings(headings: dict) -> tuple[int, list[str]]:
    """Score heading structure (0-20 points). Return (score, issues)."""
    issues = []
    score = 0

    h1_list = headings.get("h1", [])
    if not h1_list:
        issues.append("Missing H1 heading")
    elif len(h1_list) > 1:
        issues.append(f"Multiple H1 headings ({len(h1_list)} found, should be 1)")
        score += 8
    else:
        score += 10

    # Check for at least one H2
    h2_list = headings.get("h2", [])
    if h2_list:
        score += 7
    else:
        issues.append("No H2 headings found — content lacks subheading structure")

    # Bonus for deeper heading hierarchy
    if headings.get("h3"):
        score += 3

    return min(score, 20), issues


def score_images(image_count: int, images_missing_alt: int) -> tuple[int, list[str]]:
    """Score image optimization (0-15 points). Return (score, issues)."""
    issues = []

    if image_count == 0:
        # No images isn't necessarily bad, but note it
        return 10, ["No images on page — consider adding visual content"]

    alt_ratio = (image_count - images_missing_alt) / image_count
    score = int(alt_ratio * 15)

    if images_missing_alt > 0:
        issues.append(f"{images_missing_alt} image(s) missing alt text")

    return score, issues


def score_content_length(word_count: int, page_type: str) -> tuple[int, list[str]]:
    """Score content length relative to page type (0-15 points)."""
    issues = []
    lo, hi = WORD_COUNT_THRESHOLDS.get(page_type, (300, 1000))

    if word_count < lo:
        issues.append(f"Thin content ({word_count} words, recommended {lo}+ for {page_type})")
        ratio = word_count / lo
        return max(int(ratio * 15), 0), issues

    if word_count > hi:
        issues.append(f"Content may be too long ({word_count} words) — consider splitting")
        return 12, issues

    return 15, issues


def score_technical_seo(page: dict) -> tuple[int, list[str]]:
    """Score technical SEO signals (0-20 points)."""
    issues = []
    score = 0

    if page.get("has_canonical"):
        score += 5
    else:
        issues.append("Missing canonical tag")

    if page.get("has_og_tags"):
        score += 5
    else:
        issues.append("Missing Open Graph tags")

    if page.get("has_twitter_tags"):
        score += 3
    else:
        issues.append("Missing Twitter Card tags")

    robots = page.get("meta_robots", "")
    if "noindex" in robots:
        issues.append("Page is set to noindex")
    else:
        score += 4

    if page.get("load_time_ms", 0) > 3000:
        issues.append(f"Slow load time ({page['load_time_ms']}ms)")
    else:
        score += 3

    return min(score, 20), issues


# ---------------------------------------------------------------------------
# Freshness analysis
# ---------------------------------------------------------------------------

def assess_freshness(last_modified: str, publish_date: str) -> tuple[str, int, str]:
    """
    Determine content freshness.

    Returns:
        (freshness_label, days_since_update, freshness_color)
    """
    today = datetime.now()
    ref_date_str = last_modified or publish_date

    if not ref_date_str:
        return "Unknown", -1, "#9e9e9e"

    try:
        ref_date = datetime.strptime(ref_date_str[:10], "%Y-%m-%d")
    except ValueError:
        return "Unknown", -1, "#9e9e9e"

    days = (today - ref_date).days

    if days <= FRESH_DAYS:
        return "Fresh", days, "#4caf50"
    elif days <= STALE_DAYS:
        return "Aging", days, "#ff9800"
    else:
        return "Stale", days, "#f44336"


# ---------------------------------------------------------------------------
# Readability (simple approximation)
# ---------------------------------------------------------------------------

def estimate_readability(word_count: int, headings: dict) -> tuple[str, str]:
    """
    Simple readability estimate based on word count and heading density.

    A more advanced implementation would use Flesch-Kincaid or similar,
    but that requires the full page text. This heuristic works with
    the data we have.

    Returns (readability_label, readability_note).
    """
    total_headings = sum(len(v) for v in headings.values())

    if word_count == 0:
        return "N/A", "No content detected"

    words_per_heading = word_count / max(total_headings, 1)

    # Good structure: one heading per 150-300 words
    if total_headings == 0:
        return "Poor", "No headings — wall of text"
    elif words_per_heading > 500:
        return "Fair", "Headings are too sparse — long text blocks likely"
    elif words_per_heading < 50:
        return "Fair", "Very frequent headings — may feel fragmented"
    else:
        return "Good", "Well-structured with regular subheadings"


# ---------------------------------------------------------------------------
# Main analysis pipeline
# ---------------------------------------------------------------------------

def analyze_pages(pages: list[dict]) -> pd.DataFrame:
    """
    Run the full analysis pipeline on a list of page dicts.

    Adds computed columns for SEO score, freshness, readability, and issues.
    Returns a pandas DataFrame with all original + computed fields.
    """
    analyzed = []

    for page in pages:
        # --- Compute sub-scores ---
        title_score, title_issues = score_title(page.get("title", ""))
        meta_score, meta_issues = score_meta_description(page.get("meta_description", ""))
        heading_score, heading_issues = score_headings(page.get("headings", {}))
        image_score, image_issues = score_images(
            page.get("image_count", 0),
            page.get("images_missing_alt", 0),
        )
        content_score, content_issues = score_content_length(
            page.get("word_count", 0),
            page.get("page_type", "landing"),
        )
        tech_score, tech_issues = score_technical_seo(page)

        # --- Aggregate SEO score (0-100) ---
        seo_score = title_score + meta_score + heading_score + image_score + content_score + tech_score

        # --- All issues ---
        all_issues = title_issues + meta_issues + heading_issues + image_issues + content_issues + tech_issues

        # --- Freshness ---
        freshness_label, days_since_update, freshness_color = assess_freshness(
            page.get("last_modified", ""),
            page.get("publish_date", ""),
        )

        # --- Readability ---
        readability_label, readability_note = estimate_readability(
            page.get("word_count", 0),
            page.get("headings", {}),
        )

        analyzed.append({
            **page,
            "seo_score": seo_score,
            "title_score": title_score,
            "meta_score": meta_score,
            "heading_score": heading_score,
            "image_score": image_score,
            "content_score": content_score,
            "tech_score": tech_score,
            "issues": all_issues,
            "issue_count": len(all_issues),
            "freshness_label": freshness_label,
            "days_since_update": days_since_update,
            "freshness_color": freshness_color,
            "readability_label": readability_label,
            "readability_note": readability_note,
        })

    df = pd.DataFrame(analyzed)
    return df


def compute_site_health(df: pd.DataFrame) -> dict:
    """
    Compute aggregate site-level health metrics from the analyzed DataFrame.

    Returns a dict with overall scores and summary statistics.
    """
    total_pages = len(df)
    if total_pages == 0:
        return {"overall_score": 0, "total_pages": 0}

    avg_seo = df["seo_score"].mean()
    freshness_counts = df["freshness_label"].value_counts().to_dict()
    readability_counts = df["readability_label"].value_counts().to_dict()
    total_issues = df["issue_count"].sum()

    # Overall health: weighted average of SEO score + freshness bonus
    fresh_ratio = freshness_counts.get("Fresh", 0) / total_pages
    freshness_bonus = fresh_ratio * 10  # up to 10 extra points

    overall_score = min(round(avg_seo + freshness_bonus, 1), 100)

    return {
        "overall_score": overall_score,
        "avg_seo_score": round(avg_seo, 1),
        "total_pages": total_pages,
        "total_issues": int(total_issues),
        "avg_word_count": int(df["word_count"].mean()),
        "freshness_counts": freshness_counts,
        "readability_counts": readability_counts,
        "pages_missing_meta": int((df["meta_description"] == "").sum()),
        "pages_missing_h1": int(df["headings"].apply(lambda h: len(h.get("h1", [])) == 0).sum()),
        "pages_with_slow_load": int((df.get("load_time_ms", pd.Series(dtype=int)) > 3000).sum()) if "load_time_ms" in df.columns else 0,
    }


if __name__ == "__main__":
    # Quick test with sample data
    from sample_data import generate_sample_data
    import json

    pages = generate_sample_data()
    df = analyze_pages(pages)
    health = compute_site_health(df)

    print("=== Site Health ===")
    print(json.dumps(health, indent=2, default=str))
    print(f"\n=== Top Issues ===")
    for _, row in df.nlargest(5, "issue_count").iterrows():
        print(f"  {row['url']} — {row['issue_count']} issues (SEO: {row['seo_score']})")
