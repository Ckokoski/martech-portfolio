"""
visualizations.py - Plotly Chart Generator for Attribution Engine

Creates interactive Plotly charts embedded as self-contained HTML divs:
1. Attribution model comparison (grouped bar chart)
2. Sankey diagram (customer journey flow)
3. Channel ROI scatter plot
4. Time to conversion distribution
5. Touchpoints to conversion distribution
6. Markov chain transition heatmap
"""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np

# Consistent color palette for channels
CHANNEL_COLORS = {
    "Paid Search": "#1f77b4",
    "Organic Search": "#2ca02c",
    "Email": "#ff7f0e",
    "Social": "#d62728",
    "Display": "#9467bd",
    "Direct": "#8c564b",
    "Referral": "#e377c2",
    "Content Marketing": "#17becf",
}

MODEL_COLORS = {
    "First Touch": "#636EFA",
    "Last Touch": "#EF553B",
    "Linear": "#00CC96",
    "Time Decay": "#AB63FA",
    "Markov Chain": "#FFA15A",
}


def create_attribution_comparison_chart(attribution_df: pd.DataFrame) -> str:
    """
    Grouped bar chart comparing attribution credit across models.

    Each channel has one bar per model, showing credit percentage.
    Returns HTML div string.
    """
    fig = go.Figure()

    models = attribution_df["model"].unique()
    channels = sorted(attribution_df["channel"].unique())

    for model in models:
        model_data = attribution_df[attribution_df["model"] == model]
        # Ensure all channels present, fill missing with 0
        model_data = model_data.set_index("channel").reindex(channels).fillna(0).reset_index()

        fig.add_trace(go.Bar(
            name=model,
            x=model_data["channel"],
            y=model_data["credit_pct"],
            marker_color=MODEL_COLORS.get(model, "#999999"),
            text=model_data["credit_pct"].apply(lambda x: f"{x:.1f}%"),
            textposition="auto",
            textfont_size=9,
        ))

    fig.update_layout(
        title=dict(
            text="Attribution Model Comparison: Credit % by Channel",
            font=dict(size=18),
        ),
        barmode="group",
        xaxis_title="Channel",
        yaxis_title="Credit %",
        yaxis=dict(range=[0, max(attribution_df["credit_pct"]) * 1.15]),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5,
        ),
        template="plotly_white",
        height=500,
        margin=dict(t=80, b=80),
    )

    return fig.to_html(full_html=False, include_plotlyjs=False)


def create_sankey_diagram(sankey_data: dict) -> str:
    """
    Sankey diagram showing customer journey flow between channels.

    Nodes represent channel-position pairs; links show transition volume.
    Returns HTML div string.
    """
    # Assign colors to nodes based on channel name
    node_colors = []
    for label in sankey_data["labels"]:
        if label == "Conversion":
            node_colors.append("#2ecc71")
        else:
            channel_name = label.rsplit(" (", 1)[0]
            node_colors.append(CHANNEL_COLORS.get(channel_name, "#999999"))

    # Semi-transparent link colors based on source
    link_colors = []
    for src_idx in sankey_data["sources"]:
        base = node_colors[src_idx]
        # Convert hex to rgba with transparency
        r, g, b = int(base[1:3], 16), int(base[3:5], 16), int(base[5:7], 16)
        link_colors.append(f"rgba({r},{g},{b},0.3)")

    fig = go.Figure(go.Sankey(
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color="black", width=0.5),
            label=sankey_data["labels"],
            color=node_colors,
        ),
        link=dict(
            source=sankey_data["sources"],
            target=sankey_data["targets"],
            value=sankey_data["values"],
            color=link_colors,
        ),
    ))

    fig.update_layout(
        title=dict(
            text="Customer Journey Flow (Converting Journeys)",
            font=dict(size=18),
        ),
        template="plotly_white",
        height=600,
        margin=dict(t=60, b=30),
    )

    return fig.to_html(full_html=False, include_plotlyjs=False)


def create_roi_scatter(attribution_df: pd.DataFrame, spend_df: pd.DataFrame) -> str:
    """
    Scatter plot: spend vs attributed revenue, sized by conversions.
    One point per channel, using Markov Chain model for attributed values.
    Returns HTML div string.
    """
    # Use Markov Chain attribution for the scatter
    markov_data = attribution_df[attribution_df["model"] == "Markov Chain"].copy()
    if "total_spend" not in markov_data.columns:
        markov_data = markov_data.merge(
            spend_df[["channel", "total_spend"]], on="channel", how="left"
        )

    fig = go.Figure()

    for _, row in markov_data.iterrows():
        channel = row["channel"]
        fig.add_trace(go.Scatter(
            x=[row["total_spend"]],
            y=[row["attributed_revenue"]],
            mode="markers+text",
            marker=dict(
                size=max(10, row["attributed_conversions"] / 15),
                color=CHANNEL_COLORS.get(channel, "#999999"),
                line=dict(width=1, color="white"),
                opacity=0.85,
            ),
            text=[channel],
            textposition="top center",
            textfont=dict(size=10),
            name=channel,
            hovertemplate=(
                f"<b>{channel}</b><br>"
                f"Spend: ${row['total_spend']:,.0f}<br>"
                f"Revenue: ${row['attributed_revenue']:,.0f}<br>"
                f"Conversions: {row['attributed_conversions']:,.0f}<br>"
                f"ROI: {row['roi']:.2f}x"
                "<extra></extra>"
            ),
        ))

    # Add break-even line (revenue = spend)
    max_val = max(
        markov_data["total_spend"].max(),
        markov_data["attributed_revenue"].max(),
    ) * 1.1
    fig.add_trace(go.Scatter(
        x=[0, max_val],
        y=[0, max_val],
        mode="lines",
        line=dict(dash="dash", color="gray", width=1),
        name="Break-even (ROI = 1.0x)",
        showlegend=True,
    ))

    fig.update_layout(
        title=dict(
            text="Channel ROI: Spend vs Attributed Revenue (Markov Chain Model)",
            font=dict(size=18),
        ),
        xaxis_title="Total Spend (6 months)",
        yaxis_title="Attributed Revenue",
        xaxis=dict(tickformat="$,.0f"),
        yaxis=dict(tickformat="$,.0f"),
        template="plotly_white",
        height=500,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5,
        ),
        margin=dict(t=80, b=60),
    )

    return fig.to_html(full_html=False, include_plotlyjs=False)


def create_time_to_conversion_chart(days_distribution: pd.DataFrame) -> str:
    """
    Bar chart showing distribution of days to conversion.
    Returns HTML div string.
    """
    fig = go.Figure(go.Bar(
        x=days_distribution["period"],
        y=days_distribution["count"],
        marker_color="#636EFA",
        text=days_distribution["count"].astype(int),
        textposition="auto",
    ))

    fig.update_layout(
        title=dict(
            text="Time to Conversion Distribution",
            font=dict(size=18),
        ),
        xaxis_title="Days to Conversion",
        yaxis_title="Number of Journeys",
        template="plotly_white",
        height=400,
        margin=dict(t=60, b=60),
    )

    return fig.to_html(full_html=False, include_plotlyjs=False)


def create_touchpoints_distribution_chart(touchpoint_dist: pd.DataFrame) -> str:
    """
    Bar chart showing distribution of touchpoints per converting journey.
    Returns HTML div string.
    """
    fig = go.Figure(go.Bar(
        x=touchpoint_dist["touchpoints"],
        y=touchpoint_dist["count"],
        marker_color="#00CC96",
        text=touchpoint_dist["count"].astype(int),
        textposition="auto",
    ))

    fig.update_layout(
        title=dict(
            text="Touchpoints to Conversion Distribution",
            font=dict(size=18),
        ),
        xaxis_title="Number of Touchpoints",
        yaxis_title="Number of Journeys",
        xaxis=dict(dtick=1),
        template="plotly_white",
        height=400,
        margin=dict(t=60, b=60),
    )

    return fig.to_html(full_html=False, include_plotlyjs=False)


def create_markov_heatmap(transition_matrix_df: pd.DataFrame) -> str:
    """
    Heatmap of the Markov chain transition probability matrix.
    Returns HTML div string.
    """
    # Filter to channel-to-channel transitions for readability
    # Keep all states for the full picture
    labels = transition_matrix_df.index.tolist()
    values = transition_matrix_df.values

    # Custom text annotations showing probabilities
    text = [[f"{v:.2f}" if v > 0.01 else "" for v in row] for row in values]

    fig = go.Figure(go.Heatmap(
        z=values,
        x=labels,
        y=labels,
        colorscale="YlOrRd",
        text=text,
        texttemplate="%{text}",
        textfont=dict(size=9),
        hovertemplate=(
            "From: %{y}<br>"
            "To: %{x}<br>"
            "Probability: %{z:.3f}"
            "<extra></extra>"
        ),
        colorbar=dict(title="Probability"),
    ))

    fig.update_layout(
        title=dict(
            text="Markov Chain Transition Probability Heatmap",
            font=dict(size=18),
        ),
        xaxis_title="To State",
        yaxis_title="From State",
        xaxis=dict(tickangle=45),
        template="plotly_white",
        height=600,
        width=800,
        margin=dict(t=60, b=120, l=140),
    )

    return fig.to_html(full_html=False, include_plotlyjs=False)


def create_all_charts(
    attribution_df: pd.DataFrame,
    spend_df: pd.DataFrame,
    path_analysis: dict,
    sankey_data: dict,
    transition_matrix_df: pd.DataFrame,
) -> dict[str, str]:
    """
    Generate all charts and return as a dict of HTML div strings.

    Args:
        attribution_df: Combined attribution results with ROI.
        spend_df: Channel spend data.
        path_analysis: Output from analyzer.analyze_paths().
        sankey_data: Output from analyzer.build_sankey_data().
        transition_matrix_df: Markov transition matrix DataFrame.

    Returns:
        Dict mapping chart names to HTML div strings.
    """
    print("  Generating attribution comparison chart...")
    charts = {
        "attribution_comparison": create_attribution_comparison_chart(attribution_df),
    }

    print("  Generating Sankey diagram...")
    charts["sankey"] = create_sankey_diagram(sankey_data)

    print("  Generating ROI scatter plot...")
    charts["roi_scatter"] = create_roi_scatter(attribution_df, spend_df)

    print("  Generating time-to-conversion chart...")
    charts["time_distribution"] = create_time_to_conversion_chart(
        path_analysis["days_distribution"]
    )

    print("  Generating touchpoints distribution chart...")
    charts["touchpoint_distribution"] = create_touchpoints_distribution_chart(
        path_analysis["touchpoint_distribution"]
    )

    print("  Generating Markov heatmap...")
    charts["markov_heatmap"] = create_markov_heatmap(transition_matrix_df)

    return charts
