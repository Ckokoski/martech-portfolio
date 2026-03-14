/*
============================================================
  Query Name:   Channel Preference Score
  Category:     Engagement Scoring
  Purpose:      Determine each subscriber's preferred
                communication channel based on actual engagement
                data across email, SMS, and push. This replaces
                guesswork with data-driven channel selection.
  Use Case:     - Route messages through the channel each
                  subscriber is most likely to engage with
                - Reduce email fatigue by shifting to preferred
                  channels
                - Personalize journey entry points by channel
                - Inform multi-channel orchestration strategies
  Platform:     Salesforce Marketing Cloud (SFMC) Query Activity
  Tables Used:  _Subscribers, _Open, _Click, SMSMessageTracking,
                PushNotificationTracking
  Notes:        - SMSMessageTracking and PushNotificationTracking
                  are custom data extensions that mirror your
                  SMS and push engagement data.
                - If you only use email, simplify this query to
                  just the email columns and use it to compare
                  content types instead.
============================================================
*/

SELECT
    s.SubscriberKey,
    s.EmailAddress,
    s.FirstName,
    s.LastName,

    /* --- Email Engagement --- */
    COUNT(DISTINCT o.JobID)                          AS EmailOpens_90d,
    COUNT(DISTINCT c.JobID)                          AS EmailClicks_90d,
    (COUNT(DISTINCT o.JobID) * 1)
  + (COUNT(DISTINCT c.JobID) * 3)                    AS EmailScore,

    /* --- SMS Engagement --- */
    COUNT(DISTINCT sms.MessageID)                    AS SMSResponses_90d,
    COUNT(DISTINCT sms.MessageID) * 4                AS SMSScore,

    /* --- Push Engagement --- */
    COUNT(DISTINCT push.NotificationID)              AS PushOpens_90d,
    COUNT(DISTINCT push.NotificationID) * 2          AS PushScore,

    /* --- Preferred Channel (highest score wins) --- */
    CASE
        WHEN (COUNT(DISTINCT o.JobID) * 1) + (COUNT(DISTINCT c.JobID) * 3)
           >= COUNT(DISTINCT sms.MessageID) * 4
         AND (COUNT(DISTINCT o.JobID) * 1) + (COUNT(DISTINCT c.JobID) * 3)
           >= COUNT(DISTINCT push.NotificationID) * 2
            THEN 'Email'
        WHEN COUNT(DISTINCT sms.MessageID) * 4
           >= (COUNT(DISTINCT o.JobID) * 1) + (COUNT(DISTINCT c.JobID) * 3)
         AND COUNT(DISTINCT sms.MessageID) * 4
           >= COUNT(DISTINCT push.NotificationID) * 2
            THEN 'SMS'
        WHEN COUNT(DISTINCT push.NotificationID) * 2
           >= (COUNT(DISTINCT o.JobID) * 1) + (COUNT(DISTINCT c.JobID) * 3)
         AND COUNT(DISTINCT push.NotificationID) * 2
           >= COUNT(DISTINCT sms.MessageID) * 4
            THEN 'Push'
        ELSE 'No Preference (Low Activity)'
    END                                              AS PreferredChannel,

    /* --- Channel Diversity (how many channels are active) --- */
    CASE
        WHEN COUNT(DISTINCT o.JobID) > 0
         AND COUNT(DISTINCT sms.MessageID) > 0
         AND COUNT(DISTINCT push.NotificationID) > 0 THEN 'Omni-Channel'
        WHEN (CASE WHEN COUNT(DISTINCT o.JobID) > 0 THEN 1 ELSE 0 END
            + CASE WHEN COUNT(DISTINCT sms.MessageID) > 0 THEN 1 ELSE 0 END
            + CASE WHEN COUNT(DISTINCT push.NotificationID) > 0 THEN 1 ELSE 0 END) = 2
            THEN 'Dual-Channel'
        WHEN COUNT(DISTINCT o.JobID) > 0
          OR COUNT(DISTINCT sms.MessageID) > 0
          OR COUNT(DISTINCT push.NotificationID) > 0 THEN 'Single-Channel'
        ELSE 'Inactive'
    END                                              AS ChannelDiversity

FROM
    _Subscribers AS s
    LEFT JOIN _Open AS o
        ON s.SubscriberKey = o.SubscriberKey
        AND o.EventDate >= DATEADD(DAY, -90, GETDATE())
        AND o.IsUnique = 1
    LEFT JOIN _Click AS c
        ON s.SubscriberKey = c.SubscriberKey
        AND c.EventDate >= DATEADD(DAY, -90, GETDATE())
        AND c.IsUnique = 1
    LEFT JOIN SMSMessageTracking AS sms
        ON s.SubscriberKey = sms.SubscriberKey
        AND sms.EventDate >= DATEADD(DAY, -90, GETDATE())
        AND sms.ResponseType = 'Reply'
    LEFT JOIN PushNotificationTracking AS push
        ON s.SubscriberKey = push.SubscriberKey
        AND push.EventDate >= DATEADD(DAY, -90, GETDATE())
        AND push.IsOpened = 1
WHERE
    s.Status = 'Active'
GROUP BY
    s.SubscriberKey,
    s.EmailAddress,
    s.FirstName,
    s.LastName
ORDER BY
    (COUNT(DISTINCT o.JobID) * 1)
  + (COUNT(DISTINCT c.JobID) * 3)
  + (COUNT(DISTINCT sms.MessageID) * 4)
  + (COUNT(DISTINCT push.NotificationID) * 2) DESC

/*
============================================================
  EXPECTED SAMPLE OUTPUT
============================================================
| SubscriberKey | EmailAddress         | FirstName | LastName | EmailOpens_90d | EmailClicks_90d | EmailScore | SMSResponses_90d | SMSScore | PushOpens_90d | PushScore | PreferredChannel | ChannelDiversity |
|---------------|----------------------|-----------|----------|----------------|-----------------|------------|------------------|----------|---------------|-----------|------------------|------------------|
| SK-10042      | omni@example.com     | Jane      | Doe      | 12             | 5               | 27         | 4                | 16       | 6             | 12        | Email            | Omni-Channel     |
| SK-20318      | smsuser@example.com  | Mark      | Lee      | 3              | 0               | 3          | 8                | 32       | 0             | 0         | SMS              | Dual-Channel     |
| SK-30491      | pushfan@example.com  | Amy       | Torres   | 2              | 1               | 5          | 0                | 0        | 10            | 20        | Push             | Dual-Channel     |
| SK-40822      | email@example.com    | Brian     | Shah     | 8              | 3               | 17         | 0                | 0        | 0             | 0         | Email            | Single-Channel   |
| SK-55900      | quiet@example.com    | Carol     | Wu       | 0              | 0               | 0          | 0                | 0        | 0             | 0         | No Preference    | Inactive         |
============================================================
*/
