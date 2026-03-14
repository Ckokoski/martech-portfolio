"""
sample_data.py — Generates realistic fake marketing website data.

Produces 20 sample pages that simulate a typical B2B marketing site,
complete with varying SEO quality, content freshness, and page types.
This allows the tool to demonstrate full functionality without crawling
a live website.
"""

import random
from datetime import datetime, timedelta


# ---------------------------------------------------------------------------
# Realistic page templates for a fictional B2B SaaS marketing site
# ---------------------------------------------------------------------------

PAGE_TEMPLATES = [
    {
        "slug": "/",
        "title": "Acme Marketing Cloud — Unified Marketing Platform",
        "meta_description": "Acme Marketing Cloud helps mid-market teams unify email, analytics, and campaign management in one platform. Start your free trial today.",
        "page_type": "homepage",
        "headings": {
            "h1": ["Unified Marketing Platform for Growing Teams"],
            "h2": ["Why Acme?", "Trusted by 2,000+ Companies", "See It in Action"],
            "h3": ["Email Automation", "Campaign Analytics", "Lead Scoring", "Customer Testimonials"],
        },
    },
    {
        "slug": "/product/email-automation",
        "title": "Email Automation Software — Acme Marketing Cloud",
        "meta_description": "Automate drip campaigns, transactional emails, and nurture sequences with Acme's drag-and-drop email builder.",
        "page_type": "product",
        "headings": {
            "h1": ["Email Automation That Converts"],
            "h2": ["Features", "How It Works", "Pricing", "Customer Stories"],
            "h3": ["Drag-and-Drop Builder", "A/B Testing", "Deliverability Monitoring"],
        },
    },
    {
        "slug": "/product/analytics",
        "title": "Marketing Analytics Dashboard — Acme Marketing Cloud",
        "meta_description": "Track campaign ROI, attribution, and funnel performance in real time with Acme Analytics.",
        "page_type": "product",
        "headings": {
            "h1": ["Real-Time Marketing Analytics"],
            "h2": ["Multi-Touch Attribution", "Custom Dashboards", "Data Integrations"],
            "h3": ["Salesforce Sync", "Google Analytics Import", "ROI Calculator"],
        },
    },
    {
        "slug": "/product/lead-scoring",
        "title": "Lead Scoring & Routing — Acme Marketing Cloud",
        "meta_description": "",
        "page_type": "product",
        "headings": {
            "h1": ["Intelligent Lead Scoring"],
            "h2": ["How Scoring Works", "Routing Rules"],
            "h3": [],
        },
    },
    {
        "slug": "/pricing",
        "title": "Pricing — Acme Marketing Cloud",
        "meta_description": "Transparent pricing for Acme Marketing Cloud. Plans start at $99/mo for up to 5 users.",
        "page_type": "landing",
        "headings": {
            "h1": ["Simple, Transparent Pricing"],
            "h2": ["Starter Plan", "Professional Plan", "Enterprise Plan", "Compare Plans"],
            "h3": [],
        },
    },
    {
        "slug": "/blog/content-marketing-strategy-2025",
        "title": "The Complete Content Marketing Strategy Guide for 2025",
        "meta_description": "Learn how to build a content marketing strategy that drives leads and revenue. Step-by-step guide with templates.",
        "page_type": "blog",
        "headings": {
            "h1": ["The Complete Content Marketing Strategy Guide for 2025"],
            "h2": ["Why Content Marketing Matters", "Setting Goals", "Content Calendar Template", "Measuring Success"],
            "h3": ["SMART Goals Framework", "Editorial Workflow", "KPIs to Track", "Tools We Recommend"],
        },
    },
    {
        "slug": "/blog/email-deliverability-tips",
        "title": "12 Email Deliverability Tips to Improve Inbox Placement",
        "meta_description": "Struggling with emails landing in spam? These 12 proven tips will help you improve deliverability and inbox placement rates.",
        "page_type": "blog",
        "headings": {
            "h1": ["12 Email Deliverability Tips to Improve Inbox Placement"],
            "h2": ["Authentication Protocols", "List Hygiene", "Content Best Practices", "Monitoring Tools"],
            "h3": ["SPF Setup", "DKIM Configuration", "DMARC Policy", "Sunset Policies", "Re-engagement Campaigns"],
        },
    },
    {
        "slug": "/blog/marketing-automation-roi",
        "title": "How to Calculate Marketing Automation ROI",
        "meta_description": "A practical guide to measuring the ROI of your marketing automation investment with formulas and benchmarks.",
        "page_type": "blog",
        "headings": {
            "h1": ["How to Calculate Marketing Automation ROI"],
            "h2": ["The ROI Formula", "Tracking Revenue Attribution", "Common Pitfalls"],
            "h3": ["Direct vs. Influenced Revenue", "Time-to-Value Metrics"],
        },
    },
    {
        "slug": "/blog/seo-for-saas",
        "title": "SEO for SaaS: A Complete Playbook",
        "meta_description": "",
        "page_type": "blog",
        "headings": {
            "h1": ["SEO for SaaS: A Complete Playbook"],
            "h2": ["Keyword Research", "Technical SEO", "Content Strategy", "Link Building"],
            "h3": [],
        },
    },
    {
        "slug": "/blog/ab-testing-guide",
        "title": "A/B Testing Guide for Marketers",
        "meta_description": "Everything you need to know about A/B testing subject lines, CTAs, and landing pages to improve conversion rates.",
        "page_type": "blog",
        "headings": {
            "h1": ["A/B Testing Guide for Marketers"],
            "h2": ["What to Test", "Statistical Significance", "Tools & Setup", "Case Studies"],
            "h3": ["Subject Line Tests", "CTA Button Tests", "Landing Page Variants", "Sample Size Calculator"],
        },
    },
    {
        "slug": "/blog/crm-integration-best-practices",
        "title": "CRM Integration Best Practices for Marketing Teams",
        "meta_description": "Learn how to integrate your CRM with marketing tools for seamless lead management and reporting.",
        "page_type": "blog",
        "headings": {
            "h1": ["CRM Integration Best Practices"],
            "h2": ["Data Mapping", "Sync Frequency", "Error Handling"],
            "h3": ["Field Mapping Guide", "Duplicate Management"],
        },
    },
    {
        "slug": "/resources/whitepapers/state-of-martech-2025",
        "title": "State of MarTech 2025 — Free Whitepaper",
        "meta_description": "Download our annual State of MarTech report covering trends, budgets, and stack composition across 500+ companies.",
        "page_type": "resource",
        "headings": {
            "h1": ["State of MarTech 2025"],
            "h2": ["Key Findings", "Budget Trends", "Stack Consolidation", "Download the Report"],
            "h3": [],
        },
    },
    {
        "slug": "/resources/webinars/attribution-modeling",
        "title": "Webinar: Multi-Touch Attribution Modeling",
        "meta_description": "Watch our on-demand webinar on building multi-touch attribution models that accurately credit marketing channels.",
        "page_type": "resource",
        "headings": {
            "h1": ["Multi-Touch Attribution Modeling"],
            "h2": ["Speakers", "What You Will Learn", "Watch Now"],
            "h3": [],
        },
    },
    {
        "slug": "/resources/templates/email-templates",
        "title": "Free Marketing Email Templates — Acme",
        "meta_description": "",
        "page_type": "resource",
        "headings": {
            "h1": ["Free Marketing Email Templates"],
            "h2": ["Welcome Series", "Newsletter", "Product Launch", "Re-engagement"],
            "h3": [],
        },
    },
    {
        "slug": "/customers",
        "title": "Customer Stories — Acme Marketing Cloud",
        "meta_description": "See how marketing teams at companies like TechCorp and GrowthCo use Acme to drive results.",
        "page_type": "landing",
        "headings": {
            "h1": ["Customer Stories"],
            "h2": ["TechCorp Case Study", "GrowthCo Case Study", "RetailMax Case Study"],
            "h3": [],
        },
    },
    {
        "slug": "/customers/techcorp-case-study",
        "title": "How TechCorp Increased MQLs by 140% with Acme",
        "meta_description": "TechCorp shares how they used Acme Marketing Cloud to increase marketing qualified leads by 140% in 6 months.",
        "page_type": "case_study",
        "headings": {
            "h1": ["How TechCorp Increased MQLs by 140%"],
            "h2": ["The Challenge", "The Solution", "Results", "What's Next"],
            "h3": ["Before Acme", "Implementation Timeline", "Key Metrics"],
        },
    },
    {
        "slug": "/about",
        "title": "About Acme Marketing Cloud",
        "meta_description": "Acme Marketing Cloud was founded in 2018 with a mission to make enterprise marketing tools accessible to mid-market teams.",
        "page_type": "about",
        "headings": {
            "h1": ["About Acme Marketing Cloud"],
            "h2": ["Our Mission", "Leadership Team", "Careers"],
            "h3": [],
        },
    },
    {
        "slug": "/contact",
        "title": "Contact Us",
        "meta_description": "Get in touch with our sales team or submit a support request.",
        "page_type": "landing",
        "headings": {
            "h1": [],
            "h2": ["Sales Inquiries", "Support"],
            "h3": [],
        },
    },
    {
        "slug": "/integrations",
        "title": "Integrations — Connect Acme to Your Stack",
        "meta_description": "Acme integrates with Salesforce, HubSpot, Google Analytics, Slack, and 50+ other tools.",
        "page_type": "product",
        "headings": {
            "h1": ["Connect Acme to Your Entire Stack"],
            "h2": ["CRM Integrations", "Analytics Integrations", "Productivity Integrations"],
            "h3": ["Salesforce", "HubSpot", "Google Analytics", "Slack", "Zapier"],
        },
    },
    {
        "slug": "/blog/gdpr-marketing-compliance",
        "title": "GDPR Compliance for Marketers: What You Need to Know",
        "meta_description": "A practical guide to GDPR compliance for marketing teams, covering consent, data processing, and email regulations.",
        "page_type": "blog",
        "headings": {
            "h1": ["GDPR Compliance for Marketers"],
            "h2": ["Consent Requirements", "Data Processing", "Email Marketing Rules", "Checklist"],
            "h3": ["Opt-in vs. Opt-out", "Data Retention Policies", "Right to Erasure"],
        },
    },
]


def _random_date(start_days_ago: int, end_days_ago: int) -> str:
    """Return an ISO-format date string between start and end days ago."""
    days_ago = random.randint(end_days_ago, start_days_ago)
    return (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d")


def _generate_word_count(page_type: str) -> int:
    """Return a realistic word count based on page type."""
    ranges = {
        "homepage": (300, 800),
        "product": (500, 1200),
        "blog": (800, 2500),
        "resource": (400, 1000),
        "landing": (200, 600),
        "case_study": (600, 1500),
        "about": (400, 900),
    }
    lo, hi = ranges.get(page_type, (300, 1000))
    return random.randint(lo, hi)


def generate_sample_data() -> list[dict]:
    """
    Generate a list of 20 page-audit dictionaries with realistic
    marketing website data.

    Returns:
        List of dicts, each representing one audited page.
    """
    base_url = "https://www.acme-marketing.com"
    pages = []

    for template in PAGE_TEMPLATES:
        word_count = _generate_word_count(template["page_type"])
        image_count = random.randint(0, 12)
        images_with_alt = random.randint(0, image_count)
        internal_links = random.randint(2, 20)
        external_links = random.randint(0, 8)

        # Simulate varied freshness — some pages are recent, some stale
        if template["page_type"] == "blog":
            publish_date = _random_date(730, 30)
            last_modified = _random_date(
                (datetime.now() - datetime.strptime(publish_date, "%Y-%m-%d")).days, 0
            )
        else:
            publish_date = _random_date(900, 180)
            last_modified = _random_date(
                (datetime.now() - datetime.strptime(publish_date, "%Y-%m-%d")).days, 0
            )

        page = {
            "url": base_url + template["slug"],
            "title": template["title"],
            "meta_description": template["meta_description"],
            "page_type": template["page_type"],
            "headings": template["headings"],
            "word_count": word_count,
            "image_count": image_count,
            "images_with_alt": images_with_alt,
            "images_missing_alt": image_count - images_with_alt,
            "internal_links": internal_links,
            "external_links": external_links,
            "publish_date": publish_date,
            "last_modified": last_modified,
            "status_code": 200,
            "load_time_ms": random.randint(200, 3500),
            "meta_robots": random.choice(["index, follow", "index, follow", "index, follow", "noindex, nofollow"]),
            "has_canonical": random.choice([True, True, True, False]),
            "has_og_tags": random.choice([True, True, False]),
            "has_twitter_tags": random.choice([True, False, False]),
        }
        pages.append(page)

    return pages


if __name__ == "__main__":
    # Quick test — print the generated data
    import json
    data = generate_sample_data()
    print(json.dumps(data, indent=2))
    print(f"\nGenerated {len(data)} sample pages.")
