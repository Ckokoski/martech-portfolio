/*
============================================================
  Query Name:   Funnel Progression (Send to Purchase)
  Category:     Campaign Reporting
  Purpose:      Map the full conversion funnel for each campaign
                from send through delivery, open, click, and
                purchase. Shows drop-off at each stage and
                cumulative conversion rates.
  Use Case:     - Identify where the biggest drop-offs occur
                - Compare funnel shape across campaign types
                - Justify investment in specific funnel stages
                  (e.g., landing page optimization for click-to-
                  convert gap)
                - Executive-ready funnel visualization data
  Platform:     Salesforce Marketing Cloud (SFMC) Query Activity
  Tables Used:  _Job, _Sent, _Bounce, _Open, _Click,
                TransactionHistory
  Notes:        - Each funnel stage is a subset of the previous
                  stage (except bounce, which is a subtraction).
                - Conversion attribution uses a 7-day window
                  post-click. Adjust to match your attribution
                  model.
============================================================
*/

SELECT
    j.JobID,
    j.EmailName,
    j.DeliveredTime                                      AS SendDate,

    /* --- Stage 1: Sent --- */
    COUNT(DISTINCT snt.SubscriberKey)                    AS Stage1_Sent,

    /* --- Stage 2: Delivered (Sent - Bounced) --- */
    COUNT(DISTINCT snt.SubscriberKey)
      - COUNT(DISTINCT b.SubscriberKey)                  AS Stage2_Delivered,
    CASE
        WHEN COUNT(DISTINCT snt.SubscriberKey) = 0 THEN 0
        ELSE ROUND(
            (COUNT(DISTINCT snt.SubscriberKey) - COUNT(DISTINCT b.SubscriberKey)) * 100.0
            / COUNT(DISTINCT snt.SubscriberKey), 2)
    END                                                  AS DeliveryRate,

    /* --- Stage 3: Opened --- */
    COUNT(DISTINCT o.SubscriberKey)                      AS Stage3_Opened,
    CASE
        WHEN (COUNT(DISTINCT snt.SubscriberKey)
            - COUNT(DISTINCT b.SubscriberKey)) = 0 THEN 0
        ELSE ROUND(
            COUNT(DISTINCT o.SubscriberKey) * 100.0
            / (COUNT(DISTINCT snt.SubscriberKey)
             - COUNT(DISTINCT b.SubscriberKey)), 2)
    END                                                  AS OpenRate,

    /* --- Stage 4: Clicked --- */
    COUNT(DISTINCT c.SubscriberKey)                      AS Stage4_Clicked,
    CASE
        WHEN COUNT(DISTINCT o.SubscriberKey) = 0 THEN 0
        ELSE ROUND(
            COUNT(DISTINCT c.SubscriberKey) * 100.0
            / COUNT(DISTINCT o.SubscriberKey), 2)
    END                                                  AS ClickToOpenRate,

    /* --- Stage 5: Converted (purchased within 7 days of click) --- */
    COUNT(DISTINCT th.SubscriberKey)                     AS Stage5_Converted,
    CASE
        WHEN COUNT(DISTINCT c.SubscriberKey) = 0 THEN 0
        ELSE ROUND(
            COUNT(DISTINCT th.SubscriberKey) * 100.0
            / COUNT(DISTINCT c.SubscriberKey), 2)
    END                                                  AS ClickToConvertRate,

    /* --- Overall Funnel Conversion (Delivered to Converted) --- */
    CASE
        WHEN (COUNT(DISTINCT snt.SubscriberKey)
            - COUNT(DISTINCT b.SubscriberKey)) = 0 THEN 0
        ELSE ROUND(
            COUNT(DISTINCT th.SubscriberKey) * 100.0
            / (COUNT(DISTINCT snt.SubscriberKey)
             - COUNT(DISTINCT b.SubscriberKey)), 4)
    END                                                  AS OverallConversionRate,

    /* --- Revenue --- */
    ISNULL(SUM(th.OrderTotal), 0)                        AS TotalRevenue

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
    LEFT JOIN TransactionHistory AS th
        ON c.SubscriberKey = th.SubscriberKey
        AND th.PurchaseDate >= c.EventDate
        AND th.PurchaseDate <= DATEADD(DAY, 7, c.EventDate)
        AND th.OrderStatus = 'Completed'
WHERE
    j.DeliveredTime >= DATEADD(DAY, -90, GETDATE())
GROUP BY
    j.JobID,
    j.EmailName,
    j.DeliveredTime
ORDER BY
    OverallConversionRate DESC

/*
============================================================
  EXPECTED SAMPLE OUTPUT
============================================================
| JobID  | EmailName           | SendDate   | Stage1_Sent | Stage2_Delivered | DeliveryRate | Stage3_Opened | OpenRate | Stage4_Clicked | ClickToOpenRate | Stage5_Converted | ClickToConvertRate | OverallConversionRate | TotalRevenue |
|--------|---------------------|------------|-------------|------------------|--------------|---------------|----------|----------------|-----------------|------------------|--------------------|----------------------|--------------|
| 108501 | March_Promo_2026    | 2026-03-10 | 50000       | 48500            | 97.00        | 14550         | 30.00    | 3880           | 26.67           | 620              | 15.98              | 1.2784               | 31000.00     |
| 108115 | Welcome_Series_S1   | 2026-02-28 | 2000        | 1960             | 98.00        | 980           | 50.00    | 392            | 40.00           | 45               | 11.48              | 2.2959               | 2250.00      |
| 108320 | Newsletter_Mar_Wk1  | 2026-03-03 | 45000       | 44100            | 98.00        | 11025         | 25.00    | 2205           | 20.00           | 88               | 3.99               | 0.1995               | 2640.00      |
============================================================
*/
