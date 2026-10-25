"""V7.7.2 deterministic question-intent routing and source-faithful NHANES reporting."""
from __future__ import annotations
import re
from .v77 import build_v77, to_markdown as v77_markdown
from .v7 import population
from .engine import integrity, load
from .v7 import utc

POP_MARKERS=('nhanes','population','prevalence','screening','survey weight','unweighted','confidence interval','us adults','estimated adults','how many adults')
CLINICAL_MARKERS=('finerenone','kerendia','clinical trial','clinical evidence','pubmed','literature','drug efficacy','treatment effect','fid elio','fidelio','figaro','fidelity','mechanism','clinical knowledge graph','kg traversal','graph relationship')
INTEGRATED_MARKERS=('integrated','investigate the clinical','combine clinical','treatment opportunity','market opportunity','alongside clinical','together with clinical')

def classify_intent(question):
    if not isinstance(question,str) or not question.strip():raise ValueError('Question is required')
    if len(question)>1500:raise ValueError('Question exceeds 1500 characters')
    q=question.casefold()
    pop=any(t in q for t in POP_MARKERS)
    # An explicit instruction to distinguish screening from finerenone eligibility is a guard, not a request for drug evidence.
    clinical_q=re.sub(r'(?:clearly )?distinguish(?: this| it)?(?: screening-based estimate)? from confirmed[^.;]*?(?:finerenone treatment eligibility|treatment eligibility)', '', q)
    clinical_q=re.sub(r'distinguish this from finerenone treatment eligibility', '', clinical_q)
    clinical=any(t in clinical_q for t in CLINICAL_MARKERS)
    if any(t in q for t in INTEGRATED_MARKERS) or (pop and clinical):return 'INTEGRATED'
    if pop:return 'POPULATION_ONLY'
    if 'kg' in q or 'graph' in q:return 'KG_ONLY'
    if clinical:return 'CLINICAL_EVIDENCE_ONLY'
    return 'INTEGRATED'

def build_v772(question, *, fetch_live=True, external_results=None, pivotal_results=None, abstract_results=None):
    intent=classify_intent(question)
    if intent!='POPULATION_ONLY':
        bundle=build_v77(question,fetch_live=fetch_live,external_results=external_results,pivotal_results=pivotal_results,abstract_results=abstract_results)
        bundle['version']='V7.7.2';bundle['intent']=intent
        bundle['technical_trace']['intent_routing']=intent
        return bundle
    # Intentionally do not invoke KG lexical search or any external evidence connector.
    # The integrity check reads the preserved KG, without modifying it.
    integrity_result=integrity()
    q=question.lower()
    period=next((x for x in ('2015-2016','2017-2018','2021-2023') if x in q),'2021-2023')
    obs=population(period,'primary')
    if obs.get('status')=='NO_EVIDENCE':raise ValueError('Population observation unavailable for requested period')
    store=load();layer=store['observations']
    # Source observation lookup, not recomputation or prevalence inferred from a different denominator.
    raw=next((o for o in layer if o.get('id')==obs['evidence_id']),None)
    if raw is None:raise ValueError('Source prevalence observation unavailable; no value will be inferred')
    rate=raw.get('screening_prevalence_complete_case')
    prevalence=(f'{rate*100:.4f}%' if isinstance(rate,(int,float)) else 'UNAVAILABLE (not recorded in preserved observation)')
    lo,hi=obs['ci_95'] if obs.get('ci_95') else (None,None)
    ci=(f'{lo:,.0f}–{hi:,.0f}' if lo is not None and hi is not None else 'UNAVAILABLE')
    text=(f"Preserved NHANES {obs['period']} primary screening observation:\n\n"
          f"| Measure | Previously derived result |\n|---|---:|\n"
          f"| Estimated US adults meeting screening proxy | {obs['estimate']:,.0f} |\n"
          f"| Weighted screening prevalence (complete-case) | {prevalence} |\n"
          f"| Reported 95% confidence interval (estimated adults) | {ci} |\n"
          f"| Survey weight | {obs['survey_weight']} |\n"
          f"| Unweighted screening cases | {obs['unweighted_cases']:,} |\n"
          f"| Unweighted complete-case denominator | {obs['unweighted_denominator']:,} |\n"
          f"| Evidence ID | {obs['evidence_id']} |\n\n"
          "This is a single-visit CKD laboratory-screening plus probable T2D proxy, not confirmed chronic CKD or T2D diagnoses. "
          "It is **not** a finerenone treatment-eligible population, commercial opportunity estimate, or validated cross-cycle trend.")
    sections=[{'title':'NHANES population screening estimate','status':'PREVIOUSLY_DERIVED_REVIEW_REQUIRED','text':text,'citations':[obs['evidence_id']]},
              {'title':'Interpretation and limitations','status':'SCREENING_NOT_DIAGNOSIS','text':'The previously derived survey estimate has not been independently replicated in this demonstration. CKD confirmation requires longitudinal assessment. Finerenone eligibility requires separate clinical adjudication. Cross-cycle comparisons are not validated.','citations':[obs['evidence_id']]}]
    return {'version':'V7.7.2','intent':intent,'question':question,'retrieved_utc':utc(),'status':'POPULATION_ANSWER_WITH_GUARDS',
            'sections':sections,'citations':[{'id':obs['evidence_id'],'type':'NHANES observation','url':None,'verification':'PREVIOUSLY_DERIVED_REVIEW_REQUIRED'}],
            'warnings':['Screening proxy is not diagnosis or treatment eligibility.'],
            'external':{'pubmed':{'status':'NOT_REQUESTED','records':[]},'trials':{'status':'NOT_REQUESTED','records':[]}},
            'technical_trace':{'intent_routing':intent,'baseline_integrity':integrity_result,'population_observation':obs,'source_prevalence_fraction':rate,
                               'clinical_kg_lexical_retrieval':[],'external_status':{'pubmed':'NOT_REQUESTED','trials':'NOT_REQUESTED'},'source_query':None,
                               'claim_policy':'NO_UNSUPPORTED_ELIGIBILITY_OR_TRENDS'},'evidence_policy':'REAL_ONLY_NO_SIMULATED_SCIENTIFIC_EVIDENCE'}

def to_markdown(bundle):
    return re.sub(r'^# Healthcare Intelligence — V7\.[^\n]+', '# Healthcare Intelligence — V7.7.2',v77_markdown(bundle),count=1)
