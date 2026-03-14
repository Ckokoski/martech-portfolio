/*
============================================================
  Query Name:   Revenue Attribution by Email Campaign
  Category:     Campaign Reporting
  Purpose:      Attribute revenue to specific email campaigns
                using configurable attribution windows (1-day,
                7-day, 30-day post-click). This is critical for
                proving email ROI and justifying program
                investment to leadership.
  Use Case:     - Calculate email channel ROI
                - Identify highest-revenue campaigns for
                  replication
                - Compare attribution across different windows
                  to understand true email influence
                - Build a revenue-per-send report for finance
  Platform:     Salesforce Marketing Cloud (SFMC) Query Activity
  Tables Used:  _Job, _Sent, _Click, _Bounce,
                TransactionHistory
  Notes:        - This query uses last-click attribution: revenue
                  is credited to the most recent email clicked
                  before purchase.
                - Three attribution windows allow you to see
                  how revenue changes with different lookback
                  periods.
                - For multi-touch attribution, additional logic
                  (fractional credit) would be needed.
============================================================
*/

SELECT
    j.JobID,
    j.EmailName,
    j.EmailSubject,
    j.DeliveredTime                                      AS SendDate,

    /* --- Send Metrics --- */
    COUNT(DISTINCT snt.SubscriberKey)                    AS TotalSent,
    COUNT(DISTINCT snt.SubscriberKey)
      - COUNT(DISTINCT b.SubscriberKey)                  AS Delivered,
    COUNT(DISTINCT c.SubscriberKey)                      AS UniqueClickers,

    /* --- 1-Day Attribution Window --- */
    COUNT(DISTINCT CASE
        WHEN th.PurchaseDate <= DATEADD(DAY, 1, c.EventDate)
        THEN th.OrderID END)                             AS Orders_1Day,
    ISNULL(SUM(CASE
        WHEN th.PurchaseDate <= DATEADD(DAY, 1, c.EventDate)
        THEN th.OrderTotal ELSE 0 END), 0)               AS Revenue_1Day,

    /* --- 7-Day Attribution Window --- */
    COUNT(DISTINCT CASE
        WHEN th.PurchaseDate <= DATEADD(DAY, 7, c.EventDate)
        THEN th.OrderID END)                             AS Orders_7Day,
    ISNULL(SUM(CASE
        WHEN th.PurchaseDate <= DATEADD(DAY, 7, c.EventDate)
        THEN th.OrderTotal ELSE 0 END), 0)               AS Revenue_7Day,

    /* --- 30-Day Attribution Window --- */
    COUNT(DISTINCT CASE
        WHEN th.PurchaseDate <= DATEADD(DAY, 30, c.EventDate)
        THEN th.OrderID END)                             AS Orders_30Day,
    ISNULL(SUM(CASE
        WHEN th.PurchaseDate <= DATEADD(DAY, 30, c.EventDate)
        THEN th.OrderTotal ELSE 0 END), 0)               AS Revenue_30Day,

    /* --- Revenue Per Email (7-day window) --- */
    CASE
        WHEN (COUNT(DISTINCT snt.SubscriberKey)
            - COUNT(DISTINCT b.SubscriberKey)) = 0 THEN 0
        ELSE ROUND(
            ISNULL(SUM(CASE
                WHEN th.PurchaseDate <= DATEADD(DAY, 7, c.EventDate)
                THEN th.OrderTotal ELSE 0 END), 0)
            / (COUNT(DISTINCT snt.SubscriberKey)
             - COUNT(DISTINCT b.SubscriberKey)), 4)
    END                                                  AS RevenuePerEmail_7Day,

    /* --- Average Order Value (7-day window) --- */
    CASE
        WHEN COUNT(DISTINCT CASE
            WHEN th.PurchaseDate <= DATEADD(DAY, 7, c.EventDate)
            THEN th.OrderID END) = 0 THEN 0
        ELSE ROUND(
            ISNULL(SUM(CASE
                WHEN th.PurchaseDate <= DATEADD(DAY, 7, c.EventDate)
                THEN th.OrderTotal ELSE 0 END), 0)
            / COUNT(DISTINCT CASE
                WHEN th.PurchaseDate <= DATEADD(DAY, 7, c.EventDate)
                THEN th.OrderID END), 2)
    END                                                  AS AvgOrderValue_7Day,

    /* --- Click-to-Purchase Rate (7-day window) --- */
    CASE
        WHEN COUNT(DISTINCT c.SubscriberKey) = 0 THEN 0
        ELSE ROUND(
            COUNT(DISTINCT CASE
                WHEN th.PurchaseDate <= DATEADD(DAY, 7, c.EventDate)
                THEN th.SubscriberKey END) * 100.0
            / COUNT(DISTINCT c.SubscriberKey), 2)
    END                                                  AS ClickToPurchaseRate_7Day

FROM
    _Job AS j
    INNER JOIN _Sent AS snt
        ON j.JobID = snt.JobID
    LEFT JOIN _Bounce AS b
        ON snt.JobID = b.JobID
        AND snt.SubscriberKey = b.SubscriberKey
    LEFT JOIN _Click AS c
        ON snt.JobID = c.JobID
        AND snt.SubscriberKey = c.SubscriberKey
        AND c.IsUnique = 1
    LEFT JOIN TransactionHistory AS th
        ON c.SubscriberKey = th.SubscriberKey
        AND th.PurchaseDate >= c.EventDate
        AND th.OrderStatus = 'Completed'
WHERE
    j.DeliveredTime >= DATEADD(DAY, -90, GETDATE())
GROUP BY
    j.JobID,
    j.EmailName,
    j.EmailSubject,
    j.DeliveredTime
ORDER BY
    Revenue_7Day DESC

/*
============================================================
  EXPECTED SAMPLE OUTPUT
============================================================
| JobID  | EmailName           | EmailSubject              | SendDate   | TotalSent | Delivered | UniqueClickers | Orders_1Day | Revenue_1Day | Orders_7Day | Revenue_7Day | Orders_30Day | Revenue_30Day | RevenuePerEmail_7Day | AvgOrderValue_7Day | ClickToPurchaseRate_7Day |
|--------|---------------------|---------------------------|------------|-----------|-----------|----------------|-------------|--------------|-------------|--------------|--------------|---------------|----------------------|---------------------|--------------------------|
| 108501 | March_Promo_2026    | Spring Sale: 30% Off      | 2026-03-10 | 50000     | 48500     | 3880           | 420         | 21000.00     | 620         | 31000.00     | 810          | 40500.00      | 0.6392               | 50.00               | 15.98                    |
| 108115 | Welcome_Series_S1   | Welcome to Our Community  | 2026-02-28 | 2000      | 1960      | 392            | 28          | 1400.00      | 45          | 2250.00      | 62           | 3100.00       | 1.1480               | 50.00               | 11.48                    |
| 108320 | Newsletter_Mar_Wk1  | This Week in Marketing    | 2026-03-03 | 45000     | 44100     | 2205           | 32          | 960.00       | 88          | 2640.00      | 145          | 4350.00       | 0.0599               | 30.00               | 3.99                     |
============================================================
*/
