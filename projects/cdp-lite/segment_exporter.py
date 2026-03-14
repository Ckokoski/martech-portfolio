"""
segment_exporter.py — Generates audience segments from unified profiles.

Segments:
  1. High-value customers   — top 20 % by total spend
  2. Engaged subscribers    — high email + web engagement
  3. At-risk customers      — declining / low recent engagement
"""

from __future__ import annotations

import os

import pandas as pd


# ---------------------------------------------------------------------------
# Segment definitions
# ---------------------------------------------------------------------------

def _segment_high_value(profiles: pd.DataFrame) -> pd.DataFrame:
    """
    Top 20 % of profiles by total_spend (among those with any spend).
    """
    spenders = profiles[profiles["total_spend"] > 0].copy()
    if spenders.empty:
        return spenders
    threshold = spenders["total_spend"].quantile(0.80)
    return spenders[spenders["total_spend"] >= threshold].copy()


def _segment_engaged(profiles: pd.DataFrame) -> pd.DataFrame:
    """
    Profiles that are both email-active and web-active.
    Criteria:
      - subscriber_status == 'active'
      - open_count >= median open_count (among actives)
      - page_views >= median page_views (among those with any)
    """
    active = profiles[profiles["subscriber_status"] == "active"].copy()
    if active.empty:
        return active

    med_opens = active["open_count"].median()
    med_views = profiles[profiles["page_views"] > 0]["page_views"].median()

    engaged = active[
        (active["open_count"] >= med_opens)
        & (active["page_views"] >= med_views)
    ].copy()
    return engaged


def _segment_at_risk(profiles: pd.DataFrame) -> pd.DataFrame:
    """
    Profiles showing signs of declining engagement:
      - Have historical engagement (open_count > 0 or page_views > 0)
      - But low recency_score (< 0.30) — haven't been active recently
      - OR subscriber_status is 'unsubscribed'
    """
    has_history = profiles[
        (profiles["open_count"] > 0) | (profiles["page_views"] > 0)
    ].copy()
    if has_history.empty:
        return has_history

    at_risk = has_history[
        (has_history["recency_score"] < 0.30)
        | (has_history["subscriber_status"] == "unsubscribed")
    ].copy()
    return at_risk


# ---------------------------------------------------------------------------
# Export columns — what a platform import file typically needs
# ---------------------------------------------------------------------------

EXPORT_COLS = [
    "cluster_id", "first_name", "last_name", "email", "phone",
    "company", "region", "total_spend", "order_count",
    "open_count", "click_count", "page_views", "sessions",
    "quality_score", "quality_grade",
]


def _export_segment(segment_df: pd.DataFrame, name: str,
                    output_dir: str) -> str:
    """Write a segment CSV and return its path."""
    # Only include columns that exist
    cols = [c for c in EXPORT_COLS if c in segment_df.columns]
    out_path = os.path.join(output_dir, f"segment_{name}.csv")
    segment_df[cols].to_csv(out_path, index=False)
    return out_path


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def export_segments(profiles: pd.DataFrame,
                    output_dir: str = "output") -> dict:
    """
    Generate audience segments and export them as CSVs.

    Returns a dict with segment names -> {count, path, description}.
    """
    print("\n=== Exporting audience segments ===")
    os.makedirs(output_dir, exist_ok=True)

    segment_defs = {
        "high_value": {
            "fn": _segment_high_value,
            "description": "Top 20% of customers by total transaction spend",
        },
        "engaged": {
            "fn": _segment_engaged,
            "description": "Active email subscribers with above-median email and web engagement",
        },
        "at_risk": {
            "fn": _segment_at_risk,
            "description": "Previously engaged customers with declining recent activity",
        },
    }

    results = {}
    for name, defn in segment_defs.items():
        seg_df = defn["fn"](profiles)
        path = _export_segment(seg_df, name, output_dir)
        results[name] = {
            "count": len(seg_df),
            "path": path,
            "description": defn["description"],
        }
        print(f"  [{name:<14}] {len(seg_df):>6,} profiles -> {path}")

    return results
