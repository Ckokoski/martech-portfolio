/*
============================================================
  Query Name:   Geographic Segment (Subscribers by Region/State)
  Category:     Segmentation
  Purpose:      Group subscribers by geographic region, state,
                or country to enable location-based targeting.
                Includes timezone mapping for send-time
                optimization.
  Use Case:     - Regional promotions (store openings, local events)
                - Send-time optimization by timezone
                - Compliance with region-specific regulations
                - Localizing content (language, currency, offers)
  Platform:     Salesforce Marketing Cloud (SFMC) Query Activity
  Tables Used:  _Subscribers, SubscriberMaster
  Notes:        - Geographic data quality varies widely; this
                  query includes a completeness flag so you can
                  assess data gaps before relying on the segment.
                - Timezone mapping uses a simplified US model;
                  expand for international audiences.
============================================================
*/

SELECT
    s.SubscriberKey,
    s.EmailAddress,
    s.FirstName,
    s.LastName,
    sm.Country,
    sm.State,
    sm.City,
    sm.PostalCode,
    CASE
        WHEN sm.State IN ('CT','DE','FL','GA','IN','KY','MA','MD','ME',
                          'MI','NC','NH','NJ','NY','OH','PA','RI','SC',
                          'VA','VT','WV','DC')             THEN 'Eastern'
        WHEN sm.State IN ('AL','AR','IA','IL','KS','LA','MN','MO','MS',
                          'ND','NE','OK','SD','TN','TX','WI')
                                                            THEN 'Central'
        WHEN sm.State IN ('AZ','CO','ID','MT','NM','UT','WY')
                                                            THEN 'Mountain'
        WHEN sm.State IN ('AK','CA','HI','NV','OR','WA')   THEN 'Pacific'
        ELSE 'Other / International'
    END                                                     AS TimezoneRegion,
    CASE
        WHEN sm.Country IS NOT NULL
         AND sm.State IS NOT NULL
         AND sm.PostalCode IS NOT NULL                      THEN 'Complete'
        WHEN sm.Country IS NOT NULL
         OR  sm.State IS NOT NULL                           THEN 'Partial'
        ELSE 'Missing'
    END                                                     AS GeoDataQuality
FROM
    _Subscribers AS s
    LEFT JOIN SubscriberMaster AS sm
        ON s.SubscriberKey = sm.SubscriberKey
WHERE
    s.Status = 'Active'
ORDER BY
    sm.Country,
    sm.State,
    sm.City

/*
============================================================
  EXPECTED SAMPLE OUTPUT
============================================================
| SubscriberKey | EmailAddress         | FirstName | LastName | Country | State | City          | PostalCode | TimezoneRegion | GeoDataQuality |
|---------------|----------------------|-----------|----------|---------|-------|---------------|------------|----------------|----------------|
| SK-11200      | east1@example.com    | Anna      | Reeves   | US      | NY    | New York      | 10001      | Eastern        | Complete       |
| SK-22340      | cent1@example.com    | Ben       | Cortez   | US      | TX    | Austin        | 73301      | Central        | Complete       |
| SK-33100      | west1@example.com    | Cara      | Tanaka   | US      | CA    | San Francisco | 94102      | Pacific        | Complete       |
| SK-44500      | intl1@example.com    | Dieter    | Braun    | DE      | NULL  | Berlin        | 10115      | Other / Intl   | Partial        |
| SK-55010      | noaddr@example.com   | Eve       | Morales  | NULL    | NULL  | NULL          | NULL       | Other / Intl   | Missing        |
============================================================
*/
