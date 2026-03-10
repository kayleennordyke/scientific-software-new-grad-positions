#!/usr/bin/env python3
"""
Add approved jobs from scripts/approved-jobs.json into the main listings
and regenerate the README. Bypasses the GitHub issue workflow.

Usage:
  1. Copy entries from discovered-jobs.json into approved-jobs.json (or create it).
  2. Run from repo root: python scripts/add_approved_to_listings.py
  3. Commit and push the updated .github/scripts/listings.json and README.md.

approved-jobs.json format (same as discovered-jobs.json):
  [{"company": "...", "title": "...", "url": "...", "location": "..."}, ...]
"""

import json
import os
import re
import subprocess
import sys
import uuid
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
LISTINGS_PATH = REPO_ROOT / ".github" / "scripts" / "listings.json"
APPROVED_PATH = REPO_ROOT / "scripts" / "approved-jobs.json"
UPDATE_READMES = REPO_ROOT / ".github" / "scripts" / "update_readmes.py"


def _strip_utm(url):
    if not url:
        return url
    for sep in ("?utm_source", "&utm_source"):
        i = url.find(sep)
        if i != -1:
            return url[:i]
    return url


def _locations_from_string(loc):
    if not loc or not loc.strip():
        return ["Remote"]
    # Split on semicolon or pipe, strip
    parts = re.split(r"[;|]", loc)
    return [p.strip() for p in parts if p.strip()] or ["Remote"]


def main():
    if not APPROVED_PATH.exists():
        print(f"No {APPROVED_PATH} found. Create it with entries like:")
        print('  [{"company": "Acme", "title": "Software Engineer", "url": "https://...", "location": "SF"}]')
        sys.exit(1)

    with open(APPROVED_PATH) as f:
        approved = json.load(f)
    if not approved:
        print("approved-jobs.json is empty. Add jobs to approve, then run again.")
        sys.exit(0)

    # Load util from .github/scripts for classifyJobCategory
    sys.path.insert(0, str(REPO_ROOT / ".github" / "scripts"))
    import util

    with open(LISTINGS_PATH) as f:
        listings = json.load(f)
    existing_urls = {_strip_utm(l.get("url") or "") for l in listings}
    now = int(datetime.now().timestamp())
    added = 0

    for job in approved:
        url = _strip_utm((job.get("url") or "").strip())
        if not url:
            continue
        if url in existing_urls:
            print(f"Already in list: {job.get('title', '')} @ {job.get('company', '')}")
            continue
        company = (job.get("company") or "").strip()
        title = (job.get("title") or "").strip()
        if not company or not title:
            print(f"Skipping entry missing company/title: {job}")
            continue
        locations = _locations_from_string(job.get("location") or "")
        listing = {
            "id": str(uuid.uuid4()),
            "source": "approved",
            "company_name": company,
            "title": title,
            "url": url,
            "locations": locations,
            "company_url": "",
            "active": True,
            "is_visible": True,
            "date_posted": now,
            "date_updated": now,
            "sponsorship": "Offers Sponsorship",
            "degrees": [],
        }
        listing["category"] = util.classifyJobCategory(listing)
        listings.append(listing)
        existing_urls.add(url)
        added += 1
        print(f"Added: {title} @ {company}")

    if added == 0:
        print("No new jobs added.")
        sys.exit(0)

    with open(LISTINGS_PATH, "w") as f:
        json.dump(listings, f, indent=4)

    # Regenerate README
    result = subprocess.run(
        [sys.executable, str(UPDATE_READMES)],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print("update_readmes.py failed:", result.stderr or result.stdout)
        sys.exit(1)
    print(f"Added {added} job(s). README updated. Commit listings.json and README.md.")
    sys.exit(0)


if __name__ == "__main__":
    main()
