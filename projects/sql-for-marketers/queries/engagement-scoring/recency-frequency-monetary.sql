/*
============================================================
  Query Name:   RFM Scoring Model (Recency-Frequency-Monetary)
  Category:     Engagement Scoring
  Purpose:      Score each customer on three dimensions:
                  R = Recency  (how recently they purchased)
                  F = Frequency (how often they purchase)
                  M = Monetary  (how much they spend)
                Each dimension is scored 1-5 (5 = best), then
                combined into an RFM segment code like "555"
                (champion) or "111" (hibernating).
  Use Case:     - Identify champions (555) for VIP treatment
                - Target "can't lose them" (5xx with low F/M)
                  for retention campaigns
                - Find "promising" customers (x4x, x5x) for
                  upsell programs
                - Standard retail/ecommerce segmentation model
  Platform:     Salesforce Marketing Cloud (SFMC) Query Activity
  Tables Used:  _Subscribers, TransactionHistory
  Notes:        - SFMC lacks NTILE(), so we use a CASE-based
                  quintile approach with threshold values.
                - Adjust thresholds based on your actual data
                  distribution. Run a preliminary stats query
                  first to find your 20/40/60/80 percentiles.
============================================================
*/

SELECT
    s.SubscriberKey,
    s.EmailAddress,
    s.FirstName,
    s.LastName,
    rfm.DaysSinceLastPurchase,
    rfm.TotalOrders,
    rfm.TotalRevenue,

    /* --- Recency Score (1-5, lower days = higher score) --- */
    CASE
        WHEN rfm.DaysSinceLastPurchase <= 14  THEN 5
        WHEN rfm.DaysSinceLastPurchase <= 30  THEN 4
        WHEN rfm.DaysSinceLastPurchase <= 90  THEN 3
        WHEN rfm.DaysSinceLastPurchase <= 180 THEN 2
        ELSE 1
    END AS R_Score,

    /* --- Frequency Score (1-5, more orders = higher score) --- */
    CASE
        WHEN rfm.TotalOrders >= 10 THEN 5
        WHEN rfm.TotalOrders >= 6  THEN 4
        WHEN rfm.TotalOrders >= 3  THEN 3
        WHEN rfm.TotalOrders >= 2  THEN 2
        ELSE 1
    END AS F_Score,

    /* --- Monetary Score (1-5, more revenue = higher score) --- */
    CASE
        WHEN rfm.TotalRevenue >= 1000 THEN 5
        WHEN rfm.TotalRevenue >= 500  THEN 4
        WHEN rfm.TotalRevenue >= 200  THEN 3
        WHEN rfm.TotalRevenue >= 75   THEN 2
        ELSE 1
    END AS M_Score,

    /* --- Combined RFM Code --- */
    CAST(
        CASE WHEN rfm.DaysSinceLastPurchase <= 14 THEN 5
             WHEN rfm.DaysSinceLastPurchase <= 30 THEN 4
             WHEN rfm.DaysSinceLastPurchase <= 90 THEN 3
             WHEN rfm.DaysSinceLastPurchase <= 180 THEN 2
             ELSE 1 END AS VARCHAR(1)
    ) + CAST(
        CASE WHEN rfm.TotalOrders >= 10 THEN 5
             WHEN rfm.TotalOrders >= 6  THEN 4
             WHEN rfm.TotalOrders >= 3  THEN 3
             WHEN rfm.TotalOrders >= 2  THEN 2
             ELSE 1 END AS VARCHAR(1)
    ) + CAST(
        CASE WHEN rfm.TotalRevenue >= 1000 THEN 5
             WHEN rfm.TotalRevenue >= 500  THEN 4
             WHEN rfm.TotalRevenue >= 200  THEN 3
             WHEN rfm.TotalRevenue >= 75   THEN 2
             ELSE 1 END AS VARCHAR(1)
    ) AS RFM_Code,

    /* --- RFM Segment Label --- */
    CASE
        WHEN CASE WHEN rfm.DaysSinceLastPurchase <= 14 THEN 5
                  WHEN rfm.DaysSinceLastPurchase <= 30 THEN 4
                  ELSE 3 END >= 4
         AND CASE WHEN rfm.TotalOrders >= 10 THEN 5
                  WHEN rfm.TotalOrders >= 6  THEN 4
                  ELSE 3 END >= 4
         AND CASE WHEN rfm.TotalRevenue >= 1000 THEN 5
                  WHEN rfm.TotalRevenue >= 500  THEN 4
                  ELSE 3 END >= 4
            THEN 'Champion'
        WHEN rfm.DaysSinceLastPurchase <= 30 AND rfm.TotalOrders >= 3
            THEN 'Loyal Customer'
        WHEN rfm.DaysSinceLastPurchase <= 30 AND rfm.TotalOrders <= 2
            THEN 'New / Promising'
        WHEN rfm.DaysSinceLastPurchase BETWEEN 31 AND 90
            THEN 'Needs Attention'
        WHEN rfm.DaysSinceLastPurchase BETWEEN 91 AND 180
         AND rfm.TotalRevenue >= 500
            THEN 'At Risk - High Value'
        WHEN rfm.DaysSinceLastPurchase BETWEEN 91 AND 180
            THEN 'At Risk'
        WHEN rfm.DaysSinceLastPurchase > 180 AND rfm.TotalRevenue >= 500
            THEN 'Cannot Lose Them'
        ELSE 'Hibernating'
    END AS RFM_Segment

FROM (
    SELECT
        th.SubscriberKey,
        DATEDIFF(DAY, MAX(th.PurchaseDate), GETDATE())  AS DaysSinceLastPurchase,
        COUNT(DISTINCT th.OrderID)                       AS TotalOrders,
        ROUND(SUM(th.OrderTotal), 2)                     AS TotalRevenue
    FROM
        TransactionHistory AS th
    WHERE
        th.OrderStatus = 'Completed'
        AND th.PurchaseDate >= DATEADD(MONTH, -24, GETDATE())
    GROUP BY
        th.SubscriberKey
) AS rfm
INNER JOIN _Subscribers AS s
    ON rfm.SubscriberKey = s.SubscriberKey
WHERE
    s.Status = 'Active'
ORDER BY
    R_Score DESC, F_Score DESC, M_Score DESC

/*
============================================================
  EXPECTED SAMPLE OUTPUT
============================================================
| SubscriberKey | EmailAddress        | FirstName | LastName | DaysSinceLastPurchase | TotalOrders | TotalRevenue | R_Score | F_Score | M_Score | RFM_Code | RFM_Segment        |
|---------------|---------------------|-----------|----------|-----------------------|-------------|--------------|---------|---------|---------|----------|---------------------|
| SK-00125      | champ@example.com   | Olivia    | Chen     | 3                     | 18          | 4820.50      | 5       | 5       | 5       | 555      | Champion            |
| SK-00398      | loyal@example.com   | Marcus    | Patel    | 12                    | 8           | 1350.00      | 5       | 4       | 5       | 545      | Loyal Customer      |
| SK-50100      | newbuy@example.com  | Nina      | Hart     | 8                     | 1           | 89.99        | 5       | 1       | 2       | 512      | New / Promising     |
| SK-61003      | atrisk@example.com  | Derek     | Soto     | 120                   | 6           | 920.00       | 2       | 4       | 4       | 244      | At Risk - High Value|
| SK-72415      | lapsed@example.com  | Rosa      | Webb     | 250                   | 3           | 150.00       | 1       | 3       | 2       | 132      | Hibernating         |
============================================================
*/
