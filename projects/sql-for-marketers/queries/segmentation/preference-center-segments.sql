/*
============================================================
  Query Name:   Preference Center Segments
  Category:     Segmentation
  Purpose:      Build segments based on subscriber-stated
                preferences (topics, frequency, channel).
                Preference-based segments respect subscriber
                choice and typically outperform demographic
                segments on engagement.
  Use Case:     - Route subscribers to the right content streams
                - Honor frequency preferences to reduce unsubs
                - Identify under-served preference groups
                - Feed preference data into personalization
  Platform:     Salesforce Marketing Cloud (SFMC) Query Activity
  Tables Used:  _Subscribers, PreferenceCenter
  Notes:        - PreferenceCenter is a custom data extension.
                  Adapt column names to match your implementation.
                - Subscribers may have multiple topic preferences;
                  this query aggregates them into a comma-style
                  summary while also allowing per-topic filtering.
============================================================
*/

SELECT
    s.SubscriberKey,
    s.EmailAddress,
    s.FirstName,
    s.LastName,
    pc.ContentPreference,
    pc.FrequencyPreference,
    pc.ChannelPreference,
    pc.PreferenceUpdatedDate,
    DATEDIFF(DAY, pc.PreferenceUpdatedDate, GETDATE())  AS DaysSincePrefUpdate,
    CASE
        WHEN pc.ContentPreference IS NULL
         AND pc.FrequencyPreference IS NULL              THEN 'No Preferences Set'
        WHEN DATEDIFF(DAY, pc.PreferenceUpdatedDate,
                      GETDATE()) > 365                   THEN 'Stale Preferences'
        ELSE 'Preferences Current'
    END                                                  AS PreferenceStatus
FROM
    _Subscribers AS s
    LEFT JOIN PreferenceCenter AS pc
        ON s.SubscriberKey = pc.SubscriberKey
WHERE
    s.Status = 'Active'
ORDER BY
    pc.PreferenceUpdatedDate DESC

/*
------------------------------------------------------------
  FILTERING BY SPECIFIC PREFERENCE
  To pull subscribers who prefer a specific content topic,
  add a WHERE clause like:
    AND pc.ContentPreference = 'Product Updates'
  Common values might include:
    'Product Updates', 'Promotions', 'Industry News',
    'Events', 'Educational Content'
------------------------------------------------------------
*/

/*
============================================================
  EXPECTED SAMPLE OUTPUT
============================================================
| SubscriberKey | EmailAddress           | FirstName | LastName | ContentPreference | FrequencyPreference | ChannelPreference | PreferenceUpdatedDate | DaysSincePrefUpdate | PreferenceStatus     |
|---------------|------------------------|-----------|----------|-------------------|---------------------|-------------------|-----------------------|---------------------|----------------------|
| SK-14200      | promo@example.com      | Hana      | Ortiz    | Promotions        | Weekly              | Email             | 2026-03-01            | 13                  | Preferences Current  |
| SK-15830      | news@example.com       | Ivan      | Cheng    | Industry News     | Monthly             | Email + SMS       | 2026-01-18            | 55                  | Preferences Current  |
| SK-16010      | edu@example.com        | Jess      | Rao      | Educational       | Bi-Weekly           | Email             | 2025-09-10            | 185                 | Preferences Current  |
| SK-17440      | stale@example.com      | Karl      | Weber    | Product Updates   | Weekly              | Email             | 2024-11-05            | 495                 | Stale Preferences    |
| SK-18900      | nopref@example.com     | Lily      | Tran     | NULL              | NULL                | NULL              | NULL                  | NULL                | No Preferences Set   |
============================================================
*/
