/*
============================================================
  Query Name:   List Growth and Decay Report
  Category:     Data Hygiene
  Purpose:      Track net list growth over time by measuring
                new subscribers gained vs. subscribers lost
                (unsubscribes, bounces, complaints) each month.
                A healthy email program should show consistent
                net positive growth.
  Use Case:     - Monthly KPI reporting on list health
                - Identify periods of accelerated list decay
                - Justify investment in acquisition programs
                - Detect problems (e.g., a spike in unsubs after
                  a specific campaign or policy change)
  Platform:     Salesforce Marketing Cloud (SFMC) Query Activity
  Tables Used:  _Subscribers, _Bounce, _Unsubscribe
  Notes:        - This query uses date-based grouping to count
                  events per month.
                - "Lost" includes unsubscribes and hard bounces
                  (BounceCategory = 1).
                - Net growth = Gained - Lost.
                - For a full picture, also track spam complaints
                  if that data is available in your system.
============================================================
*/

SELECT
    growth.ReportMonth,

    /* --- Subscribers Gained --- */
    ISNULL(growth.NewSubscribers, 0)                     AS Gained,

    /* --- Subscribers Lost --- */
    ISNULL(loss.Unsubscribes, 0)                         AS Unsubscribes,
    ISNULL(loss.HardBounces, 0)                          AS HardBounces,
    ISNULL(loss.Unsubscribes, 0)
      + ISNULL(loss.HardBounces, 0)                      AS TotalLost,

    /* --- Net Growth --- */
    ISNULL(growth.NewSubscribers, 0)
      - (ISNULL(loss.Unsubscribes, 0)
       + ISNULL(loss.HardBounces, 0))                    AS NetGrowth,

    /* --- Growth Rate (requires running total of list size) --- */
    CASE
        WHEN ISNULL(growth.NewSubscribers, 0) = 0
         AND (ISNULL(loss.Unsubscribes, 0) + ISNULL(loss.HardBounces, 0)) = 0
            THEN 0
        WHEN ISNULL(growth.NewSubscribers, 0) = 0
            THEN -100.00
        ELSE ROUND(
            (ISNULL(growth.NewSubscribers, 0)
           - (ISNULL(loss.Unsubscribes, 0) + ISNULL(loss.HardBounces, 0)))
           * 100.0 / NULLIF(growth.NewSubscribers, 0), 2)
    END                                                  AS NetGrowthEfficiency,

    /* --- Health Indicator --- */
    CASE
        WHEN ISNULL(growth.NewSubscribers, 0)
           > (ISNULL(loss.Unsubscribes, 0)
            + ISNULL(loss.HardBounces, 0)) * 2
            THEN 'Strong Growth'
        WHEN ISNULL(growth.NewSubscribers, 0)
           > (ISNULL(loss.Unsubscribes, 0)
            + ISNULL(loss.HardBounces, 0))
            THEN 'Positive Growth'
        WHEN ISNULL(growth.NewSubscribers, 0)
           = (ISNULL(loss.Unsubscribes, 0)
            + ISNULL(loss.HardBounces, 0))
            THEN 'Flat (Stagnant)'
        ELSE 'Declining (Net Loss)'
    END                                                  AS ListHealthIndicator

FROM (
    /* --- Monthly New Subscribers --- */
    SELECT
        CAST(YEAR(s.DateJoined) AS VARCHAR(4)) + '-'
          + RIGHT('0' + CAST(MONTH(s.DateJoined) AS VARCHAR(2)), 2)
                                                         AS ReportMonth,
        COUNT(DISTINCT s.SubscriberKey)                  AS NewSubscribers
    FROM
        _Subscribers AS s
    WHERE
        s.DateJoined >= DATEADD(MONTH, -12, GETDATE())
    GROUP BY
        YEAR(s.DateJoined),
        MONTH(s.DateJoined)
) AS growth
LEFT JOIN (
    /* --- Monthly Losses (Unsubs + Hard Bounces) --- */
    SELECT
        ReportMonth,
        SUM(Unsubs)         AS Unsubscribes,
        SUM(Bounces)        AS HardBounces
    FROM (
        SELECT
            CAST(YEAR(u.EventDate) AS VARCHAR(4)) + '-'
              + RIGHT('0' + CAST(MONTH(u.EventDate) AS VARCHAR(2)), 2)
                                                         AS ReportMonth,
            COUNT(DISTINCT u.SubscriberKey)              AS Unsubs,
            0                                            AS Bounces
        FROM _Unsubscribe AS u
        WHERE u.EventDate >= DATEADD(MONTH, -12, GETDATE())
        GROUP BY YEAR(u.EventDate), MONTH(u.EventDate)

        UNION ALL

        SELECT
            CAST(YEAR(b.EventDate) AS VARCHAR(4)) + '-'
              + RIGHT('0' + CAST(MONTH(b.EventDate) AS VARCHAR(2)), 2)
                                                         AS ReportMonth,
            0                                            AS Unsubs,
            COUNT(DISTINCT b.SubscriberKey)              AS Bounces
        FROM _Bounce AS b
        WHERE b.BounceCategory = 1  /* Hard bounces only */
          AND b.EventDate >= DATEADD(MONTH, -12, GETDATE())
        GROUP BY YEAR(b.EventDate), MONTH(b.EventDate)
    ) AS combined
    GROUP BY ReportMonth
) AS loss
    ON growth.ReportMonth = loss.ReportMonth
ORDER BY
    growth.ReportMonth DESC

/*
============================================================
  EXPECTED SAMPLE OUTPUT
============================================================
| ReportMonth | Gained | Unsubscribes | HardBounces | TotalLost | NetGrowth | NetGrowthEfficiency | ListHealthIndicator  |
|-------------|--------|--------------|-------------|-----------|-----------|---------------------|----------------------|
| 2026-03     | 2800   | 180          | 95          | 275       | 2525      | 90.18               | Strong Growth        |
| 2026-02     | 2400   | 210          | 110         | 320       | 2080      | 86.67               | Strong Growth        |
| 2026-01     | 1900   | 150          | 85          | 235       | 1665      | 87.63               | Strong Growth        |
| 2025-12     | 1200   | 340          | 120         | 460       | 740       | 61.67               | Positive Growth      |
| 2025-11     | 800    | 410          | 150         | 560       | -760      | -95.00              | Declining (Net Loss) |
| 2025-10     | 2100   | 190          | 90          | 280       | 1820      | 86.67               | Strong Growth        |
============================================================
*/
