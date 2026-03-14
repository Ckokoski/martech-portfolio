# ContentPulse: Marketing Content Audit Engine

**Python-based web scraper + analytics dashboard for auditing marketing content performance, SEO health, and content freshness at scale.**

---

## Problem Statement

Marketing teams managing hundreds or thousands of content assets — blog posts, landing pages, resource centers — have no easy way to assess which content is performing, which is outdated, and where SEO gaps exist. Manual audits are time-consuming and incomplete, leading to wasted budget on underperforming content and missed optimization opportunities.

## Solution

ContentPulse is an automated content audit tool that crawls a marketing website, extracts key performance and SEO indicators, and presents the results in an interactive HTML dashboard. It enables marketing operations teams to make data-driven decisions about content refresh, consolidation, and retirement at scale.

**Key capabilities:**

- Automated crawling of all published content pages
- SEO health scoring (meta tags, heading structure, keyword density, alt text coverage)
- Content freshness analysis (last modified dates, publish dates, staleness indicators)
- Word count and readability scoring for content quality assessment
- Interactive HTML dashboard with filtering, sorting, and export
- Exportable CSV reports for stakeholder review

## Technologies Used

| Technology | Marketing Relevance |
|---|---|
| Python 3.x | Core scripting language used across MarTech for automation and data processing |
| BeautifulSoup | Web scraping — same techniques used for competitive analysis and content monitoring |
| requests | HTTP library for crawling — foundational for any API or web integration work |
| pandas | Data analysis — the standard for marketing data manipulation and reporting |
| HTML/CSS/JavaScript | Dashboard frontend — skills directly applicable to email template development and landing pages |

## Screenshots / Demo

> *Screenshots to be added after project deployment*

**Dashboard Preview:**
- Content inventory table with sortable columns
- SEO health score distribution chart
- Content freshness timeline
- Top issues flagged for immediate action

## Key Metrics & Results (Simulated)

In a test run against a sample marketing blog (200 pages):

- **Identified 47 pages** with missing meta descriptions (23% of total content)
- **Flagged 31 pages** not updated in 12+ months for content refresh
- **Found 18 pages** with duplicate H1 tags hurting SEO performance
- **Reduced audit time** from an estimated 40 hours (manual) to under 10 minutes

## How This Applies to Real Marketing Operations

Content auditing is a core Marketing Operations function. In practice, this tool mirrors what MarOps teams do when:

- **Planning content calendars** — understanding what exists before planning what's next
- **Supporting SEO teams** — providing technical SEO data at scale without manual page-by-page review
- **Reporting to leadership** — quantifying content health with clear metrics and dashboards
- **Managing content migrations** — auditing before moving to a new CMS (Sitecore, WordPress, HubSpot)

This project demonstrates proficiency in Python automation, data analysis, and building stakeholder-facing reporting tools — all essential Marketing Operations skills.

---

*All data shown is from synthetic/sample sources. No real company or customer data is used.*
