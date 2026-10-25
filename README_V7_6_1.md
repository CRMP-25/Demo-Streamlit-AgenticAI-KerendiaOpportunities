# Healthcare Intelligence V7.6.1 — Integrated Demo

## Quick start (Mac)

Unzip the package, open Terminal in the `Healthcare_KG_Agentic_Intelligence_V7_6_1` directory, then:

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements_v7_6.txt
export SSL_CERT_FILE="$(python3 -m certifi)"
python3 -m streamlit run app.py --server.port 8502
```

If `python3 -m certifi` fails, run `python3 -m pip install certifi`. For an existing environment, reuse its dependencies and activate it. Never disable TLS verification.

Open http://localhost:8502 and choose **Ask the Agent**. Select the integrated finerenone question, leave live evidence checked, and click Investigate. The results should show readable sections and source IDs. Check **KG Explorer** for dark, readable plot labels and **Intelligence Report** for the downloadable synthesis.

## Scope and scientific policy

This is a controlled demonstration, not a clinical decision system. Existing NHANES estimates are preliminary single-visit CKD screening and probable T2D proxies. No clinical eligibility, addressable market, or cross-cycle trends are inferred. External APIs are live only; errors remain visible and do not trigger fabricated fallback evidence. The original KG is immutable and the production GitHub repository is not accessed.

## Development validation

47/47 automated tests passed. Baseline checksum preserved. The updated GUI and integrated live retrieval require user-side confirmation on a Streamlit-enabled machine.
