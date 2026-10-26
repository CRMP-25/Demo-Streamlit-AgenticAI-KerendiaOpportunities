# Healthcare Intelligence V7.7.5 — Verified evidence and controlled release workflow

## Clinical changes
- Corrected FIGARO-DKD primary publication PMID 34449181 title to **Cardiovascular Events with Finerenone in Kidney Disease and Type 2 Diabetes** (Pitt et al., NEJM 2021; DOI 10.1056/NEJMoa2110956). V7.7.4 used the correct PMID but a different title, causing fail-closed verification. This correction was independently checked against PubMed; deployed live API verification remains pending.
- Preserves primary FIDELIO-DKD PMID 33264825 and pooled FIDELITY PMID 35023547.
- Adds conservative descriptive event-percentage differences **only when both exact reported percentages appear in a verified primary PubMed abstract**. No claims of independent trial appraisal, time-adjusted risk reduction, or eligible population.
- Adds non-destructive KG assertion warning for `DR6 — treats → D1`, when traversed. Baseline KG untouched.

## Automated validation and single-app deployment
- `.github/workflows/validate-release.yml` runs offline tests, KG checksum and fixed counts, version checks, and generates two reproducible **offline** Markdown investigation snapshots as downloadable GitHub Actions artifacts (90-day retention).
- Create a stable GitHub branch called `release`. Point **one existing Streamlit app** to `release` and `app.py` once. After a pull request is reviewed and merged into `release`, Streamlit Community Cloud automatically redeploys the existing app from that branch.
- **Safety:** Configure GitHub branch protection/ruleset on `release` requiring the `validate` status check and pull requests before merging. Without this configuration, the workflow is a check, **not** a predeployment gate; direct pushes can trigger Streamlit deployment before checks complete.
- This package does not connect to your GitHub or Streamlit accounts and does not perform any remote push, branch creation, deployment, or live clinical validation.
- Future updates still require putting new source code on a GitHub branch. A GitHub connector with authorized write capability could reduce this further, but is not configured here.

## One-time setup
1. Copy this package into a new GitHub development branch (e.g. `v7.7.5-testing`) based on `v7.7.4-testing`; commit and push.
2. In GitHub, create `release` from this tested branch (or make a pull request to an existing `release` branch).
3. In GitHub repository Settings > Rules > Rulesets (or Branch protection), require PRs and the `validate` check for `release`; check status name in first workflow run. GitHub plan and repository visibility can affect rule availability/enforcement.
4. In Streamlit Cloud, edit the existing `kerendia-intelligence-v774` app's GitHub source branch to `release` and main file to `app.py` if the UI permits; if branch cannot be changed, recreate **one** permanent app once and retire the previous one after validation.
5. For subsequent releases: push a development branch, open a PR into `release`, wait for checks, review, and merge. The same Streamlit URL redeploys.

## What is and is not archived
- Git commits/tags preserve historical source code.
- GitHub Actions artifacts preserve **offline** test snapshots for 90 days; these are not live PubMed/ClinicalTrials.gov outputs. Download and retain clinically important **live** Markdown and evidence JSON separately; live results can change.
- For longer retention, store signed/hashed snapshots in an approved evidence archive; this release does not automatically commit live responses or write to the clinical KG.

## Rollback
Revert the release commit via a reviewed PR into `release` (or merge a prior tagged state), validate, and let Streamlit redeploy. Do not force-push the protected release branch.
