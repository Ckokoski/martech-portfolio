"""
data_generator.py — Synthetic Email Campaign Data Generator

Generates realistic email marketing campaign data with:
- 100 campaigns over 12 months
- 50K subscriber simulation
- Seasonal patterns, trends, and intentional underperformers
- Deterministic output via seeded random state
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import os

# Seed for reproducibility
SEED = 42
RNG = np.random.RandomState(SEED)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
NUM_CAMPAIGNS = 100
NUM_SUBSCRIBERS = 50_000
START_DATE = datetime(2025, 3, 1)
END_DATE = datetime(2026, 2, 28)

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

# Subject line building blocks
SUBJECT_PREFIXES = [
    "Don't Miss:", "Exclusive:", "Last Chance:", "Breaking:",
    "New:", "Update:", "Reminder:", "Limited Time:",
    "Your Weekly", "Special Offer:", "Alert:", "Important:",
]

SUBJECT_BODIES = [
    "Our Biggest Sale of the Year",
    "Tips to Boost Your Productivity",
    "{first_name}, Your Personalized Report is Ready",
    "5 Strategies for Better Results",
    "What's New This Month",
    "Your Account Summary",
    "{first_name}, We Miss You!",
    "Unlock Premium Features Today",
    "How Top Performers Stay Ahead",
    "The Ultimate Guide to Email Marketing",
    "Save Up to 50% This Weekend Only",
    "{first_name}, Your Exclusive Invitation",
    "Industry Trends You Need to Know",
    "We've Got Something Special for You",
    "Action Required: Update Your Preferences",
    "Celebrate With Us — Anniversary Special",
    "Quick Win: Improve Your Open Rates",
    "Behind the Scenes: Our Product Roadmap",
    "Customer Spotlight: Success Stories",
    "Free Webinar: Expert Panel Discussion",
]

SUBJECT_EMOJIS = ["🔥", "🚀", "⭐", "💡", "🎉", "📊", "✅", "💰", "🎯", "📢"]

CAMPAIGN_TYPES = [
    "newsletter", "promotional", "transactional",
    "re-engagement", "announcement", "educational",
]

# Urgency keywords that tend to boost open rates
URGENCY_WORDS = ["last chance", "limited time", "expires", "urgent", "don't miss", "ending soon"]


def _seasonal_multiplier(date: datetime) -> float:
    """Return a multiplier that simulates seasonal engagement patterns.

    Higher engagement in Jan (New Year), Nov-Dec (holidays), lower in summer.
    """
    month = date.month
    multipliers = {
        1: 1.15,   # New Year resolutions
        2: 1.05,
        3: 1.00,
        4: 0.95,
        5: 0.92,
        6: 0.88,   # Summer slump begins
        7: 0.85,
        8: 0.87,
        9: 0.95,   # Back to school / work
        10: 1.00,
        11: 1.10,  # Holiday shopping ramp-up
        12: 1.12,  # Holiday peak
    }
    return multipliers.get(month, 1.0)


def _generate_send_times(n: int, rng: np.random.RandomState) -> list:
    """Generate send times with a realistic distribution.

    Most sends cluster around 9-11 AM and 1-3 PM on weekdays,
    with some weekend sends and off-hours experiments.
    """
    hours = []
    days_of_week = []
    for _ in range(n):
        roll = rng.random()
        if roll < 0.35:
            # Morning sweet spot
            h = int(rng.normal(10, 1))
        elif roll < 0.65:
            # Afternoon sweet spot
            h = int(rng.normal(14, 1.5))
        elif roll < 0.85:
            # Early morning or evening experiments
            h = rng.choice([7, 8, 17, 18, 19])
        else:
            # Off-hours (intentionally underperforming)
            h = rng.choice([5, 6, 20, 21, 22, 23])
        hours.append(max(0, min(23, h)))

        # Weekday-heavy, some weekend
        if rng.random() < 0.82:
            days_of_week.append(rng.randint(0, 5))  # Mon-Fri
        else:
            days_of_week.append(rng.choice([5, 6]))  # Sat-Sun
    return hours, days_of_week


def generate_campaigns() -> pd.DataFrame:
    """Generate a DataFrame of 100 synthetic email campaigns."""

    # Distribute send dates across 12 months
    total_days = (END_DATE - START_DATE).days
    send_dates = sorted([
        START_DATE + timedelta(days=int(RNG.uniform(0, total_days)))
        for _ in range(NUM_CAMPAIGNS)
    ])

    send_hours, send_dows = _generate_send_times(NUM_CAMPAIGNS, RNG)

    records = []
    for i in range(NUM_CAMPAIGNS):
        date = send_dates[i]
        # Override day-of-week to match generated pattern
        # (shift date to land on the desired weekday)
        target_dow = send_dows[i]
        current_dow = date.weekday()
        delta = int((target_dow - current_dow) % 7)
        date = date + timedelta(days=delta)
        send_hour = send_hours[i]
        send_datetime = date.replace(hour=send_hour, minute=RNG.randint(0, 59))

        # Build subject line
        prefix = RNG.choice(SUBJECT_PREFIXES) if RNG.random() < 0.6 else ""
        body = RNG.choice(SUBJECT_BODIES)
        has_personalization = "{first_name}" in body
        has_emoji = RNG.random() < 0.3
        emoji = " " + RNG.choice(SUBJECT_EMOJIS) if has_emoji else ""
        subject = f"{prefix} {body}{emoji}".strip()
        # Resolve personalization token for display
        subject_display = subject.replace("{first_name}", "{{first_name}}")

        has_urgency = any(w in subject.lower() for w in URGENCY_WORDS)
        subject_length = len(subject_display)

        campaign_type = RNG.choice(CAMPAIGN_TYPES)
        seasonal = _seasonal_multiplier(date)

        # ----- Metric generation -----
        list_size = int(NUM_SUBSCRIBERS * RNG.uniform(0.6, 1.0))

        # Delivery rate: 95-99%
        delivery_rate = RNG.uniform(0.95, 0.99)

        # Base open rate depends on several factors
        base_open = 0.22 * seasonal
        if has_personalization:
            base_open += RNG.uniform(0.02, 0.05)
        if has_urgency:
            base_open += RNG.uniform(0.01, 0.04)
        if has_emoji:
            base_open += RNG.uniform(0.005, 0.02)
        if subject_length < 50:
            base_open += 0.01
        elif subject_length > 80:
            base_open -= 0.02

        # Send-time effect
        if send_hour in (9, 10, 11):
            base_open += 0.03
        elif send_hour in (13, 14):
            base_open += 0.02
        elif send_hour >= 20 or send_hour <= 5:
            base_open -= 0.04

        # Weekend penalty
        if date.weekday() >= 5:
            base_open -= 0.03

        # Add noise
        open_rate = max(0.05, min(0.55, base_open + RNG.normal(0, 0.03)))

        # Click rate: typically 15-30% of opens
        click_pct_of_opens = RNG.uniform(0.15, 0.30)
        if campaign_type == "promotional":
            click_pct_of_opens += 0.05
        click_rate = open_rate * click_pct_of_opens

        # Bounce rate: 1-5%, with a few bad campaigns
        if RNG.random() < 0.08:
            bounce_rate = RNG.uniform(0.05, 0.12)  # Intentional underperformer
        else:
            bounce_rate = RNG.uniform(0.01, 0.04)

        # Unsubscribe rate: 0.1-0.5%, occasional spikes
        if RNG.random() < 0.06:
            unsub_rate = RNG.uniform(0.005, 0.02)  # Spike
        else:
            unsub_rate = RNG.uniform(0.001, 0.005)

        # Conversion rate: 1-8% of clicks
        conversion_pct_of_clicks = RNG.uniform(0.01, 0.08)
        if campaign_type in ("promotional", "re-engagement"):
            conversion_pct_of_clicks += 0.02

        # ----- Compute absolute numbers -----
        sent = list_size
        delivered = int(sent * delivery_rate)
        bounced = sent - delivered
        opened = int(delivered * open_rate)
        clicked = int(opened * click_pct_of_opens)
        unsubscribed = max(1, int(delivered * unsub_rate))
        converted = max(0, int(clicked * conversion_pct_of_clicks))

        # Revenue per conversion: $5-$120
        revenue_per = RNG.uniform(5, 120)
        revenue = round(converted * revenue_per, 2)

        records.append({
            "campaign_id": f"CP-{i+1:04d}",
            "campaign_name": f"Campaign {i+1}: {body.replace('{first_name}', 'User')}",
            "campaign_type": campaign_type,
            "send_date": send_datetime.strftime("%Y-%m-%d"),
            "send_time": send_datetime.strftime("%H:%M"),
            "send_hour": send_hour,
            "send_dow": date.strftime("%A"),
            "send_dow_num": date.weekday(),
            "subject_line": subject_display,
            "subject_length": subject_length,
            "has_personalization": has_personalization,
            "has_emoji": has_emoji,
            "has_urgency": has_urgency,
            "sent": sent,
            "delivered": delivered,
            "opened": opened,
            "clicked": clicked,
            "bounced": bounced,
            "unsubscribed": unsubscribed,
            "converted": converted,
            "revenue": revenue,
            "open_rate": round(opened / delivered, 4) if delivered else 0,
            "click_rate": round(clicked / delivered, 4) if delivered else 0,
            "bounce_rate": round(bounced / sent, 4) if sent else 0,
            "unsubscribe_rate": round(unsubscribed / delivered, 4) if delivered else 0,
            "conversion_rate": round(converted / clicked, 4) if clicked else 0,
        })

    return pd.DataFrame(records)


def generate_subscriber_data(campaigns_df: pd.DataFrame) -> pd.DataFrame:
    """Generate subscriber-level engagement data for segmentation.

    Creates a simplified subscriber profile with aggregate engagement metrics.
    """
    rng = np.random.RandomState(SEED + 1)

    subscriber_ids = [f"SUB-{j+1:06d}" for j in range(NUM_SUBSCRIBERS)]

    # Assign each subscriber an engagement tier
    # 20% highly engaged, 40% moderate, 25% low, 15% dormant
    tiers = rng.choice(
        ["high", "moderate", "low", "dormant"],
        size=NUM_SUBSCRIBERS,
        p=[0.20, 0.40, 0.25, 0.15],
    )

    tier_params = {
        "high":     {"open_mean": 0.65, "open_std": 0.10, "click_mean": 0.30, "click_std": 0.08, "campaigns_pct": 0.85},
        "moderate": {"open_mean": 0.35, "open_std": 0.12, "click_mean": 0.12, "click_std": 0.05, "campaigns_pct": 0.55},
        "low":      {"open_mean": 0.12, "open_std": 0.06, "click_mean": 0.03, "click_std": 0.02, "campaigns_pct": 0.30},
        "dormant":  {"open_mean": 0.02, "open_std": 0.02, "click_mean": 0.005, "click_std": 0.005, "campaigns_pct": 0.10},
    }

    records = []
    num_campaigns = len(campaigns_df)
    for idx in range(NUM_SUBSCRIBERS):
        tier = tiers[idx]
        params = tier_params[tier]

        campaigns_received = max(1, int(num_campaigns * params["campaigns_pct"] * rng.uniform(0.8, 1.2)))
        campaigns_received = min(campaigns_received, num_campaigns)

        avg_open_rate = max(0, min(1, rng.normal(params["open_mean"], params["open_std"])))
        avg_click_rate = max(0, min(1, rng.normal(params["click_mean"], params["click_std"])))

        total_opens = int(campaigns_received * avg_open_rate)
        total_clicks = int(campaigns_received * avg_click_rate)

        # Days since last engagement
        if tier == "high":
            days_since = max(0, int(rng.exponential(5)))
        elif tier == "moderate":
            days_since = max(0, int(rng.exponential(20)))
        elif tier == "low":
            days_since = max(0, int(rng.exponential(60)))
        else:
            days_since = max(90, int(rng.exponential(120)))

        # Signup age in days
        signup_age = rng.randint(30, 730)

        records.append({
            "subscriber_id": subscriber_ids[idx],
            "engagement_tier": tier,
            "campaigns_received": campaigns_received,
            "total_opens": total_opens,
            "total_clicks": total_clicks,
            "avg_open_rate": round(avg_open_rate, 4),
            "avg_click_rate": round(avg_click_rate, 4),
            "days_since_last_open": days_since,
            "signup_age_days": signup_age,
            "total_purchases": max(0, int(rng.poisson(2 if tier == "high" else 0.5 if tier == "moderate" else 0.1))),
        })

    return pd.DataFrame(records)


def save_data(campaigns_df: pd.DataFrame, subscribers_df: pd.DataFrame) -> tuple:
    """Save generated data to CSV files in the data/ directory."""
    os.makedirs(DATA_DIR, exist_ok=True)

    campaigns_path = os.path.join(DATA_DIR, "campaigns.csv")
    subscribers_path = os.path.join(DATA_DIR, "subscribers.csv")

    campaigns_df.to_csv(campaigns_path, index=False)
    subscribers_df.to_csv(subscribers_path, index=False)

    return campaigns_path, subscribers_path


def load_data() -> tuple:
    """Load previously generated data from CSV files."""
    campaigns_path = os.path.join(DATA_DIR, "campaigns.csv")
    subscribers_path = os.path.join(DATA_DIR, "subscribers.csv")

    campaigns_df = pd.read_csv(campaigns_path)
    subscribers_df = pd.read_csv(subscribers_path)

    return campaigns_df, subscribers_df


def generate_all() -> tuple:
    """Generate all synthetic data and save to disk.

    Returns (campaigns_df, subscribers_df).
    """
    print("[DataGen] Generating 100 synthetic campaigns...")
    campaigns_df = generate_campaigns()

    print(f"[DataGen] Generating {NUM_SUBSCRIBERS:,} subscriber profiles...")
    subscribers_df = generate_subscriber_data(campaigns_df)

    camp_path, sub_path = save_data(campaigns_df, subscribers_df)
    print(f"[DataGen] Saved campaigns  -> {camp_path}")
    print(f"[DataGen] Saved subscribers -> {sub_path}")

    return campaigns_df, subscribers_df


if __name__ == "__main__":
    generate_all()
