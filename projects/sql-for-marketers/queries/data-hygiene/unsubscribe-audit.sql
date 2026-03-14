/*
============================================================
  Query Name:   Unsubscribe Processing Audit
  Category:     Data Hygiene
  Purpose:      Verify that all unsubscribe requests have been
                properly processed and that no unsubscribed
                contacts are still receiving emails. This is
                critical for CAN-SPAM and GDPR compliance.
  Use Case:     - Compliance audit (CAN-SPAM requires processing
                  within 10 business days)
                - Identify gaps in unsubscribe automation
                - Verify that unsubscribed contacts are not in
                  active send data extensions
                - Protect against legal risk and complaints
  Platform:     Salesforce Marketing Cloud (SFMC) Query Activity
  Tables Used:  _Subscribers, _Unsubscribe, _Sent
  Notes:        - SFMC automatically sets subscriber status to
                  "Unsubscribed" when processed through the
                  standard unsub mechanism. This query catches
                  cases where manual imports or custom processes
                  may have circumvented the standard flow.
============================================================
*/

/* --- Part 1: Unsubscribes Still Receiving Email ---
   These are compliance violations that need immediate attention. */
SELECT
    u.SubscriberKey,
    s.EmailAddress,
    s.FirstName,
    s.LastName,
    s.Status                                         AS CurrentStatus,
    u.EventDate                                      AS UnsubscribeDate,
    MAX(snt.EventDate)                               AS LastSentAfterUnsub,
    DATEDIFF(DAY, u.EventDate, MAX(snt.EventDate))  AS DaysBetweenUnsubAndSend,
    COUNT(DISTINCT snt.JobID)                        AS EmailsSentAfterUnsub,
    'COMPLIANCE VIOLATION'                           AS AuditFlag

FROM
    _Unsubscribe AS u
    INNER JOIN _Subscribers AS s
        ON u.SubscriberKey = s.SubscriberKey
    INNER JOIN _Sent AS snt
        ON u.SubscriberKey = snt.SubscriberKey
        AND snt.EventDate > u.EventDate
WHERE
    u.EventDate >= DATEADD(DAY, -90, GETDATE())
GROUP BY
    u.SubscriberKey,
    s.EmailAddress,
    s.FirstName,
    s.LastName,
    s.Status,
    u.EventDate
HAVING
    COUNT(DISTINCT snt.JobID) > 0

UNION ALL

/* --- Part 2: Unsubscribed but Status Not Updated ---
   Contacts who unsubscribed but whose Status field
   was not changed (possible automation gap). */
SELECT
    u.SubscriberKey,
    s.EmailAddress,
    s.FirstName,
    s.LastName,
    s.Status                                         AS CurrentStatus,
    MAX(u.EventDate)                                 AS UnsubscribeDate,
    NULL                                             AS LastSentAfterUnsub,
    NULL                                             AS DaysBetweenUnsubAndSend,
    0                                                AS EmailsSentAfterUnsub,
    'STATUS NOT UPDATED'                             AS AuditFlag

FROM
    _Unsubscribe AS u
    INNER JOIN _Subscribers AS s
        ON u.SubscriberKey = s.SubscriberKey
WHERE
    s.Status = 'Active'
    AND u.EventDate >= DATEADD(DAY, -90, GETDATE())
GROUP BY
    u.SubscriberKey,
    s.EmailAddress,
    s.FirstName,
    s.LastName,
    s.Status

ORDER BY
    AuditFlag,
    UnsubscribeDate DESC

/*
============================================================
  EXPECTED SAMPLE OUTPUT
============================================================
| SubscriberKey | EmailAddress          | FirstName | LastName | CurrentStatus | UnsubscribeDate | LastSentAfterUnsub | DaysBetweenUnsubAndSend | EmailsSentAfterUnsub | AuditFlag              |
|---------------|-----------------------|-----------|----------|---------------|-----------------|---------------------|-------------------------|----------------------|------------------------|
| SK-70100      | unsub1@example.com    | Robin     | Lake     | Active        | 2026-02-15      | 2026-03-10          | 23                      | 3                    | COMPLIANCE VIOLATION   |
| SK-70215      | unsub2@example.com    | Casey     | Ford     | Unsubscribed  | 2026-02-20      | 2026-02-22          | 2                       | 1                    | COMPLIANCE VIOLATION   |
| SK-70320      | unsub3@example.com    | Morgan    | Bell     | Active        | 2026-03-05      | NULL                | NULL                    | 0                    | STATUS NOT UPDATED     |
| SK-70411      | unsub4@example.com    | Drew      | Stone    | Active        | 2026-03-08      | NULL                | NULL                    | 0                    | STATUS NOT UPDATED     |
============================================================
*/
