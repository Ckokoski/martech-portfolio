"""
models.py — Database models and helpers for PersonalizeKit API.

Manages SQLite schema for experiments, variants, and tracking events.
Provides CRUD operations and query helpers used by the API layer.
"""

import sqlite3
import os
import json
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "personalizekit.db")


def get_db():
    """Return a new database connection with row factory enabled."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db():
    """Create tables if they don't already exist."""
    conn = get_db()
    cursor = conn.cursor()

    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS experiments (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            name            TEXT NOT NULL,
            description     TEXT DEFAULT '',
            status          TEXT NOT NULL DEFAULT 'draft'
                            CHECK(status IN ('draft','running','paused','completed')),
            segment         TEXT NOT NULL DEFAULT 'all'
                            CHECK(segment IN ('enterprise','smb','startup','all')),
            traffic_split   TEXT DEFAULT 'equal',
            winner_variant  INTEGER DEFAULT NULL,
            created_at      TEXT NOT NULL DEFAULT (datetime('now')),
            updated_at      TEXT NOT NULL DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS variants (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            experiment_id   INTEGER NOT NULL,
            name            TEXT NOT NULL,
            content         TEXT NOT NULL DEFAULT '',
            weight          REAL NOT NULL DEFAULT 0.5,
            FOREIGN KEY (experiment_id) REFERENCES experiments(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS events (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            experiment_id   INTEGER NOT NULL,
            variant_id      INTEGER NOT NULL,
            user_id         TEXT NOT NULL,
            event_type      TEXT NOT NULL CHECK(event_type IN ('impression','conversion')),
            segment         TEXT DEFAULT 'all',
            created_at      TEXT NOT NULL DEFAULT (datetime('now')),
            FOREIGN KEY (experiment_id) REFERENCES experiments(id) ON DELETE CASCADE,
            FOREIGN KEY (variant_id) REFERENCES variants(id) ON DELETE CASCADE
        );

        CREATE INDEX IF NOT EXISTS idx_events_experiment ON events(experiment_id);
        CREATE INDEX IF NOT EXISTS idx_events_variant ON events(variant_id);
        CREATE INDEX IF NOT EXISTS idx_events_type ON events(event_type);
    """)

    conn.commit()
    conn.close()


# ---------------------------------------------------------------------------
# Experiment CRUD
# ---------------------------------------------------------------------------

def create_experiment(name, description, segment, traffic_split, variants_data):
    """
    Create a new experiment with its variants.

    Parameters
    ----------
    name : str
    description : str
    segment : str — one of enterprise, smb, startup, all
    traffic_split : str — 'equal' or JSON string of weights
    variants_data : list[dict] — each with keys: name, content, weight

    Returns
    -------
    int — the new experiment id
    """
    conn = get_db()
    cur = conn.cursor()

    cur.execute(
        """INSERT INTO experiments (name, description, segment, traffic_split, status)
           VALUES (?, ?, ?, ?, 'draft')""",
        (name, description, segment, traffic_split),
    )
    experiment_id = cur.lastrowid

    for v in variants_data:
        cur.execute(
            """INSERT INTO variants (experiment_id, name, content, weight)
               VALUES (?, ?, ?, ?)""",
            (experiment_id, v["name"], v.get("content", ""), v.get("weight", 1.0 / len(variants_data))),
        )

    conn.commit()
    conn.close()
    return experiment_id


def get_experiment(experiment_id):
    """Return a single experiment dict with nested variants and metrics."""
    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT * FROM experiments WHERE id = ?", (experiment_id,))
    row = cur.fetchone()
    if not row:
        conn.close()
        return None

    exp = dict(row)

    # Fetch variants with aggregated metrics
    cur.execute("SELECT * FROM variants WHERE experiment_id = ?", (experiment_id,))
    variants = []
    for v in cur.fetchall():
        vd = dict(v)
        # Count impressions and conversions for this variant
        cur.execute(
            "SELECT COUNT(*) FROM events WHERE variant_id = ? AND event_type = 'impression'",
            (v["id"],),
        )
        vd["impressions"] = cur.fetchone()[0]

        cur.execute(
            "SELECT COUNT(*) FROM events WHERE variant_id = ? AND event_type = 'conversion'",
            (v["id"],),
        )
        vd["conversions"] = cur.fetchone()[0]
        vd["conversion_rate"] = (
            round(vd["conversions"] / vd["impressions"] * 100, 2)
            if vd["impressions"] > 0
            else 0.0
        )
        variants.append(vd)

    exp["variants"] = variants
    conn.close()
    return exp


def list_experiments():
    """Return all experiments with basic variant metrics."""
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM experiments ORDER BY created_at DESC")
    experiments = []
    for row in cur.fetchall():
        exp = dict(row)
        # Totals across all variants
        cur.execute(
            "SELECT COUNT(*) FROM events WHERE experiment_id = ? AND event_type = 'impression'",
            (exp["id"],),
        )
        exp["total_impressions"] = cur.fetchone()[0]
        cur.execute(
            "SELECT COUNT(*) FROM events WHERE experiment_id = ? AND event_type = 'conversion'",
            (exp["id"],),
        )
        exp["total_conversions"] = cur.fetchone()[0]

        # Variant count
        cur.execute("SELECT COUNT(*) FROM variants WHERE experiment_id = ?", (exp["id"],))
        exp["variant_count"] = cur.fetchone()[0]
        experiments.append(exp)

    conn.close()
    return experiments


def update_experiment_status(experiment_id, status, winner_variant=None):
    """Update experiment status and optionally set a winner."""
    conn = get_db()
    if winner_variant is not None:
        conn.execute(
            "UPDATE experiments SET status = ?, winner_variant = ?, updated_at = datetime('now') WHERE id = ?",
            (status, winner_variant, experiment_id),
        )
    else:
        conn.execute(
            "UPDATE experiments SET status = ?, updated_at = datetime('now') WHERE id = ?",
            (status, experiment_id),
        )
    conn.commit()
    conn.close()


def get_variants_for_experiment(experiment_id):
    """Return list of variant dicts for an experiment."""
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM variants WHERE experiment_id = ?", (experiment_id,))
    variants = [dict(r) for r in cur.fetchall()]
    conn.close()
    return variants


# ---------------------------------------------------------------------------
# Event tracking
# ---------------------------------------------------------------------------

def record_event(experiment_id, variant_id, user_id, event_type, segment="all"):
    """Insert a tracking event (impression or conversion)."""
    conn = get_db()
    conn.execute(
        """INSERT INTO events (experiment_id, variant_id, user_id, event_type, segment)
           VALUES (?, ?, ?, ?, ?)""",
        (experiment_id, variant_id, user_id, event_type, segment),
    )
    conn.commit()
    conn.close()


def get_variant_stats(variant_id):
    """Return impression and conversion counts for a variant."""
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "SELECT COUNT(*) FROM events WHERE variant_id = ? AND event_type = 'impression'",
        (variant_id,),
    )
    impressions = cur.fetchone()[0]
    cur.execute(
        "SELECT COUNT(*) FROM events WHERE variant_id = ? AND event_type = 'conversion'",
        (variant_id,),
    )
    conversions = cur.fetchone()[0]
    conn.close()
    return {"impressions": impressions, "conversions": conversions}


def db_exists():
    """Check whether the database file already exists."""
    return os.path.isfile(DB_PATH)
