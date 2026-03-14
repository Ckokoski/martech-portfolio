"""
report.py — Generates an HTML pipeline report with Plotly charts.

Produces a self-contained HTML dashboard showing:
  - Records ingested per source
  - Match rates and methods
  - Deduplication statistics
  - Quality score distributions
  - Sample unified profiles
"""

from __future__ import annotations

import json
import os
from datetime import datetime

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from jinja2 import Environment, FileSystemLoader


# ---------------------------------------------------------------------------
# Chart builders (return Plotly HTML snippets)
# ---------------------------------------------------------------------------

def _chart_ingestion(source_counts: dict[str, int]) -> str:
    """Bar chart of records ingested per source."""
    fig = go.Figure(go.Bar(
        x=list(source_counts.keys()),
        y=list(source_counts.values()),
        marker_color=["#2563eb", "#7c3aed", "#059669", "#d97706"],
        text=list(source_counts.values()),
        textposition="outside",
    ))
    fig.update_layout(
        title="Records Ingested Per Source",
        xaxis_title="Source",
        yaxis_title="Record Count",
        template="plotly_white",
        height=380,
        margin=dict(t=50, b=40),
    )
    return fig.to_html(full_html=False, include_plotlyjs=False)


def _chart_match_methods(resolution_stats: dict) -> str:
    """Pie chart of match methods."""
    labels = ["Email (Exact)", "Phone (Exact)", "Fuzzy (Name+Co)"]
    values = [
        resolution_stats.get("email_merges", 0),
        resolution_stats.get("phone_merges", 0),
        resolution_stats.get("fuzzy_merges", 0),
    ]
    fig = go.Figure(go.Pie(
        labels=labels,
        values=values,
        marker_colors=["#2563eb", "#7c3aed", "#f59e0b"],
        hole=0.4,
        textinfo="percent",
        textposition="inside",
        hoverinfo="label+percent+value",
        pull=[0, 0.05, 0.05],
    ))
    fig.update_layout(
        title="Identity Resolution — Match Methods",
        template="plotly_white",
        height=380,
        margin=dict(t=50, b=40),
        legend=dict(orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5),
    )
    return fig.to_html(full_html=False, include_plotlyjs=False)


def _chart_quality_distribution(profiles: pd.DataFrame) -> str:
    """Histogram of overall quality scores."""
    fig = go.Figure(go.Histogram(
        x=profiles["quality_score"],
        nbinsx=30,
        marker_color="#2563eb",
        opacity=0.85,
    ))
    fig.update_layout(
        title="Quality Score Distribution",
        xaxis_title="Quality Score",
        yaxis_title="Profile Count",
        template="plotly_white",
        height=380,
        margin=dict(t=50, b=40),
    )
    return fig.to_html(full_html=False, include_plotlyjs=False)


def _chart_grade_distribution(quality_stats: dict) -> str:
    """Bar chart of quality grades."""
    grades = quality_stats.get("grade_distribution", {})
    grade_order = ["A", "B", "C", "D", "F"]
    colors = ["#059669", "#2563eb", "#f59e0b", "#ea580c", "#dc2626"]
    fig = go.Figure(go.Bar(
        x=grade_order,
        y=[grades.get(g, 0) for g in grade_order],
        marker_color=colors,
        text=[grades.get(g, 0) for g in grade_order],
        textposition="outside",
    ))
    fig.update_layout(
        title="Profile Quality Grades",
        xaxis_title="Grade",
        yaxis_title="Count",
        template="plotly_white",
        height=380,
        margin=dict(t=50, b=40),
    )
    return fig.to_html(full_html=False, include_plotlyjs=False)


def _chart_source_overlap(profiles: pd.DataFrame) -> str:
    """Bar chart showing how many sources contribute to profiles."""
    counts = profiles["source_count"].value_counts().sort_index()
    fig = go.Figure(go.Bar(
        x=[f"{k} source{'s' if k > 1 else ''}" for k in counts.index],
        y=counts.values,
        marker_color="#7c3aed",
        text=counts.values,
        textposition="outside",
    ))
    fig.update_layout(
        title="Sources Per Profile",
        xaxis_title="Number of Contributing Sources",
        yaxis_title="Profile Count",
        template="plotly_white",
        height=380,
        margin=dict(t=50, b=40),
    )
    return fig.to_html(full_html=False, include_plotlyjs=False)


def _chart_confidence_distribution(profiles: pd.DataFrame) -> str:
    """Histogram of match confidence scores."""
    matched = profiles[profiles["match_confidence"] > 0]
    fig = go.Figure(go.Histogram(
        x=matched["match_confidence"],
        nbinsx=20,
        marker_color="#059669",
        opacity=0.85,
    ))
    fig.update_layout(
        title="Match Confidence Distribution (Matched Profiles)",
        xaxis_title="Confidence",
        yaxis_title="Profile Count",
        template="plotly_white",
        height=380,
        margin=dict(t=50, b=40),
    )
    return fig.to_html(full_html=False, include_plotlyjs=False)


# ---------------------------------------------------------------------------
# Sample profiles formatter
# ---------------------------------------------------------------------------

def _sample_profiles(profiles: pd.DataFrame, n: int = 5) -> list[dict]:
    """Pick N multi-source profiles as samples."""
    multi = profiles[profiles["source_count"] > 1].sort_values(
        "quality_score", ascending=False
    )
    sample = multi.head(n)
    records = []
    for _, row in sample.iterrows():
        records.append({
            "name": f"{row['first_name']} {row['last_name']}".strip(),
            "email": row["email"],
            "company": row.get("company", ""),
            "sources": row["sources"],
            "total_spend": f"${row['total_spend']:,.2f}",
            "open_count": int(row["open_count"]),
            "page_views": int(row["page_views"]),
            "quality_score": round(row["quality_score"], 2),
            "quality_grade": row["quality_grade"],
        })
    return records


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def generate_report(
    profiles: pd.DataFrame,
    source_counts: dict[str, int],
    resolution_stats: dict,
    profile_stats: dict,
    quality_stats: dict,
    segment_results: dict,
    output_path: str = "output/pipeline_report.html",
    template_dir: str = "templates",
) -> str:
    """
    Render the pipeline report as a self-contained HTML file.

    Returns the output file path.
    """
    print("\n=== Generating pipeline report ===")

    # Build chart HTML snippets
    charts = {
        "ingestion": _chart_ingestion(source_counts),
        "match_methods": _chart_match_methods(resolution_stats),
        "quality_dist": _chart_quality_distribution(profiles),
        "grade_dist": _chart_grade_distribution(quality_stats),
        "source_overlap": _chart_source_overlap(profiles),
        "confidence_dist": _chart_confidence_distribution(profiles),
    }

    sample = _sample_profiles(profiles, n=6)

    # Template context
    context = {
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "charts": charts,
        "source_counts": source_counts,
        "total_ingested": sum(source_counts.values()),
        "resolution": resolution_stats,
        "profiles": profile_stats,
        "quality": quality_stats,
        "segments": segment_results,
        "sample_profiles": sample,
    }

    # Render Jinja2 template
    env = Environment(loader=FileSystemLoader(template_dir), autoescape=False)
    template = env.get_template("report.html")
    html = template.render(**context)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"  Report saved: {output_path}")
    return output_path
