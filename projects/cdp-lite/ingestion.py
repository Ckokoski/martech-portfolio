"""
ingestion.py — Reads customer data from multiple source CSV files.

Normalizes column names, tags each row with its source, and performs
basic validation before handing data to the identity resolution stage.
"""

import os
import re

import pandas as pd


# ---------------------------------------------------------------------------
# Normalisation helpers
# ---------------------------------------------------------------------------

def _normalize_email(val: str) -> str:
    """Lowercase and strip whitespace from an email address."""
    if pd.isna(val) or val == "":
        return ""
    return str(val).strip().lower()


def _normalize_phone(val: str) -> str:
    """Strip a phone number down to digits only (drop formatting)."""
    if pd.isna(val) or val == "":
        return ""
    digits = re.sub(r"\D", "", str(val))
    # Remove leading country code '1' if 11 digits
    if len(digits) == 11 and digits.startswith("1"):
        digits = digits[1:]
    return digits


def _normalize_name(val: str) -> str:
    """Title-case and strip whitespace."""
    if pd.isna(val) or val == "":
        return ""
    return str(val).strip().title()


# ---------------------------------------------------------------------------
# Per-source ingestors
# ---------------------------------------------------------------------------

def ingest_crm(path: str) -> pd.DataFrame:
    """Read CRM CSV and normalise fields."""
    df = pd.read_csv(path, dtype=str).fillna("")
    df["email_norm"] = df["email"].apply(_normalize_email)
    df["phone_norm"] = df.get("phone", pd.Series([""] * len(df))).apply(
        _normalize_phone
    )
    df["first_name_norm"] = df["first_name"].apply(_normalize_name)
    df["last_name_norm"] = df["last_name"].apply(_normalize_name)
    df["_source"] = "crm"
    df["_source_id"] = [f"crm_{i}" for i in range(len(df))]
    return df


def ingest_email(path: str) -> pd.DataFrame:
    """Read email-platform CSV and normalise fields."""
    df = pd.read_csv(path, dtype=str).fillna("")
    df["email_norm"] = df["email"].apply(_normalize_email)
    df["first_name_norm"] = df["first_name"].apply(_normalize_name)
    # Email source has no last name or phone
    df["last_name_norm"] = ""
    df["phone_norm"] = ""
    df["_source"] = "email"
    df["_source_id"] = [f"email_{i}" for i in range(len(df))]
    return df


def ingest_web(path: str) -> pd.DataFrame:
    """Read web analytics CSV and normalise fields."""
    df = pd.read_csv(path, dtype=str).fillna("")
    df["email_norm"] = df["email"].apply(_normalize_email)
    # Web source has no name or phone
    df["first_name_norm"] = ""
    df["last_name_norm"] = ""
    df["phone_norm"] = ""
    df["_source"] = "web"
    df["_source_id"] = [f"web_{i}" for i in range(len(df))]
    return df


def ingest_transactions(path: str) -> pd.DataFrame:
    """Read transaction CSV and normalise fields."""
    df = pd.read_csv(path, dtype=str).fillna("")
    df["email_norm"] = df["email"].apply(_normalize_email)
    df["first_name_norm"] = ""
    df["last_name_norm"] = ""
    df["phone_norm"] = ""
    df["_source"] = "transactions"
    df["_source_id"] = [f"txn_{i}" for i in range(len(df))]
    return df


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def ingest_all(data_dir: str = "data") -> dict[str, pd.DataFrame]:
    """
    Ingest all four source files from *data_dir*.

    Returns a dict of normalised DataFrames keyed by source name, plus
    an ``"all"`` key holding the concatenated superset.
    """
    print("\n=== Ingesting source data ===")

    sources = {}
    loaders = {
        "crm": ("source_crm.csv", ingest_crm),
        "email": ("source_email.csv", ingest_email),
        "web": ("source_web.csv", ingest_web),
        "transactions": ("source_transactions.csv", ingest_transactions),
    }

    for name, (filename, loader) in loaders.items():
        path = os.path.join(data_dir, filename)
        if not os.path.exists(path):
            print(f"  WARNING: {path} not found — skipping {name}")
            continue
        df = loader(path)
        sources[name] = df
        print(f"  [{name:<14}] {len(df):>6,} records ingested")

    # Build a combined frame with a shared schema for matching
    combined = pd.concat(sources.values(), ignore_index=True, sort=False)
    sources["all"] = combined
    print(f"  {'Total':<16}  {len(combined):>6,} records")

    return sources


if __name__ == "__main__":
    ingest_all()
