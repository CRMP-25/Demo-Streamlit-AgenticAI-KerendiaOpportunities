"""V7.7.7: reproducible evidence-gap triage, source-aware reasoning and action plan.

No synthetic NHANES microdata, no unsupported eligible-population estimate.
Preserves original KG and previous evidence retrieval machinery.
"""
from __future__ import annotations
import re
from .v776 import build_v776, to_markdown as previous_markdown
from .version import APP_VERSION


def evidence_gap_analysis(bundle):
    """Deterministic assessment of what the current run actually established."""
    intent = bundle.get('intent','')
    primary = {r.get('study'): r for r in bundle.get('primary_trial_evidence',{}).get('records',[])}
    verified = {}
    for study, pmid, pairs in (
        ('FIDELIO-DKD','33264825',('17.8%','21.1%')),
        ('FIGARO-DKD','34449181',('12.4%','14.2%')),
    ):
        record=primary.get(study,{})
        abstract=' '.join(str(s.get('text','')) for s in record.get('abstract_sections',[]))
        verified[study] = bool(record.get('pmid')==pmid and record.get('verification')=='PUBMED_TITLE_MATCH_NOT_FULL_TEXT_APPRAISAL' and all(p in abstract for p in pairs))
    sections=bundle.get('sections',[])
    has_population = any('population' in str(s.get('title','')).lower() or 'nhanes' in str(s.get('text','')).lower() for s in sections)
    graph_edges=bundle.get('graph_edges',[])
    risky_edge=any(str(e.get('source'))=='DR6' and str(e.get('target'))=='D1' and str(e.get('relation','')).lower()=='treats' for e in graph_edges)
    gates=[
        ('Primary FIDELIO efficacy', 'SOURCE_VERIFIED' if verified['FIDELIO-DKD'] else 'NOT_VERIFIED', 'Retrieve and verify PMID 33264825 abstract and endpoint definitions'),
        ('Primary FIGARO efficacy', 'SOURCE_VERIFIED' if verified['FIGARO-DKD'] else 'NOT_VERIFIED', 'Retrieve and verify PMID 34449181 abstract and endpoint definitions'),
        ('CKD/T2D screening observation', 'HISTORICAL_PROXY_ONLY' if has_population else 'NOT_IN_THIS_RUN', 'Independently reproduce NHANES estimate with microdata, survey design and missingness'),
        ('Confirmed CKD and T2D', 'NOT_ESTABLISHED', 'Obtain longitudinal CKD confirmation and validated diabetes ascertainment'),
        ('Label-aligned eligibility', 'NOT_ESTABLISHED', 'Review current US label, eGFR, potassium, contraindications and therapy requirements'),
        ('Treatment utilization and access', 'NOT_ESTABLISHED', 'Obtain prescribing, overlap, contraindication, coverage and access data'),
    ]
    priority=[
        ('P1', 'Reproduce NHANES denominator', 'Load authentic participant-level source files; document variables, inclusion rules, missingness, survey weights and uncertainty; compare with 9,233,798 historical proxy.', 'BLOCKED: participant-level NHANES files not supplied in this run'),
        ('P1', 'Establish clinical eligibility mapping', 'Build a versioned decision table from the current US label and trial criteria; map only variables actually present in NHANES.', 'BLOCKED: current label and validated mapping not reviewed'),
        ('P2', 'Review KG claim quality', 'Adjudicate the DR6 treats D1 relation; retain immutable original graph and create a separate correction overlay.', 'FLAGGED' if risky_edge else 'CHECK WHEN EDGE IS RETRIEVED'),
        ('P2', 'Quantify treatment opportunity', 'Only after diagnosis and eligibility gates, obtain utilization, coverage and treatment-overlap evidence; calculate explicit scenarios with sensitivity ranges.', 'BLOCKED: eligibility and utilization not established'),
    ]
    return {'verified_primary':verified, 'gates':gates, 'priorities':priority, 'kg_assertion_flagged':risky_edge,
            'eligible_population_status':'BLOCKED', 'new_nhanes_analysis_performed':False, 'intent':intent}


def reasoning_section(analysis):
    rows=['### What this run can conclude',
          '| Clinical evidence | Result |', '|---|---|']
    for study, ok in analysis['verified_primary'].items():
        rows.append(f'| {study} primary outcome | '+('Verified from matching PubMed primary abstract in this run' if ok else 'Not source-verified in this run; no efficacy estimate inferred')+' |')
    rows.extend(['| US treatment-eligible population | **Not estimable from current inputs** |',
                 '| New NHANES participant-level computation | **Not performed** |',
                 '', '### Evidence gates — auditable status',
                 '| Evidence gate | Status | Evidence needed |', '|---|---|---|'])
    for name,status,action in analysis['gates']:
        rows.append(f'| {name} | **{status}** | {action} |')
    rows.extend(['','### Ranked next investigations',
                 '| Priority | Investigation | Concrete work | Current state |', '|---|---|---|---|'])
    for p,title,work,state in analysis['priorities']:
        rows.append(f'| {p} | {title} | {work} | {state} |')
    rows.extend(['', '### Reasoning boundary',
                 'This is a deterministic evidence-gap and next-action analysis, **not** an autonomous hypothesis-testing agent. No new NHANES estimates, clinical eligibility rates, treatment penetration assumptions, or market figures are generated. Original KG and historical population observations remain unchanged.'])
    return '\n'.join(rows)


def build_v777(question, *, fetch_live=True, external_results=None, pivotal_results=None,
               abstract_results=None, primary_results=None):
    bundle=build_v776(question,fetch_live=fetch_live,external_results=external_results,
                      pivotal_results=pivotal_results,abstract_results=abstract_results,
                      primary_results=primary_results)
    bundle['version']=APP_VERSION
    bundle['technical_trace']['release_version']=APP_VERSION
    for s in bundle.get('sections',[]):
        if 'V7.7.6' in s.get('title',''):
            s['title']=s['title'].replace('V7.7.6',APP_VERSION)
    if bundle.get('intent') in ('INTEGRATED','CLINICAL_EVIDENCE_ONLY'):
        analysis=evidence_gap_analysis(bundle)
        bundle['evidence_gap_analysis']=analysis
        bundle['sections'].insert(0,{
            'title':'Decision-focused evidence assessment — '+APP_VERSION,
            'status':'EVIDENCE_GAP_ANALYSIS_WITH_EXPLICIT_BLOCKERS',
            'text':reasoning_section(analysis),
            'citations':[p for study,p in [('FIDELIO-DKD','33264825'),('FIGARO-DKD','34449181')] if analysis['verified_primary'][study]]})
    return bundle


def to_markdown(bundle):
    return re.sub(r'^# Healthcare Intelligence[^\n]*','# Healthcare Intelligence — '+APP_VERSION,
                  previous_markdown(bundle),count=1)
