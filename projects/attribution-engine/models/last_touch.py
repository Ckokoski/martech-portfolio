"""
Last-Touch Attribution Model

Assigns 100% of conversion credit to the last touchpoint before
conversion. This model emphasizes channels that close deals.

Use case: Understanding which channels drive final conversion action.
"""

import pandas as pd


def last_touch_attribution(touchpoints_df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply last-touch attribution to touchpoint data.

    For each converting journey, the last touchpoint (the conversion
    touchpoint) receives full credit.

    Args:
        touchpoints_df: DataFrame with touchpoint data.

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

    # Get the last touchpoint per journey
    last_touches = (
        converting_tp.sort_values(["journey_id", "touchpoint_order"])
        .groupby("journey_id")
        .last()
        .reset_index()
    )

    # Get revenue per journey
    journey_revenue = (
        converting_tp.groupby("journey_id")["revenue"].sum().reset_index()
    )
    journey_revenue.columns = ["journey_id", "total_revenue"]

    last_touches = last_touches.merge(journey_revenue, on="journey_id")

    # Aggregate by channel
    result = (
        last_touches.groupby("channel")
        .agg(
            attributed_conversions=("journey_id", "count"),
            attributed_revenue=("total_revenue", "sum"),
        )
        .reset_index()
    )

    result["model"] = "Last Touch"
    return result
