# Healthcare Intelligence V7.7.8 — Participant-level Survey Computation

## What is new

- **NHANES Compute** tab: user uploads authentic, de-identified participant-level CSV data and explicitly maps a user-derived binary screening flag, survey weight, survey stratum, PSU, and optional universe flag.
- Computes a survey-weighted **screening-proxy population total**, unweighted counts, missing screening count, and a stratified PSU Taylor-linearization variance estimate with a disclosed with-replacement/normal-CI approximation.
- Refuses to display confidence intervals for singleton strata and rejects invalid flags, weights, and missing survey design identifiers.
- Requires a written survey-cycle/weight-derivation note and screening definition; exports a JSON audit record. The app does not bundle or download participant-level NHANES data.
- Preserves all V7.7.7 KG, population observations, PubMed, ClinicalTrials.gov, evidence-gap reasoning, and prior regression tests.

## Important boundaries

This is a **real computation on uploaded data**, not a reproduction of the historical 9,233,798 estimate unless the authentic source records and correct variables/rules are supplied. The screening flag must be independently derived and verified. The app does **not** automatically merge NHANES component files, derive CKD/T2D flags, validate survey-cycle weights, confirm chronic disease, estimate finerenone eligibility, or estimate market size. The confidence interval is an approximation and must be checked against official survey-design guidance before research use. Uploaded data must be de-identified.

## Local validation

Run `python -m unittest discover -s tests -v` in the `app` directory.

## Deployment

Copy the package contents into the existing GitHub repository on the **permanent `testing` branch** (not a new version-specific branch), inspect changes, commit and push. Streamlit Community Cloud connected to `testing` should automatically redeploy at `kerendia-intelligence.streamlit.app`. Do not touch `release` / `kerendia-opportunities.streamlit.app` until review.
