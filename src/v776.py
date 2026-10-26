"""V7.7.6 evidence synthesis: deterministic, bounded, source-attributed reasoning.

Does not modify the preserved KG or turn a screening proxy into eligibility.
"""
from __future__ import annotations
import re
from .v775 import build_v775, to_markdown as previous_markdown
from .version import APP_VERSION

TRIALS = ('FIDELIO-DKD', 'FIGARO-DKD')


def _has_results(record):
    return bool(record.get('abstract_sections'))


def _has_pair(record, a, b):
    results = ' '.join(str(s.get('text','')) for s in record.get('abstract_sections',[]) if 'result' in s.get('label','').lower())
    if not results:
        results = ' '.join(str(s.get('text','')) for s in record.get('abstract_sections',[]))
    return a in results and b in results


def integrated_synthesis(bundle):
    """Only attribute clinical numbers if matching primary abstracts are present."""
    primary = {r.get('study'):r for r in bundle.get('primary_trial_evidence',{}).get('records',[])
               if r.get('verification') == 'PUBMED_TITLE_MATCH_NOT_FULL_TEXT_APPRAISAL'}
    f = primary.get('FIDELIO-DKD',{})
    g = primary.get('FIGARO-DKD',{})
    kidney = _has_pair(f,'17.8%','21.1%')
    cv = _has_pair(g,'12.4%','14.2%')
    lines = [
        '### Integrated evidence chain',
        '| Link | Evidence available in this run | Interpretation / boundary |',
        '|---|---|---|',
        '| Clinical question | CKD with T2D and finerenone | Treatment benefit is not equivalent to the size of a treatable population. |',
        '| Preserved KG | Existing disease, drug, and relationship assertions | Contextual associations only; graph edges are not independent clinical validation. |',
    ]
    if kidney:
        lines.append('| Kidney efficacy | FIDELIO-DKD [PMID 33264825](https://pubmed.ncbi.nlm.nih.gov/33264825/): primary kidney composite 17.8% vs 21.1% (finerenone vs placebo) | Within-trial result; do not extrapolate to all NHANES screen-positive adults. |')
    else:
        lines.append('| Kidney efficacy | Primary FIDELIO-DKD outcome not verified from a source abstract in this run | No numerical efficacy inference. |')
    if cv:
        lines.append('| Cardiovascular efficacy | FIGARO-DKD [PMID 34449181](https://pubmed.ncbi.nlm.nih.gov/34449181/): primary CV composite 12.4% vs 14.2% (finerenone vs placebo) | Different primary endpoint and follow-up; do not compare effect sizes directly with FIDELIO. |')
    else:
        lines.append('| Cardiovascular efficacy | Primary FIGARO-DKD outcome not verified from a source abstract in this run | No numerical efficacy inference. |')
    lines.extend([
        '| Population | Historical NHANES single-visit CKD screening + probable T2D proxy: 9,233,798 adults (previously derived, not independently replicated) | Screening proxy is neither confirmed disease nor label-based eligibility. |',
        '| Eligibility | Current label and patient-level exclusions not adjudicated | Eligible count cannot be calculated. |',
        '| Treatment opportunity | Current utilization, access, overlap, and contraindication data absent | No defensible addressable-market estimate. |',
        '', '### Cross-study interpretation',
    ])
    if kidney and cv:
        lines.append('The two primary trial abstracts report favorable results for **different prespecified primary composites**: kidney outcomes in FIDELIO-DKD and cardiovascular outcomes in FIGARO-DKD. This supports a **directional, trial-population-specific** cardiorenal evidence narrative, not a pooled effect, head-to-head comparison, or claim about all US adults with CKD/T2D.')
    else:
        lines.append('A complete primary-trial synthesis is **blocked** because both source-verified primary outcome abstracts are not available in this run. The system does not substitute secondary analyses for missing primary results.')
    lines.extend([
        '', '### Safety and applicability',
        'The report includes safety-related secondary evidence, but this automated synthesis does not establish an individualized benefit-risk balance. Review potassium monitoring, kidney function, background therapy, eligibility, and current prescribing information before any clinical interpretation.',
        '', '### Evidence-to-opportunity decision gates',
        '| Gate | Required validation | Status |', '|---|---|---|',
        '| 1. Source authenticity | Verified trial titles and relevant source abstracts | '+('PASS — abstracts present' if kidney and cv else 'PARTIAL — source abstracts missing or incomplete')+' |',
        '| 2. Disease confirmation | Validated CKD chronicity and T2D diagnosis | NOT ESTABLISHED |',
        '| 3. Clinical eligibility | Current label, renal function, potassium, exclusions, concomitant therapies | NOT ESTABLISHED |',
        '| 4. Population mapping | Reproducible survey-weighted participant-level estimates and missingness | NOT ESTABLISHED |',
        '| 5. Treatment opportunity | Utilization, overlap, access, and prescribing patterns | NOT ESTABLISHED |',
        '', '**Decision:** Evidence-informed clinical discussion is possible within the verified source limits; **eligible-population and market sizing remain blocked**.',
        '', '**Provenance:** Trial numbers above are included only when found in the corresponding verified PubMed abstract. The NHANES number is a historical project estimate, not a newly computed statistic. KG assertions are preserved, not adjudicated.'
    ])
    return '\n'.join(lines), [r['pmid'] for r in (f,g) if r.get('pmid')]


def consolidated_pivotal_table(bundle):
    verified = {r.get('study'):r for r in bundle.get('primary_trial_evidence',{}).get('records',[])}
    rows=['| Evidence tier | Study | PMID | Source status |', '|---|---|---|---|']
    for study, pmid in (('FIDELIO-DKD','33264825'),('FIGARO-DKD','34449181')):
        r=verified.get(study)
        ok=r and r.get('pmid')==pmid
        rows.append(f'| Primary pivotal trial | {study} | '+(f'[PMID {pmid}](https://pubmed.ncbi.nlm.nih.gov/{pmid}/)' if ok else 'Not verified in this run')+' | '+('Abstract retrieved' if ok and _has_results(r) else 'Abstract unavailable / unverified')+' |')
    for r in bundle.get('structured_evidence',[]):
        study,pmid=r.get('study','Unclassified'),str(r.get('pmid',''))
        if not pmid.isdigit():continue
        tier='Pooled analysis' if study=='FIDELITY' else 'Secondary / related publication (not primary)'
        rows.append(f'| {tier} | {study} | [PMID {pmid}](https://pubmed.ncbi.nlm.nih.gov/{pmid}/) | Source abstract available; not independently appraised |')
    rows.append('\nPublication tiers are based on this application’s verified primary identifiers and source records; full-text appraisal remains necessary.')
    return '\n'.join(rows)


def build_v776(question, *, fetch_live=True, external_results=None, pivotal_results=None,
               abstract_results=None, primary_results=None):
    b=build_v775(question,fetch_live=fetch_live,external_results=external_results,
                 pivotal_results=pivotal_results,abstract_results=abstract_results,
                 primary_results=primary_results)
    b['version']=APP_VERSION
    b['technical_trace']['release_version']=APP_VERSION
    for section in b['sections']:
        if section['title'].startswith('Executive evidence synthesis —'):
            section['title']='Executive evidence synthesis — '+APP_VERSION
        if section['title']=='Structured pivotal evidence comparison':
            section['title']='Consolidated primary, pooled, and secondary evidence register'
            section['text']=consolidated_pivotal_table(b)
            section['status']='PRIMARY_VS_SECONDARY_DISTINGUISHED'
    if b.get('intent') in ('INTEGRATED','CLINICAL_EVIDENCE_ONLY'):
        narrative,refs=integrated_synthesis(b)
        idx=next((i+1 for i,s in enumerate(b['sections']) if s['title'].startswith('Executive evidence synthesis')),0)
        b['sections'].insert(idx,{'title':'Integrated clinical intelligence synthesis — '+APP_VERSION,
                                 'status':'BOUNDED_EVIDENCE_SYNTHESIS_NO_MARKET_ESTIMATE',
                                 'text':narrative,'citations':refs+(['NHANES_2021_2023_PRIMARY'] if b.get('intent')=='INTEGRATED' else [])})
    return b


def to_markdown(bundle):
    return re.sub(r'^# Healthcare Intelligence[^\n]*','# Healthcare Intelligence — '+APP_VERSION,
                  previous_markdown(bundle),count=1)
