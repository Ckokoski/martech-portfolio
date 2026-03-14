"""
report.py — HTML Report Generator

Assembles analysis results, charts, and recommendations into a
self-contained interactive HTML report using Jinja2 templating.
"""

import os
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
from recommendations import Recommendation
from typing import List


TEMPLATE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")
OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))


def generate_report(
    analysis_results: dict,
    charts: dict,
    recommendations: List[Recommendation],
    output_filename: str = "report.html",
) -> str:
    """Render the HTML report and write it to disk.

    Args:
        analysis_results: Output from analyzer.run_full_analysis()
        charts: Output from visualizations.generate_all_charts()
        recommendations: Output from recommendations.generate_recommendations()
        output_filename: Name of the output HTML file

    Returns:
        Absolute path to the generated report file.
    """
    env = Environment(
        loader=FileSystemLoader(TEMPLATE_DIR),
        autoescape=False,  # Charts contain raw HTML that must not be escaped
    )
    template = env.get_template("report.html")

    # Extract data needed by the template
    perf = analysis_results["performance"]
    subj = analysis_results["subject_lines"]
    times = analysis_results["send_times"]
    health = analysis_results["list_health"]
    seg = analysis_results["segmentation"]

    # Convert cluster profiles to list of dicts for the template
    seg_profiles = seg["cluster_profiles"].to_dict("records")

    # Convert recommendations to dicts for Jinja2
    rec_dicts = [
        {
            "category": r.category,
            "priority": r.priority,
            "title": r.title,
            "description": r.description,
            "evidence": r.evidence,
            "impact_estimate": r.impact_estimate,
        }
        for r in recommendations
    ]

    context = {
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        # KPI / overall stats
        "overall": perf["overall_stats"],
        "trends": perf["trend_direction"],
        # Charts (raw HTML strings)
        "charts": charts,
        # Subject line tables
        "top_subjects": subj["top_subjects"],
        "bottom_subjects": subj["bottom_subjects"],
        # Send time highlights
        "best_hour": times["best_hour"],
        "best_dow": times["best_dow"],
        "best_hour_rate": times["best_hour_rate"],
        # List health flags
        "high_bounce_campaigns": health["high_bounce_campaigns"],
        "high_unsub_campaigns": health["high_unsub_campaigns"],
        # Segmentation
        "segment_profiles": seg_profiles,
        # Recommendations
        "recommendations": rec_dicts,
    }

    html = template.render(**context)

    output_path = os.path.join(OUTPUT_DIR, output_filename)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"[Report] HTML report saved to: {output_path}")
    return output_path
