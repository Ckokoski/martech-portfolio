"""
First-Touch Attribution Model

Assigns 100% of conversion credit to the first touchpoint in each
converting customer journey. This model emphasizes awareness-stage
channels that initiate the customer relationship.

Use case: Understanding which channels are best at generating new demand.
"""

import pandas as pd


def first_touch_attribution(touchpoints_df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply first-touch attribution to touchpoint data.

    For each converting journey, the first touchpoint receives full credit
    (1.0 conversion, 100% of revenue).

    Args:
        touchpoints_df: DataFrame with columns [journey_id, touchpoint_order,
                        channel, converted, revenue].

    Returns:
        DataFrame with columns [channel, attributed_conversions,
        attributed_revenue] aggregated across all converting journeys.
    """
    # Filter to converting journeys only
    converting_ids = touchpoints_df.loc[
        touchpoints_df["converted"], "journey_id"
    ].unique()
    converting_tp = touchpoints_df[
        touchpoints_df["journey_id"].isin(converting_ids)
    ].copy()

    # Get the first touchpoint per journey
    first_touches = (
        converting_tp.sort_values(["journey_id", "touchpoint_order"])
        .groupby("journey_id")
        .first()
        .reset_index()
    )

    # Get revenue per journey (sum of revenue across all touchpoints in journey)
    journey_revenue = (
        converting_tp.groupby("journey_id")["revenue"].sum().reset_index()
    )
    journey_revenue.columns = ["journey_id", "total_revenue"]

    # Merge revenue onto first touches
    first_touches = first_touches.merge(journey_revenue, on="journey_id")

    # Aggregate by channel
    result = (
        first_touches.groupby("channel")
        .agg(
            attributed_conversions=("journey_id", "count"),
            attributed_revenue=("total_revenue", "sum"),
        )
        .reset_index()
    )

    result["model"] = "First Touch"
    return result
