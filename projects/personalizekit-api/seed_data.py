"""
seed_data.py — Seeds the database with three realistic demo experiments.

Run automatically on first launch (when the DB doesn't exist) or
manually via `python seed_data.py`.

Experiments created:
  1. Homepage Hero CTA        — 2 variants, enterprise, ~5K impressions each, completed
  2. Email Subject Line Test  — 3 variants, all segments, ~3K impressions each, completed
  3. Pricing Page Layout      — 2 variants, startup, ~2K impressions each, still running
"""

import random
import uuid
from models import init_db, get_db

# Fix the random seed for reproducible demos (remove for true randomness)
random.seed(42)


def seed():
    """Insert sample experiments, variants, and simulated events."""
    init_db()
    conn = get_db()
    cur = conn.cursor()

    # Check if data already exists
    cur.execute("SELECT COUNT(*) FROM experiments")
    if cur.fetchone()[0] > 0:
        print("Database already seeded — skipping.")
        conn.close()
        return

    # ------------------------------------------------------------------
    # Experiment 1: Homepage Hero CTA  (enterprise, completed, has winner)
    # ------------------------------------------------------------------
    cur.execute(
        """INSERT INTO experiments (name, description, status, segment, traffic_split)
           VALUES (?, ?, 'completed', 'enterprise', 'equal')""",
        (
            "Homepage Hero CTA",
            "Testing two hero banner call-to-action variants targeting enterprise visitors. "
            "Variant B uses urgency-driven copy.",
        ),
    )
    exp1_id = cur.lastrowid

    cur.execute(
        "INSERT INTO variants (experiment_id, name, content, weight) VALUES (?, ?, ?, ?)",
        (exp1_id, "Control — Learn More", "Learn More About Our Platform", 0.5),
    )
    v1a = cur.lastrowid

    cur.execute(
        "INSERT INTO variants (experiment_id, name, content, weight) VALUES (?, ?, ?, ?)",
        (exp1_id, "Variant B — Start Free Trial", "Start Your Free Trial Today", 0.5),
    )
    v1b = cur.lastrowid

    # Simulate ~5K impressions each; Variant B converts better (8.2% vs 5.4%)
    _generate_events(cur, exp1_id, v1a, impressions=5120, conversion_rate=0.054, segment="enterprise")
    _generate_events(cur, exp1_id, v1b, impressions=5085, conversion_rate=0.082, segment="enterprise")

    # Mark winner
    cur.execute("UPDATE experiments SET winner_variant = ? WHERE id = ?", (v1b, exp1_id))

    # ------------------------------------------------------------------
    # Experiment 2: Email Subject Line Test  (all segments, completed)
    # ------------------------------------------------------------------
    cur.execute(
        """INSERT INTO experiments (name, description, status, segment, traffic_split)
           VALUES (?, ?, 'completed', 'all', 'equal')""",
        (
            "Email Subject Line Test",
            "A/B/C test on email subject lines to optimize open-to-click rate "
            "across all customer segments.",
        ),
    )
    exp2_id = cur.lastrowid

    cur.execute(
        "INSERT INTO variants (experiment_id, name, content, weight) VALUES (?, ?, ?, ?)",
        (exp2_id, "Subject A — Straightforward", "Your Weekly Product Update", 0.34),
    )
    v2a = cur.lastrowid

    cur.execute(
        "INSERT INTO variants (experiment_id, name, content, weight) VALUES (?, ?, ?, ?)",
        (exp2_id, "Subject B — Question", "Ready to Boost Your ROI This Quarter?", 0.33),
    )
    v2b = cur.lastrowid

    cur.execute(
        "INSERT INTO variants (experiment_id, name, content, weight) VALUES (?, ?, ?, ?)",
        (exp2_id, "Subject C — Urgency", "Last Chance: Exclusive Feature Access Ends Friday", 0.33),
    )
    v2c = cur.lastrowid

    _generate_events(cur, exp2_id, v2a, impressions=3050, conversion_rate=0.034, segment="all")
    _generate_events(cur, exp2_id, v2b, impressions=2980, conversion_rate=0.061, segment="all")
    _generate_events(cur, exp2_id, v2c, impressions=3015, conversion_rate=0.052, segment="all")

    cur.execute("UPDATE experiments SET winner_variant = ? WHERE id = ?", (v2b, exp2_id))

    # ------------------------------------------------------------------
    # Experiment 3: Pricing Page Layout  (startup, still running)
    # ------------------------------------------------------------------
    cur.execute(
        """INSERT INTO experiments (name, description, status, segment, traffic_split)
           VALUES (?, ?, 'running', 'startup', 'equal')""",
        (
            "Pricing Page Layout",
            "Comparing horizontal vs. vertical pricing card layouts for startup "
            "segment visitors. Still collecting data.",
        ),
    )
    exp3_id = cur.lastrowid

    cur.execute(
        "INSERT INTO variants (experiment_id, name, content, weight) VALUES (?, ?, ?, ?)",
        (exp3_id, "Horizontal Cards", "Three pricing tiers displayed side-by-side", 0.5),
    )
    v3a = cur.lastrowid

    cur.execute(
        "INSERT INTO variants (experiment_id, name, content, weight) VALUES (?, ?, ?, ?)",
        (exp3_id, "Vertical Stack", "Pricing tiers stacked vertically with feature comparison", 0.5),
    )
    v3b = cur.lastrowid

    # ~2K impressions each — rates close enough that significance is NOT reached
    _generate_events(cur, exp3_id, v3a, impressions=2040, conversion_rate=0.045, segment="startup")
    _generate_events(cur, exp3_id, v3b, impressions=1980, conversion_rate=0.051, segment="startup")

    conn.commit()
    conn.close()
    print(f"Seeded 3 experiments with simulated traffic.")


def _generate_events(cur, experiment_id, variant_id, impressions, conversion_rate, segment):
    """
    Insert simulated impression and conversion events.

    Each impression gets a unique user_id. A random subset converts
    based on the target conversion_rate.
    """
    conversions = int(impressions * conversion_rate)

    # Build all event rows in memory, then bulk-insert
    rows = []
    for i in range(impressions):
        uid = f"user-{uuid.uuid4().hex[:12]}"
        rows.append((experiment_id, variant_id, uid, "impression", segment))
        if i < conversions:
            rows.append((experiment_id, variant_id, uid, "conversion", segment))

    cur.executemany(
        "INSERT INTO events (experiment_id, variant_id, user_id, event_type, segment) VALUES (?, ?, ?, ?, ?)",
        rows,
    )


if __name__ == "__main__":
    seed()
