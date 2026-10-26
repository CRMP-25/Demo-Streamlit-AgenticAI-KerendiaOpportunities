# Healthcare Intelligence V7.7.7 — Evidence-gap triage

This release **builds directly on V7.7.6** and retains the original immutable KG, historic NHANES observation, live PubMed and ClinicalTrials.gov retrieval, Streamlit tabs, and source-guarded trial evidence.

## Actual changes
- New deterministic evidence-gap assessment that checks primary trial identity and abstract percentages before reporting verification.
- An auditable status table for primary efficacy, NHANES screening, diagnosis, label-based eligibility, and treatment utilization.
- Prioritized concrete follow-up investigations, with blockers instead of invented eligibility or market estimates.
- Highlights a potentially misleading finerenone-to-uncomplicated-diabetes KG assertion when it appears in the retrieved graph; original KG unchanged.
- Offline regression tests for missing sources, incorrect PMID, population-only routing, and version metadata.

## Important limitation
**This release does not add new NHANES microdata analysis or autonomous hypothesis testing.** No authentic participant-level survey files or validated label-mapping inputs were available in the V7.7.6 release package. The next substantive phase requires those inputs. This version improves actionability and auditability without pretending to have calculated new epidemiology.

## Deployment
Use existing Streamlit testing application `kerendia-intelligence.streamlit.app` (do not create a version-specific domain). Test branch `v7.7.7-testing`, main file `app.py`, Python 3.11. Keep `kerendia-opportunities.streamlit.app` on `release` until approved.

## Local validation
`python -m unittest discover -s tests -v`
