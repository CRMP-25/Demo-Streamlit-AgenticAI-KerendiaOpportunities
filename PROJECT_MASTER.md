# Healthcare Intelligence — Project master record

Updated: 2026-10-26. Source of truth for decisions and scientific caveats; keep alongside release READMEs.

## Purpose
An evidence-grounded, agentic clinical-intelligence demonstration integrating a clinical knowledge graph, population screening intelligence, PubMed and ClinicalTrials.gov evidence, and documented clinical eligibility gates. No screening result is a diagnosis or prescription.

## Environments
- Testing: GitHub branch `testing`, Streamlit `https://kerendia-intelligence.streamlit.app`.
- Production: GitHub branch `release`, Streamlit `https://kerendia-opportunities.streamlit.app`.
- Never merge to `release` without explicit approval.

## Release history (summary)
- V7.7.6: Clinical evidence synthesis and eligibility gates.
- V7.7.7: Evidence gaps, prioritized investigations, quality flags.
- V7.7.8: Manual participant-level NHANES CSV calculation with stratified PSU Taylor approximate variance.
- V7.7.9: Direct retrieval of five official CDC NHANES XPT files and screening calculation.
- V7.7.10: Student-t approximate CI, missing-status extreme-case bounds, master documentation.

## KG reference (historical; verify against deployed runtime)
293 concepts, 517 edges, 88 candidate links, four historical population observations. The original KG must remain read-only.

## NHANES 2021–2023 computation
Sources: DEMO_L, GHB_L, BIOPRO_L, ALB_CR_L, DIQ_L from CDC; joined by SEQN. Age >=20; kidney proxy eGFR 2021 CKD-EPI creatinine <60 or ACR >=30 mg/g; diabetes proxy HbA1c >=6.5% or self-report DIQ010=1. Uses WTPH2YR and SDMVSTRA/SDMVPSU. A single observation does not confirm CKD chronicity, diabetes subtype, or treatment eligibility.

### V7.7.9 observed audit (user-supplied 2026-10-26)
- Computed weighted screening total: 13,020,437.73; normal 95% approximate CI: 11,717,134.99–14,323,740.47.
- SE: 664,950.38; design degrees of freedom: 15.
- 398 unweighted positives; 5,668 known screening status; 396 unresolved among 6,064 adults in analysis universe.
- 11,933 DEMO rows; 7,199 rows supplied after removing 4,734 missing phlebotomy weights.
- Historical reported estimate: 9,233,798; difference 3,786,639.73. Exact historical definitions and complete-case criteria not recovered, so not a validation target.
- V7.7.10 adds a Student-t interval and missing-status bounds at computation time; do not substitute hypothetical values for a rerun.

## Validation status
- Functional: V7.7.9 real-data run succeeded on deployed testing Streamlit app; provenance captured in JSON.
- Statistical: design variance implementation, weight/analytic sample suitability, missing-data assumptions, and clinical screening validity require independent methodological validation.
- V7.7.10: offline regression testing in build environment; live CDC rerun required after testing deployment.

## Required follow-up
1. Re-run live V7.7.10 and save JSON audit.
2. Examine whether phlebotomy weights and missing weight exclusions match CDC analytic guidance for joint biomarker variables.
3. Verify PSU Taylor SE and t-based interval against an independent survey-statistics package.
4. Review missingness by age and covariates, and perform formal sensitivity/adjustment where defensible.
5. Recover historical 9.23M analysis before claiming comparability.
6. Preserve evidence references and audit SHA-256 checksums in each scientific release.

## Release protocol
Update this file and a version-specific README in each release. Run regression tests, create ZIP with source and tests (exclude __pycache__), deploy to permanent testing branch, verify Streamlit UI and live CDC run, request approval before production.
