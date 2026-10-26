# Healthcare Intelligence V7.7.10 — Methodological transparency

## Changes
- Preserve V7.7.9 official CDC data acquisition, five XPT modules, screening proxy, and all prior tabs.
- Add an approximate **Student-t 95% confidence interval** based on stratified PSU Taylor SE and design degrees of freedom. The prior normal approximation remains in the audit for comparison. This does not independently validate the variance estimator.
- Add **extreme-case missing-screening classification sensitivity**: all unresolved screening flags negative vs all positive, with the survey weights of unresolved observations. These are classification scenarios, **not** confidence intervals or formal missing-data corrections.
- Show new metrics in the NHANES Compute tab and include them in downloadable JSON.
- Add `PROJECT_MASTER.md` for project history, audit, caveats, and release protocol.

## Scientific limitations
- The 2021–2023 screening proxy is not confirmed CKD, T2D, treatment eligibility, or a commercial market.
- The historical 9,233,798 estimate cannot be reconstructed from available original definitions.
- Phlebotomy weight suitability, lab nonresponse, analytic sample selection, and survey variance methodology require independent subject-matter verification.
- Extreme-case bounds do not account for possible missing survey weights, nonresponse bias, or model uncertainty.
- No live CDC access or replication of the 13.02M result was performed in the build environment.

## Deployment
Update permanent `testing` branch; do not change production `release` until reviewed.
