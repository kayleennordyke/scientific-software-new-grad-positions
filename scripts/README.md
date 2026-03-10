# Scripts

Optional tooling for the scientific software job list.

## Job discovery (`discover_jobs.py`)

**Purpose:** Find MSSE-relevant roles at target companies by fetching their career pages (Greenhouse, Lever, Ashby). Output is **for manual review only** — nothing is auto-added to the main list.

**What it does:**

- Fetches job listings from configured companies (Greenhouse, Lever, and Ashby APIs).
- Keeps only roles that are **new grad, junior, entry-level, or internship** (and match those terms in title/description).
- Filters by scientific keywords: computational chemistry, research software engineer, scientific computing, battery modeling, bioinformatics, HPC, simulation, ML for science, etc.
- Writes `discovered-jobs.md` and `discovered-jobs.json` in this folder.

**How to run:**

```bash
python scripts/discover_jobs.py
```

Then open `scripts/discovered-jobs.md`, review each link. To add jobs **without opening a GitHub issue**, use the approval flow below.

**Customization:** Edit `discover_jobs.py`:

- **`TARGET_COMPANIES`** — Add or change `(display_name, source, board_id)`. Greenhouse: slug from `boards.greenhouse.io/<slug>`. Lever: slug from `jobs.lever.co/<slug>`. Ashby: board name from `jobs.ashbyhq.com/<BoardName>`.
- **`DISCOVERY_KEYWORDS`** — Add/remove phrases to match in job title or description.

**Target companies (examples):** Energy (Tesla, Redwood Materials, QuantumScape, Form Energy, Sila), Biotech (Genentech, Recursion, Insitro, Amgen, GSK), Scientific software (Schrödinger, D. E. Shaw Research, NVIDIA, Altos Labs). The script supports Greenhouse, Lever, and Ashby; add `("Company", "ashby", "BoardName")` for any company whose careers page is at `jobs.ashbyhq.com/BoardName`.

---

## Add approved jobs to the README (`add_approved_to_listings.py`)

**Purpose:** Add jobs to the main list and regenerate the README **without opening a GitHub issue**. Use this after you’ve reviewed `discovered-jobs.md` and decided which roles to include.

**Steps:**

1. **Copy the jobs you want** from `discovered-jobs.json` into `approved-jobs.json`. The format is the same: an array of objects with `company`, `title`, `url`, and `location`.
2. **From the repo root**, run:
   ```bash
   python scripts/add_approved_to_listings.py
   ```
3. The script appends those jobs to `.github/scripts/listings.json` (skipping any already present), then runs the README generator. **Commit and push** the updated `listings.json` and `README.md`.

**Example `approved-jobs.json`:**
```json
[
  {"company": "Sila Nanotechnologies", "title": "Battery Engineering Internship", "url": "https://job-boards.greenhouse.io/silananotechnologies/jobs/7572052", "location": "Alameda, CA"},
  {"company": "Redwood Materials", "title": "Systems Modeling Intern", "url": "https://boards.greenhouse.io/redwoodmaterials/jobs/5798152004", "location": "McCarran, NV"}
]
```

You can edit `approved-jobs.json` by hand or copy-paste from `discovered-jobs.json`. Jobs already in the main list (same URL) are skipped.
