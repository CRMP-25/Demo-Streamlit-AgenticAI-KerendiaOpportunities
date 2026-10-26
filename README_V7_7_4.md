# Healthcare Intelligence V7.7.4 — Verified Pivotal Evidence and KG Interpretation

This version extends V7.7.3 without modifying the original KG or historical NHANES observations.

## Improvements
- Targets known primary FIDELIO-DKD and FIGARO-DKD publication PMIDs; verifies PubMed ESummary titles before treating them as primary publication candidates. No verification means no claim.
- Retrieves full attributed PubMed abstract sections for verified candidates when available.
- Extracts complete effect-measure sentences from real abstracts, with citations; does not calculate unverified outcomes.
- Resolves preserved graph node descriptions from the actual list-based KG schema.
- Preserves screening-versus-diagnosis-versus-eligibility safeguards.
- Centralized V7.7.4 download filenames.

## Important limits
- Primary publication title verification is not full-text critical appraisal.
- No numerical population segmentation or market estimate is produced.
- External retrieval can fail; the report must state unavailability rather than fabricate records.
- Existing versioned documentation is historical and intentionally retained.

## Run
`pip install -r requirements.txt` then `streamlit run app.py`.

## Test
`python -m unittest discover -s tests -v`
