# Attribution Engine

**Multi-touch marketing attribution modeling tool that calculates channel ROI across first-touch, last-touch, linear, and data-driven models.**

---

## Problem Statement

Marketing teams invest across multiple channels — paid search, social, email, organic, events — but struggle to answer the fundamental question: *which channels actually drive conversions?* Single-touch attribution (first or last click) oversimplifies the buyer journey, while multi-touch models are often locked behind expensive analytics platforms. Without accurate attribution, budget allocation is based on gut feel rather than data.

## Solution

Attribution Engine is a Python-based attribution modeling tool that ingests multi-channel touchpoint data, applies multiple attribution models side-by-side, and outputs channel-level ROI analysis. It lets marketing leaders compare how different models value each channel — revealing which investments truly drive pipeline.

**Key capabilities:**

- **First-touch attribution** — credits the channel that initiated the customer journey
- **Last-touch attribution** — credits the channel immediately preceding conversion
- **Linear attribution** — distributes credit equally across all touchpoints in the journey
- **Time-decay attribution** — weights touchpoints closer to conversion more heavily
- **Data-driven attribution (Markov chains)** — uses transition probability modeling to calculate each channel's incremental contribution
- **Channel ROI comparison** — side-by-side view of how each model values each channel, with spend-weighted ROI
- **Path analysis** — most common conversion paths, average touchpoints to conversion, and channel sequence patterns
- **Interactive reporting** — Plotly Sankey diagrams, attribution comparison bar charts, and journey path visualizations

## Technologies Used

| Technology | Marketing Relevance |
|---|---|
| Python 3.x | Standard for marketing analytics and data modeling |
| pandas | Touchpoint data manipulation — sessionizing, sequencing, and aggregating customer journeys |
| numpy | Matrix operations for Markov chain transition probability calculations |
| Plotly | Sankey diagrams for journey visualization, interactive attribution comparison charts |
| networkx | Graph-based modeling for channel transition analysis in data-driven attribution |

## Screenshots

![Main Dashboard](screenshots/Attribution%20Dashboard%20Screenshot%20-%20Main%20Dashboard.png)

![Channel ROI Analysis](screenshots/Attribution%20Dashboard%20Screenshot%20-%20Channel%20ROI%20Analysis.png)

## Key Metrics & Results (Simulated)

Analysis of a synthetic dataset representing 6 months of B2B multi-channel marketing (5K conversions, 35K touchpoints):

- **Attribution gap revealed** — paid search received 42% of credit under last-touch but only 18% under data-driven, suggesting over-investment based on last-click reporting
- **Email undervalued** — email nurture received 8% credit under last-touch but 22% under data-driven, revealing its critical mid-funnel role
- **Optimal path length** — conversions with 4-6 touchpoints had the highest conversion rate (3.2%) vs. 1-touch (0.8%)
- **Budget reallocation opportunity** — data-driven model suggested shifting 15% of paid search budget to content marketing based on incremental contribution analysis

## How This Applies to Real Marketing Operations

This project addresses one of the most challenging problems in marketing operations:

- **Budget justification** — provides data-backed evidence for marketing spend allocation across channels
- **GA4 + SFMC alignment** — the attribution logic mirrors how GA4 data-driven attribution works, applicable to combining GA4 with SFMC campaign tracking
- **Executive reporting** — the model comparison view is designed for CMO-level conversations about marketing ROI
- **Campaign planning** — path analysis informs which channel combinations to invest in for upcoming campaigns
- **Marketing-finance alignment** — quantifies marketing's contribution to pipeline in language finance teams understand

This is the "marketing analytics" showcase — demonstrating the ability to move beyond vanity metrics to true marketing effectiveness measurement.

---

*All data is synthetic. No real customer, revenue, or campaign spend data is used.*
