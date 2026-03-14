/*
============================================================
  Query Name:   Subject Line Performance Analysis
  Category:     Campaign Reporting
  Purpose:      Analyze open rates and engagement by subject
                line characteristics — length, use of
                personalization, emoji, urgency words, and
                question marks. Reveals which copywriting
                patterns work best for your audience.
  Use Case:     - Inform subject line best practices
                - Build a subject line playbook for copywriters
                - Support A/B test hypothesis generation
                - Track subject line trends over time
  Platform:     Salesforce Marketing Cloud (SFMC) Query Activity
  Tables Used:  _Job, _Sent, _Open, _Click, _Bounce
  Notes:        - Subject line analysis is done via string
                  functions (LEN, CHARINDEX, LIKE).
                - SFMC SQL supports standard string functions.
                - Run this quarterly for enough data to be
                  statistically meaningful.
============================================================
*/

SELECT
    j.JobID,
    j.EmailName,
    j.EmailSubject,
    j.DeliveredTime                                      AS SendDate,
    LEN(j.EmailSubject)                                  AS SubjectLength,

    /* --- Subject Line Characteristics --- */
    CASE
        WHEN LEN(j.EmailSubject) <= 30                   THEN 'Short (1-30)'
        WHEN LEN(j.EmailSubject) <= 50                   THEN 'Medium (31-50)'
        WHEN LEN(j.EmailSubject) <= 70                   THEN 'Long (51-70)'
        ELSE 'Very Long (71+)'
    END                                                  AS LengthCategory,

    CASE
        WHEN j.EmailSubject LIKE '%%%First_Name%%%'
          OR j.EmailSubject LIKE '%{FirstName}%'         THEN 'Yes'
        ELSE 'No'
    END                                                  AS HasPersonalization,

    CASE
        WHEN j.EmailSubject LIKE '%?%'                   THEN 'Yes'
        ELSE 'No'
    END                                                  AS HasQuestion,

    CASE
        WHEN j.EmailSubject LIKE '%last chance%'
          OR j.EmailSubject LIKE '%hurry%'
          OR j.EmailSubject LIKE '%limited time%'
          OR j.EmailSubject LIKE '%ending soon%'
          OR j.EmailSubject LIKE '%don''t miss%'
          OR j.EmailSubject LIKE '%urgent%'              THEN 'Yes'
        ELSE 'No'
    END                                                  AS HasUrgency,

    CASE
        WHEN j.EmailSubject LIKE '%[0-9]%'              THEN 'Yes'
        ELSE 'No'
    END                                                  AS HasNumber,

    /* --- Performance Metrics --- */
    COUNT(DISTINCT snt.SubscriberKey)                    AS TotalSent,
    COUNT(DISTINCT snt.SubscriberKey)
      - COUNT(DISTINCT b.SubscriberKey)                  AS Delivered,
    COUNT(DISTINCT o.SubscriberKey)                      AS UniqueOpens,
    COUNT(DISTINCT c.SubscriberKey)                      AS UniqueClicks,

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
    END                                                  AS CTOR

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
    j.JobID,
    j.EmailName,
    j.EmailSubject,
    j.DeliveredTime
ORDER BY
    OpenRate DESC

/*
============================================================
  EXPECTED SAMPLE OUTPUT
============================================================
| JobID  | EmailName          | EmailSubject                          | SendDate   | SubjectLength | LengthCategory | HasPersonalization | HasQuestion | HasUrgency | HasNumber | TotalSent | Delivered | UniqueOpens | UniqueClicks | OpenRate | ClickRate | CTOR  |
|--------|--------------------|---------------------------------------|------------|---------------|----------------|--------------------|-------------|------------|-----------|-----------|-----------|-------------|--------------|----------|-----------|-------|
| 108501 | Welcome_V2         | Welcome! Here's your 20% off          | 2026-03-10 | 36            | Medium (31-50) | No                 | No          | No         | Yes       | 5000      | 4900      | 2450        | 735          | 50.00    | 15.00     | 30.00 |
| 108320 | Flash_Sale         | Last chance: Sale ends tonight         | 2026-03-03 | 36            | Medium (31-50) | No                 | No          | Yes        | No        | 50000     | 48500     | 16975       | 4365         | 35.00    | 9.00      | 25.71 |
| 108115 | Newsletter_Mar     | What's trending this week?             | 2026-02-28 | 32            | Medium (31-50) | No                 | Yes         | No         | No        | 45000     | 43650     | 10913       | 2183         | 25.00    | 5.00      | 20.00 |
| 108002 | Long_Subject_Test  | Everything you need to know about...   | 2026-02-20 | 72            | Very Long (71+)| No                 | No          | No         | No        | 40000     | 38800     | 7760        | 1164         | 20.00    | 3.00      | 15.00 |
============================================================
*/
