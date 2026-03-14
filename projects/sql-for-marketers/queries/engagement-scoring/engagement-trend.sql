/*
============================================================
  Query Name:   Engagement Trend (30/60/90 Day Windows)
  Category:     Engagement Scoring
  Purpose:      Calculate engagement metrics across three time
                windows (30, 60, 90 days) per subscriber to
                reveal whether engagement is trending up, down,
                or stable. This is more actionable than a single
                point-in-time score.
  Use Case:     - Identify subscribers whose engagement is
                  accelerating (good candidates for upsell)
                - Catch declining engagement early before
                  subscribers lapse
                - Measure the impact of program changes on
                  engagement over time
  Platform:     Salesforce Marketing Cloud (SFMC) Query Activity
  Tables Used:  _Subscribers, _Open, _Click
  Notes:        - Each window is cumulative (90d includes 60d
                  and 30d) to show the trend shape.
                - The TrendDirection column compares the most
                  recent 30d to the prior 31-60d period.
============================================================
*/

SELECT
    s.SubscriberKey,
    s.EmailAddress,
    s.FirstName,
    s.LastName,

    /* --- 30-Day Window --- */
    COUNT(DISTINCT CASE
        WHEN o.EventDate >= DATEADD(DAY, -30, GETDATE())
        THEN o.JobID END)                           AS Opens_30d,
    COUNT(DISTINCT CASE
        WHEN c.EventDate >= DATEADD(DAY, -30, GETDATE())
        THEN c.JobID END)                           AS Clicks_30d,

    /* --- 31-60 Day Window (prior month for comparison) --- */
    COUNT(DISTINCT CASE
        WHEN o.EventDate >= DATEADD(DAY, -60, GETDATE())
         AND o.EventDate <  DATEADD(DAY, -30, GETDATE())
        THEN o.JobID END)                           AS Opens_31_60d,
    COUNT(DISTINCT CASE
        WHEN c.EventDate >= DATEADD(DAY, -60, GETDATE())
         AND c.EventDate <  DATEADD(DAY, -30, GETDATE())
        THEN c.JobID END)                           AS Clicks_31_60d,

    /* --- 61-90 Day Window --- */
    COUNT(DISTINCT CASE
        WHEN o.EventDate >= DATEADD(DAY, -90, GETDATE())
         AND o.EventDate <  DATEADD(DAY, -60, GETDATE())
        THEN o.JobID END)                           AS Opens_61_90d,
    COUNT(DISTINCT CASE
        WHEN c.EventDate >= DATEADD(DAY, -90, GETDATE())
         AND c.EventDate <  DATEADD(DAY, -60, GETDATE())
        THEN c.JobID END)                           AS Clicks_61_90d,

    /* --- Total 90-Day Engagement Score --- */
    (COUNT(DISTINCT CASE
        WHEN o.EventDate >= DATEADD(DAY, -90, GETDATE())
        THEN o.JobID END) * 1)
  + (COUNT(DISTINCT CASE
        WHEN c.EventDate >= DATEADD(DAY, -90, GETDATE())
        THEN c.JobID END) * 3)                      AS EngagementScore_90d,

    /* --- Trend Direction ---
       Compare most recent 30d to previous 31-60d period.
       If recent activity is higher, trend is up. */
    CASE
        WHEN (COUNT(DISTINCT CASE WHEN o.EventDate >= DATEADD(DAY, -30, GETDATE()) THEN o.JobID END)
            + COUNT(DISTINCT CASE WHEN c.EventDate >= DATEADD(DAY, -30, GETDATE()) THEN c.JobID END))
           > (COUNT(DISTINCT CASE WHEN o.EventDate >= DATEADD(DAY, -60, GETDATE())
                                   AND o.EventDate <  DATEADD(DAY, -30, GETDATE()) THEN o.JobID END)
            + COUNT(DISTINCT CASE WHEN c.EventDate >= DATEADD(DAY, -60, GETDATE())
                                   AND c.EventDate <  DATEADD(DAY, -30, GETDATE()) THEN c.JobID END))
            THEN 'Trending Up'
        WHEN (COUNT(DISTINCT CASE WHEN o.EventDate >= DATEADD(DAY, -30, GETDATE()) THEN o.JobID END)
            + COUNT(DISTINCT CASE WHEN c.EventDate >= DATEADD(DAY, -30, GETDATE()) THEN c.JobID END))
           = (COUNT(DISTINCT CASE WHEN o.EventDate >= DATEADD(DAY, -60, GETDATE())
                                   AND o.EventDate <  DATEADD(DAY, -30, GETDATE()) THEN o.JobID END)
            + COUNT(DISTINCT CASE WHEN c.EventDate >= DATEADD(DAY, -60, GETDATE())
                                   AND c.EventDate <  DATEADD(DAY, -30, GETDATE()) THEN c.JobID END))
            THEN 'Stable'
        ELSE 'Trending Down'
    END                                             AS TrendDirection

FROM
    _Subscribers AS s
    LEFT JOIN _Open AS o
        ON s.SubscriberKey = o.SubscriberKey
        AND o.EventDate >= DATEADD(DAY, -90, GETDATE())
        AND o.IsUnique = 1
    LEFT JOIN _Click AS c
        ON s.SubscriberKey = c.SubscriberKey
        AND c.EventDate >= DATEADD(DAY, -90, GETDATE())
        AND c.IsUnique = 1
WHERE
    s.Status = 'Active'
GROUP BY
    s.SubscriberKey,
    s.EmailAddress,
    s.FirstName,
    s.LastName
HAVING
    COUNT(DISTINCT o.JobID) > 0
    OR COUNT(DISTINCT c.JobID) > 0
ORDER BY
    EngagementScore_90d DESC

/*
============================================================
  EXPECTED SAMPLE OUTPUT
============================================================
| SubscriberKey | EmailAddress         | FirstName | LastName | Opens_30d | Clicks_30d | Opens_31_60d | Clicks_31_60d | Opens_61_90d | Clicks_61_90d | EngagementScore_90d | TrendDirection |
|---------------|----------------------|-----------|----------|-----------|------------|--------------|---------------|--------------|---------------|---------------------|----------------|
| SK-10042      | accel@example.com    | Jane      | Doe      | 6         | 4          | 3            | 1             | 2            | 1             | 32                  | Trending Up    |
| SK-20318      | steady@example.com   | Mark      | Lee      | 3         | 2          | 3            | 2             | 4            | 2             | 28                  | Stable         |
| SK-30491      | fading@example.com   | Amy       | Torres   | 1         | 0          | 4            | 2             | 5            | 3             | 22                  | Trending Down  |
| SK-40822      | revival@example.com  | Brian     | Shah     | 4         | 1          | 0            | 0             | 3            | 1             | 13                  | Trending Up    |
============================================================
*/
