"""
dashboard.py — Generates a self-contained HTML dashboard from audit data.

Reads the Jinja-style template (simple string replacement) from
templates/dashboard.html and injects the analyzed data to produce
a single HTML file that can be opened directly in any browser.
"""

import json
import os
from collections import Counter
from datetime import datetime

import pandas as pd


# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

TEMPLATE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")
TEMPLATE_FILE = os.path.join(TEMPLATE_DIR, "dashboard.html")
DEFAULT_OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sample_output")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _score_class(value: float, good: float = 70, ok: float = 50) -> str:
    """Return a CSS class name based on score thresholds."""
    if value >= good:
        return "score-good"
    elif value >= ok:
        return "score-ok"
    return "score-bad"


def _freshness_badge(label: str) -> str:
    """Return badge HTML for a freshness label."""
    css_map = {
        "Fresh": "badge-fresh",
        "Aging": "badge-aging",
        "Stale": "badge-stale",
        "Unknown": "badge-unknown",
    }
    css = css_map.get(label, "badge-unknown")
    return f'<span class="badge {css}">{label}</span>'


def _seo_bar(score: int) -> str:
    """Return a mini bar + number for SEO score."""
    if score >= 70:
        color = "#16a34a"
    elif score >= 50:
        color = "#ea580c"
    else:
        color = "#dc2626"
    pct = min(score, 100)
    return (
        f'<span class="seo-bar"><span class="seo-bar-fill" '
        f'style="width:{pct}%;background:{color}"></span></span>'
        f'<strong>{score}</strong>'
    )


def _build_table_rows(df: pd.DataFrame) -> str:
    """Build the HTML table body rows from the DataFrame."""
    rows_html = []

    for idx, row in df.iterrows():
        # Data attributes for sorting / filtering
        data_attrs = (
            f'data-idx="{idx}" '
            f'data-url="{row["url"]}" '
            f'data-title="{row.get("title", "")}" '
            f'data-page_type="{row["page_type"]}" '
            f'data-seo_score="{row["seo_score"]}" '
            f'data-word_count="{row["word_count"]}" '
            f'data-freshness_label="{row["freshness_label"]}" '
            f'data-readability_label="{row["readability_label"]}" '
            f'data-issue_count="{row["issue_count"]}"'
        )

        # Truncate URL for display
        display_url = row["url"]
        if len(display_url) > 60:
            display_url = display_url[:57] + "..."

        issues_btn = ""
        if row["issue_count"] > 0:
            issues_btn = f'<button class="toggle-btn" onclick="toggleDetail({idx})">View</button>'

        row_html = f"""<tr class="data-row" {data_attrs}>
            <td class="url-cell"><a href="{row['url']}" target="_blank" title="{row['url']}">{display_url}</a></td>
            <td>{row['page_type']}</td>
            <td>{_seo_bar(row['seo_score'])}</td>
            <td>{row['word_count']:,}</td>
            <td>{_freshness_badge(row['freshness_label'])}</td>
            <td>{row['readability_label']}</td>
            <td>{row['issue_count']}</td>
            <td>{issues_btn}</td>
        </tr>"""
        rows_html.append(row_html)

        # Detail row for issues
        if row["issue_count"] > 0:
            issues = row.get("issues", [])
            li_items = "".join(f"<li>{iss}</li>" for iss in issues)
            detail_html = (
                f'<tr class="issues-detail" id="detail-{idx}">'
                f'<td colspan="8"><ul>{li_items}</ul></td></tr>'
            )
            rows_html.append(detail_html)

    return "\n".join(rows_html)


def _build_top_issues(df: pd.DataFrame) -> str:
    """Aggregate the most common issues across all pages."""
    all_issues: list[str] = []
    for issues_list in df["issues"]:
        if isinstance(issues_list, list):
            all_issues.extend(issues_list)

    counter = Counter(all_issues)
    top = counter.most_common(10)

    if not top:
        return '<p style="color:#64748b;">No issues found.</p>'

    bars = []
    for issue_text, count in top:
        bars.append(
            f'<div class="issue-bar">'
            f'<span class="issue-label">{issue_text}</span>'
            f'<span class="issue-count">{count} page{"s" if count != 1 else ""}</span>'
            f'</div>'
        )
    return "\n".join(bars)


def _build_type_options(df: pd.DataFrame) -> str:
    """Build <option> tags for the page-type filter dropdown."""
    types = sorted(df["page_type"].unique())
    return "\n".join(f'<option value="{t}">{t}</option>' for t in types)


def _prepare_page_json(df: pd.DataFrame) -> str:
    """Convert the DataFrame to a JSON array for the inline JS."""
    records = []
    for _, row in df.iterrows():
        records.append({
            "url": row["url"],
            "title": row.get("title", ""),
            "page_type": row["page_type"],
            "seo_score": int(row["seo_score"]),
            "word_count": int(row["word_count"]),
            "freshness_label": row["freshness_label"],
            "days_since_update": int(row["days_since_update"]),
            "readability_label": row["readability_label"],
            "issues": row.get("issues", []),
        })
    return json.dumps(records, indent=2)


# ---------------------------------------------------------------------------
# Main generator
# ---------------------------------------------------------------------------

def generate_dashboard(
    df: pd.DataFrame,
    site_health: dict,
    output_path: str | None = None,
) -> str:
    """
    Generate a self-contained HTML dashboard file.

    Args:
        df: Analyzed DataFrame from analyzer.analyze_pages().
        site_health: Dict from analyzer.compute_site_health().
        output_path: Where to write the HTML file. Defaults to sample_output/dashboard.html.

    Returns:
        The absolute path to the generated HTML file.
    """
    if output_path is None:
        os.makedirs(DEFAULT_OUTPUT_DIR, exist_ok=True)
        output_path = os.path.join(DEFAULT_OUTPUT_DIR, "dashboard.html")

    # Read template
    with open(TEMPLATE_FILE, "r", encoding="utf-8") as f:
        template = f.read()

    # Prepare replacements
    generated_date = datetime.now().strftime("%Y-%m-%d %H:%M")
    overall_score = site_health.get("overall_score", 0)
    avg_seo = site_health.get("avg_seo_score", 0)
    total_issues = site_health.get("total_issues", 0)

    replacements = {
        "{{generated_date}}": generated_date,
        "{{total_pages}}": str(site_health.get("total_pages", 0)),
        "{{overall_score}}": str(overall_score),
        "{{overall_score_class}}": _score_class(overall_score),
        "{{avg_seo_score}}": str(avg_seo),
        "{{avg_seo_class}}": _score_class(avg_seo),
        "{{total_issues}}": str(total_issues),
        "{{issues_class}}": "score-bad" if total_issues > 20 else ("score-ok" if total_issues > 10 else "score-good"),
        "{{avg_word_count}}": str(site_health.get("avg_word_count", 0)),
        "{{top_issues_html}}": _build_top_issues(df),
        "{{table_rows}}": _build_table_rows(df),
        "{{type_options}}": _build_type_options(df),
        "{{page_data_json}}": _prepare_page_json(df),
        "{{site_health_json}}": json.dumps(site_health, default=str),
    }

    html = template
    for placeholder, value in replacements.items():
        html = html.replace(placeholder, value)

    # Write output
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    return os.path.abspath(output_path)


if __name__ == "__main__":
    # Quick test with sample data
    from sample_data import generate_sample_data
    from analyzer import analyze_pages, compute_site_health

    pages = generate_sample_data()
    df = analyze_pages(pages)
    health = compute_site_health(df)
    path = generate_dashboard(df, health)
    print(f"Dashboard generated: {path}")
