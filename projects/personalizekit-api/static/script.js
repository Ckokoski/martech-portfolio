/**
 * script.js — PersonalizeKit Dashboard client-side logic.
 *
 * Handles experiment listing, detail views, experiment creation,
 * traffic simulation, and real-time UI updates via the JSON API.
 */

// ---------------------------------------------------------------------------
// State
// ---------------------------------------------------------------------------

let currentExperimentId = null;

// ---------------------------------------------------------------------------
// API helpers
// ---------------------------------------------------------------------------

async function api(path, options = {}) {
    const res = await fetch(path, {
        headers: { "Content-Type": "application/json" },
        ...options,
    });
    return res.json();
}

// ---------------------------------------------------------------------------
// List view
// ---------------------------------------------------------------------------

async function loadExperiments() {
    const experiments = await api("/api/experiments");
    const container = document.getElementById("experiment-cards");

    if (!experiments.length) {
        container.innerHTML = `
            <div class="empty-state">
                <h3>No experiments yet</h3>
                <p>Create your first experiment to get started.</p>
            </div>`;
        return;
    }

    container.innerHTML = experiments.map(exp => {
        const statusClass = `badge-${exp.status}`;
        const convRate = exp.total_impressions > 0
            ? (exp.total_conversions / exp.total_impressions * 100).toFixed(2)
            : "0.00";

        return `
        <div class="card exp-card" onclick="openExperiment(${exp.id})">
            <div class="exp-card-title">${esc(exp.name)}</div>
            <div class="exp-card-desc">${esc(exp.description)}</div>
            <div class="exp-card-meta">
                <span><span class="badge ${statusClass}">${exp.status}</span></span>
                <span><span class="badge badge-segment">${exp.segment}</span></span>
                <span>${exp.variant_count} variants</span>
            </div>
            <div class="exp-card-footer">
                <span class="text-muted" style="font-size:.8rem">
                    ${fmtNum(exp.total_impressions)} impressions &middot; ${convRate}% CVR
                </span>
            </div>
        </div>`;
    }).join("");
}

// ---------------------------------------------------------------------------
// Detail view
// ---------------------------------------------------------------------------

async function openExperiment(id) {
    currentExperimentId = id;
    document.getElementById("view-list").classList.add("hidden");
    document.getElementById("view-detail").classList.remove("hidden");
    await refreshDetail();
}

function backToList() {
    currentExperimentId = null;
    document.getElementById("view-detail").classList.add("hidden");
    document.getElementById("view-list").classList.remove("hidden");
    loadExperiments();
}

async function refreshDetail() {
    if (!currentExperimentId) return;

    const [exp, report] = await Promise.all([
        api(`/api/experiments/${currentExperimentId}`),
        api(`/api/report/${currentExperimentId}`),
    ]);

    renderDetailHeader(exp);
    renderVariantBars(exp, report);
    renderStatsReport(report);
    renderPairwise(report);
    renderGuidance(report);
}

// ---------------------------------------------------------------------------
// Detail header
// ---------------------------------------------------------------------------

function renderDetailHeader(exp) {
    const statusClass = `badge-${exp.status}`;
    const el = document.getElementById("detail-header");

    // Build action buttons depending on state
    let actions = "";
    if (exp.status === "draft") {
        actions += `<button class="btn btn-success btn-sm" onclick="changeStatus(${exp.id},'running')">Start</button>`;
    }
    if (exp.status === "running") {
        actions += `<button class="btn btn-warning btn-sm" onclick="changeStatus(${exp.id},'paused')">Pause</button>`;
    }
    if (exp.status === "paused") {
        actions += `<button class="btn btn-success btn-sm" onclick="changeStatus(${exp.id},'running')">Resume</button>`;
    }
    if (exp.status === "running" || exp.status === "draft") {
        actions += `<button class="btn btn-primary btn-sm" onclick="simulateTraffic(${exp.id})">Simulate Traffic</button>`;
    }

    el.innerHTML = `
        <h2>${esc(exp.name)}</h2>
        <p>${esc(exp.description)}</p>
        <div style="display:flex;gap:.5rem;align-items:center;margin-top:.5rem;flex-wrap:wrap">
            <span class="badge ${statusClass}">${exp.status}</span>
            <span class="badge badge-segment">${exp.segment}</span>
            <span class="text-muted" style="font-size:.8rem">Created ${exp.created_at}</span>
        </div>
        <div class="detail-actions">${actions}</div>`;
}

// ---------------------------------------------------------------------------
// Variant performance bars
// ---------------------------------------------------------------------------

function renderVariantBars(exp, report) {
    const container = document.getElementById("variant-bars");
    const variants = report.variants || [];
    if (!variants.length) {
        container.innerHTML = `<p class="text-muted">No variants found.</p>`;
        return;
    }

    const maxRate = Math.max(...variants.map(v => v.conversion_rate), 1);
    const winnerId = exp.winner_variant;

    const barColors = ["bar-blue", "bar-green", "bar-yellow", "bar-red", "bar-gray"];

    container.innerHTML = variants.map((v, i) => {
        const barWidth = Math.max((v.conversion_rate / maxRate) * 100, 2);
        const colorClass = barColors[i % barColors.length];
        const isWinner = winnerId && v.id === winnerId;
        const isLoser = winnerId && v.id !== winnerId;
        const tag = isWinner
            ? `<span class="winner-tag">Winner</span>`
            : (isLoser ? `<span class="loser-tag">Loser</span>` : "");

        return `
        <div class="variant-bar-group">
            <div class="variant-bar-label">
                <span class="name">${esc(v.name)}${tag}</span>
                <span class="rate">${v.conversion_rate.toFixed(2)}%</span>
            </div>
            <div class="variant-bar-track">
                <div class="variant-bar-fill ${colorClass}" style="width:${barWidth}%">
                    ${v.conversion_rate.toFixed(2)}%
                </div>
            </div>
            <div class="variant-bar-stats">
                <span>${fmtNum(v.impressions)} impressions</span>
                <span>${fmtNum(v.conversions)} conversions</span>
                <span>CI: ${v.ci_lower.toFixed(2)}% – ${v.ci_upper.toFixed(2)}%</span>
            </div>
        </div>`;
    }).join("");
}

// ---------------------------------------------------------------------------
// Statistical report
// ---------------------------------------------------------------------------

function renderStatsReport(report) {
    const chi = report.chi_squared;
    const container = document.getElementById("stats-content");

    const sigBadge = chi.significant
        ? `<span class="sig-badge sig-yes">Significant (p < 0.05)</span>`
        : `<span class="sig-badge sig-no">Not Yet Significant</span>`;

    // Star rating: based on p-value thresholds
    const stars = chi.p_value < 0.001 ? "★★★★★"
        : chi.p_value < 0.01  ? "★★★★☆"
        : chi.p_value < 0.05  ? "★★★☆☆"
        : chi.p_value < 0.10  ? "★★☆☆☆"
        : "★☆☆☆☆";

    let winnerHtml = "";
    if (report.winner) {
        winnerHtml = `
            <div style="margin-top:.75rem;padding:.6rem;background:var(--green-bg);border-radius:6px;font-size:.9rem">
                <strong>Winner:</strong> ${esc(report.winner.variant_name)}
                with a ${report.winner.conversion_rate.toFixed(2)}% conversion rate
            </div>`;
    }

    container.innerHTML = `
        <table class="stats-table">
            <tr>
                <th>Test</th>
                <th>Value</th>
            </tr>
            <tr>
                <td>Chi-Squared Statistic</td>
                <td class="text-mono">${chi.chi2}</td>
            </tr>
            <tr>
                <td>p-value</td>
                <td class="text-mono">${chi.p_value}</td>
            </tr>
            <tr>
                <td>Degrees of Freedom</td>
                <td class="text-mono">${chi.degrees_of_freedom}</td>
            </tr>
            <tr>
                <td>Significance</td>
                <td>${sigBadge}</td>
            </tr>
            <tr>
                <td>Confidence Rating</td>
                <td><span class="confidence-stars">${stars}</span></td>
            </tr>
        </table>
        ${winnerHtml}`;
}

// ---------------------------------------------------------------------------
// Pairwise comparisons
// ---------------------------------------------------------------------------

function renderPairwise(report) {
    const tests = report.pairwise_tests || [];
    const container = document.getElementById("pairwise-content");

    if (!tests.length) {
        container.innerHTML = `<p class="text-muted">Need at least 2 variants for pairwise comparison.</p>`;
        return;
    }

    const rows = tests.map(t => {
        const sig = t.significant
            ? `<span class="sig-badge sig-yes">Yes</span>`
            : `<span class="sig-badge sig-no">No</span>`;
        return `
            <tr>
                <td>${esc(t.variant_a)} vs ${esc(t.variant_b)}</td>
                <td class="text-mono">${t.z_score}</td>
                <td class="text-mono">${t.p_value}</td>
                <td>${sig}</td>
            </tr>`;
    }).join("");

    container.innerHTML = `
        <table class="stats-table">
            <tr><th>Pair</th><th>Z-Score</th><th>p-value</th><th>Significant</th></tr>
            ${rows}
        </table>`;
}

// ---------------------------------------------------------------------------
// Sample size guidance
// ---------------------------------------------------------------------------

function renderGuidance(report) {
    const g = report.sample_size_guidance || {};
    const container = document.getElementById("guidance-content");

    if (!g.baseline_rate) {
        container.innerHTML = `<p class="text-muted">Not enough data for sample-size guidance.</p>`;
        return;
    }

    container.innerHTML = `
        <table class="stats-table">
            <tr><td>Baseline Conversion Rate</td><td class="text-mono">${g.baseline_rate}%</td></tr>
            <tr><td>MDE at Current Sample</td><td class="text-mono">${g.mde_at_current_n}%</td></tr>
            <tr><td>Samples Needed for 1% MDE</td><td class="text-mono">${fmtNum(g.sample_needed_for_1pct_mde)}</td></tr>
            <tr><td>Samples Needed for 2% MDE</td><td class="text-mono">${fmtNum(g.sample_needed_for_2pct_mde)}</td></tr>
        </table>`;
}

// ---------------------------------------------------------------------------
// Actions
// ---------------------------------------------------------------------------

async function changeStatus(id, status) {
    await api(`/api/experiments/${id}/status`, {
        method: "PUT",
        body: JSON.stringify({ status }),
    });
    await refreshDetail();
}

async function simulateTraffic(id) {
    const btn = event.target;
    const origText = btn.textContent;
    btn.textContent = "Simulating...";
    btn.disabled = true;

    await api(`/api/simulate/${id}`, {
        method: "POST",
        body: JSON.stringify({ count: 250 }),
    });

    btn.textContent = origText;
    btn.disabled = false;
    await refreshDetail();
}

// ---------------------------------------------------------------------------
// Create experiment
// ---------------------------------------------------------------------------

function showCreateForm() {
    document.getElementById("create-modal").classList.remove("hidden");
}

function closeCreateForm() {
    document.getElementById("create-modal").classList.add("hidden");
    document.getElementById("create-form").reset();
    // Reset variant rows to just 2
    const fields = document.getElementById("variant-fields");
    while (fields.children.length > 2) {
        fields.removeChild(fields.lastChild);
    }
}

function addVariantRow() {
    const fields = document.getElementById("variant-fields");
    const row = document.createElement("div");
    row.className = "variant-row";
    row.innerHTML = `
        <input type="text" placeholder="Variant name" class="v-name" required>
        <input type="text" placeholder="Content / copy" class="v-content" required>`;
    fields.appendChild(row);
}

async function submitExperiment(e) {
    e.preventDefault();

    const name = document.getElementById("exp-name").value.trim();
    const description = document.getElementById("exp-desc").value.trim();
    const segment = document.getElementById("exp-segment").value;

    const vNames = document.querySelectorAll("#variant-fields .v-name");
    const vContents = document.querySelectorAll("#variant-fields .v-content");
    const variants = [];
    vNames.forEach((el, i) => {
        const n = el.value.trim();
        const c = vContents[i].value.trim();
        if (n) {
            variants.push({ name: n, content: c, weight: 1 / vNames.length });
        }
    });

    if (variants.length < 2) {
        alert("Please provide at least 2 variants.");
        return;
    }

    await api("/api/experiments", {
        method: "POST",
        body: JSON.stringify({ name, description, segment, variants }),
    });

    closeCreateForm();
    loadExperiments();
}

// ---------------------------------------------------------------------------
// Utilities
// ---------------------------------------------------------------------------

function esc(str) {
    if (!str) return "";
    const div = document.createElement("div");
    div.textContent = str;
    return div.innerHTML;
}

function fmtNum(n) {
    if (n == null) return "0";
    return Number(n).toLocaleString();
}

// ---------------------------------------------------------------------------
// Init
// ---------------------------------------------------------------------------

document.addEventListener("DOMContentLoaded", loadExperiments);
