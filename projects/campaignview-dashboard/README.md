# CampaignView: Marketing Performance Dashboard

**React + Node.js dashboard for visualizing campaign KPIs, email metrics, and marketing funnel performance.**

---

## Problem Statement

Marketing teams juggle data across multiple platforms — SFMC for email, Google Analytics for web, CRM for pipeline — and spend hours manually compiling reports in spreadsheets. Leadership needs a unified view of campaign performance, but building one typically requires expensive BI tools or heavy engineering resources.

## Solution

CampaignView is a lightweight, self-hosted marketing performance dashboard built with React and Node.js. It consolidates key marketing metrics into a single view, providing real-time visibility into campaign health, email performance, and funnel progression. Designed to be the kind of internal tool a Marketing Operations team would build and maintain.

**Key capabilities:**

- Unified campaign performance view across email, web, and conversion metrics
- Email KPI tracking: open rate, click rate, bounce rate, unsubscribe rate with trend lines
- Marketing funnel visualization: awareness → consideration → conversion → retention
- Campaign comparison tool for A/B test analysis
- Date range filtering and export to CSV/PDF
- Responsive design for stakeholder presentations

## Technologies Used

| Technology | Marketing Relevance |
|---|---|
| React | Frontend framework — increasingly used for internal marketing tools and customer-facing experiences |
| Node.js | Backend API — handles data aggregation from multiple marketing data sources |
| Chart.js | Data visualization — creating the charts and graphs that marketing leadership expects |
| Express | REST API framework — same patterns used for SFMC custom activities and integrations |
| CSS Grid/Flexbox | Responsive layout — applicable to email template and landing page development |

## Screenshots / Demo

> *Screenshots to be added after project deployment*

**Dashboard Sections:**
- Executive summary cards (total sends, overall engagement rate, conversion rate, revenue attributed)
- Email performance trends (30/60/90 day views)
- Funnel waterfall chart
- Campaign comparison side-by-side

## Key Metrics & Results (Simulated)

Using synthetic campaign data representing a B2B SaaS marketing program:

- **Dashboard loads in < 2 seconds** with 12 months of campaign data (50+ campaigns)
- **Consolidates 5 data sources** into a single unified view
- **Reduced weekly reporting time** from 4 hours of spreadsheet work to a live, always-current dashboard
- **Enabled campaign comparison** that identified a 23% lift in click rates from personalized subject lines

## How This Applies to Real Marketing Operations

Building internal dashboards and reporting tools is a critical Marketing Operations skill. This project demonstrates the same work a MarOps professional does when:

- **Building SFMC dashboards** — creating views that surface email performance data for campaign managers
- **Supporting marketing leadership** — providing executive-level KPI views without manual report compilation
- **Enabling data-driven decisions** — making campaign performance data accessible so teams can optimize in real time
- **Integrating data sources** — pulling from multiple platforms into one view, a core MarOps architecture challenge

This project shows the ability to design, build, and ship a data visualization tool using modern web technologies — a valuable skill set for any Marketing Operations or MarTech role.

---

*All data shown is synthetic. No real company, customer, or campaign data is used.*
