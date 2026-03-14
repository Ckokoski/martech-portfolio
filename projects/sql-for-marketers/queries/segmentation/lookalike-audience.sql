/*
============================================================
  Query Name:   Lookalike Audience Builder
  Category:     Segmentation
  Purpose:      Find subscribers who share behavioral and
                demographic traits with your best customers
                but have NOT yet converted. These "lookalike"
                contacts are your highest-probability prospects
                for conversion campaigns.
  Use Case:     - Target high-potential prospects for conversion
                  campaigns or product launches
                - Prioritize leads that match your best-customer
                  profile
                - Export for paid media lookalike seed audiences
  Platform:     Salesforce Marketing Cloud (SFMC) Query Activity
  Tables Used:  _Subscribers, _Open, _Click, SubscriberMaster,
                TransactionHistory
  Notes:        - This approach creates a "profile" of best
                  customers (engagement level, channel, content
                  preferences) then scores other subscribers
                  against that profile.
                - True lookalike modeling requires ML, but this
                  rule-based approach is practical for SFMC
                  Query Activities that lack ML capabilities.
============================================================
*/

/*
  Step 1: Define what a "best customer" looks like.
  We use the average engagement metrics of the top 10%
  customers as the benchmark profile.
*/
SELECT
    prospect.SubscriberKey,
    prospect.EmailAddress,
    prospect.FirstName,
    prospect.LastName,
    prospect.OpensLast90d,
    prospect.ClicksLast90d,
    prospect.EngagementScore,
    prospect.State,
    prospect.SignupSource,
    prospect.LookalikeScore,
    prospect.LookalikeRank
FROM (
    SELECT
        s.SubscriberKey,
        s.EmailAddress,
        s.FirstName,
        s.LastName,
        sm.State,
        sm.SignupSource,
        COUNT(DISTINCT o.JobID)         AS OpensLast90d,
        COUNT(DISTINCT c.JobID)         AS ClicksLast90d,

        /* Weighted engagement score */
        (COUNT(DISTINCT o.JobID) * 1)
      + (COUNT(DISTINCT c.JobID) * 3)   AS EngagementScore,

        /*
          Lookalike Score: award points for matching traits
          of best customers. Higher = more similar.
          Traits checked:
            - High open rate (5+ opens in 90d)
            - Any click activity (shows intent)
            - Same signup source as top converters
            - Same geographic region as top converters
        */
        CASE WHEN COUNT(DISTINCT o.JobID) >= 5 THEN 25 ELSE 0 END
      + CASE WHEN COUNT(DISTINCT c.JobID) >= 1 THEN 25 ELSE 0 END
      + CASE
            WHEN sm.SignupSource IN (
                SELECT TOP 3 th_src.SignupSource
                FROM TransactionHistory AS th_top
                INNER JOIN SubscriberMaster AS th_src
                    ON th_top.SubscriberKey = th_src.SubscriberKey
                WHERE th_top.OrderStatus = 'Completed'
                GROUP BY th_src.SignupSource
                ORDER BY SUM(th_top.OrderTotal) DESC
            ) THEN 25 ELSE 0
        END
      + CASE
            WHEN sm.State IN (
                SELECT TOP 5 th_geo.State
                FROM TransactionHistory AS th_top2
                INNER JOIN SubscriberMaster AS th_geo
                    ON th_top2.SubscriberKey = th_geo.SubscriberKey
                WHERE th_top2.OrderStatus = 'Completed'
                GROUP BY th_geo.State
                ORDER BY SUM(th_top2.OrderTotal) DESC
            ) THEN 25 ELSE 0
        END                             AS LookalikeScore,

        ROW_NUMBER() OVER (
            ORDER BY
                (COUNT(DISTINCT o.JobID) * 1)
              + (COUNT(DISTINCT c.JobID) * 3) DESC
        )                               AS LookalikeRank

    FROM
        _Subscribers AS s
        INNER JOIN SubscriberMaster AS sm
            ON s.SubscriberKey = sm.SubscriberKey
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
        /* Exclude existing customers (those with purchases) */
        AND s.SubscriberKey NOT IN (
            SELECT DISTINCT SubscriberKey
            FROM TransactionHistory
            WHERE OrderStatus = 'Completed'
        )
    GROUP BY
        s.SubscriberKey,
        s.EmailAddress,
        s.FirstName,
        s.LastName,
        sm.State,
        sm.SignupSource
) AS prospect
WHERE
    prospect.LookalikeScore >= 50   /* At least 2 of 4 traits match */
ORDER BY
    prospect.LookalikeScore DESC,
    prospect.EngagementScore DESC

/*
============================================================
  EXPECTED SAMPLE OUTPUT
============================================================
| SubscriberKey | EmailAddress           | FirstName | LastName | OpensLast90d | ClicksLast90d | EngagementScore | State | SignupSource    | LookalikeScore | LookalikeRank |
|---------------|------------------------|-----------|----------|--------------|----------------|-----------------|-------|----------------|----------------|---------------|
| SK-34010      | prospect1@example.com  | Rosa      | Kim      | 8            | 4              | 20              | CA    | Website Popup  | 100            | 1             |
| SK-34520      | prospect2@example.com  | Theo      | Adams    | 6            | 2              | 12              | NY    | Facebook Lead  | 75             | 3             |
| SK-35100      | prospect3@example.com  | Uma       | Singh    | 7            | 1              | 10              | TX    | Website Popup  | 75             | 5             |
| SK-36200      | prospect4@example.com  | Vera      | Nowak    | 5            | 0              | 5               | CA    | Referral       | 50             | 12            |
============================================================
*/
