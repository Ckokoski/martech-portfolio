"""
identity_resolution.py — Matching and deduplication logic.

Three-pass identity resolution:
  1. Deterministic email match (exact, normalised)
  2. Deterministic phone match (digits-only)
  3. Fuzzy name + company match (thefuzz, threshold 85 %)

Each record is assigned to a *cluster_id* representing a single real person.
A confidence score is attached to every match.
"""

from __future__ import annotations

import time
from collections import defaultdict

import pandas as pd
from thefuzz import fuzz

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
FUZZY_THRESHOLD = 85  # minimum token_sort_ratio to consider a fuzzy match


# ---------------------------------------------------------------------------
# Union-Find for efficient cluster merging
# ---------------------------------------------------------------------------

class UnionFind:
    """Disjoint-set / union-find with path compression and union by rank."""

    def __init__(self) -> None:
        self.parent: dict[str, str] = {}
        self.rank: dict[str, int] = {}

    def find(self, x: str) -> str:
        if x not in self.parent:
            self.parent[x] = x
            self.rank[x] = 0
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])  # path compression
        return self.parent[x]

    def union(self, a: str, b: str) -> None:
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return
        # union by rank
        if self.rank[ra] < self.rank[rb]:
            ra, rb = rb, ra
        self.parent[rb] = ra
        if self.rank[ra] == self.rank[rb]:
            self.rank[ra] += 1


# ---------------------------------------------------------------------------
# Pass 1 — Deterministic email match
# ---------------------------------------------------------------------------

def _match_by_email(df: pd.DataFrame, uf: UnionFind,
                    match_log: list[dict]) -> int:
    """
    Exact email match: group all rows that share the same normalised email.
    Returns the number of merge operations performed.
    """
    merges = 0
    email_groups: dict[str, list[str]] = defaultdict(list)
    for _, row in df.iterrows():
        email = row.get("email_norm", "")
        if email:
            email_groups[email].append(row["_source_id"])

    for email, ids in email_groups.items():
        if len(ids) < 2:
            continue
        anchor = ids[0]
        for other in ids[1:]:
            uf.union(anchor, other)
            merges += 1
            match_log.append({
                "id_a": anchor,
                "id_b": other,
                "method": "email_exact",
                "key": email,
                "confidence": 1.0,
            })
    return merges


# ---------------------------------------------------------------------------
# Pass 2 — Deterministic phone match
# ---------------------------------------------------------------------------

def _match_by_phone(df: pd.DataFrame, uf: UnionFind,
                    match_log: list[dict]) -> int:
    """
    Exact phone match on normalised (digits-only) phone numbers.
    Only considers records that have a non-empty phone_norm.
    """
    merges = 0
    phone_groups: dict[str, list[str]] = defaultdict(list)
    for _, row in df.iterrows():
        phone = row.get("phone_norm", "")
        if phone and len(phone) == 10:  # valid US phone
            phone_groups[phone].append(row["_source_id"])

    for phone, ids in phone_groups.items():
        if len(ids) < 2:
            continue
        anchor = ids[0]
        for other in ids[1:]:
            uf.union(anchor, other)
            merges += 1
            match_log.append({
                "id_a": anchor,
                "id_b": other,
                "method": "phone_exact",
                "key": phone,
                "confidence": 0.95,
            })
    return merges


# ---------------------------------------------------------------------------
# Pass 3 — Fuzzy name + company match
# ---------------------------------------------------------------------------

def _match_fuzzy_name_company(df: pd.DataFrame, uf: UnionFind,
                              match_log: list[dict]) -> int:
    """
    Fuzzy match on (first_name + last_name + company) for CRM records
    that were NOT already merged via email or phone.

    To keep runtime manageable on 25K records, we:
      - Only consider CRM rows (they have name + company).
      - Block on last_name initial to avoid O(n^2) full comparison.
    """
    merges = 0

    # Filter to CRM records with name data
    crm_mask = (
        (df["_source"] == "crm")
        & (df["first_name_norm"] != "")
        & (df["last_name_norm"] != "")
    )
    crm = df.loc[crm_mask].copy()
    if crm.empty:
        return merges

    # Build composite key for fuzzy comparison
    crm["_composite"] = (
        crm["first_name_norm"] + " " + crm["last_name_norm"] + " " +
        crm.get("company", pd.Series([""] * len(crm))).fillna("")
    )

    # Block on first letter of last name to reduce comparisons
    blocks: dict[str, list[tuple[str, str]]] = defaultdict(list)
    for _, row in crm.iterrows():
        key = row["last_name_norm"][0] if row["last_name_norm"] else "?"
        blocks[key].append((row["_source_id"], row["_composite"]))

    for block_key, members in blocks.items():
        n = len(members)
        for i in range(n):
            for j in range(i + 1, n):
                id_a, comp_a = members[i]
                id_b, comp_b = members[j]
                # Skip if already in same cluster
                if uf.find(id_a) == uf.find(id_b):
                    continue
                score = fuzz.token_sort_ratio(comp_a, comp_b)
                if score >= FUZZY_THRESHOLD:
                    uf.union(id_a, id_b)
                    merges += 1
                    match_log.append({
                        "id_a": id_a,
                        "id_b": id_b,
                        "method": "fuzzy_name_company",
                        "key": f"{comp_a} <-> {comp_b}",
                        "confidence": round(score / 100.0, 2),
                    })
    return merges


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def resolve_identities(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """
    Run the three-pass identity resolution pipeline.

    Parameters
    ----------
    df : pd.DataFrame
        The concatenated, normalised records from ingestion.

    Returns
    -------
    df : pd.DataFrame
        Same frame with ``cluster_id`` and ``match_confidence`` columns added.
    stats : dict
        Summary statistics about the resolution process.
    """
    print("\n=== Resolving identities ===")
    uf = UnionFind()
    match_log: list[dict] = []

    # Ensure every record starts in its own cluster
    for sid in df["_source_id"]:
        uf.find(sid)

    t0 = time.time()

    # Pass 1 — email
    email_merges = _match_by_email(df, uf, match_log)
    print(f"  Pass 1 (email exact):         {email_merges:>6,} merges")

    # Pass 2 — phone
    phone_merges = _match_by_phone(df, uf, match_log)
    print(f"  Pass 2 (phone exact):         {phone_merges:>6,} merges")

    # Pass 3 — fuzzy name + company
    fuzzy_merges = _match_fuzzy_name_company(df, uf, match_log)
    print(f"  Pass 3 (fuzzy name+company):  {fuzzy_merges:>6,} merges")

    elapsed = time.time() - t0

    # Assign cluster IDs back to the dataframe
    df["cluster_id"] = df["_source_id"].apply(uf.find)

    # Compute per-record match confidence (highest confidence from any match
    # that touched this record, or 0.0 if it was never matched)
    confidence_map: dict[str, float] = {}
    for m in match_log:
        for key in (m["id_a"], m["id_b"]):
            root = uf.find(key)
            confidence_map[root] = max(confidence_map.get(root, 0.0),
                                       m["confidence"])
    df["match_confidence"] = df["cluster_id"].map(
        lambda cid: confidence_map.get(cid, 0.0)
    )

    n_clusters = df["cluster_id"].nunique()
    n_records = len(df)
    dedup_rate = 1.0 - (n_clusters / n_records) if n_records else 0.0

    stats = {
        "total_records": n_records,
        "unique_clusters": n_clusters,
        "dedup_rate": round(dedup_rate * 100, 1),
        "email_merges": email_merges,
        "phone_merges": phone_merges,
        "fuzzy_merges": fuzzy_merges,
        "total_merges": email_merges + phone_merges + fuzzy_merges,
        "elapsed_seconds": round(elapsed, 2),
        "match_log": match_log,
    }

    print(f"\n  Unique clusters (profiles): {n_clusters:,}")
    print(f"  Deduplication rate:          {stats['dedup_rate']}%")
    print(f"  Resolution time:             {stats['elapsed_seconds']}s")

    return df, stats
