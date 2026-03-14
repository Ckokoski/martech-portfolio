/*
============================================================
  Query Name:   Bounce Management and Suppression
  Category:     Data Hygiene
  Purpose:      Identify hard bounces and chronic soft bouncers
                for suppression. Continuing to send to bouncing
                addresses is the fastest way to damage sender
                reputation and land in spam folders.
  Use Case:     - Build a suppression data extension for hard
                  bounces
                - Identify chronic soft bouncers (3+ soft bounces)
                  for removal
                - Monitor bounce rates by domain to catch
                  deliverability issues early
                - Feed into a daily/weekly automation to keep
                  lists clean
  Platform:     Salesforce Marketing Cloud (SFMC) Query Activity
  Tables Used:  _Subscribers, _Bounce, _Sent
  Notes:        - SFMC BounceCategory values:
                  1 = Hard Bounce, 2 = Soft Bounce, 3 = Block
                - Hard bounces should be suppressed immediately.
                - Soft bounces become a problem after 3+
                  consecutive occurrences.
============================================================
*/

/* --- Hard Bounces: Immediate Suppression Candidates --- */
SELECT
    s.SubscriberKey,
    s.EmailAddress,
    s.FirstName,
    s.LastName,
    b.BounceCategory,
    CASE b.BounceCategory
        WHEN 1 THEN 'Hard Bounce'
        WHEN 2 THEN 'Soft Bounce'
        WHEN 3 THEN 'Block Bounce'
        ELSE 'Unknown'
    END                                              AS BounceType,
    b.SMTPBounceReason,
    b.EventDate                                      AS BounceDate,
    COUNT(*) OVER (
        PARTITION BY s.SubscriberKey
    )                                                AS TotalBounces,

    /* Domain extraction for domain-level analysis */
    SUBSTRING(
        s.EmailAddress,
        CHARINDEX('@', s.EmailAddress) + 1,
        LEN(s.EmailAddress)
    )                                                AS EmailDomain,

    /* Suppression recommendation */
    CASE
        WHEN b.BounceCategory = 1
            THEN 'SUPPRESS - Hard Bounce'
        WHEN b.BounceCategory = 3
            THEN 'INVESTIGATE - Block Bounce'
        WHEN b.BounceCategory = 2
         AND COUNT(*) OVER (PARTITION BY s.SubscriberKey) >= 3
            THEN 'SUPPRESS - Chronic Soft Bounce'
        WHEN b.BounceCategory = 2
            THEN 'MONITOR - Soft Bounce'
        ELSE 'REVIEW'
    END                                              AS SuppressionAction

FROM
    _Bounce AS b
    INNER JOIN _Subscribers AS s
        ON b.SubscriberKey = s.SubscriberKey
WHERE
    b.EventDate >= DATEADD(DAY, -90, GETDATE())
    AND s.Status = 'Active'
ORDER BY
    b.BounceCategory ASC,
    b.EventDate DESC

/*
------------------------------------------------------------
  BONUS: Bounce Rate by Domain
  Use this to detect domain-level deliverability problems.
------------------------------------------------------------

SELECT
    SUBSTRING(s.EmailAddress, CHARINDEX('@', s.EmailAddress) + 1, LEN(s.EmailAddress)) AS EmailDomain,
    COUNT(DISTINCT snt.SubscriberKey) AS TotalSent,
    COUNT(DISTINCT b.SubscriberKey) AS TotalBounced,
    ROUND(
        COUNT(DISTINCT b.SubscriberKey) * 100.0
        / NULLIF(COUNT(DISTINCT snt.SubscriberKey), 0), 2
    ) AS BounceRate
FROM _Sent AS snt
INNER JOIN _Subscribers AS s ON snt.SubscriberKey = s.SubscriberKey
LEFT JOIN _Bounce AS b ON snt.JobID = b.JobID AND snt.SubscriberKey = b.SubscriberKey
WHERE snt.EventDate >= DATEADD(DAY, -30, GETDATE())
GROUP BY SUBSTRING(s.EmailAddress, CHARINDEX('@', s.EmailAddress) + 1, LEN(s.EmailAddress))
HAVING COUNT(DISTINCT snt.SubscriberKey) >= 100
ORDER BY BounceRate DESC
*/

/*
============================================================
  EXPECTED SAMPLE OUTPUT
============================================================
| SubscriberKey | EmailAddress            | FirstName | LastName | BounceCategory | BounceType   | SMTPBounceReason                | BounceDate | TotalBounces | EmailDomain    | SuppressionAction         |
|---------------|-------------------------|-----------|----------|----------------|--------------|----------------------------------|------------|--------------|----------------|---------------------------|
| SK-60100      | gone@olddomain.com      | Pat       | Reed     | 1              | Hard Bounce  | 550 User unknown                 | 2026-03-12 | 1            | olddomain.com  | SUPPRESS - Hard Bounce    |
| SK-60215      | invalid@nowhere.net     | Sam       | Diaz     | 1              | Hard Bounce  | 550 Mailbox not found            | 2026-03-10 | 2            | nowhere.net    | SUPPRESS - Hard Bounce    |
| SK-60320      | full@example.org        | Lee       | Chang    | 2              | Soft Bounce  | 452 Mailbox full                 | 2026-03-08 | 4            | example.org    | SUPPRESS - Chronic Soft   |
| SK-60411      | blocked@corp.com        | Kim       | Novak    | 3              | Block Bounce | 554 Message rejected by policy   | 2026-03-05 | 1            | corp.com       | INVESTIGATE - Block       |
| SK-60550      | temp@provider.com       | Alex      | Wu       | 2              | Soft Bounce  | 451 Temporary service error      | 2026-03-01 | 1            | provider.com   | MONITOR - Soft Bounce     |
============================================================
*/
