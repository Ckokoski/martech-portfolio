"""
app.py — Flask application for PersonalizeKit Dynamic Content API.

Serves both the JSON API (under /api/) and the web dashboard (at /).
Auto-initialises the database and seeds sample data on first run.

Start with:  python app.py
Dashboard:   http://localhost:5001/
"""

import json
import random
import uuid

from flask import Flask, request, jsonify, render_template

from models import (
    init_db,
    db_exists,
    create_experiment,
    get_experiment,
    list_experiments,
    update_experiment_status,
    record_event,
    get_variants_for_experiment,
    get_variant_stats,
)
from experiment_manager import (
    assign_variant,
    check_and_declare_winner,
    start_experiment,
    pause_experiment,
    resume_experiment,
)
from stats import build_report
from seed_data import seed

# ---------------------------------------------------------------------------
# App factory
# ---------------------------------------------------------------------------

app = Flask(__name__)


# ---------------------------------------------------------------------------
# Dashboard (HTML)
# ---------------------------------------------------------------------------

@app.route("/")
def dashboard():
    """Render the experiment management dashboard."""
    return render_template("dashboard.html")


# ---------------------------------------------------------------------------
# API — Experiments
# ---------------------------------------------------------------------------

@app.route("/api/experiments", methods=["POST"])
def api_create_experiment():
    """
    Create a new content experiment.

    JSON body:
      name        (str, required)
      description (str)
      segment     (str) — enterprise | smb | startup | all
      traffic_split (str) — 'equal' or custom
      variants    (list) — each: {name, content, weight}
    """
    data = request.get_json(force=True)

    name = data.get("name")
    if not name:
        return jsonify({"error": "name is required"}), 400

    variants = data.get("variants", [])
    if len(variants) < 2:
        return jsonify({"error": "at least 2 variants are required"}), 400

    exp_id = create_experiment(
        name=name,
        description=data.get("description", ""),
        segment=data.get("segment", "all"),
        traffic_split=data.get("traffic_split", "equal"),
        variants_data=variants,
    )

    return jsonify({"id": exp_id, "message": "Experiment created"}), 201


@app.route("/api/experiments", methods=["GET"])
def api_list_experiments():
    """Return all experiments with status and basic metrics."""
    experiments = list_experiments()
    return jsonify(experiments)


@app.route("/api/experiments/<int:experiment_id>", methods=["GET"])
def api_get_experiment(experiment_id):
    """Return full experiment details including variant-level metrics."""
    exp = get_experiment(experiment_id)
    if not exp:
        return jsonify({"error": "Experiment not found"}), 404
    return jsonify(exp)


@app.route("/api/experiments/<int:experiment_id>/status", methods=["PUT"])
def api_update_status(experiment_id):
    """
    Change experiment status.

    JSON body:  { "status": "running" | "paused" | "draft" }
    """
    data = request.get_json(force=True)
    status = data.get("status")
    if status not in ("draft", "running", "paused"):
        return jsonify({"error": "Invalid status"}), 400

    if status == "running":
        start_experiment(experiment_id)
    elif status == "paused":
        pause_experiment(experiment_id)
    else:
        update_experiment_status(experiment_id, status)

    return jsonify({"message": f"Experiment status set to {status}"})


# ---------------------------------------------------------------------------
# API — Serving & Tracking
# ---------------------------------------------------------------------------

@app.route("/api/serve/<int:experiment_id>")
def api_serve(experiment_id):
    """
    Return the content variant for a user.

    Query params:
      user_id  (str, required)
      segment  (str, optional)
    """
    user_id = request.args.get("user_id")
    if not user_id:
        return jsonify({"error": "user_id query param is required"}), 400

    segment = request.args.get("segment")
    result = assign_variant(experiment_id, user_id, segment)

    if not result:
        return jsonify({"error": "No applicable variant (experiment may not be running or segment mismatch)"}), 404

    return jsonify(result)


@app.route("/api/track", methods=["POST"])
def api_track():
    """
    Record an impression or conversion event.

    JSON body:
      experiment_id (int, required)
      variant_id    (int, required)
      user_id       (str, required)
      event_type    (str) — 'impression' or 'conversion'
      segment       (str)
    """
    data = request.get_json(force=True)

    required = ("experiment_id", "variant_id", "user_id", "event_type")
    for key in required:
        if key not in data:
            return jsonify({"error": f"{key} is required"}), 400

    if data["event_type"] not in ("impression", "conversion"):
        return jsonify({"error": "event_type must be impression or conversion"}), 400

    record_event(
        experiment_id=data["experiment_id"],
        variant_id=data["variant_id"],
        user_id=data["user_id"],
        event_type=data["event_type"],
        segment=data.get("segment", "all"),
    )

    # After each conversion, check whether we can declare a winner
    if data["event_type"] == "conversion":
        winner = check_and_declare_winner(data["experiment_id"])
        if winner:
            return jsonify({"message": "Event recorded. Winner declared!", "winner": winner})

    return jsonify({"message": "Event recorded"})


# ---------------------------------------------------------------------------
# API — Reporting
# ---------------------------------------------------------------------------

@app.route("/api/report/<int:experiment_id>")
def api_report(experiment_id):
    """
    Full statistical report for an experiment.

    Returns per-variant metrics, chi-squared test, pairwise z-tests,
    confidence intervals, and sample-size guidance.
    """
    exp = get_experiment(experiment_id)
    if not exp:
        return jsonify({"error": "Experiment not found"}), 404

    variants_data = []
    for v in exp["variants"]:
        variants_data.append({
            "id": v["id"],
            "name": v["name"],
            "impressions": v["impressions"],
            "conversions": v["conversions"],
        })

    report = build_report(variants_data)
    report["experiment_id"] = experiment_id
    report["experiment_name"] = exp["name"]
    report["status"] = exp["status"]

    return jsonify(report)


# ---------------------------------------------------------------------------
# API — Simulate traffic (for demo / dashboard button)
# ---------------------------------------------------------------------------

@app.route("/api/simulate/<int:experiment_id>", methods=["POST"])
def api_simulate(experiment_id):
    """
    Generate synthetic impressions and conversions for demo purposes.

    JSON body (optional):
      count  (int) — number of impressions to simulate per variant (default 200)
    """
    data = request.get_json(silent=True) or {}
    count = data.get("count", 200)

    exp = get_experiment(experiment_id)
    if not exp:
        return jsonify({"error": "Experiment not found"}), 404

    # Ensure the experiment is running
    if exp["status"] not in ("running", "draft"):
        return jsonify({"error": "Experiment must be running or draft to simulate"}), 400

    if exp["status"] == "draft":
        start_experiment(experiment_id)

    variants = exp["variants"]
    total_events = 0

    for v in variants:
        # Random conversion rate between 3% and 12%
        conv_rate = random.uniform(0.03, 0.12)
        for _ in range(count):
            uid = f"sim-{uuid.uuid4().hex[:10]}"
            record_event(experiment_id, v["id"], uid, "impression", exp["segment"])
            total_events += 1
            if random.random() < conv_rate:
                record_event(experiment_id, v["id"], uid, "conversion", exp["segment"])
                total_events += 1

    # Check for automatic winner declaration
    winner = check_and_declare_winner(experiment_id)

    return jsonify({
        "message": f"Simulated {count} impressions per variant",
        "total_events": total_events,
        "winner_declared": winner,
    })


# ---------------------------------------------------------------------------
# Bootstrap
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    already_exists = db_exists()
    init_db()

    if not already_exists:
        print("First run detected — seeding sample data...")
        seed()

    print("Starting PersonalizeKit API on http://localhost:5001")
    app.run(host="0.0.0.0", port=5001, debug=True)
