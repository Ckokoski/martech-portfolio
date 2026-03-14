"""
Markov Chain Attribution Model (Data-Driven)

Computes attribution using the "removal effect" method:
1. Build a transition probability matrix from observed journeys
   (channel states + Start/Conversion/Null absorbing states).
2. Calculate the baseline conversion probability.
3. For each channel, remove it and recalculate conversion probability.
4. The removal effect = (baseline - removed) / baseline.
5. Normalize removal effects to distribute credit proportionally.

Use case: Data-driven attribution that captures each channel's true
incremental contribution to conversion, accounting for channel interactions.
"""

import numpy as np
import pandas as pd
import networkx as nx
from itertools import product


# Special states for the Markov chain
START = "(start)"
CONVERSION = "(conversion)"
NULL = "(null)"


def markov_attribution(touchpoints_df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply Markov chain removal-effect attribution.

    Args:
        touchpoints_df: DataFrame with touchpoint data.

    Returns:
        DataFrame with [channel, attributed_conversions, attributed_revenue].
    """
    # ── Step 1: Build journey paths ──────────────────────────────────────
    paths = _build_paths(touchpoints_df)

    # ── Step 2: Build transition matrix ──────────────────────────────────
    transition_counts, states = _build_transition_counts(paths)
    transition_matrix = _normalize_transitions(transition_counts, states)

    # ── Step 3: Calculate baseline conversion rate ───────────────────────
    baseline_conv_rate = _calculate_conversion_rate(transition_matrix, states)

    # ── Step 4: Calculate removal effects ────────────────────────────────
    channels = [s for s in states if s not in (START, CONVERSION, NULL)]
    removal_effects = {}

    for channel in channels:
        removed_rate = _calculate_conversion_rate(
            transition_matrix, states, remove_channel=channel
        )
        if baseline_conv_rate > 0:
            removal_effects[channel] = (
                (baseline_conv_rate - removed_rate) / baseline_conv_rate
            )
        else:
            removal_effects[channel] = 0.0

    # ── Step 5: Normalize removal effects to get attribution weights ─────
    total_effect = sum(removal_effects.values())
    if total_effect > 0:
        attribution_weights = {
            ch: effect / total_effect
            for ch, effect in removal_effects.items()
        }
    else:
        # Fallback: equal distribution
        attribution_weights = {ch: 1.0 / len(channels) for ch in channels}

    # ── Step 6: Distribute conversions and revenue ───────────────────────
    total_conversions = touchpoints_df["converted"].sum()
    total_revenue = touchpoints_df["revenue"].sum()

    results = []
    for channel in channels:
        weight = attribution_weights.get(channel, 0)
        results.append({
            "channel": channel,
            "attributed_conversions": weight * total_conversions,
            "attributed_revenue": weight * total_revenue,
        })

    result_df = pd.DataFrame(results)
    result_df["model"] = "Markov Chain"
    return result_df


def get_transition_matrix(touchpoints_df: pd.DataFrame) -> pd.DataFrame:
    """
    Build and return the transition probability matrix as a DataFrame.
    Used for the heatmap visualization.

    Args:
        touchpoints_df: DataFrame with touchpoint data.

    Returns:
        DataFrame where rows are 'from' states and columns are 'to' states,
        values are transition probabilities.
    """
    paths = _build_paths(touchpoints_df)
    transition_counts, states = _build_transition_counts(paths)
    transition_matrix = _normalize_transitions(transition_counts, states)

    # Convert to DataFrame, excluding start/conversion/null for readability
    channel_states = [s for s in states if s not in (START, CONVERSION, NULL)]
    all_states = [START] + channel_states + [CONVERSION, NULL]

    matrix_df = pd.DataFrame(
        [[transition_matrix.get((s1, s2), 0.0) for s2 in all_states] for s1 in all_states],
        index=all_states,
        columns=all_states,
    )
    return matrix_df


def _build_paths(touchpoints_df: pd.DataFrame) -> list[list[str]]:
    """
    Convert touchpoint data into journey paths.
    Each path is a list: [START, channel1, channel2, ..., CONVERSION or NULL]
    """
    paths = []
    grouped = touchpoints_df.sort_values(
        ["journey_id", "touchpoint_order"]
    ).groupby("journey_id")

    for journey_id, group in grouped:
        path = [START]
        path.extend(group["channel"].tolist())

        # Check if journey converted
        if group["converted"].any():
            path.append(CONVERSION)
        else:
            path.append(NULL)

        paths.append(path)

    return paths


def _build_transition_counts(
    paths: list[list[str]],
) -> tuple[dict, list[str]]:
    """
    Count transitions between states across all paths.

    Returns:
        Tuple of (transition_counts dict, list of unique states).
    """
    transition_counts: dict[tuple[str, str], int] = {}
    states_set: set[str] = set()

    for path in paths:
        for i in range(len(path) - 1):
            from_state = path[i]
            to_state = path[i + 1]
            states_set.add(from_state)
            states_set.add(to_state)
            key = (from_state, to_state)
            transition_counts[key] = transition_counts.get(key, 0) + 1

    states = sorted(states_set)
    return transition_counts, states


def _normalize_transitions(
    transition_counts: dict[tuple[str, str], int],
    states: list[str],
) -> dict[tuple[str, str], float]:
    """
    Normalize transition counts to probabilities.
    Each row (from_state) sums to 1.0.
    """
    transition_matrix: dict[tuple[str, str], float] = {}

    for from_state in states:
        row_total = sum(
            transition_counts.get((from_state, to_state), 0)
            for to_state in states
        )
        for to_state in states:
            count = transition_counts.get((from_state, to_state), 0)
            if row_total > 0:
                transition_matrix[(from_state, to_state)] = count / row_total
            else:
                transition_matrix[(from_state, to_state)] = 0.0

    return transition_matrix


def _calculate_conversion_rate(
    transition_matrix: dict[tuple[str, str], float],
    states: list[str],
    remove_channel: str | None = None,
) -> float:
    """
    Calculate the probability of reaching CONVERSION from START
    using absorbing Markov chain math.

    If remove_channel is specified, that channel is removed and its
    transitions are redirected to NULL.

    The approach:
    - Transient states: START + channels (excluding removed)
    - Absorbing states: CONVERSION, NULL
    - Build the Q matrix (transient -> transient transitions)
    - Build the R matrix (transient -> absorbing transitions)
    - Fundamental matrix N = (I - Q)^(-1)
    - Absorption probabilities B = N * R
    - Return B[START, CONVERSION]
    """
    # Define transient and absorbing states
    absorbing = [CONVERSION, NULL]
    transient = [s for s in states if s not in absorbing]

    if remove_channel and remove_channel in transient:
        transient = [s for s in transient if s != remove_channel]

    n_transient = len(transient)
    n_absorbing = len(absorbing)

    if n_transient == 0:
        return 0.0

    transient_idx = {s: i for i, s in enumerate(transient)}
    absorbing_idx = {s: i for i, s in enumerate(absorbing)}

    # Build Q matrix (transient -> transient)
    Q = np.zeros((n_transient, n_transient))
    # Build R matrix (transient -> absorbing)
    R = np.zeros((n_transient, n_absorbing))

    for from_state in transient:
        i = transient_idx[from_state]
        row_sum = 0.0

        for to_state in transient:
            j = transient_idx[to_state]
            prob = transition_matrix.get((from_state, to_state), 0.0)
            Q[i, j] = prob
            row_sum += prob

        for to_state in absorbing:
            j = absorbing_idx[to_state]
            prob = transition_matrix.get((from_state, to_state), 0.0)
            R[i, j] = prob
            row_sum += prob

        # If a channel was removed, redirect its probability to NULL
        if remove_channel:
            removed_prob = transition_matrix.get(
                (from_state, remove_channel), 0.0
            )
            if removed_prob > 0:
                null_idx = absorbing_idx[NULL]
                R[i, null_idx] += removed_prob

    # Fundamental matrix: N = (I - Q)^(-1)
    try:
        I = np.eye(n_transient)
        N = np.linalg.inv(I - Q)
    except np.linalg.LinAlgError:
        return 0.0

    # Absorption probability matrix: B = N * R
    B = N @ R

    # Return P(conversion | start)
    start_idx = transient_idx.get(START)
    if start_idx is None:
        return 0.0

    conv_idx = absorbing_idx[CONVERSION]
    return float(B[start_idx, conv_idx])
