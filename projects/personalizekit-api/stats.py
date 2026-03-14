"""
stats.py — Statistical engine for PersonalizeKit A/B testing.

Provides chi-squared tests, z-tests for proportions, confidence intervals,
minimum detectable effect (MDE) calculations, and required sample size
estimation. Used by the reporting endpoint to determine significance.
"""

import math

# We use scipy for production-quality statistical functions.
from scipy import stats as sp_stats


# ---------------------------------------------------------------------------
# Core statistical tests
# ---------------------------------------------------------------------------

def chi_squared_test(variants_data):
    """
    Run a chi-squared test across all variants to check if conversion rates
    differ significantly.

    Parameters
    ----------
    variants_data : list[dict]
        Each dict must have 'impressions' and 'conversions' keys.

    Returns
    -------
    dict with chi2 statistic, p_value, degrees_of_freedom, significant (bool)
    """
    if len(variants_data) < 2:
        return {"chi2": 0, "p_value": 1.0, "degrees_of_freedom": 0, "significant": False}

    # Build the observed 2×k contingency table:
    #   row 0 = conversions,  row 1 = non-conversions
    observed = []
    for v in variants_data:
        imp = v["impressions"]
        conv = v["conversions"]
        non_conv = imp - conv
        if imp <= 0:
            continue
        observed.append([conv, non_conv])

    if len(observed) < 2:
        return {"chi2": 0, "p_value": 1.0, "degrees_of_freedom": 0, "significant": False}

    chi2, p_value, dof, _ = sp_stats.chi2_contingency(observed)

    return {
        "chi2": round(chi2, 4),
        "p_value": round(p_value, 6),
        "degrees_of_freedom": dof,
        "significant": p_value < 0.05,
    }


def z_test_two_proportions(n1, c1, n2, c2):
    """
    Two-proportion z-test comparing variant A (control) to variant B.

    Parameters
    ----------
    n1, c1 : int — impressions and conversions for variant A
    n2, c2 : int — impressions and conversions for variant B

    Returns
    -------
    dict with z_score, p_value, significant
    """
    if n1 == 0 or n2 == 0:
        return {"z_score": 0, "p_value": 1.0, "significant": False}

    p1 = c1 / n1
    p2 = c2 / n2

    # Pooled proportion
    p_pool = (c1 + c2) / (n1 + n2)

    # Avoid division by zero when pooled proportion is 0 or 1
    if p_pool == 0 or p_pool == 1:
        return {"z_score": 0, "p_value": 1.0, "significant": False}

    se = math.sqrt(p_pool * (1 - p_pool) * (1 / n1 + 1 / n2))
    z = (p1 - p2) / se

    # Two-tailed p-value
    p_value = 2 * (1 - sp_stats.norm.cdf(abs(z)))

    return {
        "z_score": round(z, 4),
        "p_value": round(p_value, 6),
        "significant": p_value < 0.05,
    }


# ---------------------------------------------------------------------------
# Confidence intervals
# ---------------------------------------------------------------------------

def conversion_rate_ci(impressions, conversions, confidence=0.95):
    """
    Compute a Wald confidence interval for a conversion rate.

    Returns
    -------
    dict with rate, lower, upper, confidence_level
    """
    if impressions == 0:
        return {"rate": 0, "lower": 0, "upper": 0, "confidence_level": confidence}

    p = conversions / impressions
    z = sp_stats.norm.ppf(1 - (1 - confidence) / 2)
    se = math.sqrt(p * (1 - p) / impressions)

    lower = max(0, p - z * se)
    upper = min(1, p + z * se)

    return {
        "rate": round(p, 6),
        "lower": round(lower, 6),
        "upper": round(upper, 6),
        "confidence_level": confidence,
    }


# ---------------------------------------------------------------------------
# Sample-size & MDE estimation
# ---------------------------------------------------------------------------

def required_sample_size(baseline_rate, mde, alpha=0.05, power=0.80):
    """
    Estimate per-variant sample size needed to detect a given MDE.

    Parameters
    ----------
    baseline_rate : float — current conversion rate (e.g. 0.05 for 5 %)
    mde : float — minimum detectable effect as absolute difference (e.g. 0.01)
    alpha : float — significance level
    power : float — statistical power (1 - beta)

    Returns
    -------
    int — required impressions per variant
    """
    if baseline_rate <= 0 or baseline_rate >= 1 or mde <= 0:
        return 0

    p1 = baseline_rate
    p2 = baseline_rate + mde

    z_alpha = sp_stats.norm.ppf(1 - alpha / 2)
    z_beta = sp_stats.norm.ppf(power)

    numerator = (z_alpha * math.sqrt(2 * p1 * (1 - p1)) + z_beta * math.sqrt(
        p1 * (1 - p1) + p2 * (1 - p2)
    )) ** 2
    denominator = (p2 - p1) ** 2

    return math.ceil(numerator / denominator)


def minimum_detectable_effect(impressions, baseline_rate, alpha=0.05, power=0.80):
    """
    Given a sample size, compute the smallest effect we can reliably detect.

    Returns
    -------
    float — absolute MDE (e.g. 0.012 means 1.2 percentage points)
    """
    if impressions <= 0 or baseline_rate <= 0 or baseline_rate >= 1:
        return 0.0

    z_alpha = sp_stats.norm.ppf(1 - alpha / 2)
    z_beta = sp_stats.norm.ppf(power)

    se = math.sqrt(2 * baseline_rate * (1 - baseline_rate) / impressions)
    mde = (z_alpha + z_beta) * se

    return round(mde, 6)


# ---------------------------------------------------------------------------
# Full report builder
# ---------------------------------------------------------------------------

def build_report(variants_data):
    """
    Generate a comprehensive statistical report for an experiment.

    Parameters
    ----------
    variants_data : list[dict]
        Each dict has keys: id, name, impressions, conversions

    Returns
    -------
    dict — full report with per-variant stats, overall chi-squared,
           pairwise z-tests, significance flag, and sample-size guidance.
    """
    # Per-variant confidence intervals
    for v in variants_data:
        ci = conversion_rate_ci(v["impressions"], v["conversions"])
        v["conversion_rate"] = round(ci["rate"] * 100, 2)
        v["ci_lower"] = round(ci["lower"] * 100, 2)
        v["ci_upper"] = round(ci["upper"] * 100, 2)

    # Overall chi-squared test
    chi2_result = chi_squared_test(variants_data)

    # Pairwise z-tests (compare every pair)
    pairwise = []
    for i in range(len(variants_data)):
        for j in range(i + 1, len(variants_data)):
            a = variants_data[i]
            b = variants_data[j]
            z_result = z_test_two_proportions(
                a["impressions"], a["conversions"],
                b["impressions"], b["conversions"],
            )
            pairwise.append({
                "variant_a": a["name"],
                "variant_b": b["name"],
                **z_result,
            })

    # Determine winner: the variant with the highest conversion rate,
    # but only if the overall test is significant.
    winner = None
    if chi2_result["significant"] and variants_data:
        best = max(variants_data, key=lambda v: v["conversion_rate"])
        winner = {"variant_id": best["id"], "variant_name": best["name"],
                  "conversion_rate": best["conversion_rate"]}

    # Sample-size guidance based on the first variant as baseline
    guidance = {}
    if variants_data and variants_data[0]["impressions"] > 0:
        baseline = variants_data[0]["conversions"] / variants_data[0]["impressions"]
        if 0 < baseline < 1:
            guidance["baseline_rate"] = round(baseline * 100, 2)
            guidance["mde_at_current_n"] = round(
                minimum_detectable_effect(variants_data[0]["impressions"], baseline) * 100, 2
            )
            guidance["sample_needed_for_1pct_mde"] = required_sample_size(baseline, 0.01)
            guidance["sample_needed_for_2pct_mde"] = required_sample_size(baseline, 0.02)

    return {
        "variants": variants_data,
        "chi_squared": chi2_result,
        "pairwise_tests": pairwise,
        "winner": winner,
        "sample_size_guidance": guidance,
    }
