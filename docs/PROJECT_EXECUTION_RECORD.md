# Healthcare Knowledge Graph Population Intelligence
## Project execution record, scientific safeguards and V7 milestone ledger

**Record date:** 25 October 2026  
**Scope:** V1 through V7.6.1; development and validation history  
**Current release classification:** CONTROLLED FUNCTIONAL DEMO — NOT CLINICALLY OR SCIENTIFICALLY CERTIFIED

### 1. Project purpose and original research objective

The project began as a clinical knowledge graph and an expanding evidence-based biomedical assistant, then incorporated NHANES population intelligence. The initial therapeutic context is chronic kidney disease (CKD), probable type 2 diabetes (T2D), and finerenone (Kerendia). The long-term objective is a reusable agentic healthcare research platform: clinical evidence, epidemiology, patient-segmentation questions, trial and literature retrieval, graph navigation, and defensible research reporting. It is **not** a system for diagnosing individuals or making prescribing decisions.

### 2. Original clinical knowledge graph and isolation

The source clinical KG has **293 nodes and 517 edges**. The baseline file is immutable; expected SHA-256 is `4b43634ec370b1a7b1dfc28e6fbb9458172ba8234959d6c5f5713ad05d6212bf`. Any mismatch is a release blocker. No GitHub access, clone, push, deployment, or production change is authorized. All V7 execution used local package files; the production GitHub repository was not accessed. Graph extensions, if later clinically approved, must be stored separately with provenance and versioning.

### 3. Development chronology and decisions

| Version | Major work | Scientific/technical qualification |
|---|---|---|
| V1 | NHANES 2017–2018 CKD screening plus probable T2D population estimates | Screening proxy, not diagnoses |
| V2 | eGFR, urine albumin/creatinine ratio, potassium, kidney segments | Single-visit interpretation |
| V3 | Denominator reconciliation, provenance, screening methodology | Case definition and missingness matter |
| V3.1 | Independent R survey checks, variance, missingness; Gemini-corrected notebook | Historical R cross-check reported; not rerun in V7 |
| V4 | Three survey periods (2015–2016, 2017–2018, 2021–2023) | No validated cross-period trend |
| V4.1 | Independent multi-period R checks and missing-data jackknife | Epidemiological review remains open |
| V4.2 | Correct 2021–2023 phlebotomy weight to WTPH2YR, albumin bridge, race harmonization | Creatinine comparability unresolved |
| V5 | Four provenance-linked population observations and 88 lexical KG candidates | Lexical mappings require clinical review |
| V5.1 | Conservative mapping adjudication and integration checks | 16 candidates retained for expert review; none clinically approved |
| V6 | Deterministic guarded evidence Q&A prototype | Not autonomous agentic reasoning |
| Consolidation | Historical notebooks, original KG, evidence outputs, read-only engine and regression tests | Original NHANES/R calculations not independently rerun |
| V7.0–V7.5 | Modular bounded investigation, live API connector code, population tools, Streamlit source, test ledger | Local tests pass; external and scientific release gates remain open |

### 4. Actual population observations preserved

The consolidated layer contains four historical NHANES observations. Primary 2015–2016 estimate: **7,180,438**, using `WTMEC2YR`. Primary 2017–2018: **9,497,620**, using `WTMEC2YR`. Primary 2021–2023: **9,233,798**, using `WTPH2YR`, reported 95% CI approximately **7,843,384 to 10,624,212**. The 2021–2023 albumin bridge sensitivity estimate is approximately **9,617,748**. These figures were **read from existing project artifacts**, not independently recomputed in this V7 run. They reflect a single-visit laboratory CKD screen and probable T2D proxy. They are not confirmed diagnoses, treatment-eligible populations, validated trends, or commercial market size.

### 5. Scientific integrity policy — mandatory

1. **Real scientific evidence only.** No simulated clinical evidence, fabricated trial records, invented PubMed references, fabricated patients, synthetic NHANES observations, or simulated statistical conclusions. Minimal artificial software-only unit-test inputs may be used solely to test input validation and cannot enter the evidence store or scientific outputs.
2. **Source authenticity and provenance.** Preserve PMIDs, NCT IDs, dataset version, retrieval time, survey weights, case definition, uncertainty and method. External API failure must be marked unavailable, not replaced with plausible content.
3. **Original baseline immutable.** Verify the exact clinical KG SHA-256 on every load and at release.
4. **Clinical mapping gate.** None of the 88 lexical links is human-approved. The 16 conservative V5.1 candidates still require expert review. Lexical overlap is not clinical equivalence.
5. **Eligibility and market-size gate.** NHANES screening proxies cannot establish finerenone eligibility, prescribing suitability, or total addressable market. Explicitly block such conclusions.
6. **Cross-period trend gate.** Do not assert NHANES trends until serum creatinine laboratory comparability, survey design and epidemiological methods are independently validated.
7. **Survey methodology.** Maintain correct weight variables (notably 2021–2023 `WTPH2YR`), design effects, confidence intervals, denominators, missing-data assumptions, and R cross-check provenance.
8. **Evidence status.** VERIFIED means source integrity and specified computational checks passed; REVIEW REQUIRED means interpretation or methodology awaits review; BLOCKED means evidence is insufficient or a required gate failed. A valid checksum alone never establishes scientific truth.
9. **Safety and privacy.** No patient-level data are required for the current research prototype; do not ingest personal health data into public services. No production repository access or deployment.
10. **Stage gates.** Develop → execute → inspect → validate → correct → rerun. Do not advance a dependent scientific claim when a prerequisite is blocked. Independent components may be implemented while clearly recording incomplete gates.
11. **Honest reporting.** Distinguish source-code implementation, actual execution, unit-test success, live integration testing, epidemiological validation, and clinical approval.
12. **User partnership.** Assistant handles local execution, debugging, tests, reports and packaging. User is asked only for genuine clinical decisions, external credentials or deployment approvals. No requirement to rerun completed local notebooks in Colab.

### 6. V7 architecture and actual work completed

**V7.0 — Unified baseline:** Reused V1–V6 consolidated package, checked baseline checksum, node/edge counts, observation and link counts, and weight invariants. The original notebooks are retained; a complete re-download and independent rerun of NHANES and R statistics was not possible from the available local evidence alone. Status: **PASS LOCAL, SCIENTIFIC REPRODUCTION PENDING**.

**V7.1 — Investigation:** Implemented a transparent bounded tool planner that combines population retrieval, baseline KG lexical retrieval, answer policy, and optional external retrieval. It is not an LLM-autonomous investigator and does not invent reasoning or citations. Status: **PASS LOCAL PROTOTYPE**.

**V7.2 — Literature and trial integration:** Implemented real PubMed ESearch/ESummary and ClinicalTrials.gov v2 HTTPS connectors with domain allowlists, PMID/NCT extraction, timestamps and response checksums. Actual HTTPS attempts in this execution environment failed because outbound network connectivity was unavailable. No scientific records were substituted. Status: **BLOCKED FOR LIVE VALIDATION**.

**V7.3 — Population intelligence:** Implemented period-selectable evidence views, provenance and weights, and explicitly user-assumed arithmetic sensitivities, always labeled hypothetical and not eligible-population estimates. Did not generate new survey results. Status: **PASS LOCAL, ADVANCED SURVEY RECOMPUTATION PENDING**.

**V7.4 — Streamlit:** Created an interactive research interface source with Ask, Population, KG Search, and Validation panels. The application was not launched or browser-tested in this environment. Status: **IMPLEMENTED, UI VALIDATION PENDING**.

**V7.5 — Validation and release:** Executed the combined historical and new local test suite: **28/28 tests passed**. Recorded explicit stage statuses, real external API failure, and source manifests. Status: **PASS LOCAL TESTS; CONDITIONAL RESEARCH RELEASE ONLY**.

### 7. Current evidence and release gate ledger

| Gate | Outcome | Consequence |
|---|---|---|
| Original KG byte integrity | PASS | Baseline usable as immutable input |
| Local regression suite | PASS (28/28) | Core local prototype functions tested |
| Source observations and weight variables | PASS (artifact consistency) | Historical results can be displayed with caveats |
| Live PubMed/ClinicalTrials.gov verification | BLOCKED (network) | No claims of fresh literature retrieval |
| Raw NHANES plus independent R rerun | NOT EXECUTED | Statistical reproduction not newly certified |
| Human clinical concept review | PENDING | No mappings approved for clinical inference |
| Creatinine cross-cycle comparability | PENDING | Trends remain blocked |
| External epidemiological review | PENDING | Scientific release not authorized |
| Streamlit GUI functional/browser test | PENDING | App source not deployment-ready |
| Production GitHub isolation | PASS for executed local code | No repo accessed or changed |

### 8. Handoff, reproducibility, and next actions

The package contains `src/v7.py` (research engine and real external API connectors), `src/release.py` (local gates), `app.py` (Streamlit), `notebooks/Healthcare_KG_V7_Master.ipynb`, historical notebooks, preserved evidence ZIPs, tests, example investigations, and reports. Run `python -m unittest discover -s tests -v` from the package root. Run `python -m src.release` for local release checks. Run `streamlit run app.py` only after installing the optional UI dependency and performing an appropriate security review.

Next, validate the actual biomedical APIs in a network-enabled environment; independently reproduce raw NHANES and R survey analyses; conduct clinical mapping review; verify laboratory comparability and epidemiological assumptions; test the Streamlit UI; and only then consider a scientifically validated release. Deployment requires separate authorization and must not modify the production GitHub repository.

### 9. Partnership and trust standard

The aim is a reliable research partner whose outputs are independently inspectable, not a demonstration that always produces an answer. When evidence is missing, the correct result is **UNAVAILABLE, REVIEW REQUIRED, or BLOCKED**. Success is measured by provenance, correctness, defensible limitations and reproducibility, not the number of features marked complete.


### 10. V7.6 demonstration release decision and reduced validation commitments (2026-10-25)

**Approved scope:** The immediate objective is a locally executable, evidence-grounded **Streamlit demonstration**, not a scientifically certified healthcare or production clinical system. No hosting, DGX deployment, or production GitHub activity is authorized as part of this milestone. The project owner agreed to this scope and requested that the commitments be recorded.

**Division of responsibility:** The assistant owns implementation, local execution, debugging, regression testing, evidence verification where network access permits, packaging, and transparent reporting. The project owner reviews the usefulness of the finished demo and supplies input only when genuinely needed. An existing developer may optionally assist with later hosting. Clinical experts, epidemiologists, and security specialists are **not prerequisites for the controlled demo**, provided their unreviewed domains are explicitly limited; they become relevant for higher-maturity claims or deployments.

**Demo features:** (1) Ask the Agent; (2) Clinical Knowledge Graph Explorer; (3) Population Intelligence; (4) Evidence Explorer using authentic PubMed and ClinicalTrials.gov records; (5) source-linked Intelligence Report. The representative workflow investigates clinical evidence, relevant screening populations, and treatment-related considerations for finerenone in CKD and T2D, without asserting confirmed diagnoses, eligibility, or addressable market size.

**Only six mandatory demonstration gates:**

| Gate | Acceptance criterion | Owner |
|---|---|---|
| G1: Immutable KG | Original baseline bytes and SHA-256 unchanged | Assistant |
| G2: Real evidence | No invented patients, literature, trials, or statistical observations in scientific outputs | Assistant |
| G3: Numeric fidelity | Every displayed population value matches an identified existing source artifact, with denominator and caveats | Assistant |
| G4: Authentic references | Displayed external PMID/NCT identifiers and titles correspond to actual retrievable source records; failures are reported, not mocked | Assistant |
| G5: Safe claims | Unreviewed clinical mappings, eligibility conclusions, unsupported market size and cross-cycle trends remain blocked | Assistant |
| G6: Working demo | Streamlit starts and representative user workflows complete, with errors and provenance visible | Assistant |

**Deferred beyond V7.6:** Full raw NHANES reanalysis and independent R survey replication; expert adjudication of all 88 candidate mappings (including the 16 conservatively shortlisted); creatinine cross-cycle laboratory comparability; independent epidemiological validation; formal clinical safety review; production security certification and deployment. These items are not waived: they remain prerequisites where their corresponding scientific or clinical claims are later proposed. Existing NHANES estimates are labeled **preliminary screening proxies**, not confirmed diagnoses, treatment eligibility, or market size. Trends remain blocked.

**Three maturity levels:** Level 1 = controlled functional demonstration using authentic traceable evidence (**current target**); Level 2 = independently research-validated system (future); Level 3 = clinical/production-grade system with appropriate security, operational and domain validation (future).

**Failure handling:** External source unavailability must be displayed as UNAVAILABLE, not filled with simulations. An unavailable live source prevents claiming G4 PASS for live retrieval; it does not justify fabricating records. Gate results must be marked PASS / FAIL / BLOCKED / NOT RUN with actual execution evidence. A demo can be delivered with a clearly disabled unavailable feature, but must not be labeled as having passed all six gates. Synthetic inputs are permitted solely for isolated software unit tests and must never enter evidence stores or reports.

**Delivery agreement:** Provide a locally executable Streamlit package, clear run instructions, a small set of real-data demo investigations, a six-gate validation ledger, and this updated execution record. Preserve all V1–V7 artifacts and keep production GitHub entirely untouched.

**Status on recording this decision:** V7.6 **AUTHORIZED / NOT YET EXECUTED**. This section records commitments and scope, not a claim of completed V7.6 testing.


### 11. V7.6 implementation and evidence-based demo status (2026-10-25)

**Execution:** Built a five-capability Streamlit source application with Ask the Agent, Clinical KG Explorer, Population Intelligence, Evidence Explorer, and downloadable Intelligence Report, plus a Validation panel. Added `src/demo.py` for traceable report composition and a new test suite. Corrected an inherited V7 lexical-search defect: the baseline KG stores nodes and edges as lists rather than dictionaries. This fix makes clinical KG search and edge retrieval operate on the real preserved graph.

**Immediate usable deliverable:** `Healthcare_Intelligence_V7_6_Offline_Demo.html` is a self-contained interactive preview that opens locally in a browser with no installation. It contains only existing real KG and NHANES observations and five pre-executed investigations. It does not simulate live API results or claim autonomous LLM operation. The Streamlit version remains the intended full application for a network-enabled environment.

**Actual validation:** The combined automated regression suite passed **38/38** tests. The immutable baseline checksum remains `4b43634ec370b1a7b1dfc28e6fbb9458172ba8234959d6c5f5713ad05d6212bf`. The new tests cover real baseline list-format KG nodes and edges, observation integrity, blocked eligibility, blocked trends, market-size blocking, report identifiers, and absence of fabricated external citations.

**Six demonstration gates:** G1 PASS (KG byte integrity); G2 PASS for local artifacts (no simulated scientific evidence); G3 PASS for display fidelity to preserved source observations (not independent epidemiological replication); G4 BLOCKED (live PubMed and ClinicalTrials.gov authentication unavailable due network restrictions); G5 PASS for tested blocking behavior; G6 NOT RUN for actual Streamlit UI because the runtime lacks the Streamlit dependency and cannot install it. The standalone HTML preview was generated but was not browser-automation tested. These statuses must not be conflated with scientific or clinical approval.

**Execution instructions:** Open the offline HTML file directly for an immediate interactive preview. For the full app, use a Python environment with internet access, install `requirements_v7_6.txt`, and execute `streamlit run app.py` from the extracted project root. Use the Evidence Explorer's explicit retrieval button to fetch real records; if unavailable, the interface displays UNAVAILABLE. No GitHub operations are necessary or authorized.

**Remaining demo-only work:** Run the actual Streamlit UI and verify live PubMed/ClinicalTrials.gov source identifiers and titles in a network-enabled environment. This is a small operational verification task, not a demand for clinical adjudication or full NHANES reanalysis. All prior V7.6 safeguards and deferred higher-maturity validation requirements remain in force.


### 12. V7.6.1 integrated intelligence upgrade and readable KG labels (2026-10-25)

**User authorization:** Proceed with V7.6.1, integrating real PubMed and ClinicalTrials.gov retrieval into Ask the Agent, preserving partial supported findings when market/eligibility claims are blocked, providing a human-readable report, and making KG labels dark and legible. Keep the production repository and baseline KG untouched.

**Observed user-side V7.6 evidence:** The user launched Streamlit successfully at localhost:8502. The UI showed 293 baseline nodes, 517 edges, 4 population observations and 88 candidate links. An initial SSL certificate-chain failure blocked both APIs; after the user activated the project's Python environment, set SSL_CERT_FILE to the installed certifi CA bundle, and restarted Streamlit, the user shared a screenshot showing five real PubMed publications with PMIDs and five ClinicalTrials.gov studies with NCT IDs, plus UTC retrieval timestamps. This is user-observed live retrieval; individual publications were not independently critically appraised in the development environment.

**Observed integrated-question weakness:** The previous bounded investigation returned a single BLOCKED_ELIGIBILITY response and an unhelpful raw JSON trace, despite successfully retrieving the existing NHANES estimate and KG concepts. The fix is **claim-level blocking**: supported population/KG facts are shown, while eligibility, market sizing and trend inferences remain blocked. External evidence retrieval is now part of the Ask workflow when the live retrieval checkbox is enabled.

**Implementation:** Added `src/v761.py` with a traceable evidence-synthesis pipeline, source query selection, live PubMed and ClinicalTrials.gov calls, structured sections (population, KG, literature, established scope, uncertainties and additional evidence), citations and downloadable Markdown. Updated `app.py` to display the readable investigation by default, keep raw provenance in an expandable technical panel, and generate the same integrated source-linked report from the Report tab. KG Plotly labels now use high-contrast nearly black text on a white plotting surface, with stronger node borders; clickable references use a visible dark-blue style where applicable. Source KG concepts are distinguished from unreviewed candidate population mappings.

**Execution and gates:** Executed the full inherited plus new Python regression suite: **47/47 tests passed**. `app.py` and `src/v761.py` compiled successfully. Baseline KG SHA-256 remains `4b43634ec370b1a7b1dfc28e6fbb9458172ba8234959d6c5f5713ad05d6212bf`. The development environment does not have Streamlit installed; therefore the updated V7.6.1 GUI has not been launched or visually verified here. Live retrieval for V7.6.1 has not been rerun locally; user-observed V7.6 live API success is recorded separately. Automated software tests use isolated minimal fixtures only and do not create scientific evidence or literature records.

**Remaining demo-only acceptance:** On the user's Mac, run `python3 -m streamlit run app.py --server.port 8502` from the extracted V7.6.1 folder in the activated environment, preserving the verified SSL_CERT_FILE setting. Confirm Ask the Agent shows integrated literature and population/KG findings, confirm the KG plot labels are readable, and confirm the Intelligence Report is coherent. This is a functional demo acceptance check, not a requirement for clinical adjudication or raw NHANES reanalysis.

**Safeguards remain mandatory:** No fabricated evidence; no disabled SSL verification; no clinical eligibility or market-size claims based on screening proxies; no cross-cycle trend claims; no production GitHub operations; original KG unchanged. Evidence-source retrieval success is not the same as critical appraisal or clinical approval.


## 13. V7.7 — evidence-grounded reasoning and opportunity funnel (2026-10-25)

**Authorization:** User approved the V7.7 development milestone after reviewing the complete V7.6.1 Markdown investigation. Scope: improve evidence reasoning, KG relationship traversal, population segmentation logic, and integrated synthesis.

**Implemented:** New `src/v77.py` introduces read-only traversal of original KG edges, targeted live PubMed searches for FIDELIO-DKD, FIGARO-DKD and FIDELITY, HTTPS retrieval of actual PubMed XML abstracts with attributed results/conclusion excerpts when available, and a five-stage evidence-requirements funnel. Streamlit now calls V7.7 and offers V7.7 Markdown exports. `requirements.txt` consolidated.

**Safeguards:** Original clinical KG remains byte-identical (SHA-256 `4b43634ec370b1a7b1dfc28e6fbb9458172ba8234959d6c5f5713ad05d6212bf`). No fabricated publications, study outcomes, eligibility fractions, patients or market numbers. Abstract excerpts are not critical appraisal. KG relationships are original, not clinically adjudicated. NHANES is single-visit screening only. Existing source failure is explicit. No production GitHub access or modification.

**Local validation:** 53/53 automated tests passed, including 6 V7.7-specific tests using isolated software fixtures; Python source compilation passed. Cloud UI and real external retrieval for V7.7 are NOT yet verified. Deployment requires a manual upload to the separate demo GitHub repository and Streamlit redeployment. This remains a controlled functional demonstration, not a validated clinical or commercial intelligence engine.


### V7.7.1 targeted corrective release (2026-10-25)

**Trigger:** V7.7 user-uploaded live Markdown report retrieved five PubMed and five ClinicalTrials.gov records but all three targeted pivotal evidence requests returned HTTP 429. Its KG traversal was functional but insufficiently relevant to finerenone.

**Implementation:** Batched targeted PubMed query and summaries, bounded retry/backoff for 429/transient server failures, successful-response-only six-hour in-process cache with original timestamps, batched abstract retrieval, relevance-ranked existing KG edges. No changes to the original KG, no artificial research evidence, no HTTPS verification bypass.

**Remaining gaps:** Live cloud PubMed/Streamlit acceptance pending; no guarantee of all three pivotal studies from title-based retrieval; no independent critical appraisal or clinical eligibility estimate. Existing V7.6.1 and V7.7 deployments must remain untouched pending V7.7.1 acceptance.
