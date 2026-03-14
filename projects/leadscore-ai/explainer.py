"""
explainer.py — SHAP-based model explainability for lead scoring.

Generates global feature importance rankings and individual lead
explanations using SHAP (SHapley Additive exPlanations).
"""

import numpy as np
import pandas as pd
import shap


def compute_shap_values(results: dict, max_samples: int = 1000) -> dict:
    """
    Compute SHAP values for the test set using TreeExplainer.

    Parameters
    ----------
    results : dict
        Output from model.train_model().
    max_samples : int
        Max samples to explain (SHAP can be slow on large datasets).

    Returns
    -------
    dict
        SHAP values, expected value, feature names, and sample data.
    """
    model = results["model"]
    X_test = results["X_test"]
    feature_cols = results["feature_cols"]

    # Subsample if test set is large
    n = min(max_samples, len(X_test))
    indices = np.random.RandomState(42).choice(len(X_test), size=n, replace=False)
    X_sample = X_test[indices]

    print(f"  -> Computing SHAP values for {n:,} samples...")

    # TreeExplainer is fast and exact for tree-based models
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X_sample)

    # Get expected value (base rate)
    expected_value = explainer.expected_value
    # For binary classification, shap_values may be a single array
    if isinstance(expected_value, np.ndarray):
        expected_value = expected_value[1] if len(expected_value) > 1 else expected_value[0]

    print(f"     Base value (expected): {expected_value:.4f}")

    return {
        "shap_values": shap_values,
        "expected_value": expected_value,
        "X_sample": X_sample,
        "feature_names": feature_cols,
        "sample_indices": indices,
    }


def get_global_importance(shap_results: dict, top_n: int = 15) -> pd.DataFrame:
    """
    Compute global feature importance from mean |SHAP values|.

    Parameters
    ----------
    shap_results : dict
        Output from compute_shap_values().
    top_n : int
        Number of top features to return.

    Returns
    -------
    pd.DataFrame
        Feature importance ranked by mean absolute SHAP value.
    """
    shap_values = shap_results["shap_values"]
    feature_names = shap_results["feature_names"]

    # Mean absolute SHAP value per feature
    mean_abs_shap = np.abs(shap_values).mean(axis=0)

    importance = pd.DataFrame({
        "feature": feature_names,
        "mean_abs_shap": mean_abs_shap,
    }).sort_values("mean_abs_shap", ascending=False).reset_index(drop=True)

    print(f"\n  Top {top_n} Features by SHAP Importance:")
    print(f"  {'-' * 50}")
    for _, row in importance.head(top_n).iterrows():
        bar = "█" * int(row["mean_abs_shap"] / importance["mean_abs_shap"].max() * 20)
        print(f"    {row['feature']:<35s} {row['mean_abs_shap']:.4f}  {bar}")

    return importance.head(top_n)


def get_individual_explanation(
    shap_results: dict,
    results: dict,
    score_type: str = "high",
) -> dict:
    """
    Get SHAP explanation for a sample individual lead.

    Parameters
    ----------
    shap_results : dict
        Output from compute_shap_values().
    results : dict
        Output from model.train_model().
    score_type : str
        "high" for top-scoring lead, "low" for lowest-scoring lead.

    Returns
    -------
    dict
        Individual SHAP values, feature values, and lead metadata.
    """
    scores = results["y_prob_test"][shap_results["sample_indices"]]

    if score_type == "high":
        idx = np.argmax(scores)
    else:
        idx = np.argmin(scores)

    shap_vals = shap_results["shap_values"][idx]
    feature_vals = shap_results["X_sample"][idx]
    feature_names = shap_results["feature_names"]

    # Sort by absolute SHAP value
    sorted_idx = np.argsort(np.abs(shap_vals))[::-1]

    explanation = pd.DataFrame({
        "feature": [feature_names[i] for i in sorted_idx],
        "value": [feature_vals[i] for i in sorted_idx],
        "shap_value": [shap_vals[i] for i in sorted_idx],
    })

    score = scores[idx] * 100
    label = "HIGH-SCORE" if score_type == "high" else "LOW-SCORE"
    print(f"\n  {label} Lead Explanation (Score: {score:.1f}):")
    print(f"  {'-' * 60}")
    for _, row in explanation.head(10).iterrows():
        direction = "+" if row["shap_value"] > 0 else ""
        print(
            f"    {row['feature']:<35s} "
            f"val={row['value']:<8.2f} "
            f"SHAP={direction}{row['shap_value']:.4f}"
        )

    return {
        "explanation_df": explanation,
        "score": score,
        "score_type": score_type,
        "shap_values": shap_vals,
        "feature_values": feature_vals,
        "expected_value": shap_results["expected_value"],
        "feature_names": feature_names,
    }


if __name__ == "__main__":
    from data_generator import generate_leads
    from feature_engineering import engineer_features
    from model import train_model

    leads = generate_leads()
    enriched = engineer_features(leads)
    results = train_model(enriched)
    shap_results = compute_shap_values(results)
    importance = get_global_importance(shap_results)
    high_exp = get_individual_explanation(shap_results, results, "high")
    low_exp = get_individual_explanation(shap_results, results, "low")
