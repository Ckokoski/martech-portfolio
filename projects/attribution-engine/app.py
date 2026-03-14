"""
Attribution Engine - Multi-Touch Marketing Attribution Modeling Tool

Main entry point. Orchestrates the full attribution analysis pipeline:
1. Generate synthetic multi-channel touchpoint data
2. Run 5 attribution models (first-touch, last-touch, linear, time-decay, Markov)
3. Calculate channel ROI and perform path analysis
4. Generate interactive HTML report with Plotly visualizations

Usage:
    python app.py
"""

import os
import sys
import time
import webbrowser

# Ensure the project root is on the Python path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from data_generator import generate_touchpoint_data
from analyzer import run_all_models, calculate_roi, analyze_paths, build_sankey_data
from models.markov import get_transition_matrix
from visualizations import create_all_charts
from report import generate_report


def main():
    """Run the full attribution analysis pipeline."""
    start_time = time.time()

    print("=" * 60)
    print("  ATTRIBUTION ENGINE")
    print("  Multi-Touch Marketing Attribution Modeling Tool")
    print("=" * 60)

    # ── Step 1: Generate data ────────────────────────────────────────────
    print("\n[1/5] Generating synthetic touchpoint data...")
    touchpoints_df, spend_df = generate_touchpoint_data(
        n_conversions=5000,
        n_non_converting=3000,
        seed=42,
    )

    total_touchpoints = len(touchpoints_df)
    total_journeys = touchpoints_df["journey_id"].nunique()
    converting = touchpoints_df[touchpoints_df["converted"]]["journey_id"].nunique()

    print(f"       {total_touchpoints:,} touchpoints across {total_journeys:,} journeys")
    print(f"       {converting:,} converting | {total_journeys - converting:,} non-converting")

    # Save raw data to CSV for reference
    data_dir = os.path.join(PROJECT_ROOT, "data")
    os.makedirs(data_dir, exist_ok=True)
    touchpoints_path = os.path.join(data_dir, "touchpoints.csv")
    spend_path = os.path.join(data_dir, "channel_spend.csv")

    touchpoints_df.to_csv(touchpoints_path, index=False)
    spend_df.to_csv(spend_path, index=False)
    print(f"       Saved to data/touchpoints.csv and data/channel_spend.csv")

    # ── Step 2: Run attribution models ───────────────────────────────────
    print("\n[2/5] Running attribution models...")
    attribution_results = run_all_models(touchpoints_df)

    # ── Step 3: Calculate ROI and path analysis ──────────────────────────
    print("\n[3/5] Calculating ROI and analyzing paths...")
    attribution_with_roi = calculate_roi(attribution_results, spend_df)
    path_analysis = analyze_paths(touchpoints_df)
    sankey_data = build_sankey_data(touchpoints_df)
    transition_matrix = get_transition_matrix(touchpoints_df)

    # Print summary to console
    _print_summary(attribution_with_roi, path_analysis)

    # ── Step 4: Generate visualizations ──────────────────────────────────
    print("\n[4/5] Generating visualizations...")
    charts = create_all_charts(
        attribution_with_roi,
        spend_df,
        path_analysis,
        sankey_data,
        transition_matrix,
    )

    # ── Step 5: Generate HTML report ─────────────────────────────────────
    print("\n[5/5] Generating HTML report...")
    report_path = os.path.join(data_dir, "attribution_report.html")
    output_path = generate_report(
        attribution_df=attribution_with_roi,
        path_analysis=path_analysis,
        charts=charts,
        top_paths=path_analysis["top_paths"],
        total_touchpoints=total_touchpoints,
        output_path=report_path,
    )

    elapsed = time.time() - start_time

    print("\n" + "=" * 60)
    print(f"  COMPLETE in {elapsed:.1f}s")
    print(f"  Report: {output_path}")
    print("=" * 60)

    # Open report in browser
    try:
        webbrowser.open(f"file://{output_path}")
        print("\n  Report opened in your default browser.")
    except Exception:
        print(f"\n  Open the report manually: {output_path}")


def _print_summary(attribution_df, path_analysis):
    """Print a console summary of key findings."""
    print(f"\n  --- Path Analysis ---")
    print(f"  Avg touchpoints to conversion: {path_analysis['avg_touchpoints']}")
    print(f"  Avg days to conversion:        {path_analysis['avg_days']}")
    print(f"  Conversion rate:               {path_analysis['conversion_rate']}%")

    print(f"\n  --- Attribution Summary (Markov Chain Model) ---")
    markov = attribution_df[attribution_df["model"] == "Markov Chain"].copy()
    markov = markov.sort_values("attributed_revenue", ascending=False)

    print(f"  {'Channel':<20} {'Conv':>8} {'Revenue':>12} {'ROI':>8} {'Credit':>8}")
    print(f"  {'-'*56}")
    for _, row in markov.iterrows():
        print(
            f"  {row['channel']:<20} "
            f"{row['attributed_conversions']:>8.0f} "
            f"${row['attributed_revenue']:>10,.0f} "
            f"{row['roi']:>7.2f}x "
            f"{row['credit_pct']:>6.1f}%"
        )

    # Highlight key insight: biggest gap between first-touch and last-touch
    ft = attribution_df[attribution_df["model"] == "First Touch"].set_index("channel")
    lt = attribution_df[attribution_df["model"] == "Last Touch"].set_index("channel")
    gaps = (ft["credit_pct"] - lt["credit_pct"]).abs()
    biggest_gap_channel = gaps.idxmax()
    ft_pct = ft.loc[biggest_gap_channel, "credit_pct"]
    lt_pct = lt.loc[biggest_gap_channel, "credit_pct"]

    print(f"\n  --- Key Insight ---")
    print(
        f"  Biggest attribution gap: {biggest_gap_channel} "
        f"({ft_pct:.1f}% first-touch vs {lt_pct:.1f}% last-touch)"
    )


if __name__ == "__main__":
    main()
