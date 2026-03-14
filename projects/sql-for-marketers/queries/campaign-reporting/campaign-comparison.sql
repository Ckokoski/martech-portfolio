/*
============================================================
  Query Name:   Campaign Comparison (Side-by-Side)
  Category:     Campaign Reporting
  Purpose:      Compare two or more campaigns side-by-side on
                all key metrics. Useful for evaluating different
                campaign strategies, creative approaches, or
                audience segments against each other.
  Use Case:     - Compare a promotional campaign vs. newsletter
                - Evaluate performance across different audience
                  segments receiving the same content
                - Year-over-year or month-over-month comparisons
                  of recurring campaigns
                - Post-campaign debrief documentation
  Platform:     Salesforce Marketing Cloud (SFMC) Query Activity
  Tables Used:  _Job, _Sent, _Open, _Click, _Bounce,
                _Unsubscribe, TransactionHistory
  Notes:        - Filter by specific JobIDs or EmailName patterns
                  to compare the campaigns you need.
                - Modify the WHERE clause to select the campaigns
                  you want to compare.
============================================================
*/

SELECT
    j.JobID,
    j.EmailName,
    j.EmailSubject,
    j.DeliveredTime                                      AS SendDate,

    /* --- Audience Size --- */
    COUNT(DISTINCT snt.SubscriberKey)                    AS Sent,
    COUNT(DISTINCT snt.SubscriberKey)
      - COUNT(DISTINCT b.SubscriberKey)                  AS Delivered,

    /* --- Engagement Counts --- */
    COUNT(DISTINCT o.SubscriberKey)                      AS UniqueOpens,
    COUNT(DISTINCT c.SubscriberKey)                      AS UniqueClicks,
    COUNT(DISTINCT u.SubscriberKey)                      AS Unsubscribes,
    COUNT(DISTINCT th.SubscriberKey)                     AS Conversions,
    ISNULL(SUM(th.OrderTotal), 0)                        AS Revenue,

    /* --- Rate Metrics --- */
    CASE
        WHEN (COUNT(DISTINCT snt.SubscriberKey)
            - COUNT(DISTINCT b.SubscriberKey)) = 0 THEN 0
        ELSE ROUND(
            COUNT(DISTINCT o.SubscriberKey) * 100.0
            / (COUNT(DISTINCT snt.SubscriberKey)
             - COUNT(DISTINCT b.SubscriberKey)), 2)
    END                                                  AS OpenRate,

    CASE
        WHEN (COUNT(DISTINCT snt.SubscriberKey)
            - COUNT(DISTINCT b.SubscriberKey)) = 0 THEN 0
        ELSE ROUND(
            COUNT(DISTINCT c.SubscriberKey) * 100.0
            / (COUNT(DISTINCT snt.SubscriberKey)
             - COUNT(DISTINCT b.SubscriberKey)), 2)
    END                                                  AS ClickRate,

    CASE
        WHEN COUNT(DISTINCT o.SubscriberKey) = 0 THEN 0
        ELSE ROUND(
            COUNT(DISTINCT c.SubscriberKey) * 100.0
            / COUNT(DISTINCT o.SubscriberKey), 2)
    END                                                  AS CTOR,

    CASE
        WHEN (COUNT(DISTINCT snt.SubscriberKey)
            - COUNT(DISTINCT b.SubscriberKey)) = 0 THEN 0
        ELSE ROUND(
            COUNT(DISTINCT u.SubscriberKey) * 100.0
            / (COUNT(DISTINCT snt.SubscriberKey)
             - COUNT(DISTINCT b.SubscriberKey)), 4)
    END                                                  AS UnsubRate,

    CASE
        WHEN (COUNT(DISTINCT snt.SubscriberKey)
            - COUNT(DISTINCT b.SubscriberKey)) = 0 THEN 0
        ELSE ROUND(
            COUNT(DISTINCT th.SubscriberKey) * 100.0
            / (COUNT(DISTINCT snt.SubscriberKey)
             - COUNT(DISTINCT b.SubscriberKey)), 4)
    END                                                  AS ConversionRate,

    /* --- Efficiency Metrics --- */
    CASE
        WHEN (COUNT(DISTINCT snt.SubscriberKey)
            - COUNT(DISTINCT b.SubscriberKey)) = 0 THEN 0
        ELSE ROUND(
            ISNULL(SUM(th.OrderTotal), 0)
            / (COUNT(DISTINCT snt.SubscriberKey)
             - COUNT(DISTINCT b.SubscriberKey)), 4)
    END                                                  AS RevenuePerEmail,

    CASE
        WHEN COUNT(DISTINCT th.SubscriberKey) = 0 THEN 0
        ELSE ROUND(
            ISNULL(SUM(th.OrderTotal), 0)
            / COUNT(DISTINCT th.SubscriberKey), 2)
    END                                                  AS AvgOrderValue

FROM
    _Job AS j
    INNER JOIN _Sent AS snt
        ON j.JobID = snt.JobID
    LEFT JOIN _Bounce AS b
        ON snt.JobID = b.JobID
        AND snt.SubscriberKey = b.SubscriberKey
    LEFT JOIN _Open AS o
        ON snt.JobID = o.JobID
        AND snt.SubscriberKey = o.SubscriberKey
        AND o.IsUnique = 1
    LEFT JOIN _Click AS c
        ON snt.JobID = c.JobID
        AND snt.SubscriberKey = c.SubscriberKey
        AND c.IsUnique = 1
    LEFT JOIN _Unsubscribe AS u
        ON snt.JobID = u.JobID
        AND snt.SubscriberKey = u.SubscriberKey
    LEFT JOIN TransactionHistory AS th
        ON snt.SubscriberKey = th.SubscriberKey
        AND th.CampaignID = CAST(j.JobID AS VARCHAR(50))
        AND th.OrderStatus = 'Completed'
WHERE
    /*
      Replace these with the specific campaigns you want to compare.
      Options:
        - By JobID:    j.JobID IN (108501, 108320, 108115)
        - By Name:     j.EmailName LIKE '%Spring%'
        - By Date:     j.DeliveredTime BETWEEN '2026-03-01' AND '2026-03-31'
    */
    j.DeliveredTime >= DATEADD(DAY, -30, GETDATE())
GROUP BY
    j.JobID,
    j.EmailName,
    j.EmailSubject,
    j.DeliveredTime
ORDER BY
    j.DeliveredTime DESC

/*
============================================================
  EXPECTED SAMPLE OUTPUT
============================================================
| JobID  | EmailName           | EmailSubject                  | SendDate   | Sent  | Delivered | UniqueOpens | UniqueClicks | Unsubscribes | Conversions | Revenue   | OpenRate | ClickRate | CTOR  | UnsubRate | ConversionRate | RevenuePerEmail | AvgOrderValue |
|--------|---------------------|-------------------------------|------------|-------|-----------|-------------|--------------|--------------|-------------|-----------|----------|-----------|-------|-----------|----------------|-----------------|---------------|
| 108501 | March_Promo_2026    | Spring Sale: 30% Off          | 2026-03-10 | 50000 | 48500     | 14550       | 3880         | 48           | 620         | 31000.00  | 30.00    | 8.00      | 26.67 | 0.0990    | 1.2784         | 0.6392          | 50.00         |
| 108320 | Newsletter_Mar_Wk1  | This Week in Marketing        | 2026-03-03 | 45000 | 44100     | 11025       | 2205         | 22           | 88          | 2640.00   | 25.00    | 5.00      | 20.00 | 0.0499    | 0.1995         | 0.0599          | 30.00         |
| 108115 | Welcome_Series_S1   | Welcome to Our Community      | 2026-02-28 | 2000  | 1960      | 980         | 392          | 4            | 45          | 2250.00   | 50.00    | 20.00     | 40.00 | 0.2041    | 2.2959         | 1.1480          | 50.00         |
============================================================
*/
