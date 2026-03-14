"""
data_generator.py — Generates synthetic multi-source customer data.

Creates four CSV files simulating real marketing data sources:
  - CRM export (source_crm.csv)
  - Email platform (source_email.csv)
  - Web analytics (source_web.csv)
  - Transaction records (source_transactions.csv)

Intentionally introduces cross-source duplicates, name variations, missing
fields, and overlapping records to simulate real-world data quality issues.
"""

import os
import random
import string
from datetime import datetime, timedelta

import pandas as pd

# ---------------------------------------------------------------------------
# Seed everything for reproducibility
# ---------------------------------------------------------------------------
SEED = 42
random.seed(SEED)

# ---------------------------------------------------------------------------
# Reference data pools
# ---------------------------------------------------------------------------
FIRST_NAMES = [
    "James", "Mary", "Robert", "Patricia", "John", "Jennifer", "Michael",
    "Linda", "David", "Elizabeth", "William", "Barbara", "Richard", "Susan",
    "Joseph", "Jessica", "Thomas", "Sarah", "Christopher", "Karen", "Charles",
    "Lisa", "Daniel", "Nancy", "Matthew", "Betty", "Anthony", "Margaret",
    "Mark", "Sandra", "Donald", "Ashley", "Steven", "Kimberly", "Paul",
    "Emily", "Andrew", "Donna", "Joshua", "Michelle", "Kenneth", "Carol",
    "Kevin", "Amanda", "Brian", "Dorothy", "George", "Melissa", "Timothy",
    "Deborah", "Ronald", "Stephanie", "Edward", "Rebecca", "Jason", "Sharon",
    "Jeffrey", "Laura", "Ryan", "Cynthia", "Jacob", "Kathleen", "Gary",
    "Amy", "Nicholas", "Angela", "Eric", "Shirley", "Jonathan", "Anna",
    "Stephen", "Brenda", "Larry", "Pamela", "Justin", "Emma", "Scott",
    "Nicole", "Brandon", "Helen", "Benjamin", "Samantha", "Samuel", "Katherine",
    "Raymond", "Christine", "Gregory", "Debra", "Frank", "Rachel", "Alexander",
    "Carolyn", "Patrick", "Janet", "Jack", "Catherine", "Dennis", "Maria",
    "Jerry", "Heather", "Tyler", "Diane", "Aaron", "Ruth", "Jose", "Julie",
    "Adam", "Olivia", "Nathan", "Joyce", "Henry", "Virginia", "Peter", "Victoria",
    "Zachary", "Kelly", "Douglas", "Lauren", "Harold", "Christina", "Carl",
    "Joan", "Arthur", "Evelyn", "Gerald", "Judith", "Roger", "Megan",
    "Keith", "Andrea", "Jeremy", "Cheryl", "Terry", "Hannah", "Lawrence",
    "Jacqueline", "Sean", "Martha", "Albert", "Gloria", "Joe", "Teresa",
    "Christian", "Ann", "Austin", "Sara", "Jesse", "Madison", "Ethan",
    "Frances", "Dylan", "Kathryn", "Willie", "Janice", "Billy", "Jean",
    "Bryan", "Abigail", "Bruce", "Alice", "Ralph", "Judy", "Roy", "Sophia",
    "Noah", "Grace", "Eugene", "Denise", "Randy", "Amber", "Philip", "Doris",
    "Harry", "Marilyn", "Vincent", "Danielle", "Bobby", "Beverly", "Johnny",
    "Isabella", "Logan", "Theresa", "Russell", "Diana", "Gabriel", "Natalie",
    "Liam", "Brittany", "Mason", "Charlotte", "Elijah", "Marie", "Oscar",
    "Kayla", "Luke", "Alexis", "Aiden", "Lori",
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller",
    "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez",
    "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin",
    "Lee", "Perez", "Thompson", "White", "Harris", "Sanchez", "Clark",
    "Ramirez", "Lewis", "Robinson", "Walker", "Young", "Allen", "King",
    "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores", "Green",
    "Adams", "Nelson", "Baker", "Hall", "Rivera", "Campbell", "Mitchell",
    "Carter", "Roberts", "Gomez", "Phillips", "Evans", "Turner", "Diaz",
    "Parker", "Cruz", "Edwards", "Collins", "Reyes", "Stewart", "Morris",
    "Morales", "Murphy", "Cook", "Rogers", "Gutierrez", "Ortiz", "Morgan",
    "Cooper", "Peterson", "Bailey", "Reed", "Kelly", "Howard", "Ramos",
    "Kim", "Cox", "Ward", "Richardson", "Watson", "Brooks", "Chavez",
    "Wood", "James", "Bennett", "Gray", "Mendoza", "Ruiz", "Hughes",
    "Price", "Alvarez", "Castillo", "Sanders", "Patel", "Myers", "Long",
    "Ross", "Foster", "Jimenez", "Powell",
]

COMPANIES = [
    "Acme Corp", "TechVista", "DataFlow Inc", "CloudNine Solutions",
    "BrightPath Media", "Summit Analytics", "NovaStar Technologies",
    "PulsePoint Digital", "Velocity Partners", "RedOak Consulting",
    "BlueShift Labs", "Ironclad Systems", "Pinnacle Group", "Mosaic Digital",
    "Catalyst Marketing", "Evergreen Solutions", "Horizon Media Group",
    "Apex Strategies", "Silverline Analytics", "Quantum Reach",
    "OmniChannel Co", "PixelForge", "Riviera Technologies", "Stratos Group",
    "Beacon Digital", "Atlas Commerce", "Frontier Data", "Keystone Media",
    "Prism Analytics", "Zenith Partners", "Northwind Traders",
    "Contoso Ltd", "Fabrikam Inc", "WingTip Toys", "Litware Inc",
    "Adventure Works", "Woodgrove Bank", "Tailspin Toys", "Coho Winery",
    "Trey Research",
]

JOB_TITLES = [
    "Marketing Manager", "Director of Marketing", "CMO", "VP of Marketing",
    "Marketing Coordinator", "Digital Marketing Specialist", "Brand Manager",
    "Content Strategist", "Growth Manager", "Product Marketing Manager",
    "Demand Gen Manager", "Email Marketing Manager", "SEO Specialist",
    "Social Media Manager", "Marketing Analyst", "CRM Manager",
    "Marketing Operations Lead", "VP of Sales", "Account Executive",
    "Sales Director", "Business Development Rep", "Customer Success Manager",
    "Head of Revenue", "CEO", "CTO", "COO", "CFO", "VP of Engineering",
    "Software Engineer", "Data Analyst", "Product Manager",
]

REGIONS = [
    "Northeast", "Southeast", "Midwest", "Southwest", "West Coast",
    "Pacific Northwest", "Mountain", "Mid-Atlantic", "New England",
    "Great Plains",
]

EMAIL_DOMAINS = [
    "gmail.com", "yahoo.com", "outlook.com", "hotmail.com", "icloud.com",
    "protonmail.com", "aol.com", "mail.com",
]

PRODUCT_CATEGORIES = [
    "Software License", "Professional Services", "Training",
    "Support Plan", "Hardware", "Subscription", "Consulting",
    "Implementation", "Data Services", "Analytics Platform",
]

TOP_PAGES_POOL = [
    "/pricing", "/features", "/demo", "/about", "/blog",
    "/blog/best-practices", "/case-studies", "/contact", "/docs",
    "/integrations", "/security", "/enterprise", "/resources",
    "/webinars", "/roi-calculator", "/compare", "/solutions",
    "/product-tour", "/api-docs", "/changelog",
]


# ---------------------------------------------------------------------------
# Helper utilities
# ---------------------------------------------------------------------------

def _random_date(start: datetime, end: datetime) -> str:
    """Return a random ISO-format date string between *start* and *end*."""
    delta = (end - start).days
    return (start + timedelta(days=random.randint(0, delta))).strftime("%Y-%m-%d")


def _random_datetime(start: datetime, end: datetime) -> str:
    """Return a random ISO-format datetime string between *start* and *end*."""
    delta = int((end - start).total_seconds())
    return (start + timedelta(seconds=random.randint(0, delta))).strftime(
        "%Y-%m-%d %H:%M:%S"
    )


def _generate_email(first: str, last: str, use_company: bool = False,
                     company: str = "") -> str:
    """Create a plausible email address for the person."""
    patterns = [
        f"{first.lower()}.{last.lower()}",
        f"{first[0].lower()}{last.lower()}",
        f"{first.lower()}{last[0].lower()}",
        f"{first.lower()}_{last.lower()}",
        f"{first.lower()}{random.randint(1, 99)}",
    ]
    local = random.choice(patterns)
    if use_company and company:
        domain = company.lower().replace(" ", "").replace(".", "") + ".com"
    else:
        domain = random.choice(EMAIL_DOMAINS)
    return f"{local}@{domain}"


def _generate_phone() -> str:
    """Return a US-style phone number in a random format."""
    area = random.randint(200, 999)
    mid = random.randint(200, 999)
    last = random.randint(1000, 9999)
    fmt = random.choice([
        f"({area}) {mid}-{last}",
        f"{area}-{mid}-{last}",
        f"{area}.{mid}.{last}",
        f"{area}{mid}{last}",
        f"+1{area}{mid}{last}",
        f"1-{area}-{mid}-{last}",
    ])
    return fmt


def _name_variation(name: str) -> str:
    """Occasionally introduce a slight name variation (typo, nickname, etc.)."""
    roll = random.random()
    if roll < 0.05:
        # Swap two adjacent characters
        if len(name) > 2:
            i = random.randint(0, len(name) - 2)
            lst = list(name)
            lst[i], lst[i + 1] = lst[i + 1], lst[i]
            return "".join(lst)
    elif roll < 0.10:
        # Drop a character
        if len(name) > 3:
            i = random.randint(1, len(name) - 1)
            return name[:i] + name[i + 1:]
    elif roll < 0.15:
        # Common nickname substitution
        nicknames = {
            "James": "Jim", "Robert": "Bob", "William": "Bill",
            "Richard": "Rich", "Joseph": "Joe", "Thomas": "Tom",
            "Christopher": "Chris", "Michael": "Mike", "Daniel": "Dan",
            "Matthew": "Matt", "Jennifer": "Jen", "Elizabeth": "Liz",
            "Patricia": "Pat", "Margaret": "Maggie", "Katherine": "Kate",
            "Benjamin": "Ben", "Nicholas": "Nick", "Timothy": "Tim",
            "Jonathan": "Jon", "Stephen": "Steve", "Rebecca": "Becca",
            "Samantha": "Sam", "Jessica": "Jess", "Kimberly": "Kim",
        }
        return nicknames.get(name, name)
    return name


# ---------------------------------------------------------------------------
# Core person generator — shared identity pool
# ---------------------------------------------------------------------------

def _build_person_pool(n_people: int = 16000) -> list[dict]:
    """
    Generate a pool of synthetic people with stable identity attributes.
    These serve as the ground-truth identities from which each source
    samples (with noise).
    """
    people = []
    used_emails = set()

    for _ in range(n_people):
        first = random.choice(FIRST_NAMES)
        last = random.choice(LAST_NAMES)
        company = random.choice(COMPANIES)

        # ~70 % get a personal email, ~30 % get a work email
        use_work = random.random() < 0.30
        email = _generate_email(first, last, use_company=use_work,
                                company=company)
        # ensure uniqueness
        while email in used_emails:
            email = _generate_email(first, last, use_company=use_work,
                                    company=company)
        used_emails.add(email)

        phone = _generate_phone()
        job_title = random.choice(JOB_TITLES)
        region = random.choice(REGIONS)

        people.append({
            "first_name": first,
            "last_name": last,
            "email": email,
            "phone": phone,
            "company": company,
            "job_title": job_title,
            "region": region,
        })
    return people


# ---------------------------------------------------------------------------
# Source-specific generators
# ---------------------------------------------------------------------------

def generate_crm(people: list[dict], n_records: int = 8000,
                 output_path: str = "data/source_crm.csv") -> pd.DataFrame:
    """
    CRM export: name, email, phone, company, job_title, region, created_date.
    """
    sample = random.sample(people, min(n_records, len(people)))
    rows = []
    now = datetime.now()
    for p in sample:
        first = _name_variation(p["first_name"])
        last = p["last_name"]
        # 5 % chance email is missing
        email = p["email"] if random.random() > 0.05 else ""
        phone = p["phone"] if random.random() > 0.08 else ""
        created = _random_date(now - timedelta(days=1095), now)
        rows.append({
            "first_name": first,
            "last_name": last,
            "email": email,
            "phone": phone,
            "company": p["company"],
            "job_title": p["job_title"],
            "region": p["region"],
            "created_date": created,
        })
    df = pd.DataFrame(rows)
    df.to_csv(output_path, index=False)
    print(f"  [CRM]          {len(df):>6,} records -> {output_path}")
    return df


def generate_email_platform(people: list[dict], n_records: int = 7000,
                            output_path: str = "data/source_email.csv") -> pd.DataFrame:
    """
    Email platform export: email, first_name, subscriber_status, open_count,
    click_count, last_engaged.
    """
    sample = random.sample(people, min(n_records, len(people)))
    rows = []
    now = datetime.now()
    for p in sample:
        first = _name_variation(p["first_name"])
        status = random.choices(
            ["active", "unsubscribed", "bounced"],
            weights=[0.75, 0.15, 0.10],
        )[0]
        opens = random.randint(0, 200)
        clicks = random.randint(0, max(1, opens // 3))
        last_engaged = _random_datetime(now - timedelta(days=365), now)
        rows.append({
            "email": p["email"],
            "first_name": first,
            "subscriber_status": status,
            "open_count": opens,
            "click_count": clicks,
            "last_engaged": last_engaged,
        })
    df = pd.DataFrame(rows)
    df.to_csv(output_path, index=False)
    print(f"  [Email]        {len(df):>6,} records -> {output_path}")
    return df


def generate_web_analytics(people: list[dict], n_records: int = 6000,
                           output_path: str = "data/source_web.csv") -> pd.DataFrame:
    """
    Web analytics: email (sometimes), anonymous_id, page_views, sessions,
    last_visit, top_pages.
    """
    sample = random.sample(people, min(n_records, len(people)))
    rows = []
    now = datetime.now()
    for p in sample:
        # Only ~60 % of web visitors are identified by email
        email = p["email"] if random.random() < 0.60 else ""
        anon_id = "anon_" + "".join(random.choices(string.ascii_lowercase +
                                                     string.digits, k=12))
        page_views = random.randint(1, 500)
        sessions = random.randint(1, max(2, page_views // 5))
        last_visit = _random_datetime(now - timedelta(days=180), now)
        n_pages = random.randint(1, 4)
        top_pages = "|".join(random.sample(TOP_PAGES_POOL, n_pages))
        rows.append({
            "email": email,
            "anonymous_id": anon_id,
            "page_views": page_views,
            "sessions": sessions,
            "last_visit": last_visit,
            "top_pages": top_pages,
        })
    df = pd.DataFrame(rows)
    df.to_csv(output_path, index=False)
    print(f"  [Web]          {len(df):>6,} records -> {output_path}")
    return df


def generate_transactions(people: list[dict], n_records: int = 4000,
                          output_path: str = "data/source_transactions.csv") -> pd.DataFrame:
    """
    Transaction records: email, order_id, order_date, amount, product_category.
    Some customers have multiple orders.
    """
    # Pick a subset of people who have transacted
    buyer_pool = random.sample(people, min(n_records, len(people)))
    rows = []
    now = datetime.now()
    order_counter = 100000
    for p in buyer_pool:
        # Each buyer gets 1-4 orders
        n_orders = random.choices([1, 2, 3, 4], weights=[0.50, 0.25, 0.15, 0.10])[0]
        for _ in range(n_orders):
            order_counter += 1
            order_date = _random_date(now - timedelta(days=730), now)
            amount = round(random.uniform(29.99, 9999.99), 2)
            category = random.choice(PRODUCT_CATEGORIES)
            rows.append({
                "email": p["email"],
                "order_id": f"ORD-{order_counter}",
                "order_date": order_date,
                "amount": amount,
                "product_category": category,
            })
    df = pd.DataFrame(rows)
    df.to_csv(output_path, index=False)
    print(f"  [Transactions] {len(df):>6,} records -> {output_path}")
    return df


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def generate_all(data_dir: str = "data") -> dict:
    """
    Generate all four synthetic data sources and write CSVs into *data_dir*.

    Returns a dict of DataFrames keyed by source name.
    """
    os.makedirs(data_dir, exist_ok=True)
    print("\n=== Generating synthetic data ===")

    people = _build_person_pool(16000)

    sources = {
        "crm": generate_crm(
            people, 8000, os.path.join(data_dir, "source_crm.csv")
        ),
        "email": generate_email_platform(
            people, 7000, os.path.join(data_dir, "source_email.csv")
        ),
        "web": generate_web_analytics(
            people, 6000, os.path.join(data_dir, "source_web.csv")
        ),
        "transactions": generate_transactions(
            people, 4000, os.path.join(data_dir, "source_transactions.csv")
        ),
    }

    total = sum(len(df) for df in sources.values())
    print(f"\n  Total records generated: {total:,}")
    return sources


if __name__ == "__main__":
    generate_all()
