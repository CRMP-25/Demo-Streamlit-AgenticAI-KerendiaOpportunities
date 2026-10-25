# Healthcare Intelligence V7.6 — Controlled Demonstration

## Fastest way to see the demo
Open `Healthcare_Intelligence_V7_6_Offline_Demo.html` directly in a browser. It is an interactive, self-contained preview with real preserved data, pre-executed bounded investigations, KG exploration, population observations, source status, and report export. It is **not** live agentic retrieval.

## Full Streamlit application
From the extracted project root, in an environment with Python and package installation access:

```bash
python -m pip install -r requirements_v7_6.txt
streamlit run app.py
```

Use the **Evidence Explorer** button to attempt live PubMed and ClinicalTrials.gov retrieval. If either API is unavailable, the app displays the failure rather than supplying invented records. Never enter personal patient data. The app is intended for local demonstration only.

## Validation

```bash
python -m unittest discover -s tests -v
python -m src.release
```

The V7.6 local test suite passed 38/38. Actual Streamlit launch and live external API retrieval **were not verified** in the build environment (Streamlit unavailable; outbound network restricted). See `reports/v7_6_demo_validation_ledger.json` and `docs/PROJECT_EXECUTION_RECORD.md` for exact gate statuses.

## Scientific boundaries
Stored NHANES outputs represent single-visit CKD screening and probable T2D proxies. No confirmed diagnoses, treatment eligibility, validated cross-cycle trends, or pharmaceutical market-size claims. Unreviewed clinical concept mappings remain unapproved. No GitHub activity, production deployment, or simulated scientific evidence.
