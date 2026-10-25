# Healthcare Intelligence V7.7.2 — Focused population answers

This version corrects the population-only report from V7.7.1. The original clinical KG and NHANES observations are preserved unchanged.

## What changed
- Explicit question intent classification. Population-only questions avoid KG concept retrieval, KG traversal, PubMed, ClinicalTrials.gov, and pivotal abstract retrieval. The checkbox cannot override this safety/efficiency routing.
- Population report includes source-derived estimated adults, complete-case weighted prevalence, reported population 95% CI, survey weight, unweighted cases, unweighted complete-case denominator, and evidence ID.
- The report preserves the screening-not-diagnosis/eligibility limitation. No trends or eligibility estimates are inferred.
- Integrated and clinical questions retain the previous V7.7.1 evidence workflow; clinical-only questions are classified but not yet isolated from all population sections.

## Deployment
On GitHub Desktop select the separate `v7.7.2-testing` branch (create it from the last tested branch if desired), copy the **contents** of this unzipped directory into the repository's Finder folder, leaving `.git` untouched, commit and push. In Streamlit Community Cloud deploy/select the testing branch; do not merge into `main` during evaluation.

## Focused acceptance question
How many US adults meet the chronic kidney disease (CKD) laboratory-screening and probable type 2 diabetes (T2D) criteria in NHANES 2021–2023? Report the estimated population, prevalence percentage, 95% confidence interval, survey weights used, and unweighted sample size. Clearly distinguish this screening-based estimate from confirmed CKD diagnosis and finerenone treatment eligibility.

Expected: 9,233,798 adults, 4.2009% weighted prevalence, 95% CI 7,843,384–10,624,212, WTPH2YR, 283 unweighted cases, 5,143 complete cases. No clinical KG, literature, or trial sections.

Run tests: `python3 -m unittest discover -s tests -v`. Live HTTPS integration and Streamlit Cloud GUI need user-side verification.
