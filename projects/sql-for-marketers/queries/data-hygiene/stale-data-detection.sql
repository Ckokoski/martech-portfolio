/*
============================================================
  Query Name:   Stale Data Detection (12+ Months Unchanged)
  Category:     Data Hygiene
  Purpose:      Identify subscriber records where key profile
                fields have not been updated in over 12 months.
                Stale data leads to inaccurate personalization,
                bad segmentation, and wasted resources targeting
                people whose circumstances have changed.
  Use Case:     - Trigger a profile update campaign asking
                  subscribers to refresh their info
                - Prioritize records for data enrichment
                - Measure data freshness as a quality KPI
                - Identify integration issues (fields that
                  should auto-update but are not)
  Platform:     Salesforce Marketing Cloud (SFMC) Query Activity
  Tables Used:  _Subscribers, SubscriberMaster
  Notes:        - SubscriberMaster.LastModifiedDate tracks the
                  last time the record was updated from any
                  source (API, import, preference center).
                - Adjust the 12-month threshold based on your
                  data model and business needs.
============================================================
*/

SELECT
    s.SubscriberKey,
    s.EmailAddress,
    s.FirstName,
    s.LastName,
    s.DateJoined,
    sm.LastModifiedDate,
    DATEDIFF(DAY, sm.LastModifiedDate, GETDATE())    AS DaysSinceUpdate,
    DATEDIFF(MONTH, sm.LastModifiedDate, GETDATE())  AS MonthsSinceUpdate,

    /* --- Stale Field Inventory ---
       Check which specific fields are likely outdated */
    CASE WHEN sm.Phone IS NULL OR sm.Phone = ''
         THEN 'Missing' ELSE 'Present' END          AS PhoneStatus,
    CASE WHEN sm.City IS NULL OR sm.City = ''
         THEN 'Missing' ELSE 'Present' END           AS CityStatus,
    CASE WHEN sm.State IS NULL OR sm.State = ''
         THEN 'Missing' ELSE 'Present' END           AS StateStatus,
    CASE WHEN sm.Company IS NULL OR sm.Company = ''
         THEN 'Missing' ELSE 'Present' END           AS CompanyStatus,
    CASE WHEN sm.JobTitle IS NULL OR sm.JobTitle = ''
         THEN 'Missing' ELSE 'Present' END           AS JobTitleStatus,

    /* --- Staleness Classification --- */
    CASE
        WHEN sm.LastModifiedDate IS NULL
            THEN 'Never Updated After Import'
        WHEN DATEDIFF(MONTH, sm.LastModifiedDate, GETDATE()) > 24
            THEN 'Critically Stale (24+ months)'
        WHEN DATEDIFF(MONTH, sm.LastModifiedDate, GETDATE()) > 12
            THEN 'Stale (12-24 months)'
        WHEN DATEDIFF(MONTH, sm.LastModifiedDate, GETDATE()) > 6
            THEN 'Aging (6-12 months)'
        ELSE 'Current (< 6 months)'
    END                                              AS StalenessLevel

FROM
    _Subscribers AS s
    LEFT JOIN SubscriberMaster AS sm
        ON s.SubscriberKey = sm.SubscriberKey
WHERE
    s.Status = 'Active'
    AND (
        sm.LastModifiedDate IS NULL
        OR sm.LastModifiedDate < DATEADD(MONTH, -12, GETDATE())
    )
ORDER BY
    sm.LastModifiedDate ASC

/*
============================================================
  EXPECTED SAMPLE OUTPUT
============================================================
| SubscriberKey | EmailAddress          | FirstName | LastName | DateJoined | LastModifiedDate | DaysSinceUpdate | MonthsSinceUpdate | PhoneStatus | CityStatus | StateStatus | CompanyStatus | JobTitleStatus | StalenessLevel              |
|---------------|-----------------------|-----------|----------|------------|------------------|-----------------|-------------------|-------------|------------|-------------|---------------|----------------|-----------------------------|
| SK-15100      | old1@example.com      | Pat       | Harris   | 2022-05-10 | NULL             | NULL            | NULL              | Missing     | Missing    | Missing     | Missing       | Missing        | Never Updated After Import  |
| SK-22300      | old2@example.com      | Sam       | Rivera   | 2022-08-15 | 2023-01-20       | 1149            | 38                | Present     | Present    | Present     | Missing       | Missing        | Critically Stale (24+ mo)   |
| SK-31500      | old3@example.com      | Lee       | Chung    | 2023-06-01 | 2024-09-10       | 551             | 18                | Missing     | Present    | Present     | Present       | Present        | Stale (12-24 months)        |
| SK-42100      | old4@example.com      | Robin     | West     | 2024-01-20 | 2025-02-28       | 379             | 12                | Present     | Missing    | Missing     | Present       | Missing        | Stale (12-24 months)        |
============================================================
*/
