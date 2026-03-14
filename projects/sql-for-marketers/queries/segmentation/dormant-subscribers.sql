/*
============================================================
  Query Name:   Dormant Subscribers (180+ Days Inactive)
  Category:     Segmentation
  Purpose:      Find subscribers who have NOT opened or clicked
                any email in the past 180 days. These contacts
                are dragging down engagement metrics and may
                hurt sender reputation if mailed regularly.
  Use Case:     Feed this segment into a re-engagement campaign
                (win-back series) or suppress them from regular
                sends. After a final re-engagement attempt,
                dormant contacts should be moved to a sunset
                suppression list.
  Platform:     Salesforce Marketing Cloud (SFMC) Query Activity
  Tables Used:  _Subscribers, _Open, _Click, _Sent
  Notes:        - This query also checks that the subscriber
                  WAS mailed during the window, so we only flag
                  contacts who had the opportunity to engage.
                - Adjust 180 days based on your sales cycle.
============================================================
*/

SELECT
    s.SubscriberKey,
    s.EmailAddress,
    s.FirstName,
    s.LastName,
    s.DateJoined,
    MAX(o.EventDate)                    AS LastOpenDate,
    MAX(c.EventDate)                    AS LastClickDate,
    MAX(snt.EventDate)                  AS LastSentDate,
    COUNT(DISTINCT snt.JobID)           AS EmailsSent180d,
    DATEDIFF(DAY, MAX(o.EventDate), GETDATE())  AS DaysSinceLastOpen,
    DATEDIFF(DAY, MAX(c.EventDate), GETDATE())  AS DaysSinceLastClick,
    CASE
        WHEN MAX(o.EventDate) IS NULL
         AND MAX(c.EventDate) IS NULL   THEN 'Never Engaged'
        WHEN DATEDIFF(DAY, MAX(o.EventDate), GETDATE()) > 365
                                        THEN 'Dormant 12+ Months'
        ELSE 'Dormant 6-12 Months'
    END                                 AS DormancyTier
FROM
    _Subscribers AS s
    INNER JOIN _Sent AS snt
        ON s.SubscriberKey = snt.SubscriberKey
        AND snt.EventDate >= DATEADD(DAY, -180, GETDATE())
    LEFT JOIN _Open AS o
        ON s.SubscriberKey = o.SubscriberKey
        AND o.IsUnique = 1
    LEFT JOIN _Click AS c
        ON s.SubscriberKey = c.SubscriberKey
        AND c.IsUnique = 1
WHERE
    s.Status = 'Active'
GROUP BY
    s.SubscriberKey,
    s.EmailAddress,
    s.FirstName,
    s.LastName,
    s.DateJoined
HAVING
    (MAX(o.EventDate) IS NULL OR MAX(o.EventDate) < DATEADD(DAY, -180, GETDATE()))
    AND (MAX(c.EventDate) IS NULL OR MAX(c.EventDate) < DATEADD(DAY, -180, GETDATE()))
ORDER BY
    DaysSinceLastOpen DESC

/*
============================================================
  EXPECTED SAMPLE OUTPUT
============================================================
| SubscriberKey | EmailAddress          | FirstName | LastName | DateJoined | LastOpenDate | LastClickDate | LastSentDate | EmailsSent180d | DaysSinceLastOpen | DaysSinceLastClick | DormancyTier         |
|---------------|-----------------------|-----------|----------|------------|--------------|---------------|--------------|----------------|-------------------|--------------------|----------------------|
| SK-88120      | ghost@example.com     | Pat       | Taylor   | 2023-06-01 | NULL         | NULL          | 2026-03-01   | 22             | NULL              | NULL               | Never Engaged        |
| SK-72415      | olduser@example.com   | Sam       | Brown    | 2022-11-15 | 2024-08-10   | 2024-07-22    | 2026-02-28   | 18             | 582               | 601                | Dormant 12+ Months   |
| SK-61003      | fading@example.com    | Lou       | Garcia   | 2024-01-20 | 2025-07-15   | 2025-06-30    | 2026-03-05   | 15             | 242               | 257                | Dormant 6-12 Months  |
============================================================
*/
