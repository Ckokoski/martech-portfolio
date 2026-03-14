"""
analyzer.py — Campaign Analysis Engine

Performs multi-dimensional analysis on email campaign data:
- Performance trends over time
- Subject line pattern analysis
- Send time optimization analysis
- List health metrics
- Subscriber segmentation via K-means clustering
"""

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler


def analyze_performance_trends(campaigns_df: pd.DataFrame) -> dict:
    """Compute monthly aggregated performance metrics and trend directions.

    Returns a dict with:
        - monthly_df: DataFrame with monthly averages
        - overall_stats: dict of overall averages
        - trend_direction: dict indicating if each metric is improving/declining
    """
    df = campaigns_df.copy()
    df["send_date"] = pd.to_datetime(df["send_date"])
    df["month"] = df["send_date"].dt.to_period("M").astype(str)

    monthly = df.groupby("month").agg(
        campaigns_count=("campaign_id", "count"),
        avg_open_rate=("open_rate", "mean"),
        avg_click_rate=("click_rate", "mean"),
        avg_bounce_rate=("bounce_rate", "mean"),
        avg_unsub_rate=("unsubscribe_rate", "mean"),
        total_sent=("sent", "sum"),
        total_delivered=("delivered", "sum"),
        total_opened=("opened", "sum"),
        total_clicked=("clicked", "sum"),
        total_revenue=("revenue", "sum"),
    ).reset_index()

    # Compute trend direction (compare last 3 months to first 3 months)
    if len(monthly) >= 6:
        first_q = monthly.head(3)
        last_q = monthly.tail(3)
    else:
        first_q = monthly.head(len(monthly) // 2)
        last_q = monthly.tail(len(monthly) // 2)

    trends = {}
    for metric in ["avg_open_rate", "avg_click_rate", "avg_bounce_rate", "avg_unsub_rate"]:
        diff = last_q[metric].mean() - first_q[metric].mean()
        if abs(diff) < 0.005:
            trends[metric] = "stable"
        elif diff > 0:
            trends[metric] = "increasing"
        else:
            trends[metric] = "decreasing"

    overall = {
        "avg_open_rate": round(df["open_rate"].mean(), 4),
        "avg_click_rate": round(df["click_rate"].mean(), 4),
        "avg_bounce_rate": round(df["bounce_rate"].mean(), 4),
        "avg_unsub_rate": round(df["unsubscribe_rate"].mean(), 4),
        "total_campaigns": len(df),
        "total_sent": int(df["sent"].sum()),
        "total_revenue": round(df["revenue"].sum(), 2),
        "avg_revenue_per_campaign": round(df["revenue"].mean(), 2),
    }

    return {
        "monthly_df": monthly,
        "overall_stats": overall,
        "trend_direction": trends,
    }


def analyze_subject_lines(campaigns_df: pd.DataFrame) -> dict:
    """Analyze the relationship between subject line features and open rate.

    Features examined:
        - Subject length bins
        - Personalization ({{first_name}})
        - Urgency words
        - Emoji usage
    """
    df = campaigns_df.copy()

    # Length buckets
    bins = [0, 40, 60, 80, 120, 999]
    labels = ["<40", "40-60", "60-80", "80-120", "120+"]
    df["length_bucket"] = pd.cut(df["subject_length"], bins=bins, labels=labels)

    length_perf = df.groupby("length_bucket", observed=True).agg(
        avg_open_rate=("open_rate", "mean"),
        count=("campaign_id", "count"),
    ).reset_index()

    # Feature comparison
    features = {}
    for feature in ["has_personalization", "has_emoji", "has_urgency"]:
        group = df.groupby(feature)["open_rate"].mean()
        features[feature] = {
            "with": round(group.get(True, 0), 4),
            "without": round(group.get(False, 0), 4),
            "lift": round(group.get(True, 0) - group.get(False, 0), 4),
        }

    # Top 10 performing subject lines
    top_subjects = (
        df.nlargest(10, "open_rate")[["subject_line", "open_rate", "click_rate", "campaign_type"]]
        .to_dict("records")
    )

    # Bottom 5 performing subject lines
    bottom_subjects = (
        df.nsmallest(5, "open_rate")[["subject_line", "open_rate", "click_rate", "campaign_type"]]
        .to_dict("records")
    )

    return {
        "length_performance": length_perf,
        "feature_impact": features,
        "top_subjects": top_subjects,
        "bottom_subjects": bottom_subjects,
    }


def analyze_send_times(campaigns_df: pd.DataFrame) -> dict:
    """Analyze engagement by hour of day and day of week.

    Returns heatmap-ready data plus best/worst time slots.
    """
    df = campaigns_df.copy()

    # By hour
    hour_perf = df.groupby("send_hour").agg(
        avg_open_rate=("open_rate", "mean"),
        avg_click_rate=("click_rate", "mean"),
        count=("campaign_id", "count"),
    ).reset_index()

    # By day of week
    dow_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    dow_perf = df.groupby("send_dow").agg(
        avg_open_rate=("open_rate", "mean"),
        avg_click_rate=("click_rate", "mean"),
        count=("campaign_id", "count"),
    ).reset_index()
    dow_perf["send_dow"] = pd.Categorical(dow_perf["send_dow"], categories=dow_order, ordered=True)
    dow_perf = dow_perf.sort_values("send_dow")

    # Heatmap: hour x dow
    heatmap = df.pivot_table(
        values="open_rate",
        index="send_hour",
        columns="send_dow",
        aggfunc="mean",
    )
    # Reorder columns
    heatmap = heatmap.reindex(columns=[d for d in dow_order if d in heatmap.columns])

    # Best and worst slots
    best_hour = hour_perf.loc[hour_perf["avg_open_rate"].idxmax()]
    worst_hour = hour_perf.loc[hour_perf["avg_open_rate"].idxmin()]
    best_dow = dow_perf.loc[dow_perf["avg_open_rate"].idxmax()]

    return {
        "hour_performance": hour_perf,
        "dow_performance": dow_perf,
        "heatmap": heatmap,
        "best_hour": int(best_hour["send_hour"]),
        "best_hour_rate": round(float(best_hour["avg_open_rate"]), 4),
        "worst_hour": int(worst_hour["send_hour"]),
        "worst_hour_rate": round(float(worst_hour["avg_open_rate"]), 4),
        "best_dow": str(best_dow["send_dow"]),
        "best_dow_rate": round(float(best_dow["avg_open_rate"]), 4),
    }


def analyze_list_health(campaigns_df: pd.DataFrame) -> dict:
    """Assess list health through bounce and unsubscribe trends.

    Flags campaigns with abnormally high bounce or unsubscribe rates.
    """
    df = campaigns_df.copy()
    df["send_date"] = pd.to_datetime(df["send_date"])

    # Rolling averages (sorted by date)
    df_sorted = df.sort_values("send_date")
    df_sorted["bounce_rate_rolling"] = df_sorted["bounce_rate"].rolling(5, min_periods=1).mean()
    df_sorted["unsub_rate_rolling"] = df_sorted["unsubscribe_rate"].rolling(5, min_periods=1).mean()

    # Flag outliers (> 2 std above mean)
    bounce_mean = df["bounce_rate"].mean()
    bounce_std = df["bounce_rate"].std()
    unsub_mean = df["unsubscribe_rate"].mean()
    unsub_std = df["unsubscribe_rate"].std()

    high_bounce = df[df["bounce_rate"] > bounce_mean + 2 * bounce_std][
        ["campaign_id", "campaign_name", "send_date", "bounce_rate"]
    ].to_dict("records")

    high_unsub = df[df["unsubscribe_rate"] > unsub_mean + 2 * unsub_std][
        ["campaign_id", "campaign_name", "send_date", "unsubscribe_rate"]
    ].to_dict("records")

    # Monthly unsubscribe velocity
    df["month"] = df["send_date"].dt.to_period("M").astype(str)
    monthly_unsubs = df.groupby("month")["unsubscribed"].sum().reset_index()
    monthly_unsubs.columns = ["month", "total_unsubscribes"]

    return {
        "rolling_df": df_sorted[["send_date", "bounce_rate", "bounce_rate_rolling",
                                  "unsubscribe_rate", "unsub_rate_rolling"]],
        "high_bounce_campaigns": high_bounce,
        "high_unsub_campaigns": high_unsub,
        "bounce_stats": {"mean": round(bounce_mean, 4), "std": round(bounce_std, 4)},
        "unsub_stats": {"mean": round(unsub_mean, 4), "std": round(unsub_std, 4)},
        "monthly_unsubs": monthly_unsubs,
    }


def segment_subscribers(subscribers_df: pd.DataFrame, n_clusters: int = 4) -> dict:
    """Cluster subscribers by engagement using K-means.

    Features used:
        - avg_open_rate
        - avg_click_rate
        - days_since_last_open (inverted — recency)
        - total_purchases

    Returns cluster labels and centroids.
    """
    df = subscribers_df.copy()
    feature_cols = ["avg_open_rate", "avg_click_rate", "days_since_last_open", "total_purchases"]

    X = df[feature_cols].values
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    labels = kmeans.fit_predict(X_scaled)
    df["cluster"] = labels

    # Compute cluster profiles
    cluster_profiles = df.groupby("cluster").agg(
        count=("subscriber_id", "count"),
        avg_open_rate=("avg_open_rate", "mean"),
        avg_click_rate=("avg_click_rate", "mean"),
        avg_days_since_open=("days_since_last_open", "mean"),
        avg_purchases=("total_purchases", "mean"),
    ).reset_index()

    # Name clusters by engagement level (sort by open rate descending)
    cluster_profiles = cluster_profiles.sort_values("avg_open_rate", ascending=False).reset_index(drop=True)
    cluster_names = ["Champions", "Active", "At-Risk", "Dormant"]
    # Map original cluster IDs to names
    name_map = dict(zip(cluster_profiles["cluster"], cluster_names[:len(cluster_profiles)]))
    df["segment_name"] = df["cluster"].map(name_map)
    cluster_profiles["segment_name"] = cluster_profiles["cluster"].map(name_map)

    # Segment distribution
    segment_dist = df["segment_name"].value_counts().to_dict()

    return {
        "subscribers_segmented": df,
        "cluster_profiles": cluster_profiles,
        "segment_distribution": segment_dist,
        "cluster_name_map": name_map,
    }


def run_full_analysis(campaigns_df: pd.DataFrame, subscribers_df: pd.DataFrame) -> dict:
    """Execute all analyses and return a consolidated results dict."""
    print("[Analyzer] Running performance trend analysis...")
    performance = analyze_performance_trends(campaigns_df)

    print("[Analyzer] Analyzing subject line patterns...")
    subject_lines = analyze_subject_lines(campaigns_df)

    print("[Analyzer] Analyzing send time patterns...")
    send_times = analyze_send_times(campaigns_df)

    print("[Analyzer] Evaluating list health...")
    list_health = analyze_list_health(campaigns_df)

    print("[Analyzer] Segmenting subscribers (K-means)...")
    segmentation = segment_subscribers(subscribers_df)

    return {
        "performance": performance,
        "subject_lines": subject_lines,
        "send_times": send_times,
        "list_health": list_health,
        "segmentation": segmentation,
    }
