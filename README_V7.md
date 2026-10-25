# V7 Agentic Healthcare Intelligence — controlled research build

**Status:** Local evidence, bounded investigation and Streamlit code implemented and locally tested; **NOT** a scientifically released autonomous agent. Live biomedical API retrieval could not be validated in the current network-restricted execution environment. No fabricated clinical evidence, patients, trial records, or survey data were used.

## Run

```bash
python -m unittest discover -s tests -v
python -m src.release
python -c "from src.v7 import investigate; print(investigate('How many adults have CKD and diabetes?'))"
pip install -r requirements_v7.txt
streamlit run app.py
```

The Streamlit UI is optional; it was not launched in this environment. The engine itself was exercised through local tests.

## Architecture and gates

- V7.0: preserved V1–V6 notebooks, baseline integrity, local data regression. **Local gates pass; raw NHANES/R survey rerun not independently demonstrated**.
- V7.1: bounded, transparent multi-tool investigation; **not LLM autonomy**. Conservative answer policies tested.
- V7.2: real PubMed ESearch/ESummary and ClinicalTrials.gov v2 connectors; **live retrieval unverified here** because external network is blocked. No mocks or simulated records.
- V7.3: period selection, provenance, weights, and user-supplied arithmetic scenario; **no fresh NHANES recalculation or eligibility inference**.
- V7.4: Streamlit application source created; **UI runtime not browser-tested**.
- V7.5: local regression, manifest, validation ledger; **overall release CONDITIONAL / NOT SCIENTIFICALLY APPROVED**.

## Data boundaries

The baseline KG file is byte-preserved with SHA-256 `4b43634ec370b1a7b1dfc28e6fbb9458172ba8234959d6c5f5713ad05d6212bf`. No GitHub operation is implemented or invoked. All artifacts are local to this package. Candidate clinical links remain unreviewed; cross-cycle trend and treatment-eligibility conclusions remain blocked. Scientific evidence is real source material only. Minimal artificial software inputs in unit tests never enter evidence or reports.

See `docs/PROJECT_EXECUTION_RECORD.md`, `reports/v7_validation_ledger.json`, and `reports/v7_execution_log.txt` for precise status.
