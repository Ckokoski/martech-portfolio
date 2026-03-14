"""
Linear Attribution Model

Distributes conversion credit equally across all touchpoints in a
converting journey. A journey with 4 touchpoints gives each 25% credit.

Use case: Balanced view that values every interaction in the customer journey.
"""

import pandas as pd


def linear_attribution(touchpoints_df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply linear (equal-weight) attribution to touchpoint data.

    Each touchpoint in a converting journey receives 1/N credit,
    where N is the total number of touchpoints in that journey.

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

    # Count touchpoints per journey for equal weighting
    journey_counts = (
        converting_tp.groupby("journey_id")["touchpoint_order"]
        .count()
        .reset_index()
    )
    journey_counts.columns = ["journey_id", "n_touchpoints"]

    # Get revenue per journey
    journey_revenue = (
        converting_tp.groupby("journey_id")["revenue"].sum().reset_index()
    )
    journey_revenue.columns = ["journey_id", "total_revenue"]

    # Merge counts and revenue onto each touchpoint
    converting_tp = converting_tp.merge(journey_counts, on="journey_id")
    converting_tp = converting_tp.merge(journey_revenue, on="journey_id")

    # Calculate fractional credit per touchpoint
    converting_tp["credit"] = 1.0 / converting_tp["n_touchpoints"]
    converting_tp["rev_credit"] = (
        converting_tp["total_revenue"] / converting_tp["n_touchpoints"]
    )

    # Aggregate by channel
    result = (
        converting_tp.groupby("channel")
        .agg(
            attributed_conversions=("credit", "sum"),
            attributed_revenue=("rev_credit", "sum"),
        )
        .reset_index()
    )

    result["model"] = "Linear"
    return result
