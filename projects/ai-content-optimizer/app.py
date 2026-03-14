"""
AI Content Optimizer - Flask Web Application
A MarTech tool for analyzing and optimizing marketing copy.
Run with: python app.py
"""

from flask import Flask, render_template, request, jsonify
from analyzer import analyze_content
from optimizer import generate_optimizations

app = Flask(__name__)
app.config["SECRET_KEY"] = "martech-content-optimizer-dev"


@app.route("/")
def index():
    """Render the main input page."""
    return render_template("index.html")


@app.route("/analyze", methods=["POST"])
def analyze():
    """Analyze submitted content and render the results page."""
    text = request.form.get("content", "").strip()
    content_type = request.form.get("content_type", "general")
    target_keyword = request.form.get("target_keyword", "").strip()

    if not text:
        return render_template("index.html", error="Please enter some content to analyze.")

    # Run analysis
    analysis = analyze_content(text, content_type, target_keyword)

    # Generate optimizations
    optimizations = generate_optimizations(text, analysis)

    return render_template(
        "results.html",
        analysis=analysis,
        optimizations=optimizations,
    )


@app.route("/api/analyze", methods=["POST"])
def api_analyze():
    """JSON API endpoint for programmatic access."""
    data = request.get_json(force=True)
    text = data.get("content", "").strip()
    content_type = data.get("content_type", "general")
    target_keyword = data.get("target_keyword", "")

    if not text:
        return jsonify({"error": "No content provided"}), 400

    analysis = analyze_content(text, content_type, target_keyword)
    optimizations = generate_optimizations(text, analysis)

    return jsonify({
        "analysis": analysis,
        "optimizations": optimizations,
    })


if __name__ == "__main__":
    print("\n  AI Content Optimizer")
    print("  ====================")
    print("  Running at: http://localhost:5000\n")
    app.run(debug=True, host="127.0.0.1", port=5000)
