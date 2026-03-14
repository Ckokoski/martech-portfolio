"""
quality_scorer.py — Data quality assessment for unified profiles.

Three quality dimensions:
  1. Completeness — percentage of key fields populated
  2. Recency — how fresh the most recent activity is
  3. Confidence — based on identity resolution match confidence

An overall quality score is the weighted average of all three.
"""

from __future__ import annotations

from datetime import datetime

import pandas as pd

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

# Fields checked for completeness and their weights
COMPLETENESS_FIELDS = {
    "first_name": 1.0,
    "last_name": 1.0,
    "email": 1.5,       # email is more valuable
    "phone": 0.8,
    "company": 1.0,
    "job_title": 0.7,
    "region": 0.5,
    "subscriber_status": 0.5,
    "total_spend": 1.0,
    "page_views": 0.5,
}

# Weights for the overall quality score
WEIGHT_COMPLETENESS = 0.45
WEIGHT_RECENCY = 0.30
WEIGHT_CONFIDENCE = 0.25

# Recency decay: days since last activity -> score
RECENCY_DECAY_DAYS = 365  # activity older than this gets score 0


# ---------------------------------------------------------------------------
# Scoring functions
# ---------------------------------------------------------------------------

def _completeness_score(row: pd.Series) -> float:
    """
    Weighted completeness: fraction of key fields that are non-empty.
    """
    total_weight = 0.0
    earned_weight = 0.0
    for field, weight in COMPLETENESS_FIELDS.items():
        total_weight += weight
        val = row.get(field, "")
        if pd.notna(val) and str(val).strip() not in ("", "0", "0.0"):
            earned_weight += weight
    return round(earned_weight / total_weight, 4) if total_weight else 0.0


def _recency_score(row: pd.Series, now: datetime) -> float:
    """
    Score from 0-1 based on days since last activity.
    Activity today = 1.0, activity RECENCY_DECAY_DAYS ago = 0.0.
    """
    last_activity = row.get("last_activity", "")
    if not last_activity or pd.isna(last_activity) or str(last_activity).strip() == "":
        return 0.0
    try:
        activity_dt = pd.to_datetime(last_activity)
        days_ago = (now - activity_dt).days
        if days_ago < 0:
            days_ago = 0
        score = max(0.0, 1.0 - (days_ago / RECENCY_DECAY_DAYS))
        return round(score, 4)
    except Exception:
        return 0.0


def _confidence_score(row: pd.Series) -> float:
    """
    Identity resolution confidence (already 0-1). Single-source records
    that were never matched get a baseline confidence of 0.5.
    """
    conf = row.get("match_confidence", 0.0)
    if conf == 0.0 and row.get("source_count", 1) == 1:
        return 0.5  # unmatched single-source record — moderate baseline
    return float(conf)


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def score_profiles(profiles_df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """
    Add quality scores to every unified profile.

    New columns added:
      - completeness_score  (0-1)
      - recency_score       (0-1)
      - confidence_score    (0-1)
      - quality_score       (0-1, weighted composite)
      - quality_grade       (A / B / C / D / F)

    Returns the updated DataFrame and summary statistics.
    """
    print("\n=== Scoring data quality ===")
    now = datetime.now()

    profiles_df["completeness_score"] = profiles_df.apply(
        _completeness_score, axis=1
    )
    profiles_df["recency_score"] = profiles_df.apply(
        lambda r: _recency_score(r, now), axis=1
    )
    profiles_df["confidence_score"] = profiles_df.apply(
        _confidence_score, axis=1
    )

    # Weighted composite
    profiles_df["quality_score"] = (
        profiles_df["completeness_score"] * WEIGHT_COMPLETENESS
        + profiles_df["recency_score"] * WEIGHT_RECENCY
        + profiles_df["confidence_score"] * WEIGHT_CONFIDENCE
    ).round(4)

    # Letter grade
    def _grade(score: float) -> str:
        if score >= 0.85:
            return "A"
        elif score >= 0.70:
            return "B"
        elif score >= 0.55:
            return "C"
        elif score >= 0.40:
            return "D"
        return "F"

    profiles_df["quality_grade"] = profiles_df["quality_score"].apply(_grade)

    # Summary statistics
    grade_dist = profiles_df["quality_grade"].value_counts().to_dict()
    stats = {
        "avg_completeness": round(profiles_df["completeness_score"].mean(), 3),
        "avg_recency": round(profiles_df["recency_score"].mean(), 3),
        "avg_confidence": round(profiles_df["confidence_score"].mean(), 3),
        "avg_quality": round(profiles_df["quality_score"].mean(), 3),
        "grade_distribution": {
            g: grade_dist.get(g, 0) for g in ["A", "B", "C", "D", "F"]
        },
        "median_quality": round(profiles_df["quality_score"].median(), 3),
    }

    print(f"  Avg completeness:  {stats['avg_completeness']}")
    print(f"  Avg recency:       {stats['avg_recency']}")
    print(f"  Avg confidence:    {stats['avg_confidence']}")
    print(f"  Avg quality score: {stats['avg_quality']}")
    print(f"  Grade distribution: {stats['grade_distribution']}")

    return profiles_df, stats
