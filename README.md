# Healthcare Knowledge Graph Population Intelligence — Consolidated V1–V6

This is a **single downloadable, read-only consolidated research package** containing all supplied V1–V6 notebook sources, preserved V5–V6 evidence, a verified immutable clinical KG baseline, a modular offline evidence query engine, regression tests, and a master notebook.

## Run locally or in Colab

Open `notebooks/Healthcare_KG_Master_Consolidated.ipynb` with the package folder available, or from the project root run:

```bash
python -m unittest discover -s tests -v
python -c "from src.engine import ask; print(ask('How many adults have CKD and diabetes?'))"
```

The master notebook is an **integrated evidence/query entry point**, not a claim that the original NHANES survey computations were rerun in this environment. The original V1–V4.2 notebooks remain separately preserved for full data reprocessing, including the Gemini-corrected V3.1. The original multi-cycle data downloads and R survey validations require the original environment and dependencies. No GitHub operations, API calls, or network downloads are made by the consolidated offline engine.

## Scientific safeguards

- 293-node, 517-edge baseline KG is SHA-256 verified and never modified.
- Four NHANES population observations are **single-visit screening proxies**, not confirmed diagnoses.
- 88 historical clinical links are review records; **no clinical mapping is declared human-approved**.
- Kerendia eligibility, addressable market sizing, and cross-cycle trend claims are blocked.
- 2021–2023 survey weighting is preserved in the V4.2 source artifacts (`WTPH2YR`).
- Cross-cycle creatinine comparability, clinical mapping review, and external epidemiological validation remain open.

## Structure

- `notebooks/history/`: full V1–V6 source notebooks (corrected V3.1 included).
- `notebooks/Healthcare_KG_Master_Consolidated.ipynb`: master entry point.
- `src/engine.py`: offline integrity checks and guarded Q&A.
- `data/`: baseline KG, population evidence, and clinical link review.
- `evidence/`: original V5, V5.1, V6 outputs ZIPs.
- `reports/`: historical validation reports and new consolidated test report.
- `tests/`: regression tests.

**Status:** Integrated offline research baseline with validated packaging and regression tests; **not** independently revalidated epidemiology or a fully autonomous LLM agent.
