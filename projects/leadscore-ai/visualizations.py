"""
visualizations.py — Generates all Plotly charts for the lead scoring report.

Each function returns a Plotly figure object that can be serialized to HTML
for embedding in the final report.
"""

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots


# ── Shared styling ───────────────────────────────────────────────────────────

COLORS = {
    "primary": "#6366F1",      # Indigo
    "secondary": "#EC4899",    # Pink
    "success": "#10B981",      # Emerald
    "warning": "#F59E0B",      # Amber
    "danger": "#EF4444",       # Red
    "info": "#3B82F6",         # Blue
    "mql_line": "#F59E0B",     # Amber for MQL threshold
    "sql_line": "#EF4444",     # Red for SQL threshold
    "bg": "#FFFFFF",
    "grid": "#F1F5F9",
    "text": "#1E293B",
}

LAYOUT_DEFAULTS = dict(
    font=dict(family="Inter, -apple-system, sans-serif", color=COLORS["text"]),
    paper_bgcolor=COLORS["bg"],
    plot_bgcolor=COLORS["bg"],
    margin=dict(l=60, r=30, t=50, b=50),
    hoverlabel=dict(bgcolor="white", font_size=12),
)


def _apply_layout(fig: go.Figure, **kwargs) -> go.Figure:
    """Apply consistent styling to a figure."""
    fig.update_layout(**LAYOUT_DEFAULTS, **kwargs)
    fig.update_xaxes(gridcolor=COLORS["grid"], zeroline=False)
    fig.update_yaxes(gridcolor=COLORS["grid"], zeroline=False)
    return fig


# ── Chart 1: Lead Score Distribution ────────────────────────────────────────

def plot_score_distribution(
    scores: np.ndarray,
    mql_threshold: int = 50,
    sql_threshold: int = 75,
) -> go.Figure:
    """
    Histogram of lead scores with MQL/SQL threshold lines.
    """
    fig = go.Figure()

    fig.add_trace(go.Histogram(
        x=scores,
        nbinsx=50,
        marker_color=COLORS["primary"],
        opacity=0.8,
        name="Lead Score",
        hovertemplate="Score: %{x:.0f}<br>Count: %{y}<extra></extra>",
    ))

    # MQL threshold line
    fig.add_vline(
        x=mql_threshold, line_dash="dash", line_color=COLORS["mql_line"],
        line_width=2,
        annotation_text=f"MQL ({mql_threshold})",
        annotation_position="top",
        annotation_font_color=COLORS["mql_line"],
    )

    # SQL threshold line
    fig.add_vline(
        x=sql_threshold, line_dash="dash", line_color=COLORS["sql_line"],
        line_width=2,
        annotation_text=f"SQL ({sql_threshold})",
        annotation_position="top",
        annotation_font_color=COLORS["sql_line"],
    )

    _apply_layout(
        fig,
        title="Lead Score Distribution",
        xaxis_title="Lead Score (0-100)",
        yaxis_title="Number of Leads",
        showlegend=False,
    )
    return fig


# ── Chart 2: ROC Curve ──────────────────────────────────────────────────────

def plot_roc_curve(fpr: np.ndarray, tpr: np.ndarray, auc: float) -> go.Figure:
    """ROC curve with AUC annotation."""
    fig = go.Figure()

    # Random baseline
    fig.add_trace(go.Scatter(
        x=[0, 1], y=[0, 1],
        mode="lines", line=dict(dash="dash", color="#CBD5E1", width=1),
        name="Random (AUC=0.50)",
        showlegend=True,
    ))

    # ROC curve
    fig.add_trace(go.Scatter(
        x=fpr, y=tpr,
        mode="lines",
        line=dict(color=COLORS["primary"], width=2.5),
        name=f"Model (AUC={auc:.3f})",
        fill="tonexty",
        fillcolor="rgba(99, 102, 241, 0.1)",
        hovertemplate="FPR: %{x:.3f}<br>TPR: %{y:.3f}<extra></extra>",
    ))

    _apply_layout(
        fig,
        title="ROC Curve",
        xaxis_title="False Positive Rate",
        yaxis_title="True Positive Rate",
        xaxis=dict(range=[0, 1], constrain="domain"),
        yaxis=dict(range=[0, 1], scaleanchor="x"),
        legend=dict(x=0.55, y=0.1),
    )
    return fig


# ── Chart 3: Precision-Recall Curve ─────────────────────────────────────────

def plot_precision_recall(
    precision: np.ndarray,
    recall: np.ndarray,
    avg_precision: float,
) -> go.Figure:
    """Precision-Recall curve."""
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=recall, y=precision,
        mode="lines",
        line=dict(color=COLORS["secondary"], width=2.5),
        name=f"AP={avg_precision:.3f}",
        fill="tozeroy",
        fillcolor="rgba(236, 72, 153, 0.1)",
        hovertemplate="Recall: %{x:.3f}<br>Precision: %{y:.3f}<extra></extra>",
    ))

    _apply_layout(
        fig,
        title="Precision-Recall Curve",
        xaxis_title="Recall",
        yaxis_title="Precision",
        xaxis=dict(range=[0, 1]),
        yaxis=dict(range=[0, 1]),
        legend=dict(x=0.05, y=0.1),
    )
    return fig


# ── Chart 4: SHAP Feature Importance ────────────────────────────────────────

def plot_shap_importance(importance_df: pd.DataFrame) -> go.Figure:
    """Horizontal bar chart of top features by mean |SHAP value|."""
    # Reverse for horizontal bar (top feature at top)
    df = importance_df.sort_values("mean_abs_shap", ascending=True)

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=df["mean_abs_shap"],
        y=df["feature"],
        orientation="h",
        marker_color=COLORS["primary"],
        opacity=0.85,
        hovertemplate="%{y}<br>Mean |SHAP|: %{x:.4f}<extra></extra>",
    ))

    _apply_layout(
        fig,
        title="Top 15 Features — SHAP Importance",
        xaxis_title="Mean |SHAP Value|",
        yaxis_title="",
        height=500,
        showlegend=False,
    )
    return fig


# ── Chart 5: SHAP Waterfall Chart ───────────────────────────────────────────

def plot_shap_waterfall(
    explanation: dict,
    top_n: int = 12,
) -> go.Figure:
    """
    Waterfall chart showing how individual features push the prediction
    from the base value to the final score.
    """
    exp_df = explanation["explanation_df"].head(top_n).copy()
    base = explanation["expected_value"]
    score = explanation["score"]
    label = "High-Score Lead" if explanation["score_type"] == "high" else "Low-Score Lead"

    # Sort by absolute value, reversed for display
    exp_df = exp_df.sort_values("shap_value", key=abs, ascending=True)

    colors = [
        COLORS["success"] if v > 0 else COLORS["danger"]
        for v in exp_df["shap_value"]
    ]

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=exp_df["shap_value"],
        y=exp_df["feature"],
        orientation="h",
        marker_color=colors,
        hovertemplate=(
            "%{y}<br>"
            "SHAP: %{x:.4f}<br>"
            "<extra></extra>"
        ),
    ))

    _apply_layout(
        fig,
        title=f"SHAP Waterfall — {label} (Score: {score:.1f})",
        xaxis_title="SHAP Value (impact on prediction)",
        yaxis_title="",
        height=450,
        showlegend=False,
        annotations=[
            dict(
                x=0.02, y=1.05, xref="paper", yref="paper",
                text=f"Base value: {base:.4f}",
                showarrow=False, font=dict(size=11, color="#64748B"),
            ),
        ],
    )
    return fig


# ── Chart 6: Calibration Plot ───────────────────────────────────────────────

def plot_calibration(
    cal_fraction: np.ndarray,
    cal_mean_predicted: np.ndarray,
) -> go.Figure:
    """Score vs actual conversion rate calibration plot."""
    fig = go.Figure()

    # Perfect calibration line
    fig.add_trace(go.Scatter(
        x=[0, 1], y=[0, 1],
        mode="lines", line=dict(dash="dash", color="#CBD5E1", width=1),
        name="Perfectly Calibrated",
    ))

    # Actual calibration
    fig.add_trace(go.Scatter(
        x=cal_mean_predicted,
        y=cal_fraction,
        mode="lines+markers",
        line=dict(color=COLORS["info"], width=2.5),
        marker=dict(size=8, color=COLORS["info"]),
        name="Model Calibration",
        hovertemplate=(
            "Predicted: %{x:.2%}<br>"
            "Actual: %{y:.2%}<extra></extra>"
        ),
    ))

    _apply_layout(
        fig,
        title="Calibration Plot — Predicted vs Actual Conversion",
        xaxis_title="Mean Predicted Probability",
        yaxis_title="Actual Conversion Rate",
        xaxis=dict(range=[0, 1]),
        yaxis=dict(range=[0, 1]),
        legend=dict(x=0.05, y=0.95),
    )
    return fig


# ── Chart 7: Lead Source Quality ─────────────────────────────────────────────

def plot_lead_source_quality(scored_df: pd.DataFrame) -> go.Figure:
    """Average lead score by acquisition channel."""
    source_stats = (
        scored_df.groupby("lead_source")["lead_score"]
        .agg(["mean", "count"])
        .sort_values("mean", ascending=True)
        .reset_index()
    )

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=source_stats["mean"],
        y=source_stats["lead_source"],
        orientation="h",
        marker_color=COLORS["success"],
        opacity=0.85,
        text=[f"{v:.1f} (n={c:,})" for v, c in zip(source_stats["mean"], source_stats["count"])],
        textposition="outside",
        hovertemplate=(
            "%{y}<br>"
            "Avg Score: %{x:.1f}<br>"
            "<extra></extra>"
        ),
    ))

    _apply_layout(
        fig,
        title="Lead Source Quality — Average Score by Channel",
        xaxis_title="Average Lead Score",
        yaxis_title="",
        height=450,
        showlegend=False,
    )
    return fig


def generate_all_charts(
    scored_df: pd.DataFrame,
    metrics: dict,
    results: dict,
    shap_importance: pd.DataFrame,
    high_explanation: dict,
    low_explanation: dict,
) -> dict:
    """
    Generate all charts and return as a dictionary of Plotly figures.

    Parameters
    ----------
    scored_df : pd.DataFrame
        Full dataset with lead_score column.
    metrics : dict
        Output from model.evaluate_model().
    results : dict
        Output from model.train_model().
    shap_importance : pd.DataFrame
        Top features from explainer.get_global_importance().
    high_explanation : dict
        SHAP explanation for a high-score lead.
    low_explanation : dict
        SHAP explanation for a low-score lead.

    Returns
    -------
    dict
        Chart name -> Plotly figure.
    """
    print("\n  Generating charts...")

    charts = {}

    charts["score_distribution"] = plot_score_distribution(
        scored_df["lead_score"].values,
        metrics["mql_threshold"],
        metrics["sql_threshold"],
    )
    print("    [1/7] Score distribution")

    charts["roc_curve"] = plot_roc_curve(
        metrics["fpr"], metrics["tpr"], metrics["auc_roc"],
    )
    print("    [2/7] ROC curve")

    charts["precision_recall"] = plot_precision_recall(
        metrics["precision_curve"], metrics["recall_curve"],
        metrics["avg_precision"],
    )
    print("    [3/7] Precision-recall curve")

    charts["shap_importance"] = plot_shap_importance(shap_importance)
    print("    [4/7] SHAP importance")

    charts["shap_waterfall_high"] = plot_shap_waterfall(high_explanation)
    print("    [5/7] SHAP waterfall (high-score)")

    charts["shap_waterfall_low"] = plot_shap_waterfall(low_explanation)
    print("    [6/7] SHAP waterfall (low-score)")

    charts["calibration"] = plot_calibration(
        metrics["cal_fraction"], metrics["cal_mean_predicted"],
    )
    print("    [7/7] Calibration plot")

    charts["lead_source_quality"] = plot_lead_source_quality(scored_df)
    print("    [8/8] Lead source quality")

    return charts
