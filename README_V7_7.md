# Healthcare Intelligence V7.7 — Evidence-Grounded Investigation

Controlled public-data demonstration. Never use identifiable patient information.

## New capabilities
- Read-only traversal of authentic original KG edges; no invented links.
- Targeted live PubMed searches for FIDELIO-DKD, FIGARO-DKD, and FIDELITY.
- Verified HTTPS PubMed XML abstract retrieval; verbatim attributed Results/Conclusions excerpts when available. Abstracts are not critically appraised and may be incomplete.
- Five-stage evidence requirements funnel; no inferred treatment-eligible or addressable market counts.
- Explicit unavailable-source handling and claim-level safeguards.

## Deployment
Copy contents into the **separate demo repository**; do not change the production repository. Community Cloud entrypoint `app.py`, Python 3.12, standard `requirements.txt`. Do not upload `.venv`, secrets, or patient data.

## Validation
Run `python3 -m unittest discover -s tests -v`. The tests use synthetic software fixtures only, never fabricated scientific evidence. Live APIs and cloud UI require separate acceptance tests.

## Limits
Bounded deterministic orchestration, not autonomous LLM reasoning. KG baseline integrity is checked on every run. NHANES outputs are historical derived single-visit proxies, not clinically verified diagnoses. PubMed titles and excerpts are not full critical appraisal or efficacy validation. Cross-cycle trends and treatment eligibility remain blocked.
