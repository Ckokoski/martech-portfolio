"""
visualizations.py — Plotly Chart Generation

Creates interactive charts for the email campaign analysis report.
All functions return Plotly figure objects or their HTML representations.
"""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd

# ---------------------------------------------------------------------------
# Color palette — consistent brand colors across all charts
# ---------------------------------------------------------------------------
COLORS = {
    "primary": "#4A90D9",
    "secondary": "#50C878",
    "accent": "#FF6B6B",
    "warning": "#FFB347",
    "dark": "#2C3E50",
    "light": "#ECF0F1",
    "purple": "#9B59B6",
    "teal": "#1ABC9C",
}

SEGMENT_COLORS = {
    "Champions": "#50C878",
    "Active": "#4A90D9",
    "At-Risk": "#FFB347",
    "Dormant": "#FF6B6B",
}


def _fig_to_html(fig: go.Figure) -> str:
    """Convert a Plotly figure to an embeddable HTML div string."""
    return fig.to_html(full_html=False, include_plotlyjs=False)


def chart_performance_trends(monthly_df: pd.DataFrame) -> str:
    """Line chart showing open rate, click rate, bounce rate, unsub rate over time."""
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        subplot_titles=("Open & Click Rates Over Time", "Bounce & Unsubscribe Rates Over Time"),
        vertical_spacing=0.12,
    )

    # Top subplot: open & click rates
    fig.add_trace(go.Scatter(
        x=monthly_df["month"], y=monthly_df["avg_open_rate"],
        name="Open Rate", mode="lines+markers",
        line=dict(color=COLORS["primary"], width=3),
        marker=dict(size=8),
        hovertemplate="%{x}<br>Open Rate: %{y:.1%}<extra></extra>",
    ), row=1, col=1)

    fig.add_trace(go.Scatter(
        x=monthly_df["month"], y=monthly_df["avg_click_rate"],
        name="Click Rate", mode="lines+markers",
        line=dict(color=COLORS["secondary"], width=3),
        marker=dict(size=8),
        hovertemplate="%{x}<br>Click Rate: %{y:.1%}<extra></extra>",
    ), row=1, col=1)

    # Bottom subplot: bounce & unsub rates
    fig.add_trace(go.Scatter(
        x=monthly_df["month"], y=monthly_df["avg_bounce_rate"],
        name="Bounce Rate", mode="lines+markers",
        line=dict(color=COLORS["accent"], width=3),
        marker=dict(size=8),
        hovertemplate="%{x}<br>Bounce Rate: %{y:.1%}<extra></extra>",
    ), row=2, col=1)

    fig.add_trace(go.Scatter(
        x=monthly_df["month"], y=monthly_df["avg_unsub_rate"],
        name="Unsubscribe Rate", mode="lines+markers",
        line=dict(color=COLORS["warning"], width=3),
        marker=dict(size=8),
        hovertemplate="%{x}<br>Unsub Rate: %{y:.2%}<extra></extra>",
    ), row=2, col=1)

    fig.update_yaxes(tickformat=".1%", row=1, col=1)
    fig.update_yaxes(tickformat=".2%", row=2, col=1)
    fig.update_layout(
        height=550, template="plotly_white",
        legend=dict(orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5),
        margin=dict(l=60, r=30, t=60, b=60),
    )

    return _fig_to_html(fig)


def chart_revenue_trend(monthly_df: pd.DataFrame) -> str:
    """Bar chart of monthly revenue with campaign count overlay."""
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(go.Bar(
        x=monthly_df["month"], y=monthly_df["total_revenue"],
        name="Revenue ($)",
        marker_color=COLORS["secondary"],
        opacity=0.8,
        hovertemplate="%{x}<br>Revenue: $%{y:,.0f}<extra></extra>",
    ), secondary_y=False)

    fig.add_trace(go.Scatter(
        x=monthly_df["month"], y=monthly_df["campaigns_count"],
        name="# Campaigns", mode="lines+markers",
        line=dict(color=COLORS["dark"], width=2, dash="dot"),
        marker=dict(size=7),
        hovertemplate="%{x}<br>Campaigns: %{y}<extra></extra>",
    ), secondary_y=True)

    fig.update_yaxes(title_text="Revenue ($)", tickprefix="$", tickformat=",", secondary_y=False)
    fig.update_yaxes(title_text="Campaigns", secondary_y=True)
    fig.update_layout(
        title="Monthly Revenue & Campaign Volume",
        height=400, template="plotly_white",
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
        margin=dict(l=60, r=60, t=60, b=60),
    )

    return _fig_to_html(fig)


def chart_subject_line_length(length_perf: pd.DataFrame) -> str:
    """Bar chart showing open rate by subject line length bucket."""
    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=length_perf["length_bucket"].astype(str),
        y=length_perf["avg_open_rate"],
        text=[f"{r:.1%}" for r in length_perf["avg_open_rate"]],
        textposition="outside",
        marker_color=COLORS["primary"],
        hovertemplate="Length: %{x} chars<br>Avg Open Rate: %{y:.1%}<br>Campaigns: %{customdata}<extra></extra>",
        customdata=length_perf["count"],
    ))

    fig.update_layout(
        title="Open Rate by Subject Line Length",
        xaxis_title="Subject Line Length (characters)",
        yaxis_title="Average Open Rate",
        yaxis_tickformat=".0%",
        height=380, template="plotly_white",
        margin=dict(l=60, r=30, t=60, b=60),
    )

    return _fig_to_html(fig)


def chart_subject_features(feature_impact: dict) -> str:
    """Grouped bar chart comparing open rates with/without each subject feature."""
    features = []
    with_vals = []
    without_vals = []
    lifts = []

    label_map = {
        "has_personalization": "Personalization",
        "has_emoji": "Emoji",
        "has_urgency": "Urgency Words",
    }

    for key, data in feature_impact.items():
        features.append(label_map.get(key, key))
        with_vals.append(data["with"])
        without_vals.append(data["without"])
        lifts.append(data["lift"])

    fig = go.Figure()

    fig.add_trace(go.Bar(
        name="With Feature", x=features, y=with_vals,
        marker_color=COLORS["secondary"],
        text=[f"{v:.1%}" for v in with_vals], textposition="outside",
    ))
    fig.add_trace(go.Bar(
        name="Without Feature", x=features, y=without_vals,
        marker_color=COLORS["light"],
        text=[f"{v:.1%}" for v in without_vals], textposition="outside",
        marker_line=dict(color=COLORS["dark"], width=1),
    ))

    fig.update_layout(
        title="Subject Line Feature Impact on Open Rate",
        yaxis_title="Average Open Rate",
        yaxis_tickformat=".0%",
        barmode="group",
        height=380, template="plotly_white",
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
        margin=dict(l=60, r=30, t=60, b=60),
    )

    return _fig_to_html(fig)


def chart_send_time_heatmap(heatmap_df: pd.DataFrame) -> str:
    """Heatmap of open rate by send hour and day of week."""
    fig = go.Figure(data=go.Heatmap(
        z=heatmap_df.values,
        x=heatmap_df.columns.tolist(),
        y=[f"{h}:00" for h in heatmap_df.index],
        colorscale="RdYlGn",
        text=[[f"{v:.1%}" if pd.notna(v) else "" for v in row] for row in heatmap_df.values],
        texttemplate="%{text}",
        hovertemplate="Day: %{x}<br>Hour: %{y}<br>Open Rate: %{z:.1%}<extra></extra>",
        colorbar=dict(title="Open Rate", tickformat=".0%"),
    ))

    fig.update_layout(
        title="Open Rate by Send Time (Hour x Day of Week)",
        xaxis_title="Day of Week",
        yaxis_title="Send Hour",
        height=500, template="plotly_white",
        yaxis=dict(autorange="reversed"),
        margin=dict(l=70, r=30, t=60, b=60),
    )

    return _fig_to_html(fig)


def chart_hourly_performance(hour_perf: pd.DataFrame) -> str:
    """Bar chart of open rate by hour of day."""
    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=[f"{h}:00" for h in hour_perf["send_hour"]],
        y=hour_perf["avg_open_rate"],
        marker_color=[
            COLORS["secondary"] if r >= hour_perf["avg_open_rate"].quantile(0.75)
            else COLORS["accent"] if r <= hour_perf["avg_open_rate"].quantile(0.25)
            else COLORS["primary"]
            for r in hour_perf["avg_open_rate"]
        ],
        hovertemplate="Hour: %{x}<br>Avg Open Rate: %{y:.1%}<br>Campaigns: %{customdata}<extra></extra>",
        customdata=hour_perf["count"],
    ))

    fig.update_layout(
        title="Open Rate by Hour of Day",
        xaxis_title="Send Hour",
        yaxis_title="Average Open Rate",
        yaxis_tickformat=".0%",
        height=380, template="plotly_white",
        margin=dict(l=60, r=30, t=60, b=60),
    )

    return _fig_to_html(fig)


def chart_list_health(rolling_df: pd.DataFrame) -> str:
    """Area chart of bounce rate and unsubscribe rate with rolling averages."""
    df = rolling_df.copy()
    df["send_date"] = pd.to_datetime(df["send_date"])
    df = df.sort_values("send_date")

    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        subplot_titles=("Bounce Rate Trend", "Unsubscribe Rate Trend"),
        vertical_spacing=0.12,
    )

    # Bounce rate
    fig.add_trace(go.Scatter(
        x=df["send_date"], y=df["bounce_rate"],
        name="Bounce Rate", mode="markers",
        marker=dict(color=COLORS["accent"], size=5, opacity=0.5),
    ), row=1, col=1)
    fig.add_trace(go.Scatter(
        x=df["send_date"], y=df["bounce_rate_rolling"],
        name="Bounce (5-campaign avg)", mode="lines",
        line=dict(color=COLORS["accent"], width=3),
    ), row=1, col=1)

    # Unsub rate
    fig.add_trace(go.Scatter(
        x=df["send_date"], y=df["unsubscribe_rate"],
        name="Unsub Rate", mode="markers",
        marker=dict(color=COLORS["warning"], size=5, opacity=0.5),
    ), row=2, col=1)
    fig.add_trace(go.Scatter(
        x=df["send_date"], y=df["unsub_rate_rolling"],
        name="Unsub (5-campaign avg)", mode="lines",
        line=dict(color=COLORS["warning"], width=3),
    ), row=2, col=1)

    fig.update_yaxes(tickformat=".1%", row=1, col=1)
    fig.update_yaxes(tickformat=".2%", row=2, col=1)
    fig.update_layout(
        height=500, template="plotly_white",
        legend=dict(orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5),
        margin=dict(l=60, r=30, t=60, b=60),
    )

    return _fig_to_html(fig)


def chart_subscriber_segments(cluster_profiles: pd.DataFrame) -> str:
    """Donut chart of subscriber segment distribution + profile comparison."""
    fig = make_subplots(
        rows=1, cols=2,
        specs=[[{"type": "pie"}, {"type": "bar"}]],
        subplot_titles=("Segment Distribution", "Segment Engagement Profiles"),
        column_widths=[0.4, 0.6],
    )

    colors = [SEGMENT_COLORS.get(name, COLORS["primary"]) for name in cluster_profiles["segment_name"]]

    # Donut chart
    fig.add_trace(go.Pie(
        labels=cluster_profiles["segment_name"],
        values=cluster_profiles["count"],
        hole=0.45,
        marker=dict(colors=colors),
        textinfo="label+percent",
        hovertemplate="%{label}<br>Count: %{value:,}<br>Share: %{percent}<extra></extra>",
    ), row=1, col=1)

    # Grouped bar: open rate + click rate per segment
    fig.add_trace(go.Bar(
        x=cluster_profiles["segment_name"],
        y=cluster_profiles["avg_open_rate"],
        name="Avg Open Rate",
        marker_color=COLORS["primary"],
        text=[f"{v:.0%}" for v in cluster_profiles["avg_open_rate"]],
        textposition="outside",
    ), row=1, col=2)

    fig.add_trace(go.Bar(
        x=cluster_profiles["segment_name"],
        y=cluster_profiles["avg_click_rate"],
        name="Avg Click Rate",
        marker_color=COLORS["teal"],
        text=[f"{v:.0%}" for v in cluster_profiles["avg_click_rate"]],
        textposition="outside",
    ), row=1, col=2)

    fig.update_layout(
        height=420, template="plotly_white",
        legend=dict(orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5),
        margin=dict(l=40, r=30, t=60, b=60),
    )
    fig.update_yaxes(tickformat=".0%", row=1, col=2)

    return _fig_to_html(fig)


def chart_campaign_scatter(campaigns_df: pd.DataFrame) -> str:
    """Scatter plot of open rate vs click rate, sized by revenue, colored by type."""
    fig = px.scatter(
        campaigns_df,
        x="open_rate", y="click_rate",
        size="revenue", size_max=25,
        color="campaign_type",
        hover_name="campaign_name",
        hover_data={
            "open_rate": ":.1%",
            "click_rate": ":.1%",
            "revenue": ":$,.0f",
            "campaign_type": True,
        },
        labels={
            "open_rate": "Open Rate",
            "click_rate": "Click Rate",
            "revenue": "Revenue",
            "campaign_type": "Type",
        },
        title="Campaign Performance: Open Rate vs Click Rate (sized by Revenue)",
    )

    fig.update_layout(
        height=450, template="plotly_white",
        xaxis_tickformat=".0%", yaxis_tickformat=".0%",
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
        margin=dict(l=60, r=30, t=60, b=60),
    )

    return _fig_to_html(fig)


def generate_all_charts(analysis_results: dict, campaigns_df: pd.DataFrame) -> dict:
    """Generate all charts and return a dict of chart name -> HTML string."""
    perf = analysis_results["performance"]
    subj = analysis_results["subject_lines"]
    times = analysis_results["send_times"]
    health = analysis_results["list_health"]
    seg = analysis_results["segmentation"]

    print("[Viz] Generating performance trend charts...")
    charts = {
        "performance_trends": chart_performance_trends(perf["monthly_df"]),
        "revenue_trend": chart_revenue_trend(perf["monthly_df"]),
        "subject_length": chart_subject_line_length(subj["length_performance"]),
        "subject_features": chart_subject_features(subj["feature_impact"]),
        "send_time_heatmap": chart_send_time_heatmap(times["heatmap"]),
        "hourly_performance": chart_hourly_performance(times["hour_performance"]),
        "list_health": chart_list_health(health["rolling_df"]),
        "subscriber_segments": chart_subscriber_segments(seg["cluster_profiles"]),
        "campaign_scatter": chart_campaign_scatter(campaigns_df),
    }

    print(f"[Viz] Generated {len(charts)} interactive charts.")
    return charts
