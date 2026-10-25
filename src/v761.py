"""V7.6.1 read-only, partial-answer biomedical intelligence synthesis.
No invented literature or eligibility inference. External retrieval is optional and explicit.
"""
from __future__ import annotations
import re
from .engine import integrity
from .v7 import population, concept_search, literature_refresh, utc

CLINICAL_TERMS=('finerenone','kerendia','clinical','kidney','ckd','diabet','evidence','treatment','trial','drug','heart')
POP_TERMS=('population','nhanes','prevalence','screening','adults','kidney','ckd','diabet','treatment opportunity','market')
UNSUPPORTED_MARKET=('market size','addressable market','tam','eligible population','number eligible','how many eligible','treatment eligible','prescription eligible')
TREND_TERMS=('trend','trends','increase across','increased across','across cycles','change over time','longitudinal')

def query_for_sources(question):
    q=question.lower()
    if 'finerenone' in q or 'kerendia' in q:return 'finerenone chronic kidney disease type 2 diabetes'
    if 'ckd' in q or 'kidney' in q:return 'chronic kidney disease type 2 diabetes'
    # Limit uncontrolled external queries; use the user's question only after length limiting.
    return re.sub(r'\s+',' ',question.strip())[:160]

def build_investigation(question, *, fetch_live=True, external_results=None):
    """Never blocks the whole answer; blocks only unsupported *claims*.
    external_results injection is for tests and for previously retrieved real session records.
    """
    if not isinstance(question,str) or not question.strip():raise ValueError('Question is required')
    if len(question)>1500:raise ValueError('Question exceeds 1500 characters')
    q=question.lower(); relevant_pop=any(t in q for t in POP_TERMS)
    relevant_clinical=any(t in q for t in CLINICAL_TERMS)
    relevant_external=relevant_clinical or 'pubmed' in q or 'literature' in q
    baseline=integrity()
    obs=population('2021-2023','primary') if relevant_pop else None
    concepts=concept_search(question,limit=8) if relevant_clinical else []
    if external_results is not None:
        external=external_results
    elif fetch_live and relevant_external:
        external=literature_refresh(query_for_sources(question))
    else:
        external={'pubmed':{'status':'NOT_REQUESTED','records':[]},'trials':{'status':'NOT_REQUESTED','records':[]}}
    citations=[];sections=[];warnings=[]
    if obs and obs.get('evidence_id'):
        citations.append({'id':obs['evidence_id'],'type':'NHANES observation','url':None,'verification':'PREVIOUSLY_DERIVED_REVIEW_REQUIRED'})
        lo,hi=obs['ci_95']
        sections.append({'title':'Population intelligence','status':'SOURCE_OBSERVATION_REVIEW_REQUIRED',
            'text':f"The preserved NHANES {obs['period']} analysis estimates {obs['estimate']:,.0f} US adults meeting the project's single-visit CKD laboratory-screening and probable T2D proxy (reported 95% CI {lo:,.0f}–{hi:,.0f}; survey weight {obs['survey_weight']}; unweighted cases {obs['unweighted_cases']}). This is not a confirmed diagnosis or treatment-eligible population.",
            'citations':[obs['evidence_id']]})
    else:sections.append({'title':'Population intelligence','status':'NOT_APPLICABLE','text':'No applicable population observation selected for this question.','citations':[]})
    if concepts:
        top=concepts[:5]
        sections.append({'title':'Clinical knowledge graph context','status':'BASELINE_GRAPH_NOT_CLINICALLY_ADJUDICATED',
            'text':'The preserved clinical KG contains relevant concepts: '+ '; '.join(f"{n['node_id']} ({n['node_type']}): {n['description'][:145]}" for n in top)+'. These are existing graph descriptions, not independently verified clinical conclusions or approved population-to-KG mappings.',
            'citations':['KG:'+str(n['node_id']) for n in top]})
        citations.extend({'id':'KG:'+str(n['node_id']),'type':'Preserved KG concept','url':None,'verification':'BASELINE_INTEGRITY_ONLY'} for n in top)
    else:sections.append({'title':'Clinical knowledge graph context','status':'NO_MATCH','text':'No matching clinical KG concepts found by lexical retrieval.','citations':[]})
    source_lines=[]; ext_ids=[]
    for source in ('pubmed','trials'):
        entry=external.get(source,{'status':'NOT_REQUESTED','records':[]})
        status=entry.get('status','UNAVAILABLE');records=entry.get('records',[])
        if status=='RETRIEVED' and records:
            label='PubMed publications' if source=='pubmed' else 'ClinicalTrials.gov registrations'
            source_lines.append(f'{label} (live retrieval {entry.get("retrieved_utc","timestamp unavailable")}):')
            for r in records:
                ident=r.get('pmid') if source=='pubmed' else r.get('nct_id')
                if not ident or not r.get('url'):continue
                ext_ids.append(str(ident))
                source_lines.append(f"• {r.get('title','Untitled')} [{ident}] — {r['url']}")
                citations.append({'id':str(ident),'type':source,'url':r['url'],'verification':'RETRIEVED_NOT_CRITICALLY_APPRAISED'})
        elif status=='UNAVAILABLE':
            source_lines.append(f'{source}: UNAVAILABLE — {entry.get("error","retrieval failed")}. No fallback citations inserted.')
            warnings.append(f'{source} retrieval unavailable')
        elif status=='NO_EVIDENCE':source_lines.append(f'{source}: No matching records returned.')
        else:source_lines.append(f'{source}: Live retrieval not requested.')
    sections.append({'title':'Authentic external evidence','status':'RETRIEVED' if ext_ids else 'INCOMPLETE',
        'text':'\n'.join(source_lines),'citations':ext_ids})
    sections.append({'title':'What is established by this demonstration','status':'SUPPORTED_SCOPE',
        'text':'The application can inspect an integrity-checked preserved clinical KG, retrieve the existing NHANES screening observation when relevant, and display identifiable real publications and trial registrations when live sources respond. Retrieved titles and registrations do not, by themselves, establish study quality, treatment efficacy, or eligibility.',
        'citations':[c['id'] for c in citations]})
    if any(t in q for t in UNSUPPORTED_MARKET) or any(t in q for t in ('opportunity','eligib','prescrib','market','treat')):
        warnings.append('Treatment eligibility and commercial market sizing cannot be inferred from NHANES screening proxies.')
    if any(t in q for t in TREND_TERMS):warnings.append('Cross-cycle NHANES trend claims are blocked pending laboratory and survey comparability review.')
    sections.append({'title':'Uncertainties and prohibited inferences','status':'CLAIM_LEVEL_BLOCK',
        'text':'\n'.join('• '+x for x in warnings) if warnings else '• Screening is not diagnosis. • KG lexical matches are not clinically adjudicated. • Trial registration is not proof of benefit. • No patient-specific advice.',
        'citations':[]})
    sections.append({'title':'Evidence needed for a defensible eligible-population estimate','status':'RESEARCH_GAP',
        'text':'Confirmed CKD/T2D diagnoses, current prescribing-label criteria, clinical laboratory eligibility and exclusions (including relevant renal function and potassium considerations), treatment utilization and overlap estimates, and appropriately validated epidemiological assumptions. This demo does not calculate an eligible population or market size.',
        'citations':[]})
    return {'version':'V7.6.1','question':question,'retrieved_utc':utc(),
        'status':'PARTIAL_ANSWER_WITH_GUARDS' if warnings else 'EVIDENCE_SUMMARY_WITH_LIMITATIONS',
        'sections':sections,'citations':citations,'warnings':warnings,'external':external,
        'technical_trace':{'baseline_integrity':baseline,'population_observation':obs,'clinical_kg_lexical_retrieval':concepts,
          'external_status':{k:v.get('status','UNKNOWN') for k,v in external.items()},
          'source_query':query_for_sources(question) if relevant_external else None,
          'claim_policy':'PARTIAL_ANSWER_BLOCK_UNSUPPORTED_CLAIMS','external_source_provenance':external},
        'evidence_policy':'REAL_ONLY_NO_SIMULATED_SCIENTIFIC_EVIDENCE'}

def to_markdown(bundle):
    out=['# Healthcare Intelligence — V7.6.1','', '**Controlled research demonstration; not clinical advice or validated market analysis.**','',
         '**Question:** '+bundle['question'],'','**Status:** '+bundle['status'],'']
    for s in bundle['sections']:
        out.extend(['## '+s['title'],s['text'],''])
        if s['citations']:out.append('Evidence IDs: '+', '.join(s['citations'])+'\n')
    out.append('## Evidence register')
    for c in bundle['citations']:
        out.append('- '+c['id']+' | '+c['type']+' | '+c['verification']+((' | '+c['url']) if c['url'] else ''))
    out.extend(['','## Source integrity and limits','The original clinical KG is read-only and checksum-verified. NHANES figures are historical project-derived screening proxies. No clinical eligibility, addressable market, or cross-cycle trend claims are supported.'])
    return '\n'.join(out)+'\n'
