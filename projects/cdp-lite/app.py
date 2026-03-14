"""
app.py — CDP Lite: Customer Data Unifier

Main entry point that orchestrates the full ETL pipeline:
  1. Generate synthetic multi-source customer data
  2. Ingest and normalise all sources
  3. Resolve identities (email, phone, fuzzy name+company)
  4. Build unified golden profiles
  5. Score data quality
  6. Export audience segments
  7. Generate HTML pipeline report

Usage:
    python app.py
"""

import os
import sys
import time

# Ensure the project root is on the path so modules resolve correctly
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(PROJECT_DIR)
sys.path.insert(0, PROJECT_DIR)

from data_generator import generate_all
from ingestion import ingest_all
from identity_resolution import resolve_identities
from profile_builder import build_profiles, save_to_sqlite, save_to_csv
from quality_scorer import score_profiles
from segment_exporter import export_segments
from report import generate_report


# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
DATA_DIR = os.path.join(PROJECT_DIR, "data")
OUTPUT_DIR = os.path.join(PROJECT_DIR, "output")
TEMPLATE_DIR = os.path.join(PROJECT_DIR, "templates")
REPORT_PATH = os.path.join(OUTPUT_DIR, "pipeline_report.html")
DB_PATH = os.path.join(OUTPUT_DIR, "unified_profiles.db")
CSV_PATH = os.path.join(OUTPUT_DIR, "unified_profiles.csv")


def main() -> None:
    """Run the full CDP Lite pipeline."""
    print("=" * 60)
    print("  CDP Lite — Customer Data Unifier")
    print("=" * 60)

    pipeline_start = time.time()

    # ------------------------------------------------------------------
    # Step 1: Generate synthetic data
    # ------------------------------------------------------------------
    generate_all(data_dir=DATA_DIR)

    # ------------------------------------------------------------------
    # Step 2: Ingest and normalise
    # ------------------------------------------------------------------
    sources = ingest_all(data_dir=DATA_DIR)
    combined = sources.pop("all")
    source_counts = {name: len(df) for name, df in sources.items()}

    # ------------------------------------------------------------------
    # Step 3: Identity resolution
    # ------------------------------------------------------------------
    resolved_df, resolution_stats = resolve_identities(combined)

    # ------------------------------------------------------------------
    # Step 4: Build unified profiles
    # ------------------------------------------------------------------
    profiles, profile_stats = build_profiles(resolved_df)

    # ------------------------------------------------------------------
    # Step 5: Quality scoring
    # ------------------------------------------------------------------
    profiles, quality_stats = score_profiles(profiles)

    # ------------------------------------------------------------------
    # Step 6: Save profiles
    # ------------------------------------------------------------------
    save_to_sqlite(profiles, db_path=DB_PATH)
    save_to_csv(profiles, csv_path=CSV_PATH)

    # ------------------------------------------------------------------
    # Step 7: Export audience segments
    # ------------------------------------------------------------------
    segment_results = export_segments(profiles, output_dir=OUTPUT_DIR)

    # ------------------------------------------------------------------
    # Step 8: Generate HTML report
    # ------------------------------------------------------------------
    report_path = generate_report(
        profiles=profiles,
        source_counts=source_counts,
        resolution_stats=resolution_stats,
        profile_stats=profile_stats,
        quality_stats=quality_stats,
        segment_results=segment_results,
        output_path=REPORT_PATH,
        template_dir=TEMPLATE_DIR,
    )

    # ------------------------------------------------------------------
    # Done
    # ------------------------------------------------------------------
    elapsed = round(time.time() - pipeline_start, 2)
    print("\n" + "=" * 60)
    print("  Pipeline complete!")
    print("=" * 60)
    print(f"\n  Total time:      {elapsed}s")
    print(f"  Profiles:        {OUTPUT_DIR}/unified_profiles.csv")
    print(f"  SQLite DB:       {DB_PATH}")
    print(f"  Segments:        {OUTPUT_DIR}/segment_*.csv")
    print(f"  Report:          {report_path}")
    print()


if __name__ == "__main__":
    main()
