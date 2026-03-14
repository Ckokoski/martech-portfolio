/*
============================================================
  Query Name:   Consent and Compliance Check (GDPR / CAN-SPAM)
  Category:     Data Hygiene
  Purpose:      Audit subscriber records for proper consent
                documentation. Identifies contacts missing
                consent timestamps, opt-in source records, or
                whose consent may have expired under GDPR's
                "freshness" expectation.
  Use Case:     - Pre-audit preparation for GDPR or privacy
                  compliance reviews
                - Identify contacts who should not be mailed
                  due to missing consent proof
                - Verify that consent collection processes are
                  working correctly
                - Generate a compliance-ready consent report
  Platform:     Salesforce Marketing Cloud (SFMC) Query Activity
  Tables Used:  _Subscribers, SubscriberMaster, ConsentLog
                (custom DE tracking consent events)
  Notes:        - ConsentLog is a custom data extension that
                  records each consent event (opt-in, opt-out,
                  consent renewal) with a timestamp and source.
                - GDPR does not specify a consent expiration,
                  but best practice is to re-confirm consent
                  every 12-24 months.
                - CAN-SPAM requires an opt-out mechanism but
                  does not require explicit opt-in (implied
                  consent is acceptable in the US).
============================================================
*/

SELECT
    s.SubscriberKey,
    s.EmailAddress,
    s.FirstName,
    s.LastName,
    s.DateJoined,
    s.Status,
    sm.Country,

    /* --- Consent Record Details --- */
    cl.ConsentType,
    cl.ConsentSource,
    cl.ConsentTimestamp,
    cl.IPAddress                                     AS ConsentIP,

    /* --- Consent Age --- */
    DATEDIFF(DAY, cl.ConsentTimestamp, GETDATE())    AS DaysSinceConsent,
    DATEDIFF(MONTH, cl.ConsentTimestamp, GETDATE())  AS MonthsSinceConsent,

    /* --- Compliance Flags --- */
    CASE
        WHEN cl.ConsentTimestamp IS NULL
            THEN 'NO CONSENT RECORD'
        WHEN cl.ConsentType = 'Explicit Opt-In'
         AND cl.ConsentTimestamp IS NOT NULL
         AND DATEDIFF(MONTH, cl.ConsentTimestamp, GETDATE()) <= 24
            THEN 'COMPLIANT'
        WHEN cl.ConsentType = 'Explicit Opt-In'
         AND DATEDIFF(MONTH, cl.ConsentTimestamp, GETDATE()) > 24
            THEN 'CONSENT STALE (24+ months)'
        WHEN cl.ConsentType = 'Implied'
         AND sm.Country IN ('US', 'CA')
            THEN 'COMPLIANT (Implied - CAN-SPAM/CASL)'
        WHEN cl.ConsentType = 'Implied'
         AND sm.Country NOT IN ('US', 'CA')
            THEN 'NON-COMPLIANT (GDPR requires explicit)'
        WHEN cl.ConsentType = 'Single Opt-In'
            THEN 'REVIEW (Consider Double Opt-In)'
        ELSE 'REVIEW'
    END                                              AS ComplianceStatus,

    /* --- Recommended Action --- */
    CASE
        WHEN cl.ConsentTimestamp IS NULL
            THEN 'Suppress until consent is obtained'
        WHEN cl.ConsentType = 'Implied'
         AND sm.Country NOT IN ('US', 'CA')
            THEN 'Suppress and request explicit consent'
        WHEN DATEDIFF(MONTH, cl.ConsentTimestamp, GETDATE()) > 24
            THEN 'Send consent renewal campaign'
        WHEN DATEDIFF(MONTH, cl.ConsentTimestamp, GETDATE()) > 18
            THEN 'Queue for upcoming consent renewal'
        ELSE 'No action needed'
    END                                              AS RecommendedAction

FROM
    _Subscribers AS s
    LEFT JOIN SubscriberMaster AS sm
        ON s.SubscriberKey = sm.SubscriberKey
    LEFT JOIN ConsentLog AS cl
        ON s.SubscriberKey = cl.SubscriberKey
        AND cl.ConsentTimestamp = (
            SELECT MAX(cl2.ConsentTimestamp)
            FROM ConsentLog AS cl2
            WHERE cl2.SubscriberKey = s.SubscriberKey
        )
WHERE
    s.Status = 'Active'
ORDER BY
    CASE
        WHEN cl.ConsentTimestamp IS NULL THEN 1
        WHEN cl.ConsentType = 'Implied'
         AND sm.Country NOT IN ('US', 'CA') THEN 2
        WHEN DATEDIFF(MONTH, cl.ConsentTimestamp, GETDATE()) > 24 THEN 3
        ELSE 4
    END,
    cl.ConsentTimestamp ASC

/*
============================================================
  EXPECTED SAMPLE OUTPUT
============================================================
| SubscriberKey | EmailAddress          | FirstName | LastName | DateJoined | Status | Country | ConsentType      | ConsentSource    | ConsentTimestamp | ConsentIP     | DaysSinceConsent | MonthsSinceConsent | ComplianceStatus                    | RecommendedAction                  |
|---------------|-----------------------|-----------|----------|------------|--------|---------|------------------|------------------|-----------------|---------------|------------------|--------------------|-------------------------------------|------------------------------------|
| SK-90100      | noconsent@example.com | Pat       | Reed     | 2024-05-10 | Active | US      | NULL             | NULL             | NULL            | NULL          | NULL             | NULL               | NO CONSENT RECORD                   | Suppress until consent is obtained |
| SK-90215      | euuser@example.com    | Hans      | Muller   | 2024-08-15 | Active | DE      | Implied          | Website Visit    | 2024-08-15      | 192.168.1.100 | 577              | 19                 | NON-COMPLIANT (GDPR requires expl) | Suppress and request explicit      |
| SK-90320      | stale@example.com     | Jane      | Doe      | 2022-01-20 | Active | US      | Explicit Opt-In  | Signup Form      | 2023-06-10      | 10.0.0.55     | 1008             | 33                 | CONSENT STALE (24+ months)          | Send consent renewal campaign      |
| SK-90411      | usimplied@example.com | Bob       | Smith    | 2025-06-01 | Active | US      | Implied          | Checkout Optin   | 2025-06-01      | 172.16.0.22   | 286              | 9                  | COMPLIANT (Implied - CAN-SPAM)      | No action needed                   |
| SK-90550      | fresh@example.com     | Amy       | Torres   | 2026-01-15 | Active | UK      | Explicit Opt-In  | Double Opt-In    | 2026-01-15      | 203.0.113.50  | 58               | 2                  | COMPLIANT                           | No action needed                   |
============================================================
*/
