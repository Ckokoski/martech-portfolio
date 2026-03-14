/*
============================================================
  Query Name:   Send Time Analysis
  Category:     Campaign Reporting
  Purpose:      Analyze email performance by send hour and
                day of week to identify optimal send windows.
                Aggregates open and click rates across all
                campaigns to find patterns.
  Use Case:     - Determine the best day/time to schedule sends
                - Support send-time optimization initiatives
                - Validate whether current send cadence aligns
                  with subscriber behavior
                - Build a data-backed send calendar
  Platform:     Salesforce Marketing Cloud (SFMC) Query Activity
  Tables Used:  _Job, _Sent, _Open, _Click, _Bounce
  Notes:        - SFMC stores event timestamps in the account's
                  configured timezone.
                - DATEPART returns integers: 1=Sunday, 7=Saturday
                  for day of week; 0-23 for hour.
                - Aggregate at least 30 days of data for
                  meaningful patterns.
============================================================
*/

SELECT
    DATEPART(WEEKDAY, j.DeliveredTime)                   AS SendDayNum,
    CASE DATEPART(WEEKDAY, j.DeliveredTime)
        WHEN 1 THEN 'Sunday'
        WHEN 2 THEN 'Monday'
        WHEN 3 THEN 'Tuesday'
        WHEN 4 THEN 'Wednesday'
        WHEN 5 THEN 'Thursday'
        WHEN 6 THEN 'Friday'
        WHEN 7 THEN 'Saturday'
    END                                                  AS SendDay,
    DATEPART(HOUR, j.DeliveredTime)                      AS SendHour,

    /* --- Volume --- */
    COUNT(DISTINCT j.JobID)                              AS CampaignCount,
    COUNT(DISTINCT snt.SubscriberKey)                    AS TotalSent,
    COUNT(DISTINCT snt.SubscriberKey)
      - COUNT(DISTINCT b.SubscriberKey)                  AS TotalDelivered,

    /* --- Engagement --- */
    COUNT(DISTINCT o.SubscriberKey)                      AS UniqueOpens,
    COUNT(DISTINCT c.SubscriberKey)                      AS UniqueClicks,

    /* --- Rates --- */
    CASE
        WHEN (COUNT(DISTINCT snt.SubscriberKey)
            - COUNT(DISTINCT b.SubscriberKey)) = 0 THEN 0
        ELSE ROUND(
            COUNT(DISTINCT o.SubscriberKey) * 100.0
            / (COUNT(DISTINCT snt.SubscriberKey)
             - COUNT(DISTINCT b.SubscriberKey)), 2)
    END                                                  AS AvgOpenRate,

    CASE
        WHEN (COUNT(DISTINCT snt.SubscriberKey)
            - COUNT(DISTINCT b.SubscriberKey)) = 0 THEN 0
        ELSE ROUND(
            COUNT(DISTINCT c.SubscriberKey) * 100.0
            / (COUNT(DISTINCT snt.SubscriberKey)
             - COUNT(DISTINCT b.SubscriberKey)), 2)
    END                                                  AS AvgClickRate,

    CASE
        WHEN COUNT(DISTINCT o.SubscriberKey) = 0 THEN 0
        ELSE ROUND(
            COUNT(DISTINCT c.SubscriberKey) * 100.0
            / COUNT(DISTINCT o.SubscriberKey), 2)
    END                                                  AS AvgCTOR

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
WHERE
    j.DeliveredTime >= DATEADD(DAY, -90, GETDATE())
GROUP BY
    DATEPART(WEEKDAY, j.DeliveredTime),
    DATEPART(HOUR, j.DeliveredTime)
HAVING
    COUNT(DISTINCT j.JobID) >= 2   /* Require at least 2 sends per slot */
ORDER BY
    AvgClickRate DESC,
    AvgOpenRate DESC

/*
============================================================
  EXPECTED SAMPLE OUTPUT
============================================================
| SendDayNum | SendDay   | SendHour | CampaignCount | TotalSent | TotalDelivered | UniqueOpens | UniqueClicks | AvgOpenRate | AvgClickRate | AvgCTOR |
|------------|-----------|----------|---------------|-----------|----------------|-------------|--------------|-------------|--------------|---------|
| 3          | Tuesday   | 10       | 8             | 120000    | 116400         | 37248       | 11640        | 32.00       | 10.00        | 31.25   |
| 5          | Thursday  | 14       | 6             | 95000     | 92150          | 27645       | 8294         | 30.00       | 9.00         | 30.00   |
| 4          | Wednesday | 9        | 5             | 80000     | 77600          | 21328       | 6208         | 27.48       | 8.00         | 29.11   |
| 2          | Monday    | 11       | 7             | 100000    | 97000          | 24250       | 5820         | 25.00       | 6.00         | 24.00   |
| 6          | Friday    | 15       | 4             | 60000     | 58200          | 11640       | 2910         | 20.00       | 5.00         | 25.00   |
============================================================
*/
