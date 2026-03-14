/*
============================================================
  Query Name:   Campaign Performance Summary
  Category:     Campaign Reporting
  Purpose:      Generate a comprehensive KPI summary for each
                email campaign: sent, delivered, bounced, opened,
                clicked, unsubscribed, converted, and revenue.
                This is the single most-used reporting query
                in any email marketing program.
  Use Case:     - Weekly/monthly performance review with leadership
                - Populate a BI dashboard or reporting data extension
                - Benchmark campaigns against historical averages
                - Identify top and bottom performing sends
  Platform:     Salesforce Marketing Cloud (SFMC) Query Activity
  Tables Used:  _Sent, _Open, _Click, _Bounce, _Unsubscribe,
                _Job, TransactionHistory
  Notes:        - _Job contains campaign-level metadata (name,
                  send date, subject line).
                - Rates are calculated as percentages of delivered
                  (not sent) for accuracy.
                - SFMC data views retain 6 months of data by
                  default.
============================================================
*/

SELECT
    j.JobID,
    j.EmailName,
    j.EmailSubject,
    j.DeliveredTime                                      AS SendDate,

    /* --- Volume Metrics --- */
    COUNT(DISTINCT snt.SubscriberKey)                    AS TotalSent,
    COUNT(DISTINCT snt.SubscriberKey)
        - COUNT(DISTINCT b.SubscriberKey)                AS TotalDelivered,
    COUNT(DISTINCT b.SubscriberKey)                      AS TotalBounced,

    /* --- Engagement Metrics --- */
    COUNT(DISTINCT o.SubscriberKey)                      AS UniqueOpens,
    COUNT(DISTINCT c.SubscriberKey)                      AS UniqueClicks,
    COUNT(DISTINCT u.SubscriberKey)                      AS Unsubscribes,
    COUNT(DISTINCT th.SubscriberKey)                     AS Conversions,

    /* --- Revenue --- */
    ISNULL(SUM(th.OrderTotal), 0)                        AS TotalRevenue,

    /* --- Rate Calculations (based on delivered) --- */
    CASE
        WHEN COUNT(DISTINCT snt.SubscriberKey) = 0 THEN 0
        ELSE ROUND(
            COUNT(DISTINCT b.SubscriberKey) * 100.0
            / COUNT(DISTINCT snt.SubscriberKey), 2)
    END                                                  AS BounceRate,

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

    /* Click-to-Open Rate (CTOR) */
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
    END                                                  AS UnsubscribeRate,

    /* Revenue per email delivered */
    CASE
        WHEN (COUNT(DISTINCT snt.SubscriberKey)
            - COUNT(DISTINCT b.SubscriberKey)) = 0 THEN 0
        ELSE ROUND(
            ISNULL(SUM(th.OrderTotal), 0)
            / (COUNT(DISTINCT snt.SubscriberKey)
             - COUNT(DISTINCT b.SubscriberKey)), 4)
    END                                                  AS RevenuePerEmail

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
    j.DeliveredTime >= DATEADD(DAY, -90, GETDATE())
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
| JobID  | EmailName              | EmailSubject               | SendDate   | TotalSent | TotalDelivered | TotalBounced | UniqueOpens | UniqueClicks | Unsubscribes | Conversions | TotalRevenue | BounceRate | OpenRate | ClickRate | CTOR  | UnsubscribeRate | RevenuePerEmail |
|--------|------------------------|----------------------------|------------|-----------|----------------|--------------|-------------|--------------|--------------|-------------|--------------|------------|----------|-----------|-------|-----------------|-----------------|
| 108501 | March_Promo_2026       | Spring Sale: 30% Off       | 2026-03-10 | 50000     | 48500          | 1500         | 14550       | 3880         | 48           | 620         | 31000.00     | 3.00       | 30.00    | 8.00      | 26.67 | 0.0990          | 0.6392          |
| 108320 | Newsletter_Mar_Wk1     | This Week in Marketing     | 2026-03-03 | 45000     | 44100          | 900          | 11025       | 2205         | 22           | 88          | 2640.00      | 2.00       | 25.00    | 5.00      | 20.00 | 0.0499          | 0.0599          |
| 108115 | Welcome_Series_Step1   | Welcome to Our Community   | 2026-02-28 | 2000      | 1960           | 40           | 980         | 392          | 4            | 45          | 2250.00      | 2.00       | 50.00    | 20.00     | 40.00 | 0.2041          | 1.1480          |
============================================================
*/
