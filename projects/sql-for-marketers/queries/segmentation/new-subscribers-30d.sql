/*
============================================================
  Query Name:   New Subscribers (Last 30 Days)
  Category:     Segmentation
  Purpose:      Retrieve all subscribers who joined within the
                last 30 days, along with their signup source
                and any early engagement signals.
  Use Case:     New subscribers are in the critical "honeymoon
                period" when engagement is highest. Use this
                segment to:
                - Trigger a welcome journey
                - Monitor onboarding health
                - Measure acquisition source quality
  Platform:     Salesforce Marketing Cloud (SFMC) Query Activity
  Tables Used:  _Subscribers, _Open, _Click, SubscriberMaster
  Notes:        - DateJoined is available on the _Subscribers
                  system data view in SFMC.
                - SignupSource is a custom field; adapt the
                  column name to your data model.
============================================================
*/

SELECT
    s.SubscriberKey,
    s.EmailAddress,
    s.FirstName,
    s.LastName,
    s.DateJoined,
    sm.SignupSource,
    sm.AcquisitionCampaign,
    DATEDIFF(DAY, s.DateJoined, GETDATE())      AS DaysSinceSignup,
    COUNT(DISTINCT o.JobID)                      AS OpensToDate,
    COUNT(DISTINCT c.JobID)                      AS ClicksToDate,
    CASE
        WHEN COUNT(DISTINCT c.JobID) >= 1        THEN 'Fast Starter'
        WHEN COUNT(DISTINCT o.JobID) >= 1        THEN 'Showing Interest'
        ELSE 'No Engagement Yet'
    END                                          AS EarlyEngagementFlag
FROM
    _Subscribers AS s
    LEFT JOIN SubscriberMaster AS sm
        ON s.SubscriberKey = sm.SubscriberKey
    LEFT JOIN _Open AS o
        ON s.SubscriberKey = o.SubscriberKey
        AND o.IsUnique = 1
    LEFT JOIN _Click AS c
        ON s.SubscriberKey = c.SubscriberKey
        AND c.IsUnique = 1
WHERE
    s.Status = 'Active'
    AND s.DateJoined >= DATEADD(DAY, -30, GETDATE())
GROUP BY
    s.SubscriberKey,
    s.EmailAddress,
    s.FirstName,
    s.LastName,
    s.DateJoined,
    sm.SignupSource,
    sm.AcquisitionCampaign
ORDER BY
    s.DateJoined DESC

/*
============================================================
  EXPECTED SAMPLE OUTPUT
============================================================
| SubscriberKey | EmailAddress           | FirstName | LastName | DateJoined | SignupSource    | AcquisitionCampaign | DaysSinceSignup | OpensToDate | ClicksToDate | EarlyEngagementFlag |
|---------------|------------------------|-----------|----------|------------|----------------|---------------------|-----------------|-------------|--------------|---------------------|
| SK-99210      | newbie1@example.com    | Dana      | Park     | 2026-03-12 | Website Popup  | Spring Sale 2026    | 2               | 1           | 1            | Fast Starter        |
| SK-99305      | newbie2@example.com    | Eli       | Ruiz     | 2026-03-10 | Facebook Lead  | FB-Lookalike-Q1     | 4               | 2           | 0            | Showing Interest    |
| SK-99418      | newbie3@example.com    | Faye      | Kim      | 2026-03-08 | Checkout Optin | None                | 6               | 0           | 0            | No Engagement Yet   |
| SK-99502      | newbie4@example.com    | Gabe      | Nair     | 2026-02-20 | Webinar Reg    | Webinar-Feb26       | 22              | 3           | 2            | Fast Starter        |
============================================================
*/
