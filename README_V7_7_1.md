# Healthcare Intelligence V7.7.1 — targeted corrective release

This update preserves the V7.7 architecture, the original KG, and the NHANES screening safeguards.

## Changes
- One batched PubMed ESearch and ESummary for targeted pivotal terms (instead of three sequential searches).
- Bounded retries (HTTP 429 and selected transient 5xx), with short exponential backoff and verified HTTPS.
- Six-hour **in-process** cache for successfully retrieved PubMed pivotal records and abstracts; cached results retain original retrieval timestamps. Failed responses are not cached. Cache is not durable across cloud restarts.
- One batched EFetch for distinct PMIDs.
- Relevance-ranked traversal of **original** KG edges; no invented nodes, relationships, or clinical equivalence.
- Report clearly distinguishes source excerpts from independently appraised trial findings.

## Limits
Title-based study tagging can miss pivotal articles whose titles do not explicitly mention FIDELIO-DKD, FIGARO-DKD or FIDELITY. A 429 may still persist after bounded retries. Source abstracts do not constitute independent critical appraisal. The system remains a controlled research demonstration, not a treatment recommendation or validated market estimate.

## Deployment
Update a NEW GitHub branch (suggested `v7.7.1-testing`) derived from `v7.7-testing`. Keep `main` and the working V7.7 deployment unchanged. Preserve `app.py` at repository root, select Python 3.12, and use `requirements.txt`. No secrets or virtual environments in public GitHub. Run `python -m unittest discover -s tests -v` locally. Test live cloud retrieval and download the new Markdown report before considering a merge.

## Verification
Offline tests exercise retry, no retry on 403, allowlist, cache behavior, and original KG checksum. Live PubMed and the Streamlit cloud UI are NOT verified by these offline tests.
