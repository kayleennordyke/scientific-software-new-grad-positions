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

Then open `scripts/discovered-jobs.md`, review each link, and if you want to add a job to the main repo list, submit it via [CONTRIBUTING](../CONTRIBUTING.md) (e.g. open an issue or use the existing process). **Do not auto-add jobs** — always keep a manual review step.

**Customization:** Edit `discover_jobs.py`:

- **`TARGET_COMPANIES`** — Add or change `(display_name, source, board_id)`. Greenhouse: slug from `boards.greenhouse.io/<slug>`. Lever: slug from `jobs.lever.co/<slug>`. Ashby: board name from `jobs.ashbyhq.com/<BoardName>`.
- **`DISCOVERY_KEYWORDS`** — Add/remove phrases to match in job title or description.

**Target companies (examples):** Energy (Tesla, Redwood Materials, QuantumScape, Form Energy, Sila), Biotech (Genentech, Recursion, Insitro, Amgen, GSK), Scientific software (Schrödinger, D. E. Shaw Research, NVIDIA, Altos Labs). The script supports Greenhouse, Lever, and Ashby; add `("Company", "ashby", "BoardName")` for any company whose careers page is at `jobs.ashbyhq.com/BoardName`.
