# Healthcare Intelligence V7.7.3 — Evidence Interpretation Upgrade

## Purpose
Targeted improvement to V7.7.2. The original KG and historical NHANES evidence are unchanged.

## Changes
- Single release constant `src/version.py` drives banner, page title, and every download filename.
- Integrated investigations add an executive evidence synthesis with explicit decision gaps.
- Source-attributed pivotal evidence table with transparent *title-only* publication-type heuristics (not verified study classification).
- Complete retrieved abstract sections replace mid-sentence truncated excerpts; abstracts remain **not independently critically appraised**.
- Original KG relationships include source concept descriptions and original node IDs; graph assertions are **not clinically adjudicated**.
- NHANES-to-trial applicability matrix separates available, derivable, and unavailable information.
- Population-only question routing and safeguards retained.

## Known limitations
This is bounded deterministic evidence orchestration, not autonomous LLM reasoning or a clinical-grade assessment. The pivotal retrieval search does not guarantee original FIDELIO-DKD and FIGARO-DKD primary reports. Publication-type labels use title heuristics and require manual verification. Clinical findings are not independently verified. Original NHANES numbers have not been independently replicated. Live PubMed and ClinicalTrials.gov calls and Streamlit Cloud rendering require deployment-side acceptance testing.

## Testing
Run `python -m unittest discover -s tests -q` from project root. 70 tests passed in the development environment. Original KG SHA-256: `4b43634ec370b1a7b1dfc28e6fbb9458172ba8234959d6c5f5713ad05d6212bf`.

## Deployment
Create branch `V7.7.3-testing` from `V7.7.2-testing`. Copy this package's **contents** into the local repository (never replace `.git`); review changes, commit and push. Create a separate Streamlit Cloud deployment targeting `V7.7.3-testing` / `app.py` / Python 3.12. Do not touch `main` or previous deployments. Do not upload `.venv`, `.env`, `.streamlit/secrets.toml`, or other credentials.

## Acceptance
1. Verify app banner, report heading and filenames all say V7.7.3.
2. Run population-only question and confirm PubMed/KG bypass.
3. Run integrated Kerendia question with live evidence checked. Review study classifications and evidence sources. Confirm no clipped abstract excerpts and no unsupported eligibility numbers.
4. Download Markdown and JSON for evaluation.
