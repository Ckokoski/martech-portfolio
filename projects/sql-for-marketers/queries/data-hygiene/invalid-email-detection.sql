/*
============================================================
  Query Name:   Invalid Email Address Detection
  Category:     Data Hygiene
  Purpose:      Identify email addresses that are malformed,
                use disposable domains, contain typos in common
                domains, or have other format issues. Sending
                to invalid addresses wastes resources and hurts
                sender reputation.
  Use Case:     - Pre-send validation to remove bad addresses
                - Data quality audit for imported lists
                - Identify data entry or integration issues
                - Protect sender reputation and deliverability
  Platform:     Salesforce Marketing Cloud (SFMC) Query Activity
  Tables Used:  _Subscribers
  Notes:        - SFMC SQL supports LIKE, CHARINDEX, LEN, and
                  PATINDEX for pattern matching.
                - This query checks for common format issues
                  but is not a full RFC 5322 validator.
                - Extend the disposable domain list based on
                  your own experience.
============================================================
*/

SELECT
    s.SubscriberKey,
    s.EmailAddress,
    s.FirstName,
    s.LastName,
    s.DateJoined,

    /* --- Validation Issue Type --- */
    CASE
        /* Missing @ symbol */
        WHEN CHARINDEX('@', s.EmailAddress) = 0
            THEN 'Missing @ Symbol'

        /* Multiple @ symbols */
        WHEN LEN(s.EmailAddress) - LEN(REPLACE(s.EmailAddress, '@', '')) > 1
            THEN 'Multiple @ Symbols'

        /* No domain after @ */
        WHEN CHARINDEX('.', s.EmailAddress,
             CHARINDEX('@', s.EmailAddress)) = 0
            THEN 'Missing Domain Extension'

        /* Ends with a dot */
        WHEN RIGHT(LTRIM(RTRIM(s.EmailAddress)), 1) = '.'
            THEN 'Ends With Dot'

        /* Starts with a dot or @ */
        WHEN LEFT(LTRIM(RTRIM(s.EmailAddress)), 1) IN ('.', '@')
            THEN 'Starts With Invalid Character'

        /* Contains spaces */
        WHEN CHARINDEX(' ', LTRIM(RTRIM(s.EmailAddress))) > 0
            THEN 'Contains Spaces'

        /* Very short email (likely invalid) */
        WHEN LEN(LTRIM(RTRIM(s.EmailAddress))) < 6
            THEN 'Too Short'

        /* Common domain typos */
        WHEN s.EmailAddress LIKE '%@gmial.com'
          OR s.EmailAddress LIKE '%@gmal.com'
          OR s.EmailAddress LIKE '%@gamil.com'
          OR s.EmailAddress LIKE '%@gnail.com'
            THEN 'Likely Typo: Gmail'

        WHEN s.EmailAddress LIKE '%@yaho.com'
          OR s.EmailAddress LIKE '%@yahooo.com'
          OR s.EmailAddress LIKE '%@tahoo.com'
            THEN 'Likely Typo: Yahoo'

        WHEN s.EmailAddress LIKE '%@hotmal.com'
          OR s.EmailAddress LIKE '%@hotmial.com'
          OR s.EmailAddress LIKE '%@hotamil.com'
            THEN 'Likely Typo: Hotmail'

        WHEN s.EmailAddress LIKE '%@outlok.com'
          OR s.EmailAddress LIKE '%@outloo.com'
            THEN 'Likely Typo: Outlook'

        /* Known disposable / temporary email domains */
        WHEN s.EmailAddress LIKE '%@mailinator.com'
          OR s.EmailAddress LIKE '%@guerrillamail.com'
          OR s.EmailAddress LIKE '%@tempmail.com'
          OR s.EmailAddress LIKE '%@throwaway.email'
          OR s.EmailAddress LIKE '%@yopmail.com'
          OR s.EmailAddress LIKE '%@sharklasers.com'
            THEN 'Disposable Email Domain'

        /* Test/fake addresses */
        WHEN s.EmailAddress LIKE 'test@%'
          OR s.EmailAddress LIKE 'test%@test%'
          OR s.EmailAddress LIKE '%@example.com'
          OR s.EmailAddress LIKE '%@test.com'
          OR s.EmailAddress LIKE 'noreply@%'
          OR s.EmailAddress LIKE 'no-reply@%'
            THEN 'Test/Fake Address'

        ELSE 'Valid Format'
    END                                                  AS ValidationIssue

FROM
    _Subscribers AS s
WHERE
    s.Status = 'Active'
    AND (
        /* Filter to only return rows with issues */
        CHARINDEX('@', s.EmailAddress) = 0
        OR LEN(s.EmailAddress) - LEN(REPLACE(s.EmailAddress, '@', '')) > 1
        OR CHARINDEX('.', s.EmailAddress, CHARINDEX('@', s.EmailAddress)) = 0
        OR RIGHT(LTRIM(RTRIM(s.EmailAddress)), 1) = '.'
        OR LEFT(LTRIM(RTRIM(s.EmailAddress)), 1) IN ('.', '@')
        OR CHARINDEX(' ', LTRIM(RTRIM(s.EmailAddress))) > 0
        OR LEN(LTRIM(RTRIM(s.EmailAddress))) < 6
        OR s.EmailAddress LIKE '%@gmial.com'
        OR s.EmailAddress LIKE '%@gmal.com'
        OR s.EmailAddress LIKE '%@gamil.com'
        OR s.EmailAddress LIKE '%@gnail.com'
        OR s.EmailAddress LIKE '%@yaho.com'
        OR s.EmailAddress LIKE '%@yahooo.com'
        OR s.EmailAddress LIKE '%@tahoo.com'
        OR s.EmailAddress LIKE '%@hotmal.com'
        OR s.EmailAddress LIKE '%@hotmial.com'
        OR s.EmailAddress LIKE '%@hotamil.com'
        OR s.EmailAddress LIKE '%@outlok.com'
        OR s.EmailAddress LIKE '%@outloo.com'
        OR s.EmailAddress LIKE '%@mailinator.com'
        OR s.EmailAddress LIKE '%@guerrillamail.com'
        OR s.EmailAddress LIKE '%@tempmail.com'
        OR s.EmailAddress LIKE '%@throwaway.email'
        OR s.EmailAddress LIKE '%@yopmail.com'
        OR s.EmailAddress LIKE '%@sharklasers.com'
        OR s.EmailAddress LIKE 'test@%'
        OR s.EmailAddress LIKE 'test%@test%'
        OR s.EmailAddress LIKE '%@example.com'
        OR s.EmailAddress LIKE '%@test.com'
        OR s.EmailAddress LIKE 'noreply@%'
        OR s.EmailAddress LIKE 'no-reply@%'
    )
ORDER BY
    ValidationIssue,
    s.EmailAddress

/*
============================================================
  EXPECTED SAMPLE OUTPUT
============================================================
| SubscriberKey | EmailAddress            | FirstName | LastName | DateJoined | ValidationIssue       |
|---------------|-------------------------|-----------|----------|------------|-----------------------|
| SK-80100      | broken.email            | Pat       | NULL     | 2025-06-10 | Missing @ Symbol      |
| SK-80215      | user@ @domain.com       | Sam       | Reed     | 2025-08-22 | Multiple @ Symbols    |
| SK-80320      | jane@gmial.com          | Jane      | Porter   | 2025-09-15 | Likely Typo: Gmail    |
| SK-80411      | bob@yaho.com            | Bob       | Stone    | 2025-10-01 | Likely Typo: Yahoo    |
| SK-80550      | temp@mailinator.com     | NULL      | NULL     | 2026-01-05 | Disposable Email      |
| SK-80601      | test@test.com           | Test      | User     | 2026-02-14 | Test/Fake Address     |
| SK-80720      | has spaces@domain.com   | Lee       | Chang    | 2026-03-01 | Contains Spaces       |
============================================================
*/
