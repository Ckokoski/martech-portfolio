/*
============================================================
  Query Name:   Lifecycle Stage Assignment
  Category:     Segmentation
  Purpose:      Assign each subscriber to a lifecycle stage
                (New, Active, At-Risk, Lapsed) based on their
                tenure and engagement behavior. This is the
                foundation for lifecycle marketing programs.
  Use Case:     - Trigger stage-specific journeys (welcome,
                  nurture, win-back, sunset)
                - Report on lifecycle distribution over time
                - Measure stage transition rates as a health KPI
                - Align email frequency to lifecycle stage
  Platform:     Salesforce Marketing Cloud (SFMC) Query Activity
  Tables Used:  _Subscribers, _Open, _Click, TransactionHistory
  Notes:        - Lifecycle definitions are business-specific.
                  Adjust the day thresholds to match your brand's
                  engagement and purchase cycles.
                - This query uses a single-pass approach with
                  CASE logic to avoid needing CTEs.
============================================================
*/

SELECT
    s.SubscriberKey,
    s.EmailAddress,
    s.FirstName,
    s.LastName,
    s.DateJoined,
    DATEDIFF(DAY, s.DateJoined, GETDATE())              AS TenureDays,
    MAX(o.EventDate)                                     AS LastOpenDate,
    MAX(c.EventDate)                                     AS LastClickDate,
    MAX(th.PurchaseDate)                                 AS LastPurchaseDate,
    COUNT(DISTINCT o.JobID)                              AS TotalOpens,
    COUNT(DISTINCT c.JobID)                              AS TotalClicks,
    COUNT(DISTINCT th.OrderID)                           AS TotalOrders,

    /* ---- Lifecycle Stage Logic ---- */
    CASE
        /* NEW: Joined in the last 30 days */
        WHEN DATEDIFF(DAY, s.DateJoined, GETDATE()) <= 30
            THEN 'New'

        /* ACTIVE: Opened or clicked in last 60 days */
        WHEN MAX(o.EventDate) >= DATEADD(DAY, -60, GETDATE())
          OR MAX(c.EventDate) >= DATEADD(DAY, -60, GETDATE())
            THEN 'Active'

        /* AT-RISK: Last engagement 61-180 days ago */
        WHEN MAX(o.EventDate) >= DATEADD(DAY, -180, GETDATE())
          OR MAX(c.EventDate) >= DATEADD(DAY, -180, GETDATE())
            THEN 'At-Risk'

        /* LAPSED: No engagement in 180+ days or never engaged */
        ELSE 'Lapsed'
    END                                                  AS LifecycleStage,

    /* ---- Sub-stage for more granular targeting ---- */
    CASE
        WHEN DATEDIFF(DAY, s.DateJoined, GETDATE()) <= 7
            THEN 'New - First Week'
        WHEN DATEDIFF(DAY, s.DateJoined, GETDATE()) <= 30
            THEN 'New - Onboarding'
        WHEN MAX(c.EventDate) >= DATEADD(DAY, -30, GETDATE())
         AND COUNT(DISTINCT th.OrderID) > 0
            THEN 'Active - Buyer'
        WHEN MAX(o.EventDate) >= DATEADD(DAY, -60, GETDATE())
            THEN 'Active - Browser'
        WHEN MAX(o.EventDate) >= DATEADD(DAY, -180, GETDATE())
            THEN 'At-Risk - Fading'
        WHEN MAX(o.EventDate) IS NULL
            THEN 'Lapsed - Never Engaged'
        ELSE 'Lapsed - Gone Dark'
    END                                                  AS LifecycleSubStage

FROM
    _Subscribers AS s
    LEFT JOIN _Open AS o
        ON s.SubscriberKey = o.SubscriberKey
        AND o.IsUnique = 1
    LEFT JOIN _Click AS c
        ON s.SubscriberKey = c.SubscriberKey
        AND c.IsUnique = 1
    LEFT JOIN TransactionHistory AS th
        ON s.SubscriberKey = th.SubscriberKey
        AND th.OrderStatus = 'Completed'
WHERE
    s.Status = 'Active'
GROUP BY
    s.SubscriberKey,
    s.EmailAddress,
    s.FirstName,
    s.LastName,
    s.DateJoined
ORDER BY
    LifecycleStage,
    s.DateJoined DESC

/*
============================================================
  EXPECTED SAMPLE OUTPUT
============================================================
| SubscriberKey | EmailAddress          | FirstName | LastName | DateJoined | TenureDays | LastOpenDate | LastClickDate | LastPurchaseDate | TotalOpens | TotalClicks | TotalOrders | LifecycleStage | LifecycleSubStage     |
|---------------|-----------------------|-----------|----------|------------|------------|--------------|---------------|-----------------|------------|-------------|-------------|----------------|-----------------------|
| SK-99210      | recent@example.com    | Dana      | Park     | 2026-03-10 | 4          | 2026-03-12   | NULL          | NULL            | 1          | 0           | 0           | New            | New - First Week      |
| SK-98005      | onboard@example.com   | Eli       | Cruz     | 2026-02-25 | 17         | 2026-03-05   | 2026-03-01    | NULL            | 3          | 1           | 0           | New            | New - Onboarding      |
| SK-10042      | buyer@example.com     | Faye      | Lin      | 2025-06-15 | 272        | 2026-03-11   | 2026-03-10    | 2026-03-08      | 28         | 14          | 5           | Active         | Active - Buyer        |
| SK-40822      | browser@example.com   | Gabe      | Roy      | 2025-01-20 | 418        | 2026-02-20   | 2026-01-05    | NULL            | 15         | 3           | 0           | Active         | Active - Browser      |
| SK-61003      | fading@example.com    | Hana      | Soto     | 2024-08-10 | 581        | 2025-11-02   | 2025-10-15    | 2025-09-20      | 10         | 4           | 2           | At-Risk        | At-Risk - Fading      |
| SK-72415      | gone@example.com      | Ivan      | Pham     | 2023-03-01 | 1109       | 2024-06-18   | NULL          | NULL            | 5          | 0           | 0           | Lapsed         | Lapsed - Gone Dark    |
============================================================
*/
