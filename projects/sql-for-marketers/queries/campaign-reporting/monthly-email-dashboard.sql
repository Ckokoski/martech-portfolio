/*
============================================================
  Query Name:   Monthly Email Dashboard
  Category:     Campaign Reporting
  Purpose:      Generate monthly aggregate email performance
                metrics with month-over-month (MoM) change
                calculations. Designed to populate a monthly
                leadership dashboard or reporting data extension.
  Use Case:     - Monthly performance report for leadership
                - Track program health trends over time
                - Identify seasonal patterns in engagement
                - Populate a BI tool or SFMC CloudPage dashboard
  Platform:     Salesforce Marketing Cloud (SFMC) Query Activity
  Tables Used:  _Job, _Sent, _Open, _Click, _Bounce,
                _Unsubscribe, TransactionHistory
  Notes:        - Groups by calendar month using YEAR/MONTH
                  date functions.
                - MoM calculations use LAG-style logic via
                  self-join since SFMC does not support window
                  functions like LAG().
                - Run as a monthly automation to build a
                  historical trend data extension.
============================================================
*/

SELECT
    curr.SendYear,
    curr.SendMonth,
    curr.MonthLabel,
    curr.TotalCampaigns,
    curr.TotalSent,
    curr.TotalDelivered,
    curr.UniqueOpens,
    curr.UniqueClicks,
    curr.Unsubscribes,
    curr.Conversions,
    curr.TotalRevenue,
    curr.OpenRate,
    curr.ClickRate,
    curr.CTOR,
    curr.UnsubRate,
    curr.ConversionRate,
    curr.RevenuePerEmail,

    /* --- Month-over-Month Changes --- */
    CASE
        WHEN prev.OpenRate IS NULL THEN NULL
        ELSE ROUND(curr.OpenRate - prev.OpenRate, 2)
    END                                                  AS OpenRate_MoM_Change,

    CASE
        WHEN prev.ClickRate IS NULL THEN NULL
        ELSE ROUND(curr.ClickRate - prev.ClickRate, 2)
    END                                                  AS ClickRate_MoM_Change,

    CASE
        WHEN prev.TotalRevenue IS NULL OR prev.TotalRevenue = 0 THEN NULL
        ELSE ROUND(
            (curr.TotalRevenue - prev.TotalRevenue) * 100.0
            / prev.TotalRevenue, 2)
    END                                                  AS Revenue_MoM_PctChange

FROM (
    /* --- Current Month Metrics --- */
    SELECT
        YEAR(j.DeliveredTime)                            AS SendYear,
        MONTH(j.DeliveredTime)                           AS SendMonth,
        CAST(YEAR(j.DeliveredTime) AS VARCHAR(4)) + '-'
          + RIGHT('0' + CAST(MONTH(j.DeliveredTime) AS VARCHAR(2)), 2)
                                                         AS MonthLabel,
        COUNT(DISTINCT j.JobID)                          AS TotalCampaigns,
        COUNT(DISTINCT snt.SubscriberKey)                AS TotalSent,
        COUNT(DISTINCT snt.SubscriberKey)
          - COUNT(DISTINCT b.SubscriberKey)              AS TotalDelivered,
        COUNT(DISTINCT o.SubscriberKey)                  AS UniqueOpens,
        COUNT(DISTINCT c.SubscriberKey)                  AS UniqueClicks,
        COUNT(DISTINCT u.SubscriberKey)                  AS Unsubscribes,
        COUNT(DISTINCT th.SubscriberKey)                 AS Conversions,
        ISNULL(SUM(th.OrderTotal), 0)                    AS TotalRevenue,
        CASE
            WHEN (COUNT(DISTINCT snt.SubscriberKey)
                - COUNT(DISTINCT b.SubscriberKey)) = 0 THEN 0
            ELSE ROUND(COUNT(DISTINCT o.SubscriberKey) * 100.0
                / (COUNT(DISTINCT snt.SubscriberKey)
                 - COUNT(DISTINCT b.SubscriberKey)), 2)
        END                                              AS OpenRate,
        CASE
            WHEN (COUNT(DISTINCT snt.SubscriberKey)
                - COUNT(DISTINCT b.SubscriberKey)) = 0 THEN 0
            ELSE ROUND(COUNT(DISTINCT c.SubscriberKey) * 100.0
                / (COUNT(DISTINCT snt.SubscriberKey)
                 - COUNT(DISTINCT b.SubscriberKey)), 2)
        END                                              AS ClickRate,
        CASE
            WHEN COUNT(DISTINCT o.SubscriberKey) = 0 THEN 0
            ELSE ROUND(COUNT(DISTINCT c.SubscriberKey) * 100.0
                / COUNT(DISTINCT o.SubscriberKey), 2)
        END                                              AS CTOR,
        CASE
            WHEN (COUNT(DISTINCT snt.SubscriberKey)
                - COUNT(DISTINCT b.SubscriberKey)) = 0 THEN 0
            ELSE ROUND(COUNT(DISTINCT u.SubscriberKey) * 100.0
                / (COUNT(DISTINCT snt.SubscriberKey)
                 - COUNT(DISTINCT b.SubscriberKey)), 4)
        END                                              AS UnsubRate,
        CASE
            WHEN (COUNT(DISTINCT snt.SubscriberKey)
                - COUNT(DISTINCT b.SubscriberKey)) = 0 THEN 0
            ELSE ROUND(COUNT(DISTINCT th.SubscriberKey) * 100.0
                / (COUNT(DISTINCT snt.SubscriberKey)
                 - COUNT(DISTINCT b.SubscriberKey)), 4)
        END                                              AS ConversionRate,
        CASE
            WHEN (COUNT(DISTINCT snt.SubscriberKey)
                - COUNT(DISTINCT b.SubscriberKey)) = 0 THEN 0
            ELSE ROUND(ISNULL(SUM(th.OrderTotal), 0)
                / (COUNT(DISTINCT snt.SubscriberKey)
                 - COUNT(DISTINCT b.SubscriberKey)), 4)
        END                                              AS RevenuePerEmail
    FROM _Job AS j
    INNER JOIN _Sent AS snt ON j.JobID = snt.JobID
    LEFT JOIN _Bounce AS b ON snt.JobID = b.JobID AND snt.SubscriberKey = b.SubscriberKey
    LEFT JOIN _Open AS o ON snt.JobID = o.JobID AND snt.SubscriberKey = o.SubscriberKey AND o.IsUnique = 1
    LEFT JOIN _Click AS c ON snt.JobID = c.JobID AND snt.SubscriberKey = c.SubscriberKey AND c.IsUnique = 1
    LEFT JOIN _Unsubscribe AS u ON snt.JobID = u.JobID AND snt.SubscriberKey = u.SubscriberKey
    LEFT JOIN TransactionHistory AS th ON snt.SubscriberKey = th.SubscriberKey
        AND th.CampaignID = CAST(j.JobID AS VARCHAR(50)) AND th.OrderStatus = 'Completed'
    WHERE j.DeliveredTime >= DATEADD(MONTH, -6, GETDATE())
    GROUP BY YEAR(j.DeliveredTime), MONTH(j.DeliveredTime)
) AS curr
LEFT JOIN (
    /* --- Previous Month Metrics (for MoM comparison) --- */
    SELECT
        YEAR(j.DeliveredTime)                            AS SendYear,
        MONTH(j.DeliveredTime)                           AS SendMonth,
        CASE
            WHEN (COUNT(DISTINCT snt.SubscriberKey)
                - COUNT(DISTINCT b.SubscriberKey)) = 0 THEN 0
            ELSE ROUND(COUNT(DISTINCT o.SubscriberKey) * 100.0
                / (COUNT(DISTINCT snt.SubscriberKey)
                 - COUNT(DISTINCT b.SubscriberKey)), 2)
        END                                              AS OpenRate,
        CASE
            WHEN (COUNT(DISTINCT snt.SubscriberKey)
                - COUNT(DISTINCT b.SubscriberKey)) = 0 THEN 0
            ELSE ROUND(COUNT(DISTINCT c.SubscriberKey) * 100.0
                / (COUNT(DISTINCT snt.SubscriberKey)
                 - COUNT(DISTINCT b.SubscriberKey)), 2)
        END                                              AS ClickRate,
        ISNULL(SUM(th.OrderTotal), 0)                    AS TotalRevenue
    FROM _Job AS j
    INNER JOIN _Sent AS snt ON j.JobID = snt.JobID
    LEFT JOIN _Bounce AS b ON snt.JobID = b.JobID AND snt.SubscriberKey = b.SubscriberKey
    LEFT JOIN _Open AS o ON snt.JobID = o.JobID AND snt.SubscriberKey = o.SubscriberKey AND o.IsUnique = 1
    LEFT JOIN _Click AS c ON snt.JobID = c.JobID AND snt.SubscriberKey = c.SubscriberKey AND c.IsUnique = 1
    LEFT JOIN TransactionHistory AS th ON snt.SubscriberKey = th.SubscriberKey
        AND th.CampaignID = CAST(j.JobID AS VARCHAR(50)) AND th.OrderStatus = 'Completed'
    WHERE j.DeliveredTime >= DATEADD(MONTH, -7, GETDATE())
    GROUP BY YEAR(j.DeliveredTime), MONTH(j.DeliveredTime)
) AS prev
    ON (curr.SendYear = prev.SendYear AND curr.SendMonth = prev.SendMonth + 1)
    OR (curr.SendMonth = 1 AND prev.SendMonth = 12 AND curr.SendYear = prev.SendYear + 1)
ORDER BY
    curr.SendYear DESC,
    curr.SendMonth DESC

/*
============================================================
  EXPECTED SAMPLE OUTPUT
============================================================
| SendYear | SendMonth | MonthLabel | TotalCampaigns | TotalSent | TotalDelivered | UniqueOpens | UniqueClicks | Unsubscribes | Conversions | TotalRevenue | OpenRate | ClickRate | CTOR  | UnsubRate | ConversionRate | RevenuePerEmail | OpenRate_MoM_Change | ClickRate_MoM_Change | Revenue_MoM_PctChange |
|----------|-----------|------------|----------------|-----------|----------------|-------------|--------------|--------------|-------------|--------------|----------|-----------|-------|-----------|----------------|-----------------|---------------------|----------------------|-----------------------|
| 2026     | 3         | 2026-03    | 18             | 250000    | 242500         | 72750       | 19400        | 242          | 1850        | 92500.00     | 30.00    | 8.00      | 26.67 | 0.0998    | 0.7629         | 0.3814          | 2.00                | 1.00                 | 12.50                 |
| 2026     | 2         | 2026-02    | 15             | 220000    | 213400         | 59752       | 14938        | 213          | 1500        | 82222.00     | 28.00    | 7.00      | 25.00 | 0.0998    | 0.7028         | 0.3854          | -1.00               | -0.50                | -3.20                 |
| 2026     | 1         | 2026-01    | 14             | 200000    | 194000         | 56260       | 14550        | 194          | 1380        | 84940.00     | 29.00    | 7.50      | 25.86 | 0.1000    | 0.7113         | 0.4378          | NULL                | NULL                 | NULL                  |
============================================================
*/
