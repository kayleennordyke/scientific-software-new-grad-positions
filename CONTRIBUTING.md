# Contributing to the Job List

Thanks for contributing to this **scientific software & computational science** job list (MSSE-oriented). The list is synced from Simplify and filtered to roles where software meets the physical sciences.

If you have questions, open a [miscellaneous issue](https://github.com/kayleennordyke/scientific-software-new-grad-positions/issues/new/choose).

## What belongs on this list

Job postings should:

- Fit at least one of the **categories** used in the README (Battery / Energy, Computational Chemistry, Bioinformatics, Scientific Software, HPC, Simulation, ML for Science, Materials Science, Research Software Engineer, or Other).
- Be for **new grads, juniors, entry-level, or internships** (recently graduated or early-career).
- Be in the **United States, Canada, or remote**.
- **Not already be** in the list.
- Be from companies using a formal ATS (e.g. Greenhouse, Lever, Ashby, Workday). Non-ATS application links may need extra verification.

## Adding a job (via issue)

1. Create a new issue [here](https://github.com/kayleennordyke/scientific-software-new-grad-positions/issues/new/choose).
2. Choose the **New Role** template.
3. Fill in the form (link, company, title, location, **category** — use the dropdown that matches the README sections — sponsorship, etc.) and submit.
4. Submit one issue per **unique position**, even if the company has multiple roles.

After a maintainer labels the issue as approved, the job is added to the list and the README is updated automatically.

## Adding jobs without an issue (maintainers)

If you use the [discovery script](scripts/README.md) and want to add jobs without opening issues:

1. Copy the jobs you want from `scripts/discovered-jobs.json` into `scripts/approved-jobs.json`.
2. From the repo root run: `python scripts/add_approved_to_listings.py`.
3. Commit and push the updated `listings.json` and `README.md`.

## Editing a job

1. Copy the job’s apply URL (right‑click the **Apply** button → copy link address).
2. Create an issue [here](https://github.com/kayleennordyke/scientific-software-new-grad-positions/issues/new/choose) and choose **Edit Role**.
3. Paste the URL in the link field; leave other fields blank unless you’re changing them.
4. Add a note in the reason box if the change isn’t obvious, then submit.

A maintainer will review and apply the edit.
