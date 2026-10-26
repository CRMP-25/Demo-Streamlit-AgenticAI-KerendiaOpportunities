"""V7.7.5: correct FIGARO primary title, evidence-grounded effects, KG QA.

Only source-verified PubMed records can produce quantitative results.
Original KG and population observations remain read-only.
"""
from __future__ import annotations
import json
import re
import urllib.parse
from .v774 import build_v774, to_markdown as previous_markdown, verify_primary_candidate, quantitative_source_findings
from .v77 import _request_bytes
from .version import APP_VERSION
from .v772 import classify_intent

PRIMARY_CANDIDATES = {
    'FIDELIO-DKD': ('33264825', 'Effect of Finerenone on Chronic Kidney Disease Outcomes in Type 2 Diabetes'),
    'FIGARO-DKD': ('34449181', 'Cardiovascular Events with Finerenone in Kidney Disease and Type 2 Diabetes'),
}


def retrieve_primary_papers():
    ids = [v[0] for v in PRIMARY_CANDIDATES.values()]
    url = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?' + urllib.parse.urlencode(
        {'db':'pubmed', 'id':','.join(ids), 'retmode':'json'})
    try:
        response = json.loads(_request_bytes(url))['result']
        records, warnings = [], []
        for group, (pmid, title) in PRIMARY_CANDIDATES.items():
            verified = verify_primary_candidate(group, pmid, title, response.get(pmid, {}))
            if verified:
                records.append(verified)
            else:
                warnings.append(group + ': expected PubMed title not verified; no trial result inferred')
        return {'status':'RETRIEVED' if records else 'NO_VERIFIED_PRIMARY',
                'records':records, 'warnings':warnings}
    except Exception as exc:
        return {'status':'UNAVAILABLE','records':[],
                'warnings':['Live PubMed primary verification unavailable: ' + type(exc).__name__]}


# Exact reported pairs are *recognition patterns*, not independent clinical data.
# A row is emitted ONLY when the source abstract explicitly contains both percentages.
ENDPOINT_PATTERNS = {
    'FIDELIO-DKD': [
        ('Primary kidney composite (reported events)', 17.8, 21.1),
        ('Key secondary cardiovascular composite (reported events)', 13.0, 14.8),
    ],
    'FIGARO-DKD': [
        ('Primary cardiovascular composite (reported events)', 12.4, 14.2),
        ('Secondary kidney composite (reported events)', 9.5, 10.8),
    ],
}


def effect_table(verified_records):
    rows = ['| Study / endpoint | Finerenone | Placebo | Observed difference | Source |',
            '|---|---:|---:|---:|---|']
    for rec in verified_records:
        group = rec.get('study')
        pmid = rec.get('pmid','')
        if (group not in PRIMARY_CANDIDATES or
            pmid != PRIMARY_CANDIDATES[group][0] or
            rec.get('verification') != 'PUBMED_TITLE_MATCH_NOT_FULL_TEXT_APPRAISAL'):
            continue
        texts = [s.get('text','') for s in rec.get('abstract_sections',[])
                 if 'result' in s.get('label','').lower()]
        if not texts:  # Some PubMed abstracts are unstructured.
            texts = [s.get('text','') for s in rec.get('abstract_sections',[])]
        source = ' '.join(texts)
        for endpoint, treated, control in ENDPOINT_PATTERNS[group]:
            # Only emit when exact percentages appear in the same source Results section.
            a, b = f'{treated:.1f}%', f'{control:.1f}%'
            if not (re.search(re.escape(a),source) and re.search(re.escape(b),source)):
                continue
            difference = round(treated-control,1)
            rows.append(f'| {group}: {endpoint} | {a} | {b} | {difference:+.1f} percentage points | [PMID {pmid}](https://pubmed.ncbi.nlm.nih.gov/{pmid}/) |')
    if len(rows)==2:
        return 'No source-verified primary abstract contained both event percentages required for a descriptive difference.'
    return '\n'.join(rows) + ('\n\nDescriptive subtraction of reported event percentages; **not** a time-adjusted absolute risk reduction, hazard ratio, NNT, or cross-trial comparison. Endpoints and follow-up differ across trials.')


def kg_assertion_review(bundle):
    edges = bundle.get('graph_edges',[])
    flagged = []
    for e in edges:
        if str(e.get('source')) == 'DR6' and str(e.get('target')) == 'D1' and str(e.get('relation','')).lower() == 'treats':
            flagged.append('- `KG:DR6 — treats → KG:D1`: **REVIEW REQUIRED.** This preserved relation could misleadingly imply that finerenone treats uncomplicated type 2 diabetes or hyperglycemia. Finerenone evidence here concerns cardiorenal outcomes in studied CKD/T2D populations. No original KG node or edge has been altered.')
    return ('\n'.join(flagged) if flagged else 'No specifically defined high-risk assertion appeared among the retrieved KG edges. This does **not** certify the graph as clinically accurate.')


def build_v775(question, *, fetch_live=True, external_results=None, pivotal_results=None,
               abstract_results=None, primary_results=None):
    # Preserve the population-only fast path: no PubMed call even when live is checked.
    population_only = classify_intent(question) == 'POPULATION_ONLY'
    prim = primary_results if primary_results is not None else (
        retrieve_primary_papers() if fetch_live and not population_only else
        {'status':'NOT_REQUESTED','records':[], 'warnings':['Live verification not requested']})
    bundle = build_v774(question, fetch_live=fetch_live, external_results=external_results,
                        pivotal_results=pivotal_results, abstract_results=abstract_results,
                        primary_results=prim)
    bundle['version'] = APP_VERSION
    bundle['technical_trace']['release_version'] = APP_VERSION
    if bundle.get('intent') == 'POPULATION_ONLY':
        return bundle
    for section in bundle['sections']:
        if section['title'] == 'Executive evidence synthesis — V7.7.4':
            section['title'] = 'Executive evidence synthesis — ' + APP_VERSION
    verified = bundle.get('primary_trial_evidence',{}).get('records',[])
    if bundle.get('intent') in ('INTEGRATED','CLINICAL_EVIDENCE_ONLY'):
        bundle['sections'].insert(2, {
            'title':'Primary trial event-rate comparison — descriptive only',
            'status':'VERIFIED_ABSTRACT_ONLY_NO_CROSS_TRIAL_INFERENCE',
            'text':effect_table(verified), 'citations':[r['pmid'] for r in verified]})
    if bundle.get('intent') in ('INTEGRATED','KG_ONLY'):
        bundle['sections'].append({
            'title':'Preserved KG assertion quality review',
            'status':'RULE_BASED_WARNING_NOT_CLINICAL_ADJUDICATION',
            'text':kg_assertion_review(bundle),
            'citations':['KG:DR6','KG:D1'] if 'REVIEW REQUIRED' in kg_assertion_review(bundle) else []})
    return bundle


def to_markdown(bundle):
    return re.sub(r'^# Healthcare Intelligence[^\n]*',
                  '# Healthcare Intelligence — ' + APP_VERSION,
                  previous_markdown(bundle), count=1)
