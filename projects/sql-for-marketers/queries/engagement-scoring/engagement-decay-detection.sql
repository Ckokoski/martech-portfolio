/*
============================================================
  Query Name:   Engagement Decay Detection
  Category:     Engagement Scoring
  Purpose:      Identify subscribers whose engagement is
                actively declining by comparing their recent
                engagement rate to their historical baseline.
                These are your "at risk" contacts who need
                intervention before they lapse completely.
  Use Case:     - Trigger a re-engagement journey before full
                  lapse occurs
                - Alert account managers about high-value
                  contacts showing decay
                - Measure the effectiveness of retention programs
                  by monitoring decay rates over time
                - Proactively adjust send frequency for decaying
                  contacts to prevent unsubscribes
  Platform:     Salesforce Marketing Cloud (SFMC) Query Activity
  Tables Used:  _Subscribers, _Open, _Click, _Sent
  Notes:        - "Decay" is defined as a subscriber whose
                  engagement rate in the recent 30 days is
                  significantly lower than their 90-day average.
                - A decay ratio below 0.5 means engagement
                  dropped by more than half.
============================================================
*/

SELECT
    s.SubscriberKey,
    s.EmailAddress,
    s.FirstName,
    s.LastName,

    /* --- Baseline: 90-day engagement --- */
    COUNT(DISTINCT CASE
        WHEN snt.EventDate >= DATEADD(DAY, -90, GETDATE())
        THEN snt.JobID END)                              AS Sent_90d,
    COUNT(DISTINCT CASE
        WHEN o.EventDate >= DATEADD(DAY, -90, GETDATE())
        THEN o.JobID END)                                AS Opens_90d,
    CASE
        WHEN COUNT(DISTINCT CASE
            WHEN snt.EventDate >= DATEADD(DAY, -90, GETDATE())
            THEN snt.JobID END) = 0 THEN 0
        ELSE ROUND(
            COUNT(DISTINCT CASE WHEN o.EventDate >= DATEADD(DAY, -90, GETDATE()) THEN o.JobID END) * 100.0
          / COUNT(DISTINCT CASE WHEN snt.EventDate >= DATEADD(DAY, -90, GETDATE()) THEN snt.JobID END), 1)
    END                                                  AS OpenRate_90d,

    /* --- Recent: 30-day engagement --- */
    COUNT(DISTINCT CASE
        WHEN snt.EventDate >= DATEADD(DAY, -30, GETDATE())
        THEN snt.JobID END)                              AS Sent_30d,
    COUNT(DISTINCT CASE
        WHEN o.EventDate >= DATEADD(DAY, -30, GETDATE())
        THEN o.JobID END)                                AS Opens_30d,
    CASE
        WHEN COUNT(DISTINCT CASE
            WHEN snt.EventDate >= DATEADD(DAY, -30, GETDATE())
            THEN snt.JobID END) = 0 THEN 0
        ELSE ROUND(
            COUNT(DISTINCT CASE WHEN o.EventDate >= DATEADD(DAY, -30, GETDATE()) THEN o.JobID END) * 100.0
          / COUNT(DISTINCT CASE WHEN snt.EventDate >= DATEADD(DAY, -30, GETDATE()) THEN snt.JobID END), 1)
    END                                                  AS OpenRate_30d,

    /* --- Decay Ratio (recent / baseline) ---
       1.0 = stable, <1.0 = declining, >1.0 = improving */
    CASE
        WHEN COUNT(DISTINCT CASE WHEN o.EventDate >= DATEADD(DAY, -90, GETDATE()) THEN o.JobID END) = 0
          OR COUNT(DISTINCT CASE WHEN snt.EventDate >= DATEADD(DAY, -90, GETDATE()) THEN snt.JobID END) = 0
          OR COUNT(DISTINCT CASE WHEN snt.EventDate >= DATEADD(DAY, -30, GETDATE()) THEN snt.JobID END) = 0
            THEN NULL
        ELSE ROUND(
            (COUNT(DISTINCT CASE WHEN o.EventDate >= DATEADD(DAY, -30, GETDATE()) THEN o.JobID END) * 1.0
           / COUNT(DISTINCT CASE WHEN snt.EventDate >= DATEADD(DAY, -30, GETDATE()) THEN snt.JobID END))
          / (COUNT(DISTINCT CASE WHEN o.EventDate >= DATEADD(DAY, -90, GETDATE()) THEN o.JobID END) * 1.0
           / COUNT(DISTINCT CASE WHEN snt.EventDate >= DATEADD(DAY, -90, GETDATE()) THEN snt.JobID END))
        , 2)
    END                                                  AS DecayRatio,

    /* --- Decay Classification --- */
    CASE
        WHEN COUNT(DISTINCT CASE WHEN o.EventDate >= DATEADD(DAY, -90, GETDATE()) THEN o.JobID END) = 0
            THEN 'No Baseline (Never Engaged)'
        WHEN COUNT(DISTINCT CASE WHEN snt.EventDate >= DATEADD(DAY, -30, GETDATE()) THEN snt.JobID END) = 0
            THEN 'Not Recently Mailed'
        WHEN (COUNT(DISTINCT CASE WHEN o.EventDate >= DATEADD(DAY, -30, GETDATE()) THEN o.JobID END) * 1.0
            / NULLIF(COUNT(DISTINCT CASE WHEN snt.EventDate >= DATEADD(DAY, -30, GETDATE()) THEN snt.JobID END), 0))
           < (COUNT(DISTINCT CASE WHEN o.EventDate >= DATEADD(DAY, -90, GETDATE()) THEN o.JobID END) * 0.25
            / NULLIF(COUNT(DISTINCT CASE WHEN snt.EventDate >= DATEADD(DAY, -90, GETDATE()) THEN snt.JobID END), 0))
            THEN 'Severe Decay'
        WHEN (COUNT(DISTINCT CASE WHEN o.EventDate >= DATEADD(DAY, -30, GETDATE()) THEN o.JobID END) * 1.0
            / NULLIF(COUNT(DISTINCT CASE WHEN snt.EventDate >= DATEADD(DAY, -30, GETDATE()) THEN snt.JobID END), 0))
           < (COUNT(DISTINCT CASE WHEN o.EventDate >= DATEADD(DAY, -90, GETDATE()) THEN o.JobID END) * 0.5
            / NULLIF(COUNT(DISTINCT CASE WHEN snt.EventDate >= DATEADD(DAY, -90, GETDATE()) THEN snt.JobID END), 0))
            THEN 'Moderate Decay'
        WHEN (COUNT(DISTINCT CASE WHEN o.EventDate >= DATEADD(DAY, -30, GETDATE()) THEN o.JobID END) * 1.0
            / NULLIF(COUNT(DISTINCT CASE WHEN snt.EventDate >= DATEADD(DAY, -30, GETDATE()) THEN snt.JobID END), 0))
           < (COUNT(DISTINCT CASE WHEN o.EventDate >= DATEADD(DAY, -90, GETDATE()) THEN o.JobID END) * 0.75
            / NULLIF(COUNT(DISTINCT CASE WHEN snt.EventDate >= DATEADD(DAY, -90, GETDATE()) THEN snt.JobID END), 0))
            THEN 'Mild Decay'
        ELSE 'Stable / Improving'
    END                                                  AS DecayClassification

FROM
    _Subscribers AS s
    INNER JOIN _Sent AS snt
        ON s.SubscriberKey = snt.SubscriberKey
        AND snt.EventDate >= DATEADD(DAY, -90, GETDATE())
    LEFT JOIN _Open AS o
        ON s.SubscriberKey = o.SubscriberKey
        AND o.EventDate >= DATEADD(DAY, -90, GETDATE())
        AND o.IsUnique = 1
    LEFT JOIN _Click AS c
        ON s.SubscriberKey = c.SubscriberKey
        AND c.EventDate >= DATEADD(DAY, -90, GETDATE())
        AND c.IsUnique = 1
WHERE
    s.Status = 'Active'
GROUP BY
    s.SubscriberKey,
    s.EmailAddress,
    s.FirstName,
    s.LastName
HAVING
    /* Only show subscribers who had some baseline engagement */
    COUNT(DISTINCT CASE
        WHEN o.EventDate >= DATEADD(DAY, -90, GETDATE())
        THEN o.JobID END) >= 2
ORDER BY
    DecayRatio ASC

/*
============================================================
  EXPECTED SAMPLE OUTPUT
============================================================
| SubscriberKey | EmailAddress          | FirstName | LastName | Sent_90d | Opens_90d | OpenRate_90d | Sent_30d | Opens_30d | OpenRate_30d | DecayRatio | DecayClassification |
|---------------|-----------------------|-----------|----------|----------|-----------|--------------|----------|-----------|--------------|------------|---------------------|
| SK-30491      | decay1@example.com    | Amy       | Torres   | 12       | 8         | 66.7         | 4        | 0         | 0.0          | 0.00       | Severe Decay        |
| SK-40822      | decay2@example.com    | Brian     | Shah     | 12       | 6         | 50.0         | 4        | 1         | 25.0         | 0.50       | Moderate Decay      |
| SK-51200      | decay3@example.com    | Carol     | Jones    | 12       | 9         | 75.0         | 4        | 2         | 50.0         | 0.67       | Mild Decay          |
| SK-10042      | stable@example.com    | Jane      | Doe      | 12       | 10        | 83.3         | 4        | 3         | 75.0         | 0.90       | Stable / Improving  |
============================================================
*/
