"""
app.py — SendPulse Analytics: Main Entry Point

AI-powered email campaign analysis tool that:
1. Generates synthetic campaign data (100 campaigns, 50K subscribers)
2. Runs multi-dimensional analysis (trends, subject lines, send times, list health, segmentation)
3. Produces rule-based recommendations
4. Outputs an interactive HTML report with Plotly charts

Usage:
    python app.py              # Generate data + full analysis + report
    python app.py --load       # Load existing data from data/ directory
"""

import sys
import os
import time

# Ensure project root is on the path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data_generator import generate_all, load_data
from analyzer import run_full_analysis
from visualizations import generate_all_charts
from recommendations import generate_recommendations
from report import generate_report


def main():
    """Run the full SendPulse Analytics pipeline."""
    start = time.time()

    print("=" * 60)
    print("  SendPulse Analytics — Email Campaign Analysis Tool")
    print("=" * 60)
    print()

    # Step 1: Data
    load_existing = "--load" in sys.argv
    data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

    if load_existing and os.path.exists(os.path.join(data_dir, "campaigns.csv")):
        print("[1/4] Loading existing data from data/ directory...")
        campaigns_df, subscribers_df = load_data()
        print(f"       Loaded {len(campaigns_df)} campaigns, {len(subscribers_df):,} subscribers.")
    else:
        print("[1/4] Generating synthetic email campaign data...")
        campaigns_df, subscribers_df = generate_all()

    print(f"       Campaigns: {len(campaigns_df)}")
    print(f"       Subscribers: {len(subscribers_df):,}")
    print()

    # Step 2: Analysis
    print("[2/4] Running analysis engine...")
    analysis_results = run_full_analysis(campaigns_df, subscribers_df)
    print()

    # Step 3: Recommendations
    print("[3/4] Generating recommendations...")
    recs = generate_recommendations(analysis_results)
    print()

    # Step 4: Visualization & Report
    print("[4/4] Building interactive report...")
    charts = generate_all_charts(analysis_results, campaigns_df)
    report_path = generate_report(analysis_results, charts, recs)

    elapsed = time.time() - start
    print()
    print("=" * 60)
    print(f"  Analysis complete in {elapsed:.1f}s")
    print(f"  Report: {report_path}")
    print(f"  Open in your browser to explore the interactive charts.")
    print("=" * 60)

    return report_path


if __name__ == "__main__":
    main()
