"""
Time-Decay Attribution Model

Applies exponential decay weighting so that touchpoints closer to
conversion receive more credit. Uses a configurable half-life
(default: 7 days).

Use case: Values recency — channels that engage users close to conversion
get more credit, while still acknowledging earlier touchpoints.
"""

import numpy as np
import pandas as pd


def time_decay_attribution(
    touchpoints_df: pd.DataFrame,
    half_life_days: float = 7.0,
) -> pd.DataFrame:
    """
    Apply time-decay attribution with exponential weighting.

    Weight formula: w(t) = 2^(-t / half_life)
    where t = days between touchpoint and conversion.

    Args:
        touchpoints_df: DataFrame with touchpoint data including timestamps.
        half_life_days: Half-life in days for the decay function.

    Returns:
        DataFrame with [channel, attributed_conversions, attributed_revenue].
    """
    # Filter to converting journeys
    converting_ids = touchpoints_df.loc[
        touchpoints_df["converted"], "journey_id"
    ].unique()
    converting_tp = touchpoints_df[
        touchpoints_df["journey_id"].isin(converting_ids)
    ].copy()

    # Ensure timestamp is datetime
    converting_tp["timestamp"] = pd.to_datetime(converting_tp["timestamp"])

    # Get conversion timestamp per journey (last touchpoint)
    conversion_times = (
        converting_tp.loc[converting_tp["is_conversion_touch"]]
        .groupby("journey_id")["timestamp"]
        .max()
        .reset_index()
    )
    conversion_times.columns = ["journey_id", "conversion_time"]

    # Get revenue per journey
    journey_revenue = (
        converting_tp.groupby("journey_id")["revenue"].sum().reset_index()
    )
    journey_revenue.columns = ["journey_id", "total_revenue"]

    # Merge conversion time and revenue
    converting_tp = converting_tp.merge(conversion_times, on="journey_id")
    converting_tp = converting_tp.merge(journey_revenue, on="journey_id")

    # Calculate days before conversion for each touchpoint
    converting_tp["days_before_conversion"] = (
        (converting_tp["conversion_time"] - converting_tp["timestamp"])
        .dt.total_seconds() / 86400.0
    )

    # Apply exponential decay: weight = 2^(-days / half_life)
    converting_tp["raw_weight"] = np.power(
        2.0, -converting_tp["days_before_conversion"] / half_life_days
    )

    # Normalize weights within each journey so they sum to 1.0
    journey_weight_sums = (
        converting_tp.groupby("journey_id")["raw_weight"].sum().reset_index()
    )
    journey_weight_sums.columns = ["journey_id", "weight_sum"]
    converting_tp = converting_tp.merge(journey_weight_sums, on="journey_id")

    converting_tp["weight"] = (
        converting_tp["raw_weight"] / converting_tp["weight_sum"]
    )

    # Calculate weighted credit
    converting_tp["conv_credit"] = converting_tp["weight"]
    converting_tp["rev_credit"] = (
        converting_tp["weight"] * converting_tp["total_revenue"]
    )

    # Aggregate by channel
    result = (
        converting_tp.groupby("channel")
        .agg(
            attributed_conversions=("conv_credit", "sum"),
            attributed_revenue=("rev_credit", "sum"),
        )
        .reset_index()
    )

    result["model"] = "Time Decay"
    return result
