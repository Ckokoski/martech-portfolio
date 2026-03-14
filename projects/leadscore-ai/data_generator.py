"""
data_generator.py — Generates synthetic B2B SaaS lead data.

Creates 10,000 leads with realistic demographics, behavioral signals,
and temporal features. Conversion rate is tuned to ~8% to reflect
real-world B2B SaaS pipeline ratios.
"""

import numpy as np
import pandas as pd
from pathlib import Path

# ── Constants ────────────────────────────────────────────────────────────────

SEED = 42
N_LEADS = 10_000
TARGET_CONVERSION_RATE = 0.08

INDUSTRIES = [
    "SaaS/Technology", "Financial Services", "Healthcare",
    "E-commerce/Retail", "Manufacturing", "Education",
    "Media/Entertainment", "Professional Services",
    "Telecommunications", "Government/Public Sector",
]

COMPANY_SIZE_BUCKETS = [
    "1-10", "11-50", "51-200", "201-500",
    "501-1000", "1001-5000", "5000+",
]

JOB_TITLES = [
    "CMO", "VP Marketing", "Director of Marketing",
    "Marketing Manager", "Marketing Coordinator",
    "Head of Growth", "Demand Gen Manager",
    "VP Sales", "Sales Director", "SDR/BDR",
    "CTO", "VP Engineering", "Product Manager",
    "CEO/Founder", "COO", "Analyst",
]

SENIORITY_MAP = {
    "CMO": "C-Suite", "VP Marketing": "VP", "Director of Marketing": "Director",
    "Marketing Manager": "Manager", "Marketing Coordinator": "Individual Contributor",
    "Head of Growth": "Director", "Demand Gen Manager": "Manager",
    "VP Sales": "VP", "Sales Director": "Director", "SDR/BDR": "Individual Contributor",
    "CTO": "C-Suite", "VP Engineering": "VP", "Product Manager": "Manager",
    "CEO/Founder": "C-Suite", "COO": "C-Suite", "Analyst": "Individual Contributor",
}

SENIORITY_LEVELS = ["C-Suite", "VP", "Director", "Manager", "Individual Contributor"]

REGIONS = [
    "North America", "Europe", "Asia-Pacific",
    "Latin America", "Middle East/Africa",
]

LEAD_SOURCES = [
    "Organic Search", "Paid Search", "Social Media",
    "Content Syndication", "Webinar", "Referral",
    "Trade Show", "Direct Traffic", "Email Campaign",
    "Partner",
]


def generate_leads(n: int = N_LEADS, seed: int = SEED) -> pd.DataFrame:
    """
    Generate synthetic lead data with demographics, behavioral signals,
    and a binary conversion outcome.

    Parameters
    ----------
    n : int
        Number of leads to generate.
    seed : int
        Random seed for reproducibility.

    Returns
    -------
    pd.DataFrame
        DataFrame with one row per lead.
    """
    rng = np.random.default_rng(seed)

    # ── Demographics ─────────────────────────────────────────────────────
    industries = rng.choice(INDUSTRIES, size=n)
    company_sizes = rng.choice(
        COMPANY_SIZE_BUCKETS, size=n,
        p=[0.10, 0.15, 0.25, 0.20, 0.15, 0.10, 0.05],
    )
    job_titles = rng.choice(JOB_TITLES, size=n)
    seniority = np.array([SENIORITY_MAP[t] for t in job_titles])
    regions = rng.choice(
        REGIONS, size=n,
        p=[0.40, 0.30, 0.15, 0.10, 0.05],
    )
    lead_sources = rng.choice(LEAD_SOURCES, size=n)

    # ── Behavioral signals ───────────────────────────────────────────────
    email_opens = rng.poisson(lam=5, size=n)
    email_clicks = np.minimum(
        rng.poisson(lam=1.5, size=n), email_opens
    )
    page_visits_total = rng.poisson(lam=8, size=n)
    pricing_page_visits = rng.poisson(lam=0.8, size=n)
    demo_page_visits = rng.poisson(lam=0.5, size=n)
    docs_page_visits = rng.poisson(lam=1.2, size=n)
    blog_page_visits = rng.poisson(lam=2.0, size=n)
    content_downloads = rng.poisson(lam=1.0, size=n)
    webinar_attended = rng.binomial(1, 0.15, size=n)
    form_submissions = rng.poisson(lam=0.6, size=n)

    # ── Temporal ─────────────────────────────────────────────────────────
    days_since_first_touch = rng.integers(1, 365, size=n)
    days_since_last_engagement = rng.integers(0, 90, size=n)
    # Ensure last engagement <= first touch
    days_since_last_engagement = np.minimum(
        days_since_last_engagement, days_since_first_touch
    )

    # ── Build a latent "propensity" score to drive realistic conversion ──
    # Higher propensity = more likely to convert
    propensity = np.zeros(n, dtype=float)

    # Seniority effect: decision-makers convert more
    seniority_weight = {
        "C-Suite": 1.2, "VP": 1.0, "Director": 0.7,
        "Manager": 0.3, "Individual Contributor": -0.3,
    }
    propensity += np.array([seniority_weight[s] for s in seniority])

    # Company size effect: mid-market is the sweet spot
    size_weight = {
        "1-10": -0.8, "11-50": -0.2, "51-200": 0.5,
        "201-500": 0.8, "501-1000": 0.6, "1001-5000": 0.3, "5000+": 0.0,
    }
    propensity += np.array([size_weight[s] for s in company_sizes])

    # Industry effect
    industry_weight = {
        "SaaS/Technology": 0.8, "Financial Services": 0.5,
        "Healthcare": 0.2, "E-commerce/Retail": 0.3,
        "Manufacturing": -0.1, "Education": -0.3,
        "Media/Entertainment": 0.1, "Professional Services": 0.4,
        "Telecommunications": 0.2, "Government/Public Sector": -0.5,
    }
    propensity += np.array([industry_weight[i] for i in industries])

    # Behavioral signals boost propensity
    propensity += 0.10 * email_opens
    propensity += 0.15 * email_clicks
    propensity += 0.05 * page_visits_total
    propensity += 0.40 * pricing_page_visits  # High-intent signal
    propensity += 0.35 * demo_page_visits      # High-intent signal
    propensity += 0.10 * docs_page_visits
    propensity += 0.02 * blog_page_visits       # Low intent
    propensity += 0.20 * content_downloads
    propensity += 0.50 * webinar_attended
    propensity += 0.25 * form_submissions

    # Recency effect: recent engagement boosts conversion
    propensity -= 0.02 * days_since_last_engagement

    # Lead source effect
    source_weight = {
        "Organic Search": 0.3, "Paid Search": 0.2,
        "Social Media": -0.1, "Content Syndication": 0.1,
        "Webinar": 0.5, "Referral": 0.7,
        "Trade Show": 0.3, "Direct Traffic": 0.2,
        "Email Campaign": 0.1, "Partner": 0.6,
    }
    propensity += np.array([source_weight[s] for s in lead_sources])

    # Add noise so the model has something to learn
    propensity += rng.normal(0, 1.0, size=n)

    # Convert propensity to probability via sigmoid, then sample outcome
    # Adjust intercept so overall conversion rate is ~8%
    intercept = -np.percentile(propensity, 100 * (1 - TARGET_CONVERSION_RATE))
    prob = 1 / (1 + np.exp(-(propensity + intercept)))
    converted = rng.binomial(1, prob)

    # ── Assemble DataFrame ───────────────────────────────────────────────
    df = pd.DataFrame({
        "lead_id": [f"LEAD-{i:05d}" for i in range(n)],
        "industry": industries,
        "company_size": company_sizes,
        "job_title": job_titles,
        "seniority": seniority,
        "region": regions,
        "lead_source": lead_sources,
        "email_opens": email_opens,
        "email_clicks": email_clicks,
        "page_visits_total": page_visits_total,
        "pricing_page_visits": pricing_page_visits,
        "demo_page_visits": demo_page_visits,
        "docs_page_visits": docs_page_visits,
        "blog_page_visits": blog_page_visits,
        "content_downloads": content_downloads,
        "webinar_attended": webinar_attended,
        "form_submissions": form_submissions,
        "days_since_first_touch": days_since_first_touch,
        "days_since_last_engagement": days_since_last_engagement,
        "converted": converted,
    })

    return df


def save_leads(df: pd.DataFrame, output_dir: str = "data") -> Path:
    """Save generated leads to CSV."""
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    filepath = out_path / "raw_leads.csv"
    df.to_csv(filepath, index=False)
    print(f"  -> Saved {len(df):,} leads to {filepath}")
    print(f"     Conversion rate: {df['converted'].mean():.1%}")
    return filepath


if __name__ == "__main__":
    leads = generate_leads()
    save_leads(leads)
