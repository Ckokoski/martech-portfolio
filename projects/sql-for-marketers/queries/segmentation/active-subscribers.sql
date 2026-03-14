/*
============================================================
  Query Name:   Active Subscribers (Last 90 Days)
  Category:     Segmentation
  Purpose:      Identify subscribers who have opened or clicked
                at least one email in the past 90 days. These
                are your healthiest, most engaged contacts and
                should be the primary audience for regular sends.
  Use Case:     Build a "safe send" list to protect deliverability.
                ISPs reward senders who mail engaged audiences,
                so starting with this segment reduces spam
                complaints and improves inbox placement.
  Platform:     Salesforce Marketing Cloud (SFMC) Query Activity
  Tables Used:  _Subscribers, _Open, _Click
  Notes:        - SFMC uses GETDATE() for current timestamp.
                - SFMC does not support CTEs; use subqueries
                  or temp data extensions instead.
                - Adjust the 90-day window to match your brand's
                  typical purchase/engagement cycle.
============================================================
*/

SELECT
    s.SubscriberKey,
    s.EmailAddress,
    s.FirstName,
    s.LastName,
    MAX(o.EventDate)                AS LastOpenDate,
    MAX(c.EventDate)                AS LastClickDate,
    COUNT(DISTINCT o.JobID)         AS OpensLast90d,
    COUNT(DISTINCT c.JobID)         AS ClicksLast90d,
    CASE
        WHEN COUNT(DISTINCT c.JobID) >= 3 THEN 'Highly Engaged'
        WHEN COUNT(DISTINCT c.JobID) >= 1 THEN 'Engaged - Clicker'
        WHEN COUNT(DISTINCT o.JobID) >= 3 THEN 'Engaged - Opener'
        ELSE 'Minimally Engaged'
    END                             AS EngagementTier
FROM
    _Subscribers AS s
    LEFT JOIN _Open AS o
        ON s.SubscriberKey = o.SubscriberKey
        AND o.EventDate >= DATEADD(DAY, -90, GETDATE())
        AND o.IsUnique = 1
    LEFT JOIN _Click AS c
        ON s.SubscriberKey = c.SubscriberKey
        AND c.EventDate >= DATEADD(DAY, -90, GETDATE())
        AND c.IsUnique = 1
WHERE
    s.Status = 'Active'
GROUP BY
    s.SubscriberKey,
    s.EmailAddress,
    s.FirstName,
    s.LastName
HAVING
    COUNT(DISTINCT o.JobID) > 0
    OR COUNT(DISTINCT c.JobID) > 0
ORDER BY
    ClicksLast90d DESC,
    OpensLast90d DESC

/*
============================================================
  EXPECTED SAMPLE OUTPUT
============================================================
| SubscriberKey | EmailAddress         | FirstName | LastName | LastOpenDate | LastClickDate | OpensLast90d | ClicksLast90d | EngagementTier    |
|---------------|----------------------|-----------|----------|--------------|---------------|--------------|----------------|-------------------|
| SK-10042      | jdoe@example.com     | Jane      | Doe      | 2026-03-12   | 2026-03-10    | 14           | 6              | Highly Engaged    |
| SK-20318      | msmith@example.com   | Mark      | Smith    | 2026-03-11   | 2026-03-05    | 9            | 3              | Highly Engaged    |
| SK-30491      | alee@example.com     | Amy       | Lee      | 2026-03-09   | 2026-02-28    | 7            | 2              | Engaged - Clicker |
| SK-40822      | bwilson@example.com  | Brian     | Wilson   | 2026-03-08   | NULL          | 11           | 0              | Engaged - Opener  |
| SK-51200      | cjones@example.com   | Carol     | Jones    | 2026-02-15   | NULL          | 2            | 0              | Minimally Engaged |
============================================================
*/
