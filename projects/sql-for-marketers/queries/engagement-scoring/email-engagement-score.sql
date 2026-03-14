/*
============================================================
  Query Name:   Email Engagement Score
  Category:     Engagement Scoring
  Purpose:      Calculate a weighted engagement score for each
                subscriber based on opens, clicks, and
                conversions over the past 90 days. Scores are
                normalized to a 0-100 scale for easy comparison
                and threshold-based segmentation.
  Use Case:     - Determine send frequency (high scorers get
                  more emails, low scorers get fewer)
                - Feed into deliverability protection strategies
                - Rank subscribers for priority targeting
                - Identify engagement-based suppression thresholds
  Platform:     Salesforce Marketing Cloud (SFMC) Query Activity
  Tables Used:  _Subscribers, _Open, _Click, _Sent,
                TransactionHistory
  Scoring Model:
                  Opens   = 1 point each  (awareness signal)
                  Clicks  = 3 points each (intent signal)
                  Conversions = 5 points  (action signal)
                  Score is capped at 100 via normalization.
============================================================
*/

SELECT
    s.SubscriberKey,
    s.EmailAddress,
    s.FirstName,
    s.LastName,
    COUNT(DISTINCT snt.JobID)                    AS EmailsSent,
    COUNT(DISTINCT o.JobID)                      AS UniqueOpens,
    COUNT(DISTINCT c.JobID)                      AS UniqueClicks,
    COUNT(DISTINCT th.OrderID)                   AS Conversions,

    /* Raw weighted score */
    (COUNT(DISTINCT o.JobID) * 1)
  + (COUNT(DISTINCT c.JobID) * 3)
  + (COUNT(DISTINCT th.OrderID) * 5)             AS RawScore,

    /* Normalized to 0-100 scale.
       Max assumed: 15 opens (15) + 8 clicks (24) + 3 conversions (15) = 54
       Adjust the divisor based on your actual data distribution. */
    CASE
        WHEN (
            (COUNT(DISTINCT o.JobID) * 1)
          + (COUNT(DISTINCT c.JobID) * 3)
          + (COUNT(DISTINCT th.OrderID) * 5)
        ) * 100.0 / 54 > 100 THEN 100
        ELSE ROUND(
            (COUNT(DISTINCT o.JobID) * 1)
          + (COUNT(DISTINCT c.JobID) * 3)
          + (COUNT(DISTINCT th.OrderID) * 5)
          * 100.0 / 54, 1)
    END                                          AS EngagementScore,

    /* Tier assignment based on score */
    CASE
        WHEN (COUNT(DISTINCT o.JobID) * 1)
           + (COUNT(DISTINCT c.JobID) * 3)
           + (COUNT(DISTINCT th.OrderID) * 5) >= 40 THEN 'Platinum'
        WHEN (COUNT(DISTINCT o.JobID) * 1)
           + (COUNT(DISTINCT c.JobID) * 3)
           + (COUNT(DISTINCT th.OrderID) * 5) >= 20 THEN 'Gold'
        WHEN (COUNT(DISTINCT o.JobID) * 1)
           + (COUNT(DISTINCT c.JobID) * 3)
           + (COUNT(DISTINCT th.OrderID) * 5) >= 8  THEN 'Silver'
        WHEN (COUNT(DISTINCT o.JobID) * 1)
           + (COUNT(DISTINCT c.JobID) * 3)
           + (COUNT(DISTINCT th.OrderID) * 5) >= 1  THEN 'Bronze'
        ELSE 'Disengaged'
    END                                          AS EngagementTier

FROM
    _Subscribers AS s
    LEFT JOIN _Sent AS snt
        ON s.SubscriberKey = snt.SubscriberKey
        AND snt.EventDate >= DATEADD(DAY, -90, GETDATE())
    LEFT JOIN _Open AS o
        ON s.SubscriberKey = o.SubscriberKey
        AND o.EventDate >= DATEADD(DAY, -90, GETDATE())
        AND o.IsUnique = 1
    LEFT JOIN _Click AS c
        ON s.SubscriberKey = c.SubscriberKey
        AND c.EventDate >= DATEADD(DAY, -90, GETDATE())
        AND c.IsUnique = 1
    LEFT JOIN TransactionHistory AS th
        ON s.SubscriberKey = th.SubscriberKey
        AND th.PurchaseDate >= DATEADD(DAY, -90, GETDATE())
        AND th.OrderStatus = 'Completed'
WHERE
    s.Status = 'Active'
GROUP BY
    s.SubscriberKey,
    s.EmailAddress,
    s.FirstName,
    s.LastName
ORDER BY
    RawScore DESC

/*
============================================================
  EXPECTED SAMPLE OUTPUT
============================================================
| SubscriberKey | EmailAddress         | FirstName | LastName | EmailsSent | UniqueOpens | UniqueClicks | Conversions | RawScore | EngagementScore | EngagementTier |
|---------------|----------------------|-----------|----------|------------|-------------|--------------|-------------|----------|-----------------|----------------|
| SK-10042      | star@example.com     | Jane      | Doe      | 24         | 14          | 7            | 3           | 50       | 92.6            | Platinum       |
| SK-20318      | solid@example.com    | Mark      | Lee      | 24         | 10          | 5            | 1           | 30       | 55.6            | Gold           |
| SK-30491      | casual@example.com   | Amy       | Torres   | 24         | 6           | 2            | 0           | 12       | 22.2            | Silver         |
| SK-40822      | quiet@example.com    | Brian     | Shah     | 24         | 3           | 0            | 0           | 3        | 5.6             | Bronze         |
| SK-55900      | silent@example.com   | Carol     | Wu       | 24         | 0           | 0            | 0           | 0        | 0.0             | Disengaged     |
============================================================
*/
