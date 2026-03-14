/*
============================================================
  Query Name:   Data Completeness Audit (Profile Scoring)
  Category:     Data Hygiene
  Purpose:      Score each subscriber profile on completeness
                by checking how many key fields are populated.
                Profiles with low completeness limit your ability
                to personalize, segment, and target effectively.
  Use Case:     - Identify which profiles need enrichment
                - Measure data completeness as a KPI (% of
                  profiles above a threshold)
                - Trigger progressive profiling campaigns for
                  incomplete records
                - Audit data quality after imports or migrations
  Platform:     Salesforce Marketing Cloud (SFMC) Query Activity
  Tables Used:  _Subscribers, SubscriberMaster
  Notes:        - Adjust the fields checked to match your data
                  model. The fields below are common marketing
                  profile attributes.
                - Each populated field adds points; score is
                  expressed as both points and a percentage.
============================================================
*/

SELECT
    s.SubscriberKey,
    s.EmailAddress,
    s.FirstName,
    s.LastName,

    /* --- Individual Field Checks (1 = populated, 0 = empty) --- */
    CASE WHEN s.FirstName IS NOT NULL AND s.FirstName <> ''
         THEN 1 ELSE 0 END                              AS Has_FirstName,
    CASE WHEN s.LastName IS NOT NULL AND s.LastName <> ''
         THEN 1 ELSE 0 END                              AS Has_LastName,
    CASE WHEN sm.Phone IS NOT NULL AND sm.Phone <> ''
         THEN 1 ELSE 0 END                              AS Has_Phone,
    CASE WHEN sm.Company IS NOT NULL AND sm.Company <> ''
         THEN 1 ELSE 0 END                              AS Has_Company,
    CASE WHEN sm.JobTitle IS NOT NULL AND sm.JobTitle <> ''
         THEN 1 ELSE 0 END                              AS Has_JobTitle,
    CASE WHEN sm.City IS NOT NULL AND sm.City <> ''
         THEN 1 ELSE 0 END                              AS Has_City,
    CASE WHEN sm.State IS NOT NULL AND sm.State <> ''
         THEN 1 ELSE 0 END                              AS Has_State,
    CASE WHEN sm.PostalCode IS NOT NULL AND sm.PostalCode <> ''
         THEN 1 ELSE 0 END                              AS Has_PostalCode,
    CASE WHEN sm.Country IS NOT NULL AND sm.Country <> ''
         THEN 1 ELSE 0 END                              AS Has_Country,
    CASE WHEN sm.DateOfBirth IS NOT NULL
         THEN 1 ELSE 0 END                              AS Has_DateOfBirth,

    /* --- Completeness Score (out of 10 fields) --- */
    (CASE WHEN s.FirstName IS NOT NULL AND s.FirstName <> '' THEN 1 ELSE 0 END
   + CASE WHEN s.LastName IS NOT NULL AND s.LastName <> '' THEN 1 ELSE 0 END
   + CASE WHEN sm.Phone IS NOT NULL AND sm.Phone <> '' THEN 1 ELSE 0 END
   + CASE WHEN sm.Company IS NOT NULL AND sm.Company <> '' THEN 1 ELSE 0 END
   + CASE WHEN sm.JobTitle IS NOT NULL AND sm.JobTitle <> '' THEN 1 ELSE 0 END
   + CASE WHEN sm.City IS NOT NULL AND sm.City <> '' THEN 1 ELSE 0 END
   + CASE WHEN sm.State IS NOT NULL AND sm.State <> '' THEN 1 ELSE 0 END
   + CASE WHEN sm.PostalCode IS NOT NULL AND sm.PostalCode <> '' THEN 1 ELSE 0 END
   + CASE WHEN sm.Country IS NOT NULL AND sm.Country <> '' THEN 1 ELSE 0 END
   + CASE WHEN sm.DateOfBirth IS NOT NULL THEN 1 ELSE 0 END
    )                                                    AS FieldsPopulated,

    /* --- Percentage Score --- */
    (CASE WHEN s.FirstName IS NOT NULL AND s.FirstName <> '' THEN 1 ELSE 0 END
   + CASE WHEN s.LastName IS NOT NULL AND s.LastName <> '' THEN 1 ELSE 0 END
   + CASE WHEN sm.Phone IS NOT NULL AND sm.Phone <> '' THEN 1 ELSE 0 END
   + CASE WHEN sm.Company IS NOT NULL AND sm.Company <> '' THEN 1 ELSE 0 END
   + CASE WHEN sm.JobTitle IS NOT NULL AND sm.JobTitle <> '' THEN 1 ELSE 0 END
   + CASE WHEN sm.City IS NOT NULL AND sm.City <> '' THEN 1 ELSE 0 END
   + CASE WHEN sm.State IS NOT NULL AND sm.State <> '' THEN 1 ELSE 0 END
   + CASE WHEN sm.PostalCode IS NOT NULL AND sm.PostalCode <> '' THEN 1 ELSE 0 END
   + CASE WHEN sm.Country IS NOT NULL AND sm.Country <> '' THEN 1 ELSE 0 END
   + CASE WHEN sm.DateOfBirth IS NOT NULL THEN 1 ELSE 0 END
    ) * 10                                               AS CompletenessPercent,

    /* --- Completeness Tier --- */
    CASE
        WHEN (CASE WHEN s.FirstName IS NOT NULL AND s.FirstName <> '' THEN 1 ELSE 0 END
            + CASE WHEN s.LastName IS NOT NULL AND s.LastName <> '' THEN 1 ELSE 0 END
            + CASE WHEN sm.Phone IS NOT NULL AND sm.Phone <> '' THEN 1 ELSE 0 END
            + CASE WHEN sm.Company IS NOT NULL AND sm.Company <> '' THEN 1 ELSE 0 END
            + CASE WHEN sm.JobTitle IS NOT NULL AND sm.JobTitle <> '' THEN 1 ELSE 0 END
            + CASE WHEN sm.City IS NOT NULL AND sm.City <> '' THEN 1 ELSE 0 END
            + CASE WHEN sm.State IS NOT NULL AND sm.State <> '' THEN 1 ELSE 0 END
            + CASE WHEN sm.PostalCode IS NOT NULL AND sm.PostalCode <> '' THEN 1 ELSE 0 END
            + CASE WHEN sm.Country IS NOT NULL AND sm.Country <> '' THEN 1 ELSE 0 END
            + CASE WHEN sm.DateOfBirth IS NOT NULL THEN 1 ELSE 0 END
            ) >= 9 THEN 'Complete (90-100%)'
        WHEN (CASE WHEN s.FirstName IS NOT NULL AND s.FirstName <> '' THEN 1 ELSE 0 END
            + CASE WHEN s.LastName IS NOT NULL AND s.LastName <> '' THEN 1 ELSE 0 END
            + CASE WHEN sm.Phone IS NOT NULL AND sm.Phone <> '' THEN 1 ELSE 0 END
            + CASE WHEN sm.Company IS NOT NULL AND sm.Company <> '' THEN 1 ELSE 0 END
            + CASE WHEN sm.JobTitle IS NOT NULL AND sm.JobTitle <> '' THEN 1 ELSE 0 END
            + CASE WHEN sm.City IS NOT NULL AND sm.City <> '' THEN 1 ELSE 0 END
            + CASE WHEN sm.State IS NOT NULL AND sm.State <> '' THEN 1 ELSE 0 END
            + CASE WHEN sm.PostalCode IS NOT NULL AND sm.PostalCode <> '' THEN 1 ELSE 0 END
            + CASE WHEN sm.Country IS NOT NULL AND sm.Country <> '' THEN 1 ELSE 0 END
            + CASE WHEN sm.DateOfBirth IS NOT NULL THEN 1 ELSE 0 END
            ) >= 6 THEN 'Good (60-80%)'
        WHEN (CASE WHEN s.FirstName IS NOT NULL AND s.FirstName <> '' THEN 1 ELSE 0 END
            + CASE WHEN s.LastName IS NOT NULL AND s.LastName <> '' THEN 1 ELSE 0 END
            + CASE WHEN sm.Phone IS NOT NULL AND sm.Phone <> '' THEN 1 ELSE 0 END
            + CASE WHEN sm.Company IS NOT NULL AND sm.Company <> '' THEN 1 ELSE 0 END
            + CASE WHEN sm.JobTitle IS NOT NULL AND sm.JobTitle <> '' THEN 1 ELSE 0 END
            + CASE WHEN sm.City IS NOT NULL AND sm.City <> '' THEN 1 ELSE 0 END
            + CASE WHEN sm.State IS NOT NULL AND sm.State <> '' THEN 1 ELSE 0 END
            + CASE WHEN sm.PostalCode IS NOT NULL AND sm.PostalCode <> '' THEN 1 ELSE 0 END
            + CASE WHEN sm.Country IS NOT NULL AND sm.Country <> '' THEN 1 ELSE 0 END
            + CASE WHEN sm.DateOfBirth IS NOT NULL THEN 1 ELSE 0 END
            ) >= 3 THEN 'Sparse (30-50%)'
        ELSE 'Minimal (0-20%)'
    END                                                  AS CompletenessTier

FROM
    _Subscribers AS s
    LEFT JOIN SubscriberMaster AS sm
        ON s.SubscriberKey = sm.SubscriberKey
WHERE
    s.Status = 'Active'
ORDER BY
    FieldsPopulated ASC

/*
============================================================
  EXPECTED SAMPLE OUTPUT
============================================================
| SubscriberKey | EmailAddress         | FirstName | LastName | Has_FirstName | Has_LastName | Has_Phone | Has_Company | Has_JobTitle | Has_City | Has_State | Has_PostalCode | Has_Country | Has_DateOfBirth | FieldsPopulated | CompletenessPercent | CompletenessTier |
|---------------|----------------------|-----------|----------|---------------|--------------|-----------|-------------|--------------|----------|-----------|----------------|-------------|-----------------|-----------------|---------------------|------------------|
| SK-85010      | bare@example.com     | NULL      | NULL     | 0             | 0            | 0         | 0           | 0            | 0        | 0         | 0              | 0           | 0               | 0               | 0                   | Minimal (0-20%)  |
| SK-85120      | half@example.com     | Jane      | Doe      | 1             | 1            | 0         | 1           | 0            | 0        | 0         | 0              | 1           | 0               | 4               | 40                  | Sparse (30-50%)  |
| SK-85230      | good@example.com     | Mark      | Lee      | 1             | 1            | 1         | 1           | 1            | 1        | 1         | 0              | 1           | 0               | 8               | 80                  | Good (60-80%)    |
| SK-85340      | full@example.com     | Amy       | Torres   | 1             | 1            | 1         | 1           | 1            | 1        | 1         | 1              | 1           | 1               | 10              | 100                 | Complete (90-100%)|
============================================================
*/
