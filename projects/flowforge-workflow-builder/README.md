# FlowForge: Marketing Automation Workflow Builder

**Visual drag-and-drop workflow builder for designing marketing automation journeys — welcome series, re-engagement, cart abandonment, and more.**

---

## Problem Statement

Marketing automation platforms like SFMC Journey Builder, HubSpot Workflows, and Marketo Programs are powerful but complex. Designing automation logic — triggers, decision splits, wait steps, and channel actions — requires both marketing strategy and technical understanding. There's no lightweight tool for prototyping and documenting automation workflows before building them in a production platform.

## Solution

FlowForge is a React-based visual workflow builder that lets users design marketing automation journeys by dragging and dropping nodes onto a canvas. It demonstrates deep understanding of automation architecture — the triggers, conditions, actions, and timing that power real marketing automation programs.

**Key capabilities:**

- **Drag-and-drop canvas** — visual workflow design with connectable nodes
- **Node types:**
  - **Triggers** — form submission, list membership, date-based, event-based, API webhook
  - **Conditions** — if/else branching based on subscriber attributes, engagement history, or segment membership
  - **Actions** — send email, send SMS, update field, add to list, remove from list, create task
  - **Timing** — wait steps (hours/days/weeks), wait until date, wait until event
- **Pre-built templates** — welcome series, cart abandonment, re-engagement, onboarding, win-back
- **Workflow validation** — checks for common errors (dead ends, missing triggers, infinite loops)
- **Export to JSON** — workflow definitions exportable for documentation or platform import
- **Deployed on GitHub Pages** — fully functional in the browser

## Technologies Used

| Technology | Marketing Relevance |
|---|---|
| React | Component-based UI — the same framework used for SFMC custom CloudPage applications |
| React Flow | Node-based graph library — mirrors the visual paradigm of Journey Builder and similar tools |
| Zustand | State management — lightweight store for workflow state |
| HTML5 Drag & Drop | Native browser API — applicable to interactive marketing tool development |
| GitHub Pages | Deployment — demonstrates ability to ship tools without heavy infrastructure |

## Screenshots / Demo

> *Live demo link and screenshots to be added after deployment*

**Planned interface:**
- Left sidebar with draggable node palette (triggers, conditions, actions, timing)
- Central canvas for workflow design
- Right panel for node configuration (email template selection, condition logic, timing settings)
- Top toolbar for templates, validation, and export

## Key Metrics & Results (Simulated)

- **5 pre-built workflow templates** covering the most common marketing automation use cases
- **12 node types** spanning triggers, conditions, actions, and timing
- **Workflow validation engine** catches 8 common automation design errors
- **JSON export** produces structured workflow definitions compatible with documentation standards

## How This Applies to Real Marketing Operations

Workflow design is the core technical skill of Marketing Operations. This project demonstrates:

- **Journey Builder expertise** — the node types and logic directly map to SFMC Journey Builder, HubSpot Workflows, and similar platforms
- **Automation architecture** — understanding triggers, branching logic, timing, and multi-channel orchestration
- **Template thinking** — pre-built templates show awareness of common automation patterns and best practices
- **Quality assurance** — the validation engine reflects the real-world need to QA automation before go-live
- **Tool building** — creating internal tools that make the marketing team more efficient is a hallmark of senior MarOps professionals

This project is designed to be the strongest demonstration of marketing automation fluency in the portfolio.

---

*All workflow templates and examples are fictional. No real campaign or subscriber data is used.*
