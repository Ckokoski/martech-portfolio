"""
data_generator.py - Synthetic Multi-Channel Touchpoint Data Generator

Generates realistic marketing touchpoint data for attribution modeling:
- 5,000 converting journeys with 35,000+ total touchpoints
- Non-converting journeys for realism
- 8 marketing channels with realistic transition patterns
- Channel-level spend data
- Seeded randomness for reproducibility
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta


# ── Channel definitions ──────────────────────────────────────────────────────

CHANNELS = [
    "Paid Search",
    "Organic Search",
    "Email",
    "Social",
    "Display",
    "Direct",
    "Referral",
    "Content Marketing",
]

# Monthly spend per channel (used for ROI calculations)
CHANNEL_SPEND = {
    "Paid Search": 45_000,
    "Organic Search": 12_000,      # SEO investment
    "Email": 8_000,
    "Social": 25_000,
    "Display": 30_000,
    "Direct": 2_000,               # Minimal (brand awareness residual)
    "Referral": 5_000,
    "Content Marketing": 18_000,
}

# Average revenue per conversion (varies by entry channel)
CHANNEL_AVG_REVENUE = {
    "Paid Search": 220,
    "Organic Search": 280,
    "Email": 190,
    "Social": 150,
    "Display": 130,
    "Direct": 350,
    "Referral": 310,
    "Content Marketing": 260,
}

# ── Transition probabilities ─────────────────────────────────────────────────
# Row = current channel, Col = next channel
# These define realistic journey patterns (e.g., display awareness -> search)

TRANSITION_MATRIX = {
    "Paid Search":       [0.05, 0.10, 0.20, 0.05, 0.05, 0.30, 0.05, 0.20],
    "Organic Search":    [0.15, 0.05, 0.25, 0.05, 0.05, 0.20, 0.10, 0.15],
    "Email":             [0.15, 0.10, 0.10, 0.10, 0.05, 0.25, 0.05, 0.20],
    "Social":            [0.10, 0.15, 0.15, 0.10, 0.15, 0.10, 0.10, 0.15],
    "Display":           [0.20, 0.15, 0.10, 0.15, 0.05, 0.10, 0.10, 0.15],
    "Direct":            [0.10, 0.10, 0.15, 0.05, 0.05, 0.15, 0.15, 0.25],
    "Referral":          [0.10, 0.15, 0.20, 0.10, 0.05, 0.20, 0.05, 0.15],
    "Content Marketing": [0.15, 0.20, 0.20, 0.10, 0.05, 0.15, 0.05, 0.10],
}

# Probability of starting a journey on each channel
ENTRY_PROBABILITIES = [0.18, 0.22, 0.08, 0.15, 0.12, 0.10, 0.05, 0.10]

# Probability of converting after each touchpoint (cumulative fatigue)
# Index = touchpoint number (0-based), higher index = higher convert probability
CONVERSION_PROB_BY_TOUCH = [0.08, 0.12, 0.18, 0.25, 0.32, 0.40, 0.50, 0.60]


def generate_touchpoint_data(
    n_conversions: int = 5000,
    n_non_converting: int = 3000,
    seed: int = 42,
    start_date: str = "2025-07-01",
    end_date: str = "2025-12-31",
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Generate synthetic touchpoint data for attribution modeling.

    Args:
        n_conversions: Number of converting customer journeys to generate.
        n_non_converting: Number of non-converting journeys.
        seed: Random seed for reproducibility.
        start_date: Start of the date range for touchpoints.
        end_date: End of the date range for touchpoints.

    Returns:
        Tuple of (touchpoints_df, spend_df):
        - touchpoints_df: One row per touchpoint with journey_id, channel, timestamp, etc.
        - spend_df: Channel-level spend data.
    """
    rng = np.random.default_rng(seed)
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    total_days = (end - start).days

    all_touchpoints = []
    journey_id = 0

    # ── Generate converting journeys ─────────────────────────────────────
    for _ in range(n_conversions):
        journey_id += 1
        path_length = _sample_path_length(rng, converting=True)
        touchpoints = _generate_journey(
            rng, journey_id, path_length, start, total_days, converted=True
        )
        all_touchpoints.extend(touchpoints)

    # ── Generate non-converting journeys ─────────────────────────────────
    for _ in range(n_non_converting):
        journey_id += 1
        path_length = _sample_path_length(rng, converting=False)
        touchpoints = _generate_journey(
            rng, journey_id, path_length, start, total_days, converted=False
        )
        all_touchpoints.extend(touchpoints)

    # ── Build DataFrames ─────────────────────────────────────────────────
    touchpoints_df = pd.DataFrame(all_touchpoints)
    touchpoints_df.sort_values(["journey_id", "touchpoint_order"], inplace=True)
    touchpoints_df.reset_index(drop=True, inplace=True)

    # Assign revenue to converting journeys based on first-touch channel
    touchpoints_df["revenue"] = 0.0
    converting_journeys = touchpoints_df[touchpoints_df["converted"]].groupby("journey_id")
    for jid, group in converting_journeys:
        first_channel = group.iloc[0]["channel"]
        base_rev = CHANNEL_AVG_REVENUE[first_channel]
        # Add some variance (+/- 40%)
        actual_rev = base_rev * rng.uniform(0.6, 1.4)
        # Revenue is assigned to the journey (last touchpoint carries it for reference)
        last_idx = group.index[-1]
        touchpoints_df.loc[last_idx, "revenue"] = round(actual_rev, 2)

    # ── Spend DataFrame ──────────────────────────────────────────────────
    # 6-month period spend
    spend_df = pd.DataFrame([
        {"channel": ch, "monthly_spend": spend, "total_spend": spend * 6}
        for ch, spend in CHANNEL_SPEND.items()
    ])

    return touchpoints_df, spend_df


def _sample_path_length(rng: np.random.Generator, converting: bool) -> int:
    """
    Sample a realistic path length.
    Converting journeys tend to be longer (2-8 touchpoints).
    Non-converting journeys tend to be shorter (1-5 touchpoints).
    """
    if converting:
        # Weighted toward 3-5 touchpoints for converters
        weights = [0.05, 0.12, 0.22, 0.25, 0.18, 0.10, 0.05, 0.03]
        lengths = list(range(1, 9))
    else:
        # Non-converters drop off earlier
        weights = [0.30, 0.30, 0.20, 0.12, 0.08]
        lengths = list(range(1, 6))
    return rng.choice(lengths, p=weights)


def _generate_journey(
    rng: np.random.Generator,
    journey_id: int,
    path_length: int,
    start: datetime,
    total_days: int,
    converted: bool,
) -> list[dict]:
    """Generate a single customer journey as a list of touchpoint dicts."""
    touchpoints = []

    # Pick a random journey start date, leaving room for the journey to unfold
    journey_start_offset = rng.integers(0, max(1, total_days - 30))
    journey_start = start + timedelta(days=int(journey_start_offset))

    # Select entry channel
    entry_channel = rng.choice(CHANNELS, p=ENTRY_PROBABILITIES)
    current_channel = entry_channel

    for i in range(path_length):
        # Time between touchpoints: 0.5 to 7 days, with some randomness
        if i == 0:
            ts = journey_start
        else:
            gap_hours = rng.exponential(scale=48)  # ~2 day average gap
            gap_hours = max(1, min(gap_hours, 168))  # Clamp to 1hr - 7 days
            ts = touchpoints[-1]["timestamp"] + timedelta(hours=float(gap_hours))

        touchpoints.append({
            "journey_id": journey_id,
            "touchpoint_order": i + 1,
            "channel": current_channel,
            "timestamp": ts,
            "converted": converted and (i == path_length - 1),
            "is_conversion_touch": converted and (i == path_length - 1),
        })

        # Transition to next channel using the transition matrix
        if i < path_length - 1:
            transition_probs = TRANSITION_MATRIX[current_channel]
            current_channel = rng.choice(CHANNELS, p=transition_probs)

    return touchpoints


def get_channel_spend() -> pd.DataFrame:
    """Return channel spend as a DataFrame."""
    return pd.DataFrame([
        {"channel": ch, "monthly_spend": spend, "total_spend": spend * 6}
        for ch, spend in CHANNEL_SPEND.items()
    ])


if __name__ == "__main__":
    # Quick test: generate data and print summary
    print("Generating synthetic touchpoint data...")
    tp_df, spend_df = generate_touchpoint_data()

    print(f"\nTotal touchpoints: {len(tp_df):,}")
    print(f"Total journeys: {tp_df['journey_id'].nunique():,}")
    print(f"Converting journeys: {tp_df[tp_df['converted']]['journey_id'].nunique():,}")
    print(f"\nTouchpoints per channel:")
    print(tp_df["channel"].value_counts().to_string())
    print(f"\nSpend data:")
    print(spend_df.to_string(index=False))
