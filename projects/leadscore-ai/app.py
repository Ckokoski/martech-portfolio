"""
app.py — LeadScore AI: ML-Powered Lead Scoring Pipeline

Main entry point. Runs the full pipeline:
  1. Generate synthetic B2B SaaS lead data
  2. Engineer ML features
  3. Train XGBoost classifier
  4. Evaluate model performance
  5. Compute SHAP explanations
  6. Generate visualizations
  7. Output scored leads + interactive HTML report

Usage:
    python app.py
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

import sys
import time
from pathlib import Path

# Ensure project root is on the path so modules can import each other
PROJECT_DIR = Path(__file__).parent
sys.path.insert(0, str(PROJECT_DIR))

DATA_DIR = PROJECT_DIR / "data"


def main():
    """Run the full LeadScore AI pipeline."""
    start = time.time()
    print("=" * 60)
    print("  LeadScore AI — ML-Powered Lead Scoring")
    print("=" * 60)

    # ── Step 1: Generate synthetic data ──────────────────────────────────
    print("\n[1/7] Generating synthetic lead data...")
    from data_generator import generate_leads, save_leads

    leads = generate_leads()
    save_leads(leads, output_dir=str(DATA_DIR))

    # ── Step 2: Feature engineering ──────────────────────────────────────
    print("\n[2/7] Engineering features...")
    from feature_engineering import engineer_features

    enriched = engineer_features(leads)

    # ── Step 3: Train model ──────────────────────────────────────────────
    print("\n[3/7] Training XGBoost model...")
    from model import train_model

    results = train_model(enriched)

    # ── Step 4: Evaluate ─────────────────────────────────────────────────
    print("\n[4/7] Evaluating model...")
    from model import evaluate_model, score_all_leads

    metrics = evaluate_model(results)

    # Score all leads
    print("\n[5/7] Scoring all leads...")
    scored_df = score_all_leads(enriched, results)

    # Save scored leads to CSV
    scored_output = DATA_DIR / "scored_leads.csv"
    # Select key columns for the output file
    output_cols = [
        "lead_id", "lead_score", "lead_tier",
        "industry", "company_size", "job_title", "seniority",
        "region", "lead_source",
        "email_opens", "email_clicks", "page_visits_total",
        "pricing_page_visits", "demo_page_visits",
        "content_downloads", "webinar_attended", "form_submissions",
        "days_since_first_touch", "days_since_last_engagement",
        "converted",
    ]
    scored_df[output_cols].to_csv(scored_output, index=False)
    print(f"  -> Scored leads saved to {scored_output}")

    # ── Step 5: SHAP explanations ────────────────────────────────────────
    print("\n[6/7] Computing SHAP explanations...")
    from explainer import (
        compute_shap_values,
        get_global_importance,
        get_individual_explanation,
    )

    shap_results = compute_shap_values(results)
    shap_importance = get_global_importance(shap_results)
    high_explanation = get_individual_explanation(shap_results, results, "high")
    low_explanation = get_individual_explanation(shap_results, results, "low")

    # ── Step 6: Generate visualizations ──────────────────────────────────
    print("\n[7/7] Generating report...")
    from visualizations import generate_all_charts
    from report import generate_report

    charts = generate_all_charts(
        scored_df, metrics, results,
        shap_importance, high_explanation, low_explanation,
    )

    report_path = generate_report(
        scored_df, metrics, charts,
        output_dir=str(DATA_DIR),
    )

    # ── Done ─────────────────────────────────────────────────────────────
    elapsed = time.time() - start
    print("\n" + "=" * 60)
    print("  Pipeline complete!")
    print(f"  Time elapsed: {elapsed:.1f}s")
    print(f"\n  Outputs:")
    print(f"    Raw data:     {DATA_DIR / 'raw_leads.csv'}")
    print(f"    Scored leads: {scored_output}")
    print(f"    HTML report:  {report_path}")
    print(f"\n  Open the report in a browser:")
    print(f"    {report_path.resolve()}")
    print("=" * 60)


if __name__ == "__main__":
    main()
