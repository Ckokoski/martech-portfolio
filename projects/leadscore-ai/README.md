# LeadScore AI

**ML-powered lead scoring model that analyzes behavioral and demographic signals to prioritize leads for sales handoff.**

---

## Problem Statement

Marketing teams generate leads across dozens of channels — webinars, gated content, paid ads, organic search — but struggle to determine which leads are genuinely sales-ready versus merely curious. Without a data-driven scoring model, sales teams waste cycles on low-intent leads while high-value prospects go cold in the funnel.

## Solution

LeadScore AI is a Python-based predictive lead scoring system that ingests CRM and marketing automation data, engineers features from behavioral and demographic signals, and trains a classification model to predict conversion likelihood. It outputs a prioritized lead list with explainable scores — giving sales teams confidence in which leads to pursue first.

**Key capabilities:**

- **Behavioral signal analysis** — tracks engagement patterns (email opens, page visits, content downloads, webinar attendance) and weights recency, frequency, and depth of interaction
- **Demographic scoring** — evaluates firmographic fit (company size, industry, job title seniority) against ideal customer profile (ICP) criteria
- **ML classification model** — gradient boosted classifier trained on historical conversion data to predict lead-to-opportunity probability
- **Explainable scores** — SHAP-based feature importance so marketing and sales understand *why* a lead scored high or low
- **Threshold recommendations** — data-driven MQL/SQL threshold suggestions based on score distributions and historical conversion rates
- **Segment analysis** — identifies which lead sources and campaigns produce the highest-scoring leads
- **Scoring dashboard** — interactive Plotly visualizations of score distributions, feature importance, and lead funnel progression

## Technologies Used

| Technology | Marketing Relevance |
|---|---|
| Python 3.x | Standard for marketing data science and automation |
| pandas | Data wrangling — merging CRM exports, marketing automation logs, and web analytics |
| scikit-learn | ML model training — the same library used for production-grade scoring models |
| XGBoost | Gradient boosting — the go-to algorithm for tabular classification tasks like lead scoring |
| SHAP | Model explainability — critical for stakeholder buy-in and sales adoption |
| Plotly | Interactive dashboards — score distributions, ROC curves, feature importance charts |

## Screenshots

![LeadScore AI Results](screenshots/LeadScore%20AI%20Home%20-%20Results.png)

![Lead Source Quality Averages](screenshots/LeadScore%20AI%20-%20Lead%20Source%20Quality%20Averages.png)

## Key Metrics & Results (Simulated)

Analysis of a synthetic dataset representing 12 months of B2B SaaS lead data (10K leads, 800 conversions):

- **Model AUC: 0.87** — strong discriminative power between converters and non-converters
- **Top predictive features** — pricing page visits (3x), demo request form starts (2.5x), email engagement recency (2x), job title seniority (1.8x)
- **Efficiency gain** — the top 20% of scored leads contained 68% of actual conversions, enabling sales to focus effort where it matters
- **Threshold recommendation** — suggested MQL cutoff at score 0.45 (captures 82% of conversions) and SQL cutoff at 0.72 (65% conversion rate in this tier)

## How This Applies to Real Marketing Operations

This project directly mirrors production lead scoring implementations:

- **SFMC + CRM integration** — the same data pipeline pattern applies to scoring leads from SFMC engagement data joined with Salesforce CRM records
- **Sales-marketing alignment** — explainable scores bridge the gap between marketing's lead generation and sales' pipeline expectations
- **Model governance** — includes model performance monitoring patterns applicable to any scoring model in production
- **Campaign ROI** — segment analysis reveals which marketing investments produce the highest-quality leads, informing budget allocation
- **Lifecycle automation** — scores can trigger SFMC journey entries, moving leads into nurture or sales handoff workflows automatically

This is the "predictive analytics" showcase — demonstrating that marketing operations can move from rules-based lead scoring to ML-powered prioritization.

---

*All data is synthetic. No real lead, company, or conversion data is used.*
