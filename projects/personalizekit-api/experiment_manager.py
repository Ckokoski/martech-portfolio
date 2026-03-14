"""
experiment_manager.py — A/B test assignment and lifecycle logic.

Handles deterministic variant assignment based on user_id hashing,
experiment state transitions, and automatic winner declaration when
statistical significance is reached.
"""

import hashlib
from models import (
    get_experiment,
    get_variants_for_experiment,
    update_experiment_status,
    get_variant_stats,
)
from stats import chi_squared_test

# Minimum impressions per variant before we even check for significance.
MIN_SAMPLE_SIZE = 100


def assign_variant(experiment_id, user_id, segment=None):
    """
    Deterministically assign a user to a variant.

    The assignment is stable: the same user_id always sees the same
    variant for a given experiment, which prevents flickering.

    Parameters
    ----------
    experiment_id : int
    user_id : str
    segment : str or None — if provided, only serve if the experiment
              targets this segment (or 'all').

    Returns
    -------
    dict with variant info and content, or None if the experiment
    doesn't apply.
    """
    experiment = get_experiment(experiment_id)
    if not experiment:
        return None

    # Only serve running experiments
    if experiment["status"] != "running":
        return None

    # Segment gate: experiment must target the user's segment or 'all'
    if segment and experiment["segment"] not in ("all", segment):
        return None

    variants = experiment["variants"]
    if not variants:
        return None

    # Deterministic hash → bucket
    hash_input = f"{experiment_id}:{user_id}"
    digest = hashlib.sha256(hash_input.encode()).hexdigest()
    bucket = int(digest[:8], 16) % 10000  # 0–9999

    # Walk the cumulative weight distribution
    total_weight = sum(v["weight"] for v in variants)
    cumulative = 0
    chosen = variants[0]
    for v in variants:
        cumulative += v["weight"] / total_weight * 10000
        if bucket < cumulative:
            chosen = v
            break

    return {
        "experiment_id": experiment_id,
        "experiment_name": experiment["name"],
        "variant_id": chosen["id"],
        "variant_name": chosen["name"],
        "content": chosen["content"],
    }


def check_and_declare_winner(experiment_id):
    """
    Evaluate whether an experiment has a statistically significant winner.

    If the chi-squared test across variants is significant (p < 0.05) and
    every variant has at least MIN_SAMPLE_SIZE impressions, the experiment
    is moved to 'completed' and the winning variant is recorded.

    Returns
    -------
    dict or None — winner info if declared, else None.
    """
    variants = get_variants_for_experiment(experiment_id)
    if len(variants) < 2:
        return None

    # Build stats payload
    stats_data = []
    for v in variants:
        s = get_variant_stats(v["id"])
        if s["impressions"] < MIN_SAMPLE_SIZE:
            return None  # Not enough data yet
        stats_data.append({
            "id": v["id"],
            "name": v["name"],
            "impressions": s["impressions"],
            "conversions": s["conversions"],
        })

    result = chi_squared_test(stats_data)
    if not result["significant"]:
        return None

    # Find the best-performing variant
    best = max(stats_data, key=lambda v: v["conversions"] / v["impressions"] if v["impressions"] else 0)
    update_experiment_status(experiment_id, "completed", winner_variant=best["id"])

    return {
        "experiment_id": experiment_id,
        "winner_variant_id": best["id"],
        "winner_name": best["name"],
        "p_value": result["p_value"],
    }


def start_experiment(experiment_id):
    """Transition an experiment to the 'running' state."""
    update_experiment_status(experiment_id, "running")


def pause_experiment(experiment_id):
    """Pause a running experiment."""
    update_experiment_status(experiment_id, "paused")


def resume_experiment(experiment_id):
    """Resume a paused experiment."""
    update_experiment_status(experiment_id, "running")
