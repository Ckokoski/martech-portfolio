/*
============================================================
  Query Name:   Content Affinity Score
  Category:     Engagement Scoring
  Purpose:      Determine which content topics/categories
                drive the most engagement for each subscriber.
                This enables content personalization at scale
                by matching content to proven interests.
  Use Case:     - Personalize email content blocks based on
                  demonstrated interest
                - Build topic-based segments for targeted sends
                - Inform content strategy (what topics resonate
                  with which audiences)
                - Power dynamic content rules in SFMC
  Platform:     Salesforce Marketing Cloud (SFMC) Query Activity
  Tables Used:  _Subscribers, _Open, _Click, _Sent,
                CampaignMetadata (custom DE with content tags)
  Notes:        - CampaignMetadata is a custom data extension
                  that maps each JobID to content categories.
                  You tag campaigns at send time (e.g., "Promo",
                  "Educational", "Product Launch").
                - This is one of the most powerful personalization
                  queries you can build in SFMC.
============================================================
*/

SELECT
    s.SubscriberKey,
    s.EmailAddress,
    s.FirstName,
    s.LastName,
    cm.ContentCategory,

    /* Engagement metrics for this content category */
    COUNT(DISTINCT snt.JobID)                        AS TimesSent,
    COUNT(DISTINCT o.JobID)                          AS TimesOpened,
    COUNT(DISTINCT c.JobID)                          AS TimesClicked,

    /* Engagement rates for this category */
    CASE
        WHEN COUNT(DISTINCT snt.JobID) = 0 THEN 0
        ELSE ROUND(
            COUNT(DISTINCT o.JobID) * 100.0
            / COUNT(DISTINCT snt.JobID), 1)
    END                                              AS OpenRate,
    CASE
        WHEN COUNT(DISTINCT snt.JobID) = 0 THEN 0
        ELSE ROUND(
            COUNT(DISTINCT c.JobID) * 100.0
            / COUNT(DISTINCT snt.JobID), 1)
    END                                              AS ClickRate,

    /* Affinity score: weighted engagement with this content */
    (COUNT(DISTINCT o.JobID) * 1)
  + (COUNT(DISTINCT c.JobID) * 3)                    AS AffinityScore,

    /* Rank content categories per subscriber */
    ROW_NUMBER() OVER (
        PARTITION BY s.SubscriberKey
        ORDER BY (COUNT(DISTINCT o.JobID) * 1)
               + (COUNT(DISTINCT c.JobID) * 3) DESC
    )                                                AS CategoryRank

FROM
    _Subscribers AS s
    INNER JOIN _Sent AS snt
        ON s.SubscriberKey = snt.SubscriberKey
        AND snt.EventDate >= DATEADD(DAY, -180, GETDATE())
    INNER JOIN CampaignMetadata AS cm
        ON snt.JobID = cm.JobID
    LEFT JOIN _Open AS o
        ON s.SubscriberKey = o.SubscriberKey
        AND o.JobID = snt.JobID
        AND o.IsUnique = 1
    LEFT JOIN _Click AS c
        ON s.SubscriberKey = c.SubscriberKey
        AND c.JobID = snt.JobID
        AND c.IsUnique = 1
WHERE
    s.Status = 'Active'
GROUP BY
    s.SubscriberKey,
    s.EmailAddress,
    s.FirstName,
    s.LastName,
    cm.ContentCategory
ORDER BY
    s.SubscriberKey,
    AffinityScore DESC

/*
------------------------------------------------------------
  To get only the TOP content category per subscriber
  (for dynamic content rules), wrap this query and filter
  WHERE CategoryRank = 1.
------------------------------------------------------------
*/

/*
============================================================
  EXPECTED SAMPLE OUTPUT
============================================================
| SubscriberKey | EmailAddress        | FirstName | LastName | ContentCategory | TimesSent | TimesOpened | TimesClicked | OpenRate | ClickRate | AffinityScore | CategoryRank |
|---------------|---------------------|-----------|----------|-----------------|-----------|-------------|--------------|----------|-----------|---------------|--------------|
| SK-10042      | jane@example.com    | Jane      | Doe      | Promotions      | 12        | 10          | 6            | 83.3     | 50.0      | 28            | 1            |
| SK-10042      | jane@example.com    | Jane      | Doe      | Product Launch  | 4         | 3           | 2            | 75.0     | 50.0      | 9             | 2            |
| SK-10042      | jane@example.com    | Jane      | Doe      | Educational     | 8         | 2           | 0            | 25.0     | 0.0       | 2             | 3            |
| SK-20318      | mark@example.com    | Mark      | Lee      | Educational     | 8         | 7           | 4            | 87.5     | 50.0      | 19            | 1            |
| SK-20318      | mark@example.com    | Mark      | Lee      | Promotions      | 12        | 4           | 1            | 33.3     | 8.3       | 7             | 2            |
============================================================
*/
