"""CDC NHANES Aug 2021-Aug 2023 official-XPT retrieval and screening analysis.

All numerical outputs are computed from fetched CDC public-use rows. No baked-in
population result or synthetic data is used. Screening is NOT clinical diagnosis.
"""
from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256
from io import BytesIO
import math
from urllib.request import urlopen, Request
import pandas as pd
from src.nhanes_compute import compute_screening_total, SurveyInputError

CDC_BASE = 'https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2021/DataFiles/'
FILES = ('DEMO_L', 'GHB_L', 'BIOPRO_L', 'ALB_CR_L', 'DIQ_L')
COLUMNS = {
    'DEMO_L': ('SEQN','RIDAGEYR','RIAGENDR','SDMVSTRA','SDMVPSU'),
    'GHB_L': ('SEQN','LBXGH','WTPH2YR'),
    'BIOPRO_L': ('SEQN','LBXSCR'),
    'ALB_CR_L': ('SEQN','URDACT'),
    'DIQ_L': ('SEQN','DIQ010'),
}
MAX_BYTES = 12_000_000


def load_official_files(fetch=None):
    """Return merged public-use data and file-level audit. Inject fetch for tests.

    fetch(url) must return raw bytes; actual runtime uses CDC HTTPS with timeout.
    """
    if fetch is None:
        def fetch(url):
            req = Request(url, headers={'User-Agent':'HealthcareIntelligence/7.7.9 (public NHANES research)'})
            with urlopen(req, timeout=35) as response:
                blob = response.read(MAX_BYTES + 1)
            return blob
    tables, audit = [], []
    for name in FILES:
        url = CDC_BASE + name + '.xpt'
        raw = fetch(url)
        if not isinstance(raw, bytes) or not raw or len(raw) > MAX_BYTES:
            raise SurveyInputError(f'Invalid or oversized CDC file: {name}')
        try:
            df = pd.read_sas(BytesIO(raw), format='xport')
        except Exception as exc:
            raise SurveyInputError(f'Could not decode official SAS XPT {name}: {exc}') from exc
        required = COLUMNS[name]
        absent = set(required).difference(df.columns)
        if absent:
            raise SurveyInputError(f'{name} missing required fields: {sorted(absent)}')
        df = df[list(required)].copy()
        if df.SEQN.isna().any() or df.SEQN.duplicated().any():
            raise SurveyInputError(f'{name} has invalid/duplicate SEQN')
        tables.append(df)
        audit.append({'file': name+'.xpt', 'url':url, 'sha256':sha256(raw).hexdigest(),
                      'bytes':len(raw), 'participants':len(df)})
    merged = tables[0]
    for table in tables[1:]:
        merged = merged.merge(table, on='SEQN', how='left', validate='one_to_one')
    return merged, audit


def egfr_2021(scr, age, sex):
    """2021 CKD-EPI creatinine eGFR; sex 1=male, 2=female; no race coefficient."""
    if any(pd.isna(v) for v in (scr, age, sex)) or scr <= 0 or age < 0 or sex not in (1,2):
        return math.nan
    female = sex == 2
    k = 0.7 if female else 0.9
    a = -0.241 if female else -0.302
    ratio = scr/k
    return 142 * min(ratio,1)**a * max(ratio,1)**(-1.2) * (0.9938**age) * (1.012 if female else 1)


def _or_with_missing(a, b):
    """Three-valued OR: True if any true; False only if both known false."""
    a, b = a.astype('boolean'), b.astype('boolean')
    return a | b


def derive_screening_rows(df):
    """Explicit proxy: age>=20, (eGFR<60 OR ACR>=30), (A1c>=6.5 OR DIQ010=1).

    A positive component is sufficient even if the other is missing; a negative
    composite requires both components known. DIQ010=1 does NOT establish T2D.
    """
    missing = set(sum((list(v) for v in COLUMNS.values()), [])).difference(df.columns)
    if missing:
        raise SurveyInputError('Missing NHANES variables: '+', '.join(sorted(missing)))
    data = df.copy()
    age = pd.to_numeric(data.RIDAGEYR, errors='coerce')
    data['universe'] = (age >= 20).astype(int)
    egfr = [egfr_2021(s,a,x) for s,a,x in zip(data.LBXSCR, age, data.RIAGENDR)]
    data['eGFR_2021'] = egfr
    egfr_s = pd.Series(egfr, index=data.index)
    acr = pd.to_numeric(data.URDACT, errors='coerce')
    hba1c = pd.to_numeric(data.LBXGH, errors='coerce')
    diq = pd.to_numeric(data.DIQ010, errors='coerce')
    low_egfr = (egfr_s < 60).astype('boolean').mask(egfr_s.isna(), pd.NA)
    albuminuria = (acr >= 30).astype('boolean').mask(acr.isna(), pd.NA)
    high_a1c = (hba1c >= 6.5).astype('boolean').mask(hba1c.isna(), pd.NA)
    self_report = diq.eq(1).astype('boolean').mask(~diq.isin([1,2]), pd.NA)
    kidney = _or_with_missing(low_egfr, albuminuria)
    diabetes = _or_with_missing(high_a1c, self_report)
    flag = (kidney & diabetes).astype('Int64')
    data['screening_flag'] = flag
    return data


def compute_official_nhanes(fetch=None):
    df, sources = load_official_files(fetch=fetch)
    derived = derive_screening_rows(df)
    if 'WTPH2YR' not in derived or derived.WTPH2YR.isna().any():
        # Some respondents may have no phlebotomy weight; exclude them explicitly,
        # without substituting MEC weights or changing the sampling universe.
        excluded_weight = int(derived.WTPH2YR.isna().sum())
        derived = derived.loc[derived.WTPH2YR.notna()].copy()
    else:
        excluded_weight = 0
    result = compute_screening_total(derived, flag='screening_flag', weight='WTPH2YR',
                                     strata='SDMVSTRA', psu='SDMVPSU', universe='universe')
    result.update({
        'status':'COMPUTED_FROM_CDC_PUBLIC_XPT',
        'retrieved_utc':datetime.now(timezone.utc).isoformat(),
        'cycle':'NHANES August 2021-August 2023',
        'definition':('Adults age >=20; kidney screening proxy eGFR (2021 CKD-EPI creatinine) <60 '
                      'OR urine albumin/creatinine ratio >=30 mg/g; diabetes proxy HbA1c >=6.5% '
                      'OR self-reported diabetes DIQ010=1. Neither confirms chronicity or T2D subtype.'),
        'weight':'WTPH2YR (GHB_L); no substitution',
        'excluded_missing_weight':excluded_weight,
        'merged_rows':len(df),
        'sources':sources,
        'historical_reference':9233798,
        'difference_from_historical':result['estimate']-9233798,
        'historical_comparability':('Historical 9,233,798 estimate is not a validation target: '
            'original exact screening and complete-case definitions have not been recovered.'),
        'cautions':('Single-visit CKD screen is not persistent CKD; DIQ010 or HbA1c does not '
            'establish T2D subtype. Laboratory nonresponse and WTPH2YR suitability need '
            'formal review; CI uses approximate PSU Taylor normal method, not CDC-certified.'),
    })
    return result
