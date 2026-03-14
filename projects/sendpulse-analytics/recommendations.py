"""
recommendations.py — Rule-Based Recommendation Engine

Generates actionable recommendations from analysis results without
calling any external AI API. Uses pattern matching and threshold-based
rules to produce advice across four categories:

1. Best send times
2. Subject line recommendations
3. List hygiene actions
4. A/B test suggestions
"""

from dataclasses import dataclass, field
from typing import List


@dataclass
class Recommendation:
    """A single actionable recommendation."""
    category: str          # e.g. "Send Time", "Subject Line", "List Hygiene", "A/B Test"
    priority: str          # "high", "medium", "low"
    title: str
    description: str
    evidence: str          # data point backing the recommendation
    impact_estimate: str   # e.g. "+2-4% open rate"


def _send_time_recommendations(send_times: dict) -> List[Recommendation]:
    """Generate recommendations about optimal send times."""
    recs = []

    best_hour = send_times["best_hour"]
    best_rate = send_times["best_hour_rate"]
    worst_hour = send_times["worst_hour"]
    worst_rate = send_times["worst_hour_rate"]
    best_dow = send_times["best_dow"]
    best_dow_rate = send_times["best_dow_rate"]

    # Primary send time recommendation
    recs.append(Recommendation(
        category="Send Time",
        priority="high",
        title=f"Optimize sends around {best_hour}:00",
        description=(
            f"Campaigns sent at {best_hour}:00 achieved the highest average open rate "
            f"of {best_rate:.1%}. Consolidate the majority of sends into the "
            f"{best_hour-1}:00-{best_hour+1}:00 window to maximize engagement."
        ),
        evidence=f"Best hour: {best_hour}:00 ({best_rate:.1%} open rate)",
        impact_estimate=f"+{(best_rate - worst_rate):.1%} potential open rate lift vs worst time",
    ))

    # Avoid worst times
    if worst_rate < best_rate * 0.7:
        recs.append(Recommendation(
            category="Send Time",
            priority="high",
            title=f"Avoid sending at {worst_hour}:00",
            description=(
                f"Campaigns sent at {worst_hour}:00 had the lowest open rate of {worst_rate:.1%}, "
                f"significantly below the best-performing window. Move any scheduled sends "
                f"from this time slot."
            ),
            evidence=f"Worst hour: {worst_hour}:00 ({worst_rate:.1%} open rate)",
            impact_estimate=f"+{(best_rate - worst_rate):.1%} open rate by shifting",
        ))

    # Day of week
    recs.append(Recommendation(
        category="Send Time",
        priority="medium",
        title=f"Prefer {best_dow}s for campaign sends",
        description=(
            f"{best_dow} showed the strongest engagement with a {best_dow_rate:.1%} "
            f"average open rate. Prioritize this day for high-value campaigns "
            f"like product launches and major announcements."
        ),
        evidence=f"Best day: {best_dow} ({best_dow_rate:.1%} open rate)",
        impact_estimate="Incremental engagement lift on key campaigns",
    ))

    # Check weekend performance
    dow_perf = send_times["dow_performance"]
    weekend = dow_perf[dow_perf["send_dow"].isin(["Saturday", "Sunday"])]
    weekday = dow_perf[~dow_perf["send_dow"].isin(["Saturday", "Sunday"])]
    if len(weekend) > 0 and len(weekday) > 0:
        weekend_avg = weekend["avg_open_rate"].mean()
        weekday_avg = weekday["avg_open_rate"].mean()
        if weekend_avg < weekday_avg * 0.85:
            recs.append(Recommendation(
                category="Send Time",
                priority="medium",
                title="Reduce weekend sends",
                description=(
                    f"Weekend campaigns average {weekend_avg:.1%} open rate vs "
                    f"{weekday_avg:.1%} on weekdays. Reserve weekend sends only for "
                    f"time-sensitive promotions or specific audience segments."
                ),
                evidence=f"Weekend: {weekend_avg:.1%} vs Weekday: {weekday_avg:.1%}",
                impact_estimate=f"+{(weekday_avg - weekend_avg):.1%} by shifting to weekdays",
            ))

    return recs


def _subject_line_recommendations(subject_lines: dict) -> List[Recommendation]:
    """Generate subject line optimization recommendations."""
    recs = []
    features = subject_lines["feature_impact"]

    # Personalization impact
    pers = features.get("has_personalization", {})
    if pers.get("lift", 0) > 0.01:
        recs.append(Recommendation(
            category="Subject Line",
            priority="high",
            title="Increase use of personalization in subject lines",
            description=(
                f"Personalized subject lines (using subscriber name) achieved "
                f"{pers['with']:.1%} open rate vs {pers['without']:.1%} without. "
                f"This {pers['lift']:.1%} lift justifies expanding personalization "
                f"to all campaign types."
            ),
            evidence=f"Personalization lift: +{pers['lift']:.1%} open rate",
            impact_estimate=f"+{pers['lift']:.1%} open rate across campaigns",
        ))

    # Urgency words
    urg = features.get("has_urgency", {})
    if urg.get("lift", 0) > 0.005:
        recs.append(Recommendation(
            category="Subject Line",
            priority="medium",
            title="Use urgency language strategically",
            description=(
                f"Subject lines with urgency words (e.g., 'Last Chance', 'Limited Time') "
                f"achieved {urg['with']:.1%} vs {urg['without']:.1%}. Use sparingly to "
                f"maintain credibility — limit to 1-2 urgency campaigns per month."
            ),
            evidence=f"Urgency lift: +{urg['lift']:.1%} open rate",
            impact_estimate=f"+{urg['lift']:.1%} on urgency campaigns",
        ))

    # Emoji usage
    emoji = features.get("has_emoji", {})
    if emoji.get("lift", 0) > 0.005:
        recs.append(Recommendation(
            category="Subject Line",
            priority="low",
            title="Test emoji inclusion in subject lines",
            description=(
                f"Emojis in subject lines correlated with a {emoji['lift']:.1%} open rate lift "
                f"({emoji['with']:.1%} vs {emoji['without']:.1%}). Test emoji placement "
                f"(beginning vs end) and type (topical vs decorative)."
            ),
            evidence=f"Emoji lift: +{emoji['lift']:.1%} open rate",
            impact_estimate=f"+{emoji['lift']:.1%} potential lift",
        ))
    elif emoji.get("lift", 0) <= 0:
        recs.append(Recommendation(
            category="Subject Line",
            priority="low",
            title="Reconsider emoji usage in subject lines",
            description=(
                f"Emojis showed no positive impact ({emoji['with']:.1%} with vs "
                f"{emoji['without']:.1%} without). Consider removing or limiting emoji "
                f"use to maintain a professional tone."
            ),
            evidence=f"Emoji effect: {emoji['lift']:.1%} open rate difference",
            impact_estimate="Neutral to slightly positive by removing",
        ))

    # Top subject patterns — extract common traits
    top = subject_lines.get("top_subjects", [])
    if top:
        personalized_top = sum(1 for s in top if "first_name" in s["subject_line"].lower())
        if personalized_top >= len(top) * 0.4:
            recs.append(Recommendation(
                category="Subject Line",
                priority="medium",
                title="Top performers favor personalization",
                description=(
                    f"{personalized_top} of the top {len(top)} performing campaigns used "
                    f"personalized subject lines. This reinforces the value of dynamic "
                    f"merge tags in driving engagement."
                ),
                evidence=f"{personalized_top}/{len(top)} top campaigns used personalization",
                impact_estimate="Validates personalization strategy",
            ))

    # Length recommendation
    length_perf = subject_lines["length_performance"]
    if len(length_perf) > 0:
        best_bucket = length_perf.loc[length_perf["avg_open_rate"].idxmax()]
        recs.append(Recommendation(
            category="Subject Line",
            priority="medium",
            title=f"Target subject line length of {best_bucket['length_bucket']} characters",
            description=(
                f"Subject lines with {best_bucket['length_bucket']} characters achieved "
                f"the highest open rate of {best_bucket['avg_open_rate']:.1%}. "
                f"Keep subjects concise and impactful within this range."
            ),
            evidence=f"Best length bucket: {best_bucket['length_bucket']} chars ({best_bucket['avg_open_rate']:.1%})",
            impact_estimate="Incremental open rate improvement",
        ))

    return recs


def _list_hygiene_recommendations(list_health: dict, segmentation: dict) -> List[Recommendation]:
    """Generate list hygiene and subscriber management recommendations."""
    recs = []

    # High bounce campaigns
    high_bounce = list_health.get("high_bounce_campaigns", [])
    if high_bounce:
        recs.append(Recommendation(
            category="List Hygiene",
            priority="high",
            title=f"Investigate {len(high_bounce)} high-bounce campaigns",
            description=(
                f"{len(high_bounce)} campaign(s) had bounce rates significantly above average. "
                f"This may indicate stale list segments, purchased lists, or email "
                f"authentication issues (SPF/DKIM). Run a list verification pass on "
                f"the affected segments and remove invalid addresses."
            ),
            evidence=f"Campaigns flagged: {', '.join(c['campaign_id'] for c in high_bounce[:5])}",
            impact_estimate="Reduce bounces by 40-60%, improve deliverability score",
        ))

    # High unsubscribe campaigns
    high_unsub = list_health.get("high_unsub_campaigns", [])
    if high_unsub:
        recs.append(Recommendation(
            category="List Hygiene",
            priority="high",
            title=f"Review content of {len(high_unsub)} high-unsubscribe campaigns",
            description=(
                f"{len(high_unsub)} campaign(s) triggered unsubscribe spikes. Audit their "
                f"content, frequency, and targeting. These may have been sent to "
                f"mismatched segments or had overly aggressive messaging."
            ),
            evidence=f"Campaigns flagged: {', '.join(c['campaign_id'] for c in high_unsub[:5])}",
            impact_estimate="Reduce unsubscribe rate by addressing root causes",
        ))

    # Dormant subscriber action
    seg_dist = segmentation.get("segment_distribution", {})
    dormant_count = seg_dist.get("Dormant", 0)
    total_subs = sum(seg_dist.values())
    if total_subs > 0:
        dormant_pct = dormant_count / total_subs

        if dormant_pct > 0.10:
            recs.append(Recommendation(
                category="List Hygiene",
                priority="high",
                title=f"Suppress {dormant_count:,} dormant subscribers ({dormant_pct:.0%} of list)",
                description=(
                    f"Dormant subscribers (no engagement in 90+ days) represent "
                    f"{dormant_pct:.0%} of your list. Continuing to email them hurts "
                    f"deliverability and inflates costs. Move them to a suppression list "
                    f"after a final re-engagement attempt."
                ),
                evidence=f"Dormant segment: {dormant_count:,} / {total_subs:,} subscribers",
                impact_estimate="Improve deliverability score, reduce ESP costs",
            ))

    # At-risk re-engagement
    at_risk_count = seg_dist.get("At-Risk", 0)
    if at_risk_count > 0:
        at_risk_pct = at_risk_count / total_subs if total_subs > 0 else 0
        recs.append(Recommendation(
            category="List Hygiene",
            priority="medium",
            title=f"Launch re-engagement campaign for {at_risk_count:,} at-risk subscribers",
            description=(
                f"{at_risk_count:,} subscribers ({at_risk_pct:.0%} of list) show declining "
                f"engagement. Deploy a 3-touch re-engagement sequence: (1) 'We miss you' "
                f"with incentive, (2) preference center update, (3) final opt-in "
                f"confirmation. Suppress non-responders after 30 days."
            ),
            evidence=f"At-Risk segment: {at_risk_count:,} subscribers",
            impact_estimate="Recover 10-20% of at-risk subscribers, clean the rest",
        ))

    # Overall list health
    bounce_mean = list_health.get("bounce_stats", {}).get("mean", 0)
    if bounce_mean > 0.03:
        recs.append(Recommendation(
            category="List Hygiene",
            priority="high",
            title="Average bounce rate exceeds industry threshold",
            description=(
                f"Your average bounce rate of {bounce_mean:.1%} exceeds the 3% industry "
                f"benchmark. This risks ESP throttling and IP reputation damage. "
                f"Implement real-time email verification at signup and run a full "
                f"list cleaning pass immediately."
            ),
            evidence=f"Avg bounce rate: {bounce_mean:.1%} (threshold: 3%)",
            impact_estimate="Prevent deliverability degradation",
        ))

    return recs


def _ab_test_recommendations(analysis_results: dict) -> List[Recommendation]:
    """Suggest A/B tests based on patterns found in the analysis."""
    recs = []
    features = analysis_results["subject_lines"]["feature_impact"]
    times = analysis_results["send_times"]

    # Subject line A/B tests
    pers_lift = features.get("has_personalization", {}).get("lift", 0)
    if pers_lift > 0.01:
        recs.append(Recommendation(
            category="A/B Test",
            priority="medium",
            title="A/B test: Personalization depth",
            description=(
                "First-name personalization works. Test deeper personalization: "
                "past purchase references, location-based content, or behavioral "
                "triggers vs simple name insertion."
            ),
            evidence=f"Current personalization lift: +{pers_lift:.1%}",
            impact_estimate="Additional +1-3% open rate from advanced personalization",
        ))

    # Send time A/B test
    best_h = times["best_hour"]
    recs.append(Recommendation(
        category="A/B Test",
        priority="medium",
        title=f"A/B test: {best_h}:00 vs {best_h-1}:00 vs {best_h+1}:00 send times",
        description=(
            f"The {best_h}:00 hour performs best overall. Run a three-way split test "
            f"across {best_h-1}:00, {best_h}:00, and {best_h+1}:00 with identical "
            f"content to find the precise optimal minute window."
        ),
        evidence=f"Current best hour: {best_h}:00 ({times['best_hour_rate']:.1%})",
        impact_estimate="+0.5-1.5% open rate from fine-tuning send time",
    ))

    # Emoji A/B test
    emoji_lift = features.get("has_emoji", {}).get("lift", 0)
    recs.append(Recommendation(
        category="A/B Test",
        priority="low",
        title="A/B test: Emoji placement and type",
        description=(
            "Test emojis at the start vs end of subject lines, and "
            "topical emojis (matching content) vs generic attention-grabbers. "
            "Run for at least 10 campaigns to reach statistical significance."
        ),
        evidence=f"Current emoji effect: {'+' if emoji_lift >= 0 else ''}{emoji_lift:.1%}",
        impact_estimate="Clarify whether emojis help or hurt for your audience",
    ))

    # Campaign type A/B test
    recs.append(Recommendation(
        category="A/B Test",
        priority="low",
        title="A/B test: Educational vs promotional content mix",
        description=(
            "Test the ratio of value-driven educational content to "
            "promotional offers. Try 80/20 vs 60/40 content-to-promotion "
            "ratios over a 4-week period and measure long-term engagement."
        ),
        evidence="Industry benchmarks suggest educational content improves retention",
        impact_estimate="Reduce unsubscribe rate, improve long-term CLV",
    ))

    # Segmentation-based test
    seg = analysis_results["segmentation"]
    if "At-Risk" in seg.get("segment_distribution", {}):
        recs.append(Recommendation(
            category="A/B Test",
            priority="high",
            title="A/B test: Re-engagement incentive types",
            description=(
                "For your At-Risk segment, test three re-engagement approaches: "
                "(A) discount/coupon offer, (B) exclusive content access, "
                "(C) simple 'we miss you' emotional appeal. Measure which "
                "drives the highest re-activation rate."
            ),
            evidence="At-Risk segment identified via K-means clustering",
            impact_estimate="Identify best re-engagement strategy for your audience",
        ))

    return recs


def generate_recommendations(analysis_results: dict) -> List[Recommendation]:
    """Generate all recommendations from analysis results.

    Returns a list of Recommendation objects sorted by priority (high first).
    """
    print("[Recommendations] Generating send time recommendations...")
    recs = _send_time_recommendations(analysis_results["send_times"])

    print("[Recommendations] Generating subject line recommendations...")
    recs.extend(_subject_line_recommendations(analysis_results["subject_lines"]))

    print("[Recommendations] Generating list hygiene recommendations...")
    recs.extend(_list_hygiene_recommendations(
        analysis_results["list_health"],
        analysis_results["segmentation"],
    ))

    print("[Recommendations] Generating A/B test suggestions...")
    recs.extend(_ab_test_recommendations(analysis_results))

    # Sort by priority
    priority_order = {"high": 0, "medium": 1, "low": 2}
    recs.sort(key=lambda r: priority_order.get(r.priority, 99))

    print(f"[Recommendations] Generated {len(recs)} recommendations "
          f"({sum(1 for r in recs if r.priority == 'high')} high, "
          f"{sum(1 for r in recs if r.priority == 'medium')} medium, "
          f"{sum(1 for r in recs if r.priority == 'low')} low priority).")

    return recs
