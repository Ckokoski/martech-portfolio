"""
feature_engineering.py — Transforms raw lead data into ML-ready features.

Creates engagement scores, ICP fit scores, behavioral intent signals,
and interaction velocity metrics from raw lead attributes.
"""

import numpy as np
import pandas as pd


# ── Ideal Customer Profile (ICP) configuration ──────────────────────────────
# Weights reflect how well each attribute matches the ideal B2B SaaS buyer.

ICP_INDUSTRY_SCORES = {
    "SaaS/Technology": 1.0, "Financial Services": 0.8,
    "Professional Services": 0.7, "E-commerce/Retail": 0.6,
    "Healthcare": 0.5, "Telecommunications": 0.5,
    "Media/Entertainment": 0.4, "Manufacturing": 0.3,
    "Education": 0.2, "Government/Public Sector": 0.1,
}

ICP_SIZE_SCORES = {
    "1-10": 0.1, "11-50": 0.3, "51-200": 0.8,
    "201-500": 1.0, "501-1000": 0.9,
    "1001-5000": 0.6, "5000+": 0.4,
}

ICP_SENIORITY_SCORES = {
    "C-Suite": 1.0, "VP": 0.9, "Director": 0.7,
    "Manager": 0.4, "Individual Contributor": 0.1,
}

ICP_REGION_SCORES = {
    "North America": 1.0, "Europe": 0.8,
    "Asia-Pacific": 0.5, "Latin America": 0.3,
    "Middle East/Africa": 0.2,
}

# Page visit weights for intent scoring (higher = stronger buying signal)
PAGE_INTENT_WEIGHTS = {
    "pricing_page_visits": 5.0,
    "demo_page_visits": 4.0,
    "docs_page_visits": 2.0,
    "blog_page_visits": 0.5,
}


def compute_engagement_frequency(df: pd.DataFrame) -> pd.Series:
    """
    Frequency score: total count of all engagement actions.
    Normalized to 0-100 scale using percentile rank.
    """
    raw = (
        df["email_opens"]
        + df["email_clicks"]
        + df["page_visits_total"]
        + df["content_downloads"]
        + df["webinar_attended"]
        + df["form_submissions"]
    )
    # Percentile-rank normalization
    return raw.rank(pct=True) * 100


def compute_engagement_recency(df: pd.DataFrame) -> pd.Series:
    """
    Recency score: inverse of days since last engagement.
    More recent engagement = higher score (0-100).
    """
    max_days = df["days_since_last_engagement"].max()
    if max_days == 0:
        return pd.Series(100.0, index=df.index)
    recency = 1 - (df["days_since_last_engagement"] / max_days)
    return recency * 100


def compute_engagement_depth(df: pd.DataFrame) -> pd.Series:
    """
    Depth score: diversity of engagement channels used.
    Counts how many distinct engagement types a lead has touched.
    """
    channels = pd.DataFrame({
        "has_email": (df["email_opens"] > 0).astype(int),
        "has_clicks": (df["email_clicks"] > 0).astype(int),
        "has_pages": (df["page_visits_total"] > 0).astype(int),
        "has_downloads": (df["content_downloads"] > 0).astype(int),
        "has_webinar": (df["webinar_attended"] > 0).astype(int),
        "has_forms": (df["form_submissions"] > 0).astype(int),
    })
    depth = channels.sum(axis=1)
    # Scale to 0-100
    return (depth / channels.shape[1]) * 100


def compute_icp_fit_score(df: pd.DataFrame) -> pd.Series:
    """
    ICP (Ideal Customer Profile) fit score based on firmographics.
    Weighted combination of industry, company size, seniority, and region.
    Returns 0-100 score.
    """
    industry_score = df["industry"].map(ICP_INDUSTRY_SCORES).fillna(0.0)
    size_score = df["company_size"].map(ICP_SIZE_SCORES).fillna(0.0)
    seniority_score = df["seniority"].map(ICP_SENIORITY_SCORES).fillna(0.0)
    region_score = df["region"].map(ICP_REGION_SCORES).fillna(0.0)

    # Weighted average (seniority and size matter most for B2B)
    icp = (
        0.30 * seniority_score
        + 0.30 * size_score
        + 0.25 * industry_score
        + 0.15 * region_score
    )
    return icp * 100


def compute_behavioral_intent(df: pd.DataFrame) -> pd.Series:
    """
    Behavioral intent score: weighted sum of page visits.
    Pricing and demo pages signal stronger buying intent.
    Returns 0-100 score.
    """
    raw = sum(
        df[col] * weight
        for col, weight in PAGE_INTENT_WEIGHTS.items()
    )
    # Percentile-rank normalization
    return raw.rank(pct=True) * 100


def compute_interaction_velocity(df: pd.DataFrame) -> pd.Series:
    """
    Interaction velocity: engagement density over time.
    High velocity = many actions in a short window (acceleration).
    Low velocity = spread out over a long period (deceleration).
    """
    total_actions = (
        df["email_opens"] + df["email_clicks"]
        + df["page_visits_total"] + df["content_downloads"]
        + df["form_submissions"]
    )
    # Avoid division by zero
    days = df["days_since_first_touch"].replace(0, 1)
    velocity = total_actions / days

    # Percentile-rank normalization
    return velocity.rank(pct=True) * 100


def compute_email_engagement_rate(df: pd.DataFrame) -> pd.Series:
    """Click-to-open rate for email engagement."""
    opens = df["email_opens"].replace(0, np.nan)
    rate = df["email_clicks"] / opens
    return rate.fillna(0.0)


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Main entry point: takes raw lead data and returns a feature-enriched
    DataFrame ready for model training.

    Parameters
    ----------
    df : pd.DataFrame
        Raw lead data from data_generator.

    Returns
    -------
    pd.DataFrame
        Original columns plus engineered feature columns.
    """
    result = df.copy()

    # ── Engagement scores ────────────────────────────────────────────────
    result["engagement_frequency_score"] = compute_engagement_frequency(df)
    result["engagement_recency_score"] = compute_engagement_recency(df)
    result["engagement_depth_score"] = compute_engagement_depth(df)

    # ── ICP & intent ─────────────────────────────────────────────────────
    result["icp_fit_score"] = compute_icp_fit_score(df)
    result["behavioral_intent_score"] = compute_behavioral_intent(df)

    # ── Velocity ─────────────────────────────────────────────────────────
    result["interaction_velocity"] = compute_interaction_velocity(df)

    # ── Derived ratios ───────────────────────────────────────────────────
    result["email_engagement_rate"] = compute_email_engagement_rate(df)

    # Pricing-to-total page ratio (intent density)
    total_pages = df["page_visits_total"].replace(0, 1)
    result["pricing_page_ratio"] = df["pricing_page_visits"] / total_pages
    result["demo_page_ratio"] = df["demo_page_visits"] / total_pages

    # ── Encode categoricals for ML ───────────────────────────────────────
    # One-hot encode categorical columns
    cat_cols = ["industry", "company_size", "seniority", "region", "lead_source"]
    dummies = pd.get_dummies(result[cat_cols], prefix=cat_cols, drop_first=False)
    result = pd.concat([result, dummies], axis=1)

    print(f"  -> Engineered {len(result.columns) - len(df.columns)} new features")
    print(f"     Total columns: {len(result.columns)}")

    return result


def get_feature_columns(df: pd.DataFrame) -> list[str]:
    """
    Return the list of columns suitable for model training.
    Excludes identifiers, raw categoricals, and the target.
    """
    exclude = {
        "lead_id", "industry", "company_size", "job_title",
        "seniority", "region", "lead_source", "converted",
    }
    return [c for c in df.columns if c not in exclude]


if __name__ == "__main__":
    from data_generator import generate_leads
    leads = generate_leads()
    enriched = engineer_features(leads)
    print(enriched.head())
