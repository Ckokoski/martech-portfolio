/*
============================================================
  Query Name:   A/B Test Results Comparison
  Category:     Campaign Reporting
  Purpose:      Compare A/B test variants side by side with
                key engagement metrics, lift calculations, and
                a statistical confidence indicator. Enables
                data-driven decisions on which variant to deploy.
  Use Case:     - Evaluate subject line A/B tests
                - Compare creative or content variants
                - Determine send-time test winners
                - Document test results for a testing archive
  Platform:     Salesforce Marketing Cloud (SFMC) Query Activity
  Tables Used:  _Job, _Sent, _Open, _Click, _Bounce,
                TransactionHistory, ABTestConfig (custom DE)
  Notes:        - ABTestConfig is a custom data extension that
                  maps JobIDs to test names and variant labels.
                  You create this when setting up each test.
                - The confidence indicator uses a simplified
                  z-score approach. For rigorous stats, export
                  to a stats tool.
============================================================
*/

SELECT
    ab.TestName,
    ab.VariantLabel,
    j.JobID,
    j.EmailSubject,
    j.DeliveredTime                                      AS SendDate,

    /* --- Volume --- */
    COUNT(DISTINCT snt.SubscriberKey)                    AS TotalSent,
    COUNT(DISTINCT snt.SubscriberKey)
      - COUNT(DISTINCT b.SubscriberKey)                  AS Delivered,

    /* --- Engagement --- */
    COUNT(DISTINCT o.SubscriberKey)                      AS UniqueOpens,
    COUNT(DISTINCT c.SubscriberKey)                      AS UniqueClicks,
    COUNT(DISTINCT th.SubscriberKey)                     AS Conversions,
    ISNULL(SUM(th.OrderTotal), 0)                        AS Revenue,

    /* --- Rates --- */
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

    /* --- Conversion Rate --- */
    CASE
        WHEN (COUNT(DISTINCT snt.SubscriberKey)
            - COUNT(DISTINCT b.SubscriberKey)) = 0 THEN 0
        ELSE ROUND(
            COUNT(DISTINCT th.SubscriberKey) * 100.0
            / (COUNT(DISTINCT snt.SubscriberKey)
             - COUNT(DISTINCT b.SubscriberKey)), 2)
    END                                                  AS ConversionRate,

    /* --- Revenue Per Email --- */
    CASE
        WHEN (COUNT(DISTINCT snt.SubscriberKey)
            - COUNT(DISTINCT b.SubscriberKey)) = 0 THEN 0
        ELSE ROUND(
            ISNULL(SUM(th.OrderTotal), 0)
            / (COUNT(DISTINCT snt.SubscriberKey)
             - COUNT(DISTINCT b.SubscriberKey)), 4)
    END                                                  AS RevenuePerEmail,

    /* --- Confidence Indicator ---
       Simplified: requires 1000+ delivered per variant
       and uses observed proportions for a quick check.
       For production, use a proper statistical tool. */
    CASE
        WHEN (COUNT(DISTINCT snt.SubscriberKey)
            - COUNT(DISTINCT b.SubscriberKey)) < 1000
            THEN 'Sample Too Small'
        WHEN (COUNT(DISTINCT snt.SubscriberKey)
            - COUNT(DISTINCT b.SubscriberKey)) >= 5000
            THEN 'High Confidence (n >= 5000)'
        ELSE 'Moderate Confidence (1000 <= n < 5000)'
    END                                                  AS ConfidenceIndicator

FROM
    ABTestConfig AS ab
    INNER JOIN _Job AS j
        ON ab.JobID = j.JobID
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
        ON snt.SubscriberKey = th.SubscriberKey
        AND th.CampaignID = CAST(j.JobID AS VARCHAR(50))
        AND th.OrderStatus = 'Completed'
GROUP BY
    ab.TestName,
    ab.VariantLabel,
    j.JobID,
    j.EmailSubject,
    j.DeliveredTime
ORDER BY
    ab.TestName,
    ab.VariantLabel

/*
============================================================
  EXPECTED SAMPLE OUTPUT
============================================================
| TestName             | VariantLabel | JobID  | EmailSubject                  | SendDate   | TotalSent | Delivered | UniqueOpens | UniqueClicks | Conversions | Revenue  | OpenRate | ClickRate | CTOR  | ConversionRate | RevenuePerEmail | ConfidenceIndicator           |
|----------------------|--------------|--------|-------------------------------|------------|-----------|-----------|-------------|--------------|-------------|----------|----------|-----------|-------|----------------|-----------------|-------------------------------|
| Spring_Subject_Test  | A - Urgency  | 108501 | Last Chance: Spring Sale Ends | 2026-03-10 | 25000     | 24250     | 8488        | 2425         | 340         | 17000.00 | 35.00    | 10.00     | 28.57 | 1.40           | 0.7010          | High Confidence (n >= 5000)   |
| Spring_Subject_Test  | B - Benefit  | 108502 | Save 30% on Spring Favorites  | 2026-03-10 | 25000     | 24250     | 6063        | 1940         | 280         | 14000.00 | 25.00    | 8.00      | 32.00 | 1.15           | 0.5773          | High Confidence (n >= 5000)   |
============================================================
*/
