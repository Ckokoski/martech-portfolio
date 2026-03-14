"""
profile_builder.py — Creates unified customer profiles from clustered records.

Merge rules:
  - Contact info (name, email, phone, company): most recent non-empty value wins
  - Engagement metrics: aggregated (summed or averaged as appropriate)
  - Dates: most recent value
  - Source lineage: tracked per field
  - Transaction data: aggregated (total spend, order count)
"""

from __future__ import annotations

import json
import os
import sqlite3
from datetime import datetime

import pandas as pd


# ---------------------------------------------------------------------------
# Merge helpers
# ---------------------------------------------------------------------------

def _most_recent_value(series: pd.Series, dates: pd.Series | None = None) -> str:
    """
    Return the most recent non-empty value from *series*.
    If *dates* is provided, use it to determine recency; otherwise take
    the last non-empty value.
    """
    non_empty = series[series.astype(str).str.strip() != ""]
    if non_empty.empty:
        return ""
    if dates is not None:
        valid_dates = dates[non_empty.index]
        try:
            parsed = pd.to_datetime(valid_dates, errors="coerce")
            best_idx = parsed.idxmax()
            if pd.notna(best_idx):
                return str(non_empty.loc[best_idx])
        except Exception:
            pass
    return str(non_empty.iloc[-1])


def _safe_sum(series: pd.Series) -> float:
    """Sum numeric values, treating blanks and non-numeric as 0."""
    return pd.to_numeric(series, errors="coerce").fillna(0).sum()


def _safe_max_date(series: pd.Series) -> str:
    """Return the most recent date string from a series."""
    parsed = pd.to_datetime(series, errors="coerce")
    valid = parsed.dropna()
    if valid.empty:
        return ""
    return valid.max().strftime("%Y-%m-%d %H:%M:%S")


# ---------------------------------------------------------------------------
# Profile builder
# ---------------------------------------------------------------------------

def build_profiles(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """
    Build one unified profile per cluster_id.

    Returns
    -------
    profiles : pd.DataFrame
        One row per unified customer profile.
    stats : dict
        Build statistics.
    """
    print("\n=== Building unified profiles ===")

    profiles = []
    grouped = df.groupby("cluster_id")

    for cluster_id, group in grouped:
        sources = set(group["_source"].tolist())
        source_ids = group["_source_id"].tolist()

        # --- Contact info (most recent non-empty wins) ---
        # Try to find a date column for recency
        date_col = None
        for col_candidate in ["created_date", "last_engaged", "last_visit", "order_date"]:
            if col_candidate in group.columns:
                non_empty = group[col_candidate][group[col_candidate].astype(str).str.strip() != ""]
                if not non_empty.empty:
                    date_col = group[col_candidate]
                    break

        first_name = _most_recent_value(group.get("first_name_norm", pd.Series(dtype=str)), date_col)
        last_name = _most_recent_value(group.get("last_name_norm", pd.Series(dtype=str)), date_col)
        email = _most_recent_value(group.get("email_norm", pd.Series(dtype=str)), date_col)
        phone = _most_recent_value(group.get("phone_norm", pd.Series(dtype=str)), date_col)
        company = _most_recent_value(group.get("company", pd.Series(dtype=str)), date_col)
        job_title = _most_recent_value(group.get("job_title", pd.Series(dtype=str)), date_col)
        region = _most_recent_value(group.get("region", pd.Series(dtype=str)), date_col)

        # --- Email engagement (summed) ---
        open_count = _safe_sum(group.get("open_count", pd.Series(dtype=str)))
        click_count = _safe_sum(group.get("click_count", pd.Series(dtype=str)))
        subscriber_status = _most_recent_value(
            group.get("subscriber_status", pd.Series(dtype=str)), date_col
        )
        last_engaged = _safe_max_date(group.get("last_engaged", pd.Series(dtype=str)))

        # --- Web engagement (summed) ---
        page_views = _safe_sum(group.get("page_views", pd.Series(dtype=str)))
        sessions = _safe_sum(group.get("sessions", pd.Series(dtype=str)))
        last_visit = _safe_max_date(group.get("last_visit", pd.Series(dtype=str)))

        # --- Transaction metrics (aggregated) ---
        total_spend = round(_safe_sum(group.get("amount", pd.Series(dtype=str))), 2)
        order_count = int(group.get("order_id", pd.Series(dtype=str)).replace("", pd.NA).dropna().nunique())

        # --- Match confidence ---
        match_confidence = float(group["match_confidence"].max()) if "match_confidence" in group.columns else 0.0

        # --- Source lineage ---
        lineage = {
            "sources": sorted(sources),
            "source_record_count": len(group),
            "source_ids": source_ids,
        }

        # --- Most recent activity across all sources ---
        all_dates = []
        for dcol in ["created_date", "last_engaged", "last_visit", "order_date"]:
            if dcol in group.columns:
                all_dates.append(group[dcol])
        if all_dates:
            combined_dates = pd.concat(all_dates)
            last_activity = _safe_max_date(combined_dates)
        else:
            last_activity = ""

        profiles.append({
            "cluster_id": cluster_id,
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "phone": phone,
            "company": company,
            "job_title": job_title,
            "region": region,
            "subscriber_status": subscriber_status,
            "open_count": int(open_count),
            "click_count": int(click_count),
            "last_engaged": last_engaged,
            "page_views": int(page_views),
            "sessions": int(sessions),
            "last_visit": last_visit,
            "total_spend": total_spend,
            "order_count": order_count,
            "match_confidence": round(match_confidence, 2),
            "source_count": len(sources),
            "sources": ",".join(sorted(sources)),
            "last_activity": last_activity,
            "source_lineage": json.dumps(lineage),
        })

    profiles_df = pd.DataFrame(profiles)

    stats = {
        "total_profiles": len(profiles_df),
        "multi_source_profiles": int((profiles_df["source_count"] > 1).sum()),
        "single_source_profiles": int((profiles_df["source_count"] == 1).sum()),
        "avg_sources_per_profile": round(profiles_df["source_count"].mean(), 2),
    }

    print(f"  Unified profiles built:     {stats['total_profiles']:,}")
    print(f"  Multi-source profiles:      {stats['multi_source_profiles']:,}")
    print(f"  Single-source profiles:     {stats['single_source_profiles']:,}")
    print(f"  Avg sources per profile:    {stats['avg_sources_per_profile']}")

    return profiles_df, stats


# ---------------------------------------------------------------------------
# SQLite persistence
# ---------------------------------------------------------------------------

def save_to_sqlite(profiles_df: pd.DataFrame,
                   db_path: str = "output/unified_profiles.db") -> str:
    """Write unified profiles to a SQLite database and return the path."""
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    profiles_df.to_sql("unified_profiles", conn, if_exists="replace", index=False)

    # Create useful indexes
    cursor = conn.cursor()
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_email ON unified_profiles(email)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_company ON unified_profiles(company)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_cluster ON unified_profiles(cluster_id)")
    conn.commit()
    conn.close()

    print(f"\n  Profiles saved to SQLite:   {db_path}")
    return db_path


def save_to_csv(profiles_df: pd.DataFrame,
                csv_path: str = "output/unified_profiles.csv") -> str:
    """Write unified profiles to CSV and return the path."""
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)
    profiles_df.to_csv(csv_path, index=False)
    print(f"  Profiles saved to CSV:      {csv_path}")
    return csv_path
