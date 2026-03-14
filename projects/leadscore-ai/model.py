"""
model.py — Trains and evaluates an XGBoost lead scoring classifier.

Handles train/test splitting, model training, probability calibration,
and comprehensive evaluation metrics.
"""

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    roc_auc_score, roc_curve, precision_recall_curve,
    average_precision_score, confusion_matrix,
    classification_report, f1_score,
)
from sklearn.calibration import calibration_curve
from xgboost import XGBClassifier

from feature_engineering import get_feature_columns

SEED = 42
TEST_SIZE = 0.2

# Lead qualification thresholds (applied to 0-100 score)
MQL_THRESHOLD = 50  # Marketing Qualified Lead
SQL_THRESHOLD = 75  # Sales Qualified Lead


def train_model(
    df: pd.DataFrame,
    feature_cols: list[str] | None = None,
) -> dict:
    """
    Train an XGBoost classifier on the lead data.

    Parameters
    ----------
    df : pd.DataFrame
        Feature-engineered lead data.
    feature_cols : list[str], optional
        Columns to use as features. If None, auto-detected.

    Returns
    -------
    dict
        Contains model, train/test splits, predictions, and metrics.
    """
    if feature_cols is None:
        feature_cols = get_feature_columns(df)

    X = df[feature_cols].values
    y = df["converted"].values

    # -- Train / test split -----------------------------------------------
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=TEST_SIZE, random_state=SEED, stratify=y,
    )

    print(f"  -> Train size: {len(X_train):,}  |  Test size: {len(X_test):,}")
    print(f"     Train conversion rate: {y_train.mean():.1%}")
    print(f"     Test  conversion rate: {y_test.mean():.1%}")

    # -- Train XGBoost ----------------------------------------------------
    model = XGBClassifier(
        n_estimators=300,
        max_depth=5,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        min_child_weight=3,
        scale_pos_weight=(1 - y_train.mean()) / y_train.mean(),
        random_state=SEED,
        eval_metric="logloss",
        use_label_encoder=False,
        verbosity=0,
    )

    model.fit(
        X_train, y_train,
        eval_set=[(X_test, y_test)],
        verbose=False,
    )

    # -- Predictions ------------------------------------------------------
    y_prob_train = model.predict_proba(X_train)[:, 1]
    y_prob_test = model.predict_proba(X_test)[:, 1]

    # Scale probabilities to 0-100 lead score
    scores_test = y_prob_test * 100
    scores_train = y_prob_train * 100

    # Binary predictions at MQL threshold
    y_pred_test = (scores_test >= MQL_THRESHOLD).astype(int)

    return {
        "model": model,
        "feature_cols": feature_cols,
        "X_train": X_train, "X_test": X_test,
        "y_train": y_train, "y_test": y_test,
        "y_prob_train": y_prob_train, "y_prob_test": y_prob_test,
        "scores_train": scores_train, "scores_test": scores_test,
        "y_pred_test": y_pred_test,
    }


def evaluate_model(results: dict) -> dict:
    """
    Compute evaluation metrics from model results.

    Returns
    -------
    dict
        Comprehensive metrics including AUC, precision-recall, calibration, etc.
    """
    y_test = results["y_test"]
    y_prob = results["y_prob_test"]
    y_pred = results["y_pred_test"]
    scores = results["scores_test"]

    # -- Core metrics -----------------------------------------------------
    auc_roc = roc_auc_score(y_test, y_prob)
    avg_precision = average_precision_score(y_test, y_prob)
    f1 = f1_score(y_test, y_pred)
    cm = confusion_matrix(y_test, y_pred)
    report = classification_report(y_test, y_pred, output_dict=True)

    print(f"\n  Model Evaluation Results:")
    print(f"  {'-' * 40}")
    print(f"  AUC-ROC:            {auc_roc:.4f}")
    print(f"  Average Precision:  {avg_precision:.4f}")
    print(f"  F1 Score (MQL):     {f1:.4f}")
    print(f"  {'-' * 40}")
    print(f"  Confusion Matrix (threshold={MQL_THRESHOLD}):")
    print(f"    TN={cm[0][0]:,}  FP={cm[0][1]:,}")
    print(f"    FN={cm[1][0]:,}  TP={cm[1][1]:,}")

    # -- Curves -----------------------------------------------------------
    fpr, tpr, roc_thresholds = roc_curve(y_test, y_prob)
    precision, recall, pr_thresholds = precision_recall_curve(y_test, y_prob)

    # -- Calibration ------------------------------------------------------
    cal_fraction, cal_mean_predicted = calibration_curve(
        y_test, y_prob, n_bins=10, strategy="uniform",
    )

    # -- Score distribution stats -----------------------------------------
    mql_count = (scores >= MQL_THRESHOLD).sum()
    sql_count = (scores >= SQL_THRESHOLD).sum()
    total = len(scores)
    print(f"\n  Lead Qualification (test set):")
    print(f"    MQL (score >= {MQL_THRESHOLD}): {mql_count:,} ({mql_count/total:.1%})")
    print(f"    SQL (score >= {SQL_THRESHOLD}): {sql_count:,} ({sql_count/total:.1%})")

    return {
        "auc_roc": auc_roc,
        "avg_precision": avg_precision,
        "f1_score": f1,
        "confusion_matrix": cm,
        "classification_report": report,
        "fpr": fpr, "tpr": tpr,
        "precision_curve": precision, "recall_curve": recall,
        "cal_fraction": cal_fraction, "cal_mean_predicted": cal_mean_predicted,
        "mql_threshold": MQL_THRESHOLD,
        "sql_threshold": SQL_THRESHOLD,
    }


def score_all_leads(df: pd.DataFrame, results: dict) -> pd.DataFrame:
    """
    Score the entire lead dataset and add score + qualification tier.
    """
    feature_cols = results["feature_cols"]
    model = results["model"]

    X_all = df[feature_cols].values
    probs = model.predict_proba(X_all)[:, 1]
    scores = probs * 100

    scored = df.copy()
    scored["lead_score"] = np.round(scores, 1)
    scored["lead_tier"] = pd.cut(
        scored["lead_score"],
        bins=[-1, MQL_THRESHOLD, SQL_THRESHOLD, 101],
        labels=["Cold", "MQL", "SQL"],
    )
    scored = scored.sort_values("lead_score", ascending=False).reset_index(drop=True)

    print(f"\n  Lead Score Distribution:")
    print(f"    Mean:   {scored['lead_score'].mean():.1f}")
    print(f"    Median: {scored['lead_score'].median():.1f}")
    print(f"    Std:    {scored['lead_score'].std():.1f}")
    print(f"\n  Tier Breakdown:")
    tier_counts = scored["lead_tier"].value_counts()
    for tier in ["SQL", "MQL", "Cold"]:
        count = tier_counts.get(tier, 0)
        print(f"    {tier}: {count:,} ({count/len(scored):.1%})")

    return scored


if __name__ == "__main__":
    from data_generator import generate_leads
    from feature_engineering import engineer_features

    leads = generate_leads()
    enriched = engineer_features(leads)
    results = train_model(enriched)
    metrics = evaluate_model(results)
