# SQL for Marketers: Query Library

**30+ documented SQL queries for SFMC and marketing databases — subscriber segmentation, engagement scoring, campaign performance reporting, and data hygiene.**

---

## Table of Contents

### Subscriber Segmentation (8 queries)

| # | Query | Description |
|---|-------|-------------|
| 1 | [active-subscribers.sql](queries/segmentation/active-subscribers.sql) | Subscribers who opened or clicked in the last 90 days, with engagement tier classification |
| 2 | [dormant-subscribers.sql](queries/segmentation/dormant-subscribers.sql) | Subscribers with no engagement in 180+ days, flagged for re-engagement or sunset |
| 3 | [new-subscribers-30d.sql](queries/segmentation/new-subscribers-30d.sql) | Contacts who joined in the last 30 days with signup source and early engagement signals |
| 4 | [high-value-customers.sql](queries/segmentation/high-value-customers.sql) | Top 10% of customers by 12-month purchase value for VIP treatment |
| 5 | [geographic-segment.sql](queries/segmentation/geographic-segment.sql) | Subscribers grouped by region/state with timezone mapping and data quality flags |
| 6 | [preference-center-segments.sql](queries/segmentation/preference-center-segments.sql) | Segments based on subscriber-stated content, frequency, and channel preferences |
| 7 | [lifecycle-stage.sql](queries/segmentation/lifecycle-stage.sql) | Assign lifecycle stages (New, Active, At-Risk, Lapsed) with sub-stage granularity |
| 8 | [lookalike-audience.sql](queries/segmentation/lookalike-audience.sql) | Find non-customers who share traits with your best buyers for conversion targeting |

### Engagement Scoring (6 queries)

| # | Query | Description |
|---|-------|-------------|
| 1 | [email-engagement-score.sql](queries/engagement-scoring/email-engagement-score.sql) | Weighted score from opens, clicks, and conversions normalized to a 0-100 scale |
| 2 | [recency-frequency-monetary.sql](queries/engagement-scoring/recency-frequency-monetary.sql) | Classic RFM scoring model with 1-5 scores per dimension and segment labels |
| 3 | [engagement-trend.sql](queries/engagement-scoring/engagement-trend.sql) | 30/60/90-day engagement windows per subscriber with trend direction detection |
| 4 | [channel-preference-score.sql](queries/engagement-scoring/channel-preference-score.sql) | Determine preferred channel (email, SMS, push) based on actual engagement data |
| 5 | [content-affinity-score.sql](queries/engagement-scoring/content-affinity-score.sql) | Rank which content topics drive the most engagement per subscriber |
| 6 | [engagement-decay-detection.sql](queries/engagement-scoring/engagement-decay-detection.sql) | Identify subscribers whose engagement is actively declining before they lapse |

### Campaign Performance Reporting (8 queries)

| # | Query | Description |
|---|-------|-------------|
| 1 | [campaign-performance-summary.sql](queries/campaign-reporting/campaign-performance-summary.sql) | Full KPI summary per campaign: sent, delivered, opened, clicked, converted, revenue |
| 2 | [ab-test-results.sql](queries/campaign-reporting/ab-test-results.sql) | Compare A/B test variants with engagement metrics, lift, and confidence indicators |
| 3 | [send-time-analysis.sql](queries/campaign-reporting/send-time-analysis.sql) | Performance by send hour and day of week to find optimal send windows |
| 4 | [subject-line-performance.sql](queries/campaign-reporting/subject-line-performance.sql) | Open/click rates by subject line characteristics (length, urgency, personalization) |
| 5 | [funnel-progression.sql](queries/campaign-reporting/funnel-progression.sql) | Full conversion funnel from send through delivery, open, click, and purchase |
| 6 | [campaign-comparison.sql](queries/campaign-reporting/campaign-comparison.sql) | Side-by-side comparison of campaigns on all engagement and revenue metrics |
| 7 | [monthly-email-dashboard.sql](queries/campaign-reporting/monthly-email-dashboard.sql) | Monthly aggregate metrics with month-over-month change calculations |
| 8 | [revenue-attribution.sql](queries/campaign-reporting/revenue-attribution.sql) | Revenue attributed to email campaigns with 1-day, 7-day, and 30-day windows |

### Data Hygiene (8 queries)

| # | Query | Description |
|---|-------|-------------|
| 1 | [duplicate-detection.sql](queries/data-hygiene/duplicate-detection.sql) | Find duplicate subscriber records by normalized email address |
| 2 | [invalid-email-detection.sql](queries/data-hygiene/invalid-email-detection.sql) | Identify malformed emails, domain typos, disposable addresses, and test accounts |
| 3 | [bounce-management.sql](queries/data-hygiene/bounce-management.sql) | Hard bounce identification, chronic soft bounce flagging, and domain-level analysis |
| 4 | [unsubscribe-audit.sql](queries/data-hygiene/unsubscribe-audit.sql) | Verify unsubscribe processing and catch compliance violations |
| 5 | [stale-data-detection.sql](queries/data-hygiene/stale-data-detection.sql) | Records not updated in 12+ months with field-level staleness inventory |
| 6 | [data-completeness-audit.sql](queries/data-hygiene/data-completeness-audit.sql) | Profile completeness scoring across 10 key fields with tier classification |
| 7 | [consent-compliance-check.sql](queries/data-hygiene/consent-compliance-check.sql) | GDPR/CAN-SPAM consent verification with compliance status and recommended actions |
| 8 | [list-growth-decay-report.sql](queries/data-hygiene/list-growth-decay-report.sql) | Net list growth tracking over time (gained vs. unsubscribes and bounces by month) |

---

## Problem Statement

Marketing Operations professionals working in Salesforce Marketing Cloud (SFMC) and other marketing platforms need SQL constantly — for building data extensions, creating subscriber segments, generating performance reports, and maintaining data quality. But SQL resources are overwhelmingly geared toward software engineers, not marketers. There's a gap between "learn SQL basics" and "write the query I actually need for my SFMC job."

## Solution

SQL for Marketers is a curated, documented library of 30+ SQL queries that address the most common tasks in marketing databases and SFMC. Each query includes a plain-language use case, the SQL code, an explanation of the logic, sample output, and notes on how to adapt it for different marketing platforms.

## Query File Format

Every `.sql` file in this library follows a consistent structure:

```
/*  Header Block
    - Query Name and Category
    - Purpose: what the query does and why it matters
    - Use Case: specific marketing scenarios
    - Platform: SFMC Query Activity compatibility notes
    - Tables Used: which data views and data extensions
    - Notes: SFMC-specific dialect considerations
*/

SELECT ...   -- The working SQL query

/*  Sample Output
    - Expected columns and example rows
    - Helps you verify the query is working correctly
*/
```

## Technologies Used

| Technology | Marketing Relevance |
|---|---|
| SQL (ANSI standard) | The query language used in SFMC Query Activities, marketing data warehouses, and BI tools |
| SFMC SQL dialect | Notes on SFMC-specific syntax (no CTEs, TOP instead of LIMIT, date function differences) |
| Markdown | Documentation format — demonstrates technical writing skills essential for MarOps |

## Screenshots

![High Value Customers SQL](screenshots/SQL%20for%20Marketers%20-%20High%20Value%20Customers%20SQL.png)

## SFMC Tables Referenced

| Table / Data View | Type | Description |
|---|---|---|
| `_Subscribers` | System Data View | All subscriber records with status, email, join date |
| `_Sent` | System Data View | Email send events (one row per subscriber per send) |
| `_Open` | System Data View | Email open tracking events |
| `_Click` | System Data View | Email click tracking events |
| `_Bounce` | System Data View | Bounce events with category (hard/soft/block) |
| `_Unsubscribe` | System Data View | Unsubscribe events |
| `_Job` | System Data View | Campaign/job metadata (name, subject, send date) |
| `SubscriberMaster` | Custom Data Extension | Extended profile fields (address, phone, company) |
| `TransactionHistory` | Custom Data Extension | Purchase/order data for revenue attribution |
| `PreferenceCenter` | Custom Data Extension | Subscriber-stated preferences (content, frequency) |
| `ConsentLog` | Custom Data Extension | Consent event tracking for GDPR/CAN-SPAM |
| `CampaignMetadata` | Custom Data Extension | Content category tags per campaign |
| `ABTestConfig` | Custom Data Extension | A/B test variant mapping |
| `SMSMessageTracking` | Custom Data Extension | SMS engagement data |
| `PushNotificationTracking` | Custom Data Extension | Push notification engagement data |

## Key Metrics & Results

- **30 queries** organized across 4 marketing function categories
- **Each query documented** with use case, explanation, sample output, and platform notes
- **SFMC-specific notes** for every query — addressing the platform's SQL dialect limitations
- **Copy-paste ready** — queries designed to be adapted and used immediately in real marketing databases

## How This Applies to Real Marketing Operations

SQL is the technical backbone of Marketing Operations. This project demonstrates:

- **SFMC Query Activity expertise** — the queries directly map to SFMC's SQL-based segmentation and reporting capabilities
- **Data-driven segmentation** — building audience segments from behavioral data, not just demographics
- **Reporting and analytics** — creating the campaign performance reports that marketing leadership relies on
- **Data quality management** — the hygiene queries reflect the real-world challenge of maintaining clean subscriber data
- **Technical documentation** — each query is documented in a way that a non-SQL marketer could understand and adapt

This project is designed to be immediately useful to hiring managers — they can see the exact SQL skills that would be applied on the job.

---

*All queries use fictional table names and sample data. No real subscriber or company data is included.*
