"""
report.py - HTML Report Generator

Renders the Jinja2 HTML template with attribution data and Plotly charts
to produce a self-contained interactive HTML report.
"""

import os
from datetime import datetime
import pandas as pd
from jinja2 import Environment, FileSystemLoader


def generate_report(
    attribution_df: pd.DataFrame,
    path_analysis: dict,
    charts: dict[str, str],
    top_paths: pd.DataFrame,
    total_touchpoints: int,
    output_path: str,
) -> str:
    """
    Generate an interactive HTML report.

    Args:
        attribution_df: Attribution results with ROI columns.
        path_analysis: Path analysis dict from analyzer.
        charts: Dict of chart HTML divs from visualizations.
        top_paths: Top conversion paths DataFrame.
        total_touchpoints: Total number of touchpoints in the dataset.
        output_path: File path for the output HTML report.

    Returns:
        Absolute path to the generated report.
    """
    # Set up Jinja2 environment
    template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")
    env = Environment(loader=FileSystemLoader(template_dir))

    # Custom filters for formatting
    def format_number(value):
        """Format number with commas."""
        try:
            return f"{int(value):,}"
        except (ValueError, TypeError):
            return str(value)

    def round_num(value, decimals=1):
        """Round a number to specified decimals."""
        try:
            return round(float(value), decimals)
        except (ValueError, TypeError):
            return value

    env.filters["format_number"] = format_number
    env.filters["round_num"] = round_num

    template = env.get_template("report.html")

    # Sort attribution table for readability: by channel then model
    attribution_table = attribution_df.sort_values(
        ["channel", "model"]
    ).reset_index(drop=True)

    # Render template
    html_content = template.render(
        generated_date=datetime.now().strftime("%B %d, %Y at %I:%M %p"),
        total_journeys=path_analysis["total_journeys"],
        total_conversions=path_analysis["total_conversions"],
        conversion_rate=path_analysis["conversion_rate"],
        total_touchpoints=total_touchpoints,
        avg_touchpoints=path_analysis["avg_touchpoints"],
        avg_days=path_analysis["avg_days"],
        charts=charts,
        attribution_table=attribution_table,
        top_paths=top_paths,
    )

    # Write report
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    return os.path.abspath(output_path)
