"""
report.py — Generates a self-contained HTML report from model results.

Uses Jinja2 templating to combine KPIs, charts, and lead data into
a single HTML file that can be opened in any browser.
"""

import json
from datetime import datetime
from pathlib import Path

import plotly.io as pio
from jinja2 import Environment, FileSystemLoader

import pandas as pd


def _fig_to_js(fig, div_id: str) -> str:
    """Convert a Plotly figure to a JavaScript snippet that renders it."""
    fig_json = pio.to_json(fig)
    return f"Plotly.newPlot('{div_id}', {fig_json}.data, {fig_json}.layout, {{responsive: true}});\n"


def generate_report(
    scored_df: pd.DataFrame,
    metrics: dict,
    charts: dict,
    output_dir: str = "data",
) -> Path:
    """
    Generate a self-contained HTML report.

    Parameters
    ----------
    scored_df : pd.DataFrame
        Full scored lead dataset.
    metrics : dict
        Model evaluation metrics.
    charts : dict
        Dictionary of chart_name -> Plotly figure.
    output_dir : str
        Directory to write the report file.

    Returns
    -------
    Path
        Path to the generated HTML report.
    """
    # ── Prepare template variables ───────────────────────────────────────
    cm = metrics["confusion_matrix"]

    # Top leads for the table
    top_leads = scored_df.head(20).to_dict("records")

    # Tier counts from full dataset
    tier_counts = scored_df["lead_tier"].value_counts()
    sql_count = tier_counts.get("SQL", 0)
    mql_count = tier_counts.get("MQL", 0)

    # ── Build chart JavaScript ───────────────────────────────────────────
    chart_js_parts = []
    chart_id_map = {
        "score_distribution": "chart_score_distribution",
        "roc_curve": "chart_roc_curve",
        "precision_recall": "chart_precision_recall",
        "shap_importance": "chart_shap_importance",
        "shap_waterfall_high": "chart_shap_waterfall_high",
        "shap_waterfall_low": "chart_shap_waterfall_low",
        "calibration": "chart_calibration",
        "lead_source_quality": "chart_lead_source_quality",
    }

    for chart_name, div_id in chart_id_map.items():
        if chart_name in charts:
            chart_js_parts.append(_fig_to_js(charts[chart_name], div_id))

    chart_js = "\n".join(chart_js_parts)

    # ── Render template ──────────────────────────────────────────────────
    template_dir = Path(__file__).parent / "templates"
    env = Environment(loader=FileSystemLoader(str(template_dir)))
    template = env.get_template("report.html")

    html = template.render(
        generated_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        total_leads=f"{len(scored_df):,}",
        auc_roc=f"{metrics['auc_roc']:.3f}",
        avg_precision=f"{metrics['avg_precision']:.3f}",
        f1_score=f"{metrics['f1_score']:.3f}",
        sql_count=f"{sql_count:,}",
        mql_count=f"{mql_count:,}",
        sql_threshold=metrics["sql_threshold"],
        mql_threshold=metrics["mql_threshold"],
        conversion_rate=f"{scored_df['converted'].mean():.1%}",
        cm_tn=f"{cm[0][0]:,}",
        cm_fp=f"{cm[0][1]:,}",
        cm_fn=f"{cm[1][0]:,}",
        cm_tp=f"{cm[1][1]:,}",
        top_leads=top_leads,
        chart_js=chart_js,
    )

    # ── Write output ─────────────────────────────────────────────────────
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    report_path = out_path / "leadscore_report.html"
    report_path.write_text(html, encoding="utf-8")

    print(f"  -> Report saved to {report_path}")
    return report_path


if __name__ == "__main__":
    print("Run via app.py for full pipeline.")
