# Healthcare Intelligence V7.7.9 — CDC NHANES automatic computation

## What changed
The **NHANES Compute** tab now includes **Retrieve CDC data and compute screening estimate**. No user-prepared dataset is needed. It downloads authentic, public-use **August 2021–August 2023** CDC SAS XPT files directly from the official NHANES server: `DEMO_L`, `GHB_L`, `BIOPRO_L`, `ALB_CR_L`, and `DIQ_L`. Files are linked by `SEQN` and file SHA-256 hashes are included in the downloadable audit JSON. The V7.7.8 manual CSV workflow remains available under Advanced.

## Pre-specified, transparent screening proxy (NOT confirmed disease)
- Age 20 years or older.
- Kidney screening: eGFR (2021 CKD-EPI creatinine, race-free) <60 mL/min/1.73m² **or** urinary albumin/creatinine ratio (URDACT) >=30 mg/g.
- Diabetes proxy: HbA1c (LBXGH) >=6.5% **or** self-reported diabetes (DIQ010=1). This does **not** establish type 2 diabetes.
- Three-valued missingness: an OR is positive if one component is positive; negative only when both components are observed and negative. Other missing states are excluded from known-screening totals and reported.
- WTPH2YR phlebotomy weight from GHB_L; survey strata SDMVSTRA and PSU SDMVPSU from DEMO_L.
- Variance: stratified PSU with-replacement Taylor approximation, 1.96 normal confidence interval. Singleton strata prevent CI. No claim of formal CDC variance replication.

## Historical benchmark
The earlier estimate **9,233,798** is displayed **only as a historical comparator**, not a result to be forced or claimed reproduced. The earlier complete-case rules and source analysis script have not been recovered. Any difference requires method reconciliation. A single-visit kidney screen cannot establish persistent CKD; HbA1c and self-report cannot establish T2D subtype, treatment eligibility, or addressable market.

## Deployment
Commit this release to the permanent `testing` branch (connected to `kerendia-intelligence.streamlit.app`). Production `release` branch remains untouched. The Streamlit host must be able to access `wwwn.cdc.gov` over HTTPS. If CDC download or parsing fails, the application displays an error and **does not invent an estimate**.

## Official CDC references
- https://wwwn.cdc.gov/Nchs/Nhanes/ContinuousNhanes/default.aspx?Cycle=2021-2023
- https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2021/DataFiles/DEMO_L.htm
- https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2021/DataFiles/GHB_L.htm
- https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2021/DataFiles/BIOPRO_L.htm
- https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2021/DataFiles/ALB_CR_L.htm
- https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2021/DataFiles/DIQ_L.htm

## Verification status
Offline regression tests validate module joins, screening flags, missingness, basic eGFR behavior, and survey estimation using **explicit test fixtures**. Live CDC network access was **not available in the build environment**; real-data retrieval and statistical results must be tested after deployment. No authentic NHANES numerical estimate is claimed in this release package.
