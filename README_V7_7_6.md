# Healthcare Intelligence V7.7.6 — Clinical Intelligence Synthesis

Incremental release built on V7.7.5. Preserves the original KG, NHANES observations, Streamlit interface, live PubMed and ClinicalTrials.gov integrations, and automated offline validation.

## New in V7.7.6
- Evidence-chain narrative connecting the clinical question, preserved KG, source-verified FIDELIO-DKD/FIGARO-DKD abstracts, historical NHANES screening proxy, eligibility limitations, and treatment opportunity.
- A consolidated evidence register explicitly separates primary pivotal trials from pooled and secondary publications.
- Decision gates prevent an unsupported transition from screening proxy to diagnosed, eligible, or addressable populations.
- Missing source abstracts produce explicit unavailable/blocked statements instead of fabricated efficacy numbers.
- New offline regression tests and consistent release metadata/download naming.

## Deploy
Create branch `v7.7.6-testing` from your current `release` branch, then copy this package's contents into the repository root, commit, and push. Deploy a separate Streamlit app from `v7.7.6-testing` with main file `app.py`. Keep the existing `release` deployment untouched until validated. The public `kerendia-opportunities.streamlit.app` URL currently points to the release branch; do not repoint it until this test release is approved.

## Validate
`python -m unittest discover -s tests -q`

Tests are offline and do not prove external APIs will be reachable in Streamlit Cloud. This remains a controlled demonstration, not clinical advice or a validated market estimate.
