import json
import re
from datetime import date, datetime, timezone, timedelta
import random
import os

# SIMPLIFY_BUTTON = "https://i.imgur.com/kvraaHg.png"
SIMPLIFY_BUTTON = "https://i.imgur.com/MXdpmi0.png" # says apply
SHORT_APPLY_BUTTON = "https://i.imgur.com/fbjwDvo.png"
SQUARE_SIMPLIFY_BUTTON = "https://i.imgur.com/aVnQdox.png"
LONG_APPLY_BUTTON = "https://i.imgur.com/G5Bzlx3.png"
INACTIVE_THRESHOLD_MONTHS = 4

# Set of Simplify company URLs to block from appearing in the README
# Add Simplify company URLs to block them (e.g., "https://simplify.jobs/c/Jerry")
BLOCKED_COMPANIES = {
    "https://simplify.jobs/c/Jerry",
}

# Companies known to hire scientific software / computational science roles (lowercase for matching)
SCIENTIFIC_COMPANIES = {
    "tesla", "sila nanotechnologies", "quantumscape", "redwood materials", "form energy",
    "genentech", "amgen", "recursion", "insitro", "gsk", "personalis", "illumina", "pacbio",
    "schrödinger", "schrodinger", "d. e. shaw research", "deshaw", "nvidia", "altos labs", "c3 ai", "ansys",
    "lawrence livermore", "berkeley lab", "sandia", "los alamos", "ornl", "oak ridge",
    "argonne", "pnnl", "pacific northwest", "brookhaven", "national renewable energy", "nrel",
    "mit lincoln lab", "lincoln laboratory", "johns hopkins apl", "spacex",
    "benchling", "tempus", "veracyte", "fulcrum", "kbr", "leidos", "booz allen", "battelle",
    "cadence design", "synopsys", "mentor graphics", "mathworks", "wolfram",
}

# Title/role keywords that indicate scientific software / MSSE-relevant roles
SCIENTIFIC_TITLE_KEYWORDS = [
    "computational chemistry", "computational scientist", "simulation engineer", "simulation software",
    "battery", "energy storage", "materials science", "materials modeling",
    "bioinformatics", "computational biology", "genomics", "computational drug",
    "ml for science", "machine learning for science", "scientific computing", "hpc", "high performance computing",
    "research software", "research engineer", "research sci", "scientific software", "scientific developer",
    "robotics", "scientific instrumentation", "physics engine", "molecular", "quantum",
    "computational physics", "computational chem", "materials informatics", "drug discovery",
    "compiler engineer", "gpu", "cuda", "distributed systems", "scientific ml", "applied ml",
]

# MSSE / scientific software categories for this repo (order determines table order and browse links)
MSSE_CATEGORIES = [
    {"key": "Battery/Energy", "name": "Battery / Energy", "emoji": "🔋"},
    {"key": "Computational Chemistry", "name": "Computational Chemistry", "emoji": "⚗️"},
    {"key": "Bioinformatics", "name": "Bioinformatics", "emoji": "🧬"},
    {"key": "Scientific Software", "name": "Scientific Software", "emoji": "🔬"},
    {"key": "HPC", "name": "HPC", "emoji": "⚡"},
    {"key": "Simulation", "name": "Simulation", "emoji": "🖥️"},
    {"key": "ML for Science", "name": "ML for Science", "emoji": "🤖"},
    {"key": "Materials Science", "name": "Materials Science", "emoji": "🧪"},
    {"key": "Research Software Engineer", "name": "Research Software Engineer", "emoji": "🛠️"},
]

# Define categories with their correct anchor formats and emojis (used when not filtering to scientific)
CATEGORIES = {
    "Software": {
        "name": "Software Engineering",
        "emoji": "💻"
    },
    "Product": {
        "name": "Product Management",
        "emoji": "📱"
    },
    "AI/ML/Data": {
        "name": "Data Science, AI & Machine Learning",
        "emoji": "🤖"
    },
    "Quant": {
        "name": "Quantitative Finance",
        "emoji": "📈"
    },
    "Hardware": {
        "name": "Hardware Engineering",
        "emoji": "🔧"
    },
    "Other": {
        "name": "Other",
        "emoji": "💼"
    }
}

# FAANG+ companies - will be marked with fire emoji
FAANG_PLUS = {
    "airbnb", "adobe", "amazon", "amd", "anthropic", "apple", "asana", "atlassian", "bytedance", "cloudflare","coinbase", "crowdstrike","databricks", "datadog",
    "doordash", "dropbox", "duolingo", "figma", "google", "ibm", "instacart", "intel", "linkedin", "lyft", "meta", "microsoft",
    "netflix", "notion", "nvidia", "openai", "oracle", "palantir", "paypal", "perplexity", "pinterest", "ramp", "reddit","rippling", "robinhood", "roblox",
    "salesforce", "samsara", "servicenow", "shopify", "slack", "snap", "snapchat", "spacex", "splunk","snowflake", "stripe", "square", "tesla", "tinder","tiktok", "uber",
    "visa","waymo", "x"
}

def setOutput(key, value):
    if 'GITHUB_OUTPUT' in os.environ:
        with open(os.environ['GITHUB_OUTPUT'], 'a') as fh:
            # Handle multiline values using heredoc format
            if isinstance(value, str) and ('\n' in value or '\r' in value or value.startswith('#') or value.startswith('*')):
                # Use heredoc format for multiline or markdown content
                delimiter = f"EOF_{key}_{hash(value) % 10000}"
                print(f'{key}<<{delimiter}', file=fh)
                print(value, file=fh)
                print(delimiter, file=fh)
            else:
                # Use simple format for single-line values
                print(f'{key}={value}', file=fh)
    else:
        # Safe fallback for local/dev use
        print(f'[set-output] {key}={value}')
        
def fail(why):
    setOutput("error_message", why)
    exit(1)

def getLocations(listing):
    locations = "</br>".join(listing["locations"])
    if len(listing["locations"]) <= 3:
        return locations
    num = str(len(listing["locations"])) + " locations"
    return f'<details><summary>**{num}**</summary>{locations}</details>'

def getSponsorship(listing):
    if listing["sponsorship"] == "Does Not Offer Sponsorship":
        return " 🛂"
    elif listing["sponsorship"] == "U.S. Citizenship is Required":
        return " 🇺🇸"
    return ""

def getLink(listing):
    if not listing["active"]:
        return "🔒"
    link = listing["url"]
    if "?" not in link:
        link += "?utm_source=Simplify&ref=Simplify"
    else:
        link += "&utm_source=Simplify&ref=Simplify"
    # return f'<a href="{link}" style="display: inline-block;"><img src="{SHORT_APPLY_BUTTON}" width="160" alt="Apply"></a>'

    if listing["source"] != "Simplify":
        return f'<a href="{link}"><img src="{LONG_APPLY_BUTTON}" width="100" alt="Apply"></a>'
    
    simplifyLink = f"https://simplify.jobs/p/{listing['id']}?utm_source=GHList"
    return (
        f'<div align="center">'
        f'<a href="{link}"><img src="{SHORT_APPLY_BUTTON}" width="52" alt="Apply"></a> '
        f'<a href="{simplifyLink}"><img src="{SQUARE_SIMPLIFY_BUTTON}" width="28" alt="Simplify"></a>'
        f'</div>'
    )
    
def mark_stale_listings(listings):
    now = datetime.now()
    for listing in listings:
        if listing["source"] != "Simplify":
            age_in_months = (now - datetime.fromtimestamp(listing["date_posted"])).days / 30
            if age_in_months > INACTIVE_THRESHOLD_MONTHS:
                listing["active"] = False
    return listings    

def filter_active(listings):
    return [listing for listing in listings if listing.get("active", False)]

def convert_markdown_to_html(text):
    """Convert basic markdown formatting to HTML for use in HTML tables"""
    if not text:
        return text
    
    # Convert **bold** to <strong>bold</strong>
    text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
    
    # Convert [link text](url) to <a href="url">link text</a>
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', text)
    
    return text

def create_md_table(listings):
    table = ""
    # Use HTML table with CSS for better width control and spacing
    # This provides much better column width control than markdown tables
    table = '<table style="width: 100%; border-collapse: collapse;">\n'
    table += '<thead>\n'
    table += '<tr>\n'
    table += '<th style="width: 25%; min-width: 200px; padding: 8px; text-align: left; border-bottom: 2px solid #ddd;">Company</th>\n'
    table += '<th style="width: 30%; min-width: 250px; padding: 8px; text-align: left; border-bottom: 2px solid #ddd;">Role</th>\n'
    table += '<th style="width: 20%; min-width: 150px; padding: 8px; text-align: left; border-bottom: 2px solid #ddd;">Location</th>\n'
    table += '<th style="width: 15%; min-width: 120px; padding: 8px; text-align: center; border-bottom: 2px solid #ddd;">Application</th>\n'
    table += '<th style="width: 10%; min-width: 80px; padding: 8px; text-align: center; border-bottom: 2px solid #ddd;">Age</th>\n'
    table += '</tr>\n'
    table += '</thead>\n'
    table += '<tbody>\n'
    prev_company = None
    prev_days_active = None

    for listing in listings:
        # Add fire emoji for FAANG+ companies
        company_name = listing["company_name"]
        if company_name.lower() in FAANG_PLUS:
            company_name = f"🔥 {company_name}"
            listing["company_name"] = company_name  # Update the listing as well
        
        raw_url = listing.get("company_url", "").strip()
        company_url = raw_url + '?utm_source=GHList&utm_medium=company' if raw_url.startswith("http") else ""
        company = f"**[{company_name}]({company_url})**" if company_url else f"**{company_name}**"
        
        location = getLocations(listing)
        
        # Check for advanced degree requirements and add graduation cap emoji
        title_with_degree_emoji = listing["title"]
        
        # Check degrees field for advanced degree requirements
        degrees = listing.get("degrees", [])
        if degrees:
            # Check if only advanced degrees are required (no Bachelor's or Associate's)
            has_bachelors_or_associates = any(
                degree.lower() in ["bachelor's", "associate's"]
                for degree in degrees
            )
            has_advanced_degrees = any(
                degree.lower() in ["master's", "phd", "mba"]
                for degree in degrees
            )
            
            if has_advanced_degrees and not has_bachelors_or_associates:
                title_with_degree_emoji += " 🎓"
        
        # Also check title text for degree mentions
        title_lower = listing["title"].lower()
        if any(term in title_lower for term in ["master's", "masters", "master", "mba", "phd", "ph.d", "doctorate", "doctoral"]):
            if "🎓" not in title_with_degree_emoji:
                title_with_degree_emoji += " 🎓"
        
        position = title_with_degree_emoji + getSponsorship(listing)
        link = getLink(listing)

        # Days active calculation
        days_active = (datetime.now() - datetime.fromtimestamp(listing["date_posted"])).days
        days_active = max(days_active, 0)

        days_display = (
            "0d" if days_active == 0 else
            f"{(days_active // 30)}mo" if days_active >= 30 else
            f"{days_active}d"
        )

        if prev_company == company_name and prev_days_active == days_active:
            company = "↳"
        else:
            prev_company = company_name
            prev_days_active = days_active

        # Convert markdown formatting to HTML for proper rendering in HTML tables
        company_html = convert_markdown_to_html(company)
        position_html = convert_markdown_to_html(position)
        location_html = convert_markdown_to_html(location)
        
        table += '<tr>\n'
        table += f'<td>{company_html}</td>\n'
        table += f'<td>{position_html}</td>\n'
        table += f'<td>{location_html}</td>\n'
        table += f'<td>{link}</td>\n'
        table += f'<td>{days_display}</td>\n'
        table += '</tr>\n'

    table += '</tbody>\n'
    table += '</table>\n'
    return table
    

def filterListings(listings, earliest_date):
    final_listings = []
    inclusion_terms = ["software eng", "software dev", "product engineer", "fullstack engineer", "frontend", "front end", "front-end", "backend", "back end", "full-stack", "full stack", "founding engineer", "mobile dev", "mobile engineer", "data scientist", "data engineer", "research eng", "product manag", "apm", "product", "devops", "android", "ios", "sre", "site reliability eng", "quantitative trad", "quantitative research", "quantitative dev", "security eng", "compiler eng", "machine learning eng", "hardware eng", "firmware eng", "infrastructure eng", "embedded", "fpga", "circuit", "chip", "silicon", "asic", "quant", "quantitative", "trading", "finance", "investment", "ai &", "machine learning", "ml", "analytics", "analyst", "research sci"]
    new_grad_terms = ["new grad", "early career", "college grad", "entry level", "founding", "early in career", "university grad", "fresh grad", "2024 grad", "2025 grad", "2026 grad", "engineer 0", "engineer 1", "engineer i ", "junior", "sde 1", "sde i", "intern", "co-op", "coop"]
    
    # Convert blocked URLs to lowercase for case-insensitive comparison
    blocked_urls_lower = {url.lower() for url in BLOCKED_COMPANIES}
    
    for listing in listings:
        if listing["is_visible"] and listing["date_posted"] > earliest_date:
            # Check if listing is from a blocked company
            company_url = listing.get("company_url", "").lower()
            if any(blocked_url in company_url for blocked_url in blocked_urls_lower):
                continue  # Skip blocked companies
            
            if listing['source'] != "Simplify" or (any(term in listing["title"].lower() for term in inclusion_terms) and (any(term in listing["title"].lower() for term in new_grad_terms) or (listing["title"].lower().endswith("engineer i")))):
                final_listings.append(listing)

    return final_listings


def filter_to_scientific(listings):
    """Keep only listings that are scientific / MSSE-relevant (company or title match)."""
    out = []
    title_kw = [k.lower() for k in SCIENTIFIC_TITLE_KEYWORDS]
    for listing in listings:
        company_lower = (listing.get("company_name") or "").lower()
        title_lower = (listing.get("title") or "").lower()
        if company_lower in SCIENTIFIC_COMPANIES:
            out.append(listing)
            continue
        if any(kw in company_lower for kw in title_kw):
            out.append(listing)
            continue
        if any(kw in title_lower for kw in title_kw):
            out.append(listing)
    return out


def classify_msse_category(listing):
    """Assign one MSSE category based on title and company."""
    title_lower = (listing.get("title") or "").lower()
    company_lower = (listing.get("company_name") or "").lower()
    text = title_lower + " " + company_lower
    # Order matters: more specific first
    if any(x in text for x in ["battery", "energy storage", "redwood", "quantumscape", "sila", "form energy"]):
        return "Battery / Energy"
    if any(x in text for x in ["computational chem", "chemistry", "schrödinger", "molecular"]):
        return "Computational Chemistry"
    if any(x in text for x in ["bioinformatics", "genomics", "computational biolog", "genentech", "amgen", "recursion", "insitro", "personalis", "illumina"]):
        return "Bioinformatics"
    if any(x in text for x in ["ml for science", "machine learning for science", "ai for science"]):
        return "ML for Science"
    if any(x in text for x in ["hpc", "high performance", "distributed computing", "parallel computing"]):
        return "HPC"
    if any(x in text for x in ["simulation", "physics engine", "modeling"]):
        return "Simulation"
    if any(x in text for x in ["materials science", "materials modeling", "materials informatics"]):
        return "Materials Science"
    if any(x in text for x in ["research software", "research engineer", "research sci", "rse"]):
        return "Research Software Engineer"
    return "Scientific Software"


def ensure_msse_categories(listings):
    MSSE_NAMES = {c["name"] for c in MSSE_CATEGORIES}
    for listing in listings:
        # Keep form-selected MSSE category if present and valid
        existing = (listing.get("msse_category") or "").strip()
        if existing in MSSE_NAMES:
            listing["msse_category"] = existing
        else:
            listing["msse_category"] = classify_msse_category(listing)
    return listings


def getListingsFromJSON(filename=".github/scripts/listings.json"):
    with open(filename) as f:
        listings = json.load(f)
        print("Recieved " + str(len(listings)) +
              " listings from listings.json")
        return listings

def create_category_table(listings, category_name):
    category_listings = [listing for listing in listings if listing["category"] == category_name]
    if not category_listings:
        return ""

    emoji = next((cat["emoji"] for cat in CATEGORIES.values() if cat["name"] == category_name), "")
    header = f"\n\n## {emoji} {category_name} New Grad Roles\n\n"
    header += "[Back to top](#2026-new-grad-positions-by-coder-quad-and-simplify)\n\n"

    # Optional callout under Data Science section
    if category_name == "Data Science, AI & Machine Learning":
        header += (
            "> 📄 Here's the [resume template](https://docs.google.com/document/d/1azvJt51U2CbpvyO0ZkICqYFDhzdfGxU_lsPQTGhsn94/edit?usp=sharing) that Pitt CSC and Stanford CS share with software new grads.\n"
            ">\n"
            "> 🧠 Want to know what keywords your resume is missing for a job? Use the blue Simplify application link to instantly compare your resume to any job description.\n\n"
        )
        
    if category_name == 'Product Management':
        header += (
            "> 📅 Curious when Big Tech APM roles typically open? Simplify put together an [openings tracker](https://simplify.jobs/top-list/Associate-Product-Manager?utm_source=GHList&utm_medium=ot) based on historical data for those companies.\n"
            "\n"
        )

    # Sort and split
    active = sorted([l for l in category_listings if l["active"]], key=lambda l: l["date_posted"], reverse=True)
    inactive = sorted([l for l in category_listings if not l["active"]], key=lambda l: l["date_posted"], reverse=True)

    result = header
    if active:
        result += create_md_table(active) + "\n\n"

    if inactive:
        result += (
            "<details>\n"
            f"<summary>🗃️ Inactive roles ({len(inactive)})</summary>\n\n"
            + create_md_table(inactive) +
            "\n\n</details>\n\n"
        )

    return result


README_TOP_ANCHOR = "scientific-software--computational-science-jobs"


def create_msse_category_table(listings, category_name):
    """Build a section and table for one MSSE category."""
    category_listings = [l for l in listings if l.get("msse_category") == category_name]
    if not category_listings:
        return ""
    info = next((c for c in MSSE_CATEGORIES if c["name"] == category_name), None)
    emoji = info["emoji"] if info else "🔬"
    anchor = category_name.lower().replace(" ", "-").replace("/", "-").replace(" & ", "-")
    header = f"\n\n## {emoji} {category_name}\n\n"
    header += f"[Back to top](#{README_TOP_ANCHOR})\n\n"
    active = sorted([l for l in category_listings if l["active"]], key=lambda l: l["date_posted"], reverse=True)
    inactive = sorted([l for l in category_listings if not l["active"]], key=lambda l: l["date_posted"], reverse=True)
    result = header
    if active:
        result += create_md_table(active) + "\n\n"
    if inactive:
        result += (
            "<details>\n"
            f"<summary>🗃️ Inactive roles ({len(inactive)})</summary>\n\n"
            + create_md_table(inactive) +
            "\n\n</details>\n\n"
        )
    return result


def classifyJobCategory(job):
    # First check if there's an existing category
    if "category" in job and job["category"]:
        # Map the existing category to our standardized categories
        category = job["category"].lower().strip()
        
        # Hardware variations
        if category in ["hardware", "hardware engineering", "embedded engineering", "embedded", "firmware", "fpga", "circuit", "chip", "silicon", "asic"]:
            return "Hardware Engineering"
        
        # Quantitative Finance variations
        elif category in ["quant", "quantitative finance", "quantitative", "finance", "trading", "investment", "financial"]:
            return "Quantitative Finance"
        
        # Data Science, AI & ML variations
        elif category in ["ai/ml/data", "data & analytics", "ai & machine learning", "data science", "data science, ai & machine learning", 
                         "ai", "ml", "machine learning", "data", "analytics", "research", "ai/ml", "data science & analytics"]:
            return "Data Science, AI & Machine Learning"
        
        # Product Management variations
        elif category in ["product", "product management", "pm", "apm", "product manager"]:
            return "Product Management"
        
        # Software Engineering variations (most common)
        elif category in ["software", "software engineering", "software engineer", "engineering", "swe", "dev", "developer", 
                         "backend", "frontend", "fullstack", "full-stack", "mobile", "web", "infrastructure", "devops", "sre"]:
            return "Software Engineering"
        
        # Other
        elif category in ["other", "misc", "miscellaneous"]:
            return "Other"
        
        # If category is already in the correct format, return it as-is
        if job["category"] in ["Hardware Engineering", "Quantitative Finance", "Data Science, AI & Machine Learning", "Product Management", "Software Engineering", "Other"]:
            return job["category"]
    
    # If no category exists or it's not recognized, classify by title
    # Order of filtering based on title: hardware -> quant -> data science -> software eng -> product -> other
    title = job.get("title", "").lower()
    
    # Hardware (first priority)
    if any(term in title for term in ["hardware", "embedded", "fpga", "circuit", "chip", "silicon", "asic", "robotics"]):
        return "Hardware Engineering"
    
    # Quant (second priority)
    elif any(term in title for term in ["quant", "quantitative", "trading", "finance", "investment"]):
        return "Quantitative Finance"
    
    # Data Science (third priority)
    elif any(term in title for term in ["data science", "data scientist", "ai &", "machine learning", "ml", "data analytics", "data analyst", "research eng", "research sci"]):
        return "Data Science, AI & Machine Learning"
    
    # Software Engineering (fourth priority)
    elif any(term in title for term in ["forward deployed", "forward-deployed","software", "software eng", "software dev", "product engineer", "fullstack engineer", "frontend", "backend", "founding engineer", "mobile dev", "mobile engineer"]):
        return "Software Engineering"
    
    # Product (fifth priority)
    elif any(term in title for term in ["product manag", "product analyst", "apm"]) or ("product" in title and "analyst" in title):
        return "Product Management"
    
    # Other (everything else)
    else:
        return "Other"

def ensureCategories(listings):
    for listing in listings:
        # Always classify to ensure proper category mapping
        # This handles missing categories AND maps existing categories to standard format
        listing["category"] = classifyJobCategory(listing)
    return listings

def embedTable(listings):
    listings = ensureCategories(listings)
    listings = mark_stale_listings(listings)
    listings = filter_to_scientific(listings)
    listings = ensure_msse_categories(listings)

    active_listings = filter_active(listings)
    category_counts = {}
    for c in MSSE_CATEGORIES:
        name = c["name"]
        category_counts[name] = len([l for l in active_listings if l.get("msse_category") == name])
    total_active = len(active_listings)

    category_links = []
    for c in MSSE_CATEGORIES:
        name = c["name"]
        count = category_counts.get(name, 0)
        anchor = name.lower().replace(" ", "-").replace("/", "-").replace(" & ", "-")
        category_links.append(f"{c['emoji']} **[{name}](#{anchor})** ({count})")
    category_counts_str = "\n\n".join(category_links)

    filepath = "README.md"
    newText = ""
    in_browse_section = False
    browse_section_replaced = False
    in_table_section = False

    with open(filepath, "r") as f:
        for line in f.readlines():
            if not browse_section_replaced and line.startswith("### Browse"):
                in_browse_section = True
                newText += f"### Browse {total_active} scientific / MSSE-relevant roles by category\n\n{category_counts_str}\n\n---\n"
                browse_section_replaced = True
                continue

            if in_browse_section:
                if line.startswith("---"):
                    in_browse_section = False
                continue

            if not in_table_section and "TABLE_START" in line:
                in_table_section = True
                newText += line
                newText += "\n---\n\n"
                for c in MSSE_CATEGORIES:
                    newText += create_msse_category_table(listings, c["name"])
                newText += "\n"
                continue

            if in_table_section:
                if "TABLE_END" in line:
                    in_table_section = False
                    newText += line
                continue

            if not in_browse_section and not in_table_section:
                newText += line

    with open(filepath, "w") as f:
        f.write(newText)

def sortListings(listings):
    oldestListingFromCompany = {}
    linkForCompany = {}

    for listing in listings:
        date_posted = listing["date_posted"]
        if listing["company_name"].lower() not in oldestListingFromCompany or oldestListingFromCompany[listing["company_name"].lower()] > date_posted:
            oldestListingFromCompany[listing["company_name"].lower()] = date_posted
        if listing["company_name"] not in linkForCompany or len(listing["company_url"]) > 0:
            linkForCompany[listing["company_name"]] = listing["company_url"]

    listings.sort(
        key=lambda x: (
            x["active"],  # Active listings first
            x['date_posted'],
            x['company_name'].lower(),
            x['date_updated']
        ),
        reverse=True
    )

    for listing in listings:
        listing["company_url"] = linkForCompany[listing["company_name"]]

    return listings


def checkSchema(listings):
    props = ["source", "company_name",
             "id", "title", "active", "date_updated", "is_visible",
             "date_posted", "url", "locations", "company_url",
             "sponsorship"]
    for listing in listings:
        for prop in props:
            if prop not in listing:
                fail("ERROR: Schema check FAILED - object with id " +
                      listing["id"] + " does not contain prop '" + prop + "'")