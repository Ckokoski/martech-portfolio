"""
analyzer.py - Attribution Model Orchestrator & Path Analysis

Runs all five attribution models against the touchpoint data and
performs path analysis to generate comprehensive marketing insights.
"""

import pandas as pd
import numpy as np
from models import (
    first_touch_attribution,
    last_touch_attribution,
    linear_attribution,
    time_decay_attribution,
    markov_attribution,
)


def run_all_models(touchpoints_df: pd.DataFrame) -> pd.DataFrame:
    """
    Run all five attribution models and combine results.

    Args:
        touchpoints_df: Full touchpoint dataset.

    Returns:
        Combined DataFrame with columns [channel, attributed_conversions,
        attributed_revenue, model] for all models.
    """
    print("  Running First-Touch model...")
    ft = first_touch_attribution(touchpoints_df)

    print("  Running Last-Touch model...")
    lt = last_touch_attribution(touchpoints_df)

    print("  Running Linear model...")
    lin = linear_attribution(touchpoints_df)

    print("  Running Time-Decay model...")
    td = time_decay_attribution(touchpoints_df)

    print("  Running Markov Chain model...")
    mk = markov_attribution(touchpoints_df)

    # Combine all model results
    combined = pd.concat([ft, lt, lin, td, mk], ignore_index=True)
    return combined


def calculate_roi(
    attribution_df: pd.DataFrame,
    spend_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Merge attribution results with spend data and calculate ROI.

    ROI = attributed_revenue / total_spend

    Args:
        attribution_df: Combined attribution results from all models.
        spend_df: Channel spend data.

    Returns:
        DataFrame with ROI and credit percentage added.
    """
    result = attribution_df.merge(spend_df[["channel", "total_spend"]], on="channel", how="left")
    result["total_spend"] = result["total_spend"].fillna(0)

    # Calculate ROI (revenue / spend)
    result["roi"] = result.apply(
        lambda row: (
            row["attributed_revenue"] / row["total_spend"]
            if row["total_spend"] > 0
            else 0.0
        ),
        axis=1,
    )

    # Calculate credit percentage within each model
    for model in result["model"].unique():
        mask = result["model"] == model
        total_conv = result.loc[mask, "attributed_conversions"].sum()
        if total_conv > 0:
            result.loc[mask, "credit_pct"] = (
                result.loc[mask, "attributed_conversions"] / total_conv * 100
            )
        else:
            result.loc[mask, "credit_pct"] = 0.0

    # Round for readability
    result["attributed_conversions"] = result["attributed_conversions"].round(1)
    result["attributed_revenue"] = result["attributed_revenue"].round(2)
    result["roi"] = result["roi"].round(3)
    result["credit_pct"] = result["credit_pct"].round(1)

    return result


def analyze_paths(touchpoints_df: pd.DataFrame) -> dict:
    """
    Perform path analysis on the touchpoint data.

    Returns a dict with:
    - top_paths: Most common conversion paths (top 10)
    - avg_touchpoints: Average touchpoints to conversion
    - avg_days: Average days to conversion
    - touchpoint_distribution: Distribution of path lengths
    - days_distribution: Distribution of days to conversion
    - total_conversions: Total number of conversions
    - total_journeys: Total number of journeys
    - conversion_rate: Overall conversion rate
    """
    # ── Identify converting journeys ─────────────────────────────────────
    converting_ids = touchpoints_df.loc[
        touchpoints_df["converted"], "journey_id"
    ].unique()

    all_journey_ids = touchpoints_df["journey_id"].unique()
    total_journeys = len(all_journey_ids)
    total_conversions = len(converting_ids)
    conversion_rate = total_conversions / total_journeys if total_journeys > 0 else 0

    converting_tp = touchpoints_df[
        touchpoints_df["journey_id"].isin(converting_ids)
    ].copy()
    converting_tp["timestamp"] = pd.to_datetime(converting_tp["timestamp"])

    # ── Build conversion paths ───────────────────────────────────────────
    paths = (
        converting_tp.sort_values(["journey_id", "touchpoint_order"])
        .groupby("journey_id")["channel"]
        .apply(lambda x: " > ".join(x))
        .reset_index()
    )
    paths.columns = ["journey_id", "path"]

    # Top 10 most common paths
    top_paths = (
        paths["path"]
        .value_counts()
        .head(10)
        .reset_index()
    )
    top_paths.columns = ["path", "count"]
    top_paths["pct"] = (top_paths["count"] / total_conversions * 100).round(1)

    # ── Touchpoints per converting journey ───────────────────────────────
    touchpoints_per_journey = (
        converting_tp.groupby("journey_id")["touchpoint_order"]
        .count()
        .reset_index()
    )
    touchpoints_per_journey.columns = ["journey_id", "n_touchpoints"]
    avg_touchpoints = touchpoints_per_journey["n_touchpoints"].mean()

    # Distribution of path lengths
    touchpoint_dist = (
        touchpoints_per_journey["n_touchpoints"]
        .value_counts()
        .sort_index()
        .reset_index()
    )
    touchpoint_dist.columns = ["touchpoints", "count"]

    # ── Days to conversion ───────────────────────────────────────────────
    journey_times = converting_tp.groupby("journey_id")["timestamp"].agg(["min", "max"])
    journey_times["days_to_convert"] = (
        (journey_times["max"] - journey_times["min"]).dt.total_seconds() / 86400.0
    )
    avg_days = journey_times["days_to_convert"].mean()

    # Bin days for distribution chart
    bins = [0, 1, 3, 7, 14, 21, 30, 60, 999]
    labels = ["< 1 day", "1-3 days", "3-7 days", "7-14 days", "14-21 days", "21-30 days", "30-60 days", "60+ days"]
    journey_times["day_bin"] = pd.cut(
        journey_times["days_to_convert"], bins=bins, labels=labels, right=False
    )
    days_dist = journey_times["day_bin"].value_counts().reindex(labels).fillna(0).reset_index()
    days_dist.columns = ["period", "count"]

    # ── Channel-level journey stats ──────────────────────────────────────
    channel_stats = (
        touchpoints_df.groupby("channel")
        .agg(
            total_touchpoints=("journey_id", "count"),
            unique_journeys=("journey_id", "nunique"),
        )
        .reset_index()
    )

    return {
        "top_paths": top_paths,
        "avg_touchpoints": round(avg_touchpoints, 1),
        "avg_days": round(avg_days, 1),
        "touchpoint_distribution": touchpoint_dist,
        "days_distribution": days_dist,
        "total_conversions": total_conversions,
        "total_journeys": total_journeys,
        "conversion_rate": round(conversion_rate * 100, 1),
        "channel_stats": channel_stats,
        "days_to_convert_raw": journey_times["days_to_convert"].tolist(),
        "touchpoints_raw": touchpoints_per_journey["n_touchpoints"].tolist(),
    }


def build_sankey_data(touchpoints_df: pd.DataFrame) -> dict:
    """
    Build data for a Sankey diagram showing customer journey flows.

    Returns dict with labels, sources, targets, and values for Plotly Sankey.
    """
    # Filter to converting journeys
    converting_ids = touchpoints_df.loc[
        touchpoints_df["converted"], "journey_id"
    ].unique()
    converting_tp = touchpoints_df[
        touchpoints_df["journey_id"].isin(converting_ids)
    ].copy()
    converting_tp.sort_values(["journey_id", "touchpoint_order"], inplace=True)

    # Build transition pairs with position labels
    # Position 1 = "Paid Search (1st)", Position 2 = "Email (2nd)", etc.
    max_position = 5  # Limit Sankey to first 5 positions for readability
    ordinals = ["1st", "2nd", "3rd", "4th", "5th"]
    channels = touchpoints_df["channel"].unique().tolist()

    # Create labeled nodes: "Channel (position)"
    labels = []
    label_to_idx = {}
    for pos in range(max_position):
        for ch in channels:
            label = f"{ch} ({ordinals[pos]})"
            label_to_idx[label] = len(labels)
            labels.append(label)

    # Add conversion node
    conv_label = "Conversion"
    label_to_idx[conv_label] = len(labels)
    labels.append(conv_label)

    # Count transitions
    flows: dict[tuple[str, str], int] = {}

    for journey_id, group in converting_tp.groupby("journey_id"):
        channel_list = group["channel"].tolist()
        path_len = min(len(channel_list), max_position)

        for i in range(path_len - 1):
            source = f"{channel_list[i]} ({ordinals[i]})"
            target = f"{channel_list[i + 1]} ({ordinals[i + 1]})"
            flows[(source, target)] = flows.get((source, target), 0) + 1

        # Last touchpoint -> Conversion
        last_pos = path_len - 1
        source = f"{channel_list[last_pos]} ({ordinals[last_pos]})"
        flows[(source, conv_label)] = flows.get((source, conv_label), 0) + 1

    # Filter out tiny flows for readability (< 0.5% of total)
    total_flow = sum(flows.values())
    min_flow = total_flow * 0.005

    sources = []
    targets = []
    values = []

    for (src, tgt), val in flows.items():
        if val >= min_flow and src in label_to_idx and tgt in label_to_idx:
            sources.append(label_to_idx[src])
            targets.append(label_to_idx[tgt])
            values.append(val)

    return {
        "labels": labels,
        "sources": sources,
        "targets": targets,
        "values": values,
    }
