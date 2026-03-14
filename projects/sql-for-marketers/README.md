# SQL for Marketers: Query Library

**30+ documented SQL queries for SFMC and marketing databases — subscriber segmentation, engagement scoring, campaign performance reporting, and data hygiene.**

---

## Problem Statement

Marketing Operations professionals working in Salesforce Marketing Cloud (SFMC) and other marketing platforms need SQL constantly — for building data extensions, creating subscriber segments, generating performance reports, and maintaining data quality. But SQL resources are overwhelmingly geared toward software engineers, not marketers. There's a gap between "learn SQL basics" and "write the query I actually need for my SFMC job."

## Solution

SQL for Marketers is a curated, documented library of 30+ SQL queries that address the most common tasks in marketing databases and SFMC. Each query includes a plain-language use case, the SQL code, an explanation of the logic, sample output, and notes on how to adapt it for different marketing platforms.

**Query categories:**

### Subscriber Segmentation (8 queries)
- Active subscribers by engagement window (30/60/90 day)
- New subscriber cohort segmentation by signup source
- VIP segment based on purchase frequency and recency
- Geographic segmentation with timezone mapping
- Re-engagement candidates (opened in past but inactive recently)
- Birthday/anniversary targeting window
- Preference center-based segment builder
- Exclusion list compilation (unsubscribes, bounces, complaints)

### Engagement Scoring (6 queries)
- Recency-Frequency-Monetary (RFM) scoring model
- Email engagement score (weighted opens, clicks, conversions)
- Multi-channel engagement composite score
- Engagement decay calculation (activity trending over time)
- Lead scoring query for marketing-qualified lead identification
- Subscriber lifecycle stage assignment

### Campaign Performance Reporting (8 queries)
- Campaign summary with open rate, click rate, bounce rate, and conversion rate
- Campaign comparison (A/B test results with statistical significance flag)
- Month-over-month trend report for email KPIs
- Funnel conversion analysis (send → open → click → convert)
- Revenue attribution by campaign and channel
- Best-performing content/subject line analysis
- Send volume and frequency analysis per subscriber
- Deliverability report (inbox vs. spam placement indicators)

### Data Hygiene (8+ queries)
- Duplicate subscriber detection (email, name, and fuzzy matching)
- Invalid email format identification
- Hard bounce suppression list maintenance
- Subscriber record completeness scoring
- Orphaned records (subscribers with no campaign history)
- Data freshness audit (fields not updated in 6+ months)
- Consent and preference compliance check
- Cross-data-extension integrity validation

## Technologies Used

| Technology | Marketing Relevance |
|---|---|
| SQL (ANSI standard) | The query language used in SFMC Query Activities, marketing data warehouses, and BI tools |
| SFMC SQL dialect | Notes on SFMC-specific syntax (no CTEs, TOP instead of LIMIT, date function differences) |
| Markdown | Documentation format — demonstrates technical writing skills essential for MarOps |

## Sample Query

```sql
-- Active Subscribers: Engaged in the Last 90 Days
-- Use Case: Build a healthy send list by targeting only recently engaged subscribers
-- Platform: SFMC Query Activity or any marketing database

SELECT
    s.SubscriberKey,
    s.EmailAddress,
    s.FirstName,
    MAX(o.EventDate) AS LastOpenDate,
    MAX(c.EventDate) AS LastClickDate,
    COUNT(DISTINCT o.JobID) AS TotalOpens90d,
    COUNT(DISTINCT c.JobID) AS TotalClicks90d
FROM Subscribers s
LEFT JOIN Opens o
    ON s.SubscriberKey = o.SubscriberKey
    AND o.EventDate >= DATEADD(day, -90, GETDATE())
LEFT JOIN Clicks c
    ON s.SubscriberKey = c.SubscriberKey
    AND c.EventDate >= DATEADD(day, -90, GETDATE())
WHERE
    s.Status = 'Active'
GROUP BY
    s.SubscriberKey, s.EmailAddress, s.FirstName
HAVING
    COUNT(DISTINCT o.JobID) > 0
    OR COUNT(DISTINCT c.JobID) > 0
ORDER BY
    TotalClicks90d DESC, TotalOpens90d DESC;
```

**Sample Output:**

| SubscriberKey | EmailAddress | FirstName | LastOpenDate | LastClickDate | TotalOpens90d | TotalClicks90d |
|---|---|---|---|---|---|---|
| SK-001 | jane@example.com | Jane | 2026-03-10 | 2026-03-08 | 12 | 5 |
| SK-002 | mark@example.com | Mark | 2026-03-09 | 2026-03-01 | 8 | 3 |

## Key Metrics & Results

- **30+ queries** organized by marketing function
- **Each query documented** with use case, explanation, sample output, and platform adaptation notes
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
