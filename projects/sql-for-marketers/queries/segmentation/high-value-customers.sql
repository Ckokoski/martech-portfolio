/*
============================================================
  Query Name:   High-Value Customers (Top 10% by Purchase Value)
  Category:     Segmentation
  Purpose:      Identify the top 10% of customers by total
                purchase value over the past 12 months. These
                are your VIP contacts who warrant exclusive
                treatment — early access, loyalty perks, and
                dedicated communication streams.
  Use Case:     - Build a VIP segment for exclusive campaigns
                - Feed into a loyalty / rewards journey
                - Protect these contacts from over-mailing
                - Use as a seed audience for lookalike modeling
  Platform:     Salesforce Marketing Cloud (SFMC) Query Activity
  Tables Used:  _Subscribers, TransactionHistory
  Notes:        - SFMC does not support PERCENTILE functions,
                  so we use a subquery to find the 90th
                  percentile threshold by row count.
                - TransactionHistory is a custom data extension;
                  adapt table/column names to your schema.
============================================================
*/

SELECT
    t.SubscriberKey,
    s.EmailAddress,
    s.FirstName,
    s.LastName,
    t.TotalRevenue,
    t.TotalOrders,
    t.AvgOrderValue,
    t.FirstPurchaseDate,
    t.LastPurchaseDate,
    DATEDIFF(DAY, t.LastPurchaseDate, GETDATE())    AS DaysSinceLastPurchase
FROM (
    SELECT
        th.SubscriberKey,
        SUM(th.OrderTotal)                           AS TotalRevenue,
        COUNT(DISTINCT th.OrderID)                   AS TotalOrders,
        ROUND(SUM(th.OrderTotal)
              / NULLIF(COUNT(DISTINCT th.OrderID), 0), 2)  AS AvgOrderValue,
        MIN(th.PurchaseDate)                         AS FirstPurchaseDate,
        MAX(th.PurchaseDate)                         AS LastPurchaseDate
    FROM
        TransactionHistory AS th
    WHERE
        th.PurchaseDate >= DATEADD(MONTH, -12, GETDATE())
        AND th.OrderStatus = 'Completed'
    GROUP BY
        th.SubscriberKey
) AS t
INNER JOIN _Subscribers AS s
    ON t.SubscriberKey = s.SubscriberKey
WHERE
    s.Status = 'Active'
    AND t.TotalRevenue >= (
        /*
            Find the revenue threshold for the top 10%.
            Since SFMC lacks PERCENTILE_CONT, we use a
            row-counting approach: order all customers by
            revenue descending, take the top 10% row count,
            and use the minimum revenue in that set.
        */
        SELECT MIN(sub.TotalRevenue)
        FROM (
            SELECT TOP 10 PERCENT
                th2.SubscriberKey,
                SUM(th2.OrderTotal) AS TotalRevenue
            FROM
                TransactionHistory AS th2
            WHERE
                th2.PurchaseDate >= DATEADD(MONTH, -12, GETDATE())
                AND th2.OrderStatus = 'Completed'
            GROUP BY
                th2.SubscriberKey
            ORDER BY
                SUM(th2.OrderTotal) DESC
        ) AS sub
    )
ORDER BY
    t.TotalRevenue DESC

/*
============================================================
  EXPECTED SAMPLE OUTPUT
============================================================
| SubscriberKey | EmailAddress          | FirstName | LastName | TotalRevenue | TotalOrders | AvgOrderValue | FirstPurchaseDate | LastPurchaseDate | DaysSinceLastPurchase |
|---------------|-----------------------|-----------|----------|--------------|-------------|---------------|-------------------|------------------|-----------------------|
| SK-00125      | vip1@example.com      | Olivia    | Chen     | 4820.50      | 18          | 267.81        | 2025-04-10        | 2026-03-11       | 3                     |
| SK-00398      | vip2@example.com      | Marcus    | Patel    | 3975.00      | 12          | 331.25        | 2025-06-22        | 2026-03-08       | 6                     |
| SK-00541      | vip3@example.com      | Nina      | Foster   | 3210.75      | 15          | 214.05        | 2025-05-03        | 2026-02-27       | 15                    |
| SK-00710      | vip4@example.com      | Derek     | Yamamoto | 2890.00      | 9           | 321.11        | 2025-08-14        | 2026-03-02       | 12                    |
============================================================
*/
