/*
============================================================
  Query Name:   Duplicate Subscriber Detection
  Category:     Data Hygiene
  Purpose:      Find duplicate subscriber records based on
                email address. Duplicates inflate list counts,
                cause over-mailing, and skew engagement metrics.
                This query identifies exact-match and near-match
                duplicates for review and deduplication.
  Use Case:     - Clean up subscriber lists before major campaigns
                - Merge duplicate records to create a single
                  source of truth
                - Prevent the same person from receiving
                  multiple copies of the same email
                - Improve reporting accuracy by eliminating
                  inflated counts
  Platform:     Salesforce Marketing Cloud (SFMC) Query Activity
  Tables Used:  _Subscribers, SubscriberMaster
  Notes:        - SFMC enforces unique SubscriberKeys, but
                  the same person can have multiple keys
                  (e.g., different email variations, re-imports).
                - This query checks for exact email matches
                  and also for duplicates after normalizing
                  the email (lowercased, trimmed).
============================================================
*/

/* --- Part 1: Exact Email Duplicates --- */
SELECT
    LOWER(LTRIM(RTRIM(s.EmailAddress)))              AS NormalizedEmail,
    COUNT(*)                                         AS DuplicateCount,
    MIN(s.SubscriberKey)                             AS FirstSubscriberKey,
    MAX(s.SubscriberKey)                             AS LatestSubscriberKey,
    MIN(s.DateJoined)                                AS EarliestJoinDate,
    MAX(s.DateJoined)                                AS LatestJoinDate
FROM
    _Subscribers AS s
WHERE
    s.Status = 'Active'
GROUP BY
    LOWER(LTRIM(RTRIM(s.EmailAddress)))
HAVING
    COUNT(*) > 1
ORDER BY
    DuplicateCount DESC

/*
------------------------------------------------------------
  Part 2: Detailed Duplicate Review
  Once you identify duplicate emails above, use this query
  to pull the full records for manual review before merging.
------------------------------------------------------------

SELECT
    s.SubscriberKey,
    s.EmailAddress,
    s.FirstName,
    s.LastName,
    s.DateJoined,
    s.Status,
    sm.SignupSource,
    sm.LastModifiedDate,
    (SELECT COUNT(DISTINCT o.JobID)
     FROM _Open AS o
     WHERE o.SubscriberKey = s.SubscriberKey) AS TotalOpens,
    (SELECT COUNT(DISTINCT c.JobID)
     FROM _Click AS c
     WHERE c.SubscriberKey = s.SubscriberKey) AS TotalClicks
FROM
    _Subscribers AS s
    LEFT JOIN SubscriberMaster AS sm
        ON s.SubscriberKey = sm.SubscriberKey
WHERE
    LOWER(LTRIM(RTRIM(s.EmailAddress))) IN (
        SELECT LOWER(LTRIM(RTRIM(s2.EmailAddress)))
        FROM _Subscribers AS s2
        WHERE s2.Status = 'Active'
        GROUP BY LOWER(LTRIM(RTRIM(s2.EmailAddress)))
        HAVING COUNT(*) > 1
    )
ORDER BY
    LOWER(s.EmailAddress),
    s.DateJoined ASC
*/

/*
============================================================
  EXPECTED SAMPLE OUTPUT (Part 1)
============================================================
| NormalizedEmail         | DuplicateCount | FirstSubscriberKey | LatestSubscriberKey | EarliestJoinDate | LatestJoinDate |
|-------------------------|----------------|--------------------|---------------------|------------------|----------------|
| jdoe@example.com        | 3              | SK-00101           | SK-45200            | 2023-01-15       | 2025-11-20     |
| m.smith@example.com     | 2              | SK-02340           | SK-38100            | 2024-03-10       | 2025-08-05     |
| amy.torres@example.com  | 2              | SK-05500           | SK-41000            | 2024-06-22       | 2025-12-01     |
============================================================
*/
