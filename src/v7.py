"""V7 safe evidence orchestration. All scientific evidence is real or explicitly unavailable.
No GitHub, repository, shell, or arbitrary URL access. No synthetic research data.
"""
from __future__ import annotations
import csv,hashlib,json,math,re,datetime,urllib.parse,urllib.request
from pathlib import Path
from .engine import load,integrity,ask,ROOT

ALLOWED_DOMAINS={'eutils.ncbi.nlm.nih.gov','clinicaltrials.gov'}
API={'pubmed':'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/', 'trials':'https://clinicaltrials.gov/api/v2/studies'}
STOPWORDS={'the','and','for','with','from','that','this','about','have','what','which','where','could','should','are','how','many','patients','adults','disease','study'}

class EvidenceUnavailable(RuntimeError): pass

def utc():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def digest(b):return hashlib.sha256(b).hexdigest()

def _get_json(url, timeout=12):
    parsed=urllib.parse.urlparse(url)
    if parsed.scheme!='https' or parsed.hostname not in ALLOWED_DOMAINS:
        raise ValueError('External host not on approved biomedical-source allowlist')
    request=urllib.request.Request(url,headers={'User-Agent':'Healthcare-KG-Research-V7/0.1 (research prototype)'})
    try:
        with urllib.request.urlopen(request,timeout=timeout) as resp:
            if resp.status!=200:raise EvidenceUnavailable('HTTP '+str(resp.status))
            data=resp.read(5_000_001)
            if len(data)>5_000_000:raise EvidenceUnavailable('Response size limit exceeded')
            return json.loads(data),digest(data)
    except (OSError,ValueError) as exc:raise EvidenceUnavailable(str(exc)) from exc

def pubmed_live(term='finerenone chronic kidney disease',max_results=5):
    """Real PubMed ESearch and ESummary. Never fabricate articles on failure."""
    n=max(1,min(int(max_results),10))
    q=urllib.parse.urlencode({'db':'pubmed','term':term,'retmax':n,'retmode':'json'})
    search,sha=_get_json(API['pubmed']+'esearch.fcgi?'+q)
    ids=search.get('esearchresult',{}).get('idlist',[])
    if not ids:return {'status':'NO_EVIDENCE','source':'PubMed','records':[],'retrieved_utc':utc(),'search_sha256':sha}
    q=urllib.parse.urlencode({'db':'pubmed','id':','.join(ids),'retmode':'json'})
    summaries,sha2=_get_json(API['pubmed']+'esummary.fcgi?'+q)
    records=[]
    for pmid in ids:
        entry=summaries.get('result',{}).get(pmid)
        if not entry:continue
        records.append({'source':'PubMed','pmid':pmid,'title':entry.get('title',''),'pubdate':entry.get('pubdate',''),'authors':[a.get('name','') for a in entry.get('authors',[])], 'url':'https://pubmed.ncbi.nlm.nih.gov/'+pmid+'/'})
    return {'status':'RETRIEVED','source':'PubMed','records':records,'retrieved_utc':utc(),'search_sha256':sha,'summary_sha256':sha2,'query':term}

def trials_live(term='finerenone',max_results=5):
    q=urllib.parse.urlencode({'query.term':term,'pageSize':max(1,min(int(max_results),10)),'format':'json'})
    result,sha=_get_json(API['trials']+'?'+q)
    records=[]
    for study in result.get('studies',[]):
        prot=study.get('protocolSection',{}); ident=prot.get('identificationModule',{}); stat=prot.get('statusModule',{})
        nct=ident.get('nctId','')
        if nct and re.fullmatch(r'NCT\d{8}',nct):records.append({'source':'ClinicalTrials.gov','nct_id':nct,'title':ident.get('briefTitle',''),'overall_status':stat.get('overallStatus',''),'url':'https://clinicaltrials.gov/study/'+nct})
    return {'status':'RETRIEVED','source':'ClinicalTrials.gov','records':records,'retrieved_utc':utc(),'response_sha256':sha,'query':term}

def literature_refresh(term='finerenone chronic kidney disease', include_trials=True):
    """Live retrieval only. Failed sources explicitly unavailable; no fallback masquerading as fresh."""
    results={}
    for name,func,args in [('pubmed',pubmed_live,(term,)),('trials',trials_live,(term,))]:
        if name=='trials' and not include_trials:continue
        try:results[name]=func(*args)
        except EvidenceUnavailable as exc:results[name]={'status':'UNAVAILABLE','source':name,'records':[],'error':str(exc),'retrieved_utc':utc()}
    return results

def get_observations():return load()['observations']

def population(period='2021-2023',scenario='primary'):
    obs=next((x for x in get_observations() if x['period']==period and x['scenario']==scenario),None)
    if obs is None:return {'status':'NO_EVIDENCE','period':period,'scenario':scenario}
    return {'status':'REVIEW_REQUIRED','evidence_id':obs['id'],'period':period,'scenario':scenario,'estimate':obs['estimated_adults'],'ci_95':obs.get('count_ci_95'),'survey_weight':obs['survey_weight'],'unweighted_cases':obs['unweighted_cases'],'unweighted_denominator':obs['unweighted_denominator'],'definition':obs['definition'],'provenance':obs['provenance'],'limitations':['Single-visit screening proxy; not a confirmed diagnosis','Not an eligibility or market-size estimate','Cross-cycle trends not validated','External epidemiological validation outstanding']}

def scenario_analysis(period='2021-2023',fraction=None):
    """Only explicit user-specified arithmetic sensitivity; never label as clinical eligibility."""
    base=population(period)
    if base['status']=='NO_EVIDENCE':return base
    if fraction is None:return {'status':'NEEDS_ASSUMPTION','answer':'Specify a hypothetical fraction (0 to 1); no clinical eligibility fraction is supported by these data.','baseline_evidence_id':base['evidence_id']}
    if isinstance(fraction,bool) or not isinstance(fraction,(int,float)) or not math.isfinite(fraction) or not 0<=fraction<=1:raise ValueError('Fraction must be finite between 0 and 1')
    return {'status':'HYPOTHETICAL_ARITHMETIC_ONLY','baseline_evidence_id':base['evidence_id'],'user_assumption_fraction':fraction,'arithmetic_result':base['estimate']*fraction,'answer':'Arithmetic scenario only; not treatment eligibility, forecast, or addressable market.','source_ci_95':base['ci_95']}

def concept_search(query,limit=8):
    """Baseline-only lexical retrieval; not clinical validation or ontological matching."""
    store=load();tokens={t for t in re.findall(r'[a-z0-9]+',query.lower()) if len(t)>3 and t not in STOPWORDS}
    matches=[]
    for node in store['kg'].get('nodes',[]):
        if isinstance(node,dict):
            nid=node.get('id'); typ=node.get('type'); desc=str(node.get('description') or node.get('desc') or node.get('label') or node.get('name') or '')
        elif isinstance(node,(list,tuple)) and len(node)>=3:
            nid,typ,desc=node[:3];desc=str(desc)
        else:continue
        words=set(re.findall(r'[a-z0-9]+',desc.lower())); score=len(tokens & words)
        if score:matches.append({'node_id':nid,'node_type':typ,'description':desc[:400],'lexical_overlap':score,'mapping_status':'NOT_CLINICALLY_VALIDATED'})
    matches.sort(key=lambda x:(-x['lexical_overlap'],str(x['node_id'])))
    return matches[:limit]

def plan(question):
    """Transparent bounded tool plan; not autonomous LLM reasoning."""
    q=question.lower();steps=['baseline_integrity']
    if any(w in q for w in ('nhanes','population','prevalence','adults','ckd','diabet','kidney')):steps.append('population_observation')
    if any(w in q for w in ('clinical','mechanism','evidence','finerenone','kerendia','kidney','ckd')):steps.append('clinical_kg_lexical_retrieval')
    if any(w in q for w in ('pubmed','literature','trial','latest','new study')):steps.append('external_literature_live')
    return steps

def investigate(question,external=False):
    """Bounded tool orchestration with conservative scientific response policy."""
    if not isinstance(question,str) or not question.strip():raise ValueError('Question required')
    if len(question)>1500:raise ValueError('Question too long')
    steps=plan(question);results={};results['baseline_integrity']=integrity()
    q=question.lower()
    if 'population_observation' in steps:
        period=next((p for p in ('2015-2016','2017-2018','2021-2023') if p in q),'2021-2023')
        results['population_observation']=population(period)
    if 'clinical_kg_lexical_retrieval' in steps:results['clinical_kg_lexical_retrieval']=concept_search(question)
    if 'external_literature_live' in steps:
        results['external_literature_live']=literature_refresh() if external else {'status':'NOT_REQUESTED_FOR_EXECUTION','reason':'Enable external=True to attempt real biomedical APIs; no cached/simulated results substituted'}
    guarded=ask(question)
    # Guard broad eligibility/market and cross-cycle questions even if historical router misses synonyms.
    if re.search(r'\b(eligible|eligibility|indicated|prescrib|market|tam|sam|som|commercial|treatable)\b',q):
        guarded={'status':'BLOCKED_ELIGIBILITY','answer':'Screening proxies do not support clinical eligibility or market sizing.','evidence_ids':[]}
    if re.search(r'\b(trend|trends|growth|longitudinal|change over time|across cycles|increase|increased|decrease|decreased|compare|comparison)\b',q):
        guarded={'status':'BLOCKED_TREND','answer':'Cross-cycle trend inference remains blocked pending laboratory and epidemiological comparability review.','evidence_ids':[]}
    return {'question':question,'timestamp_utc':utc(),'plan':steps,'tools':results,'response':guarded,'overall_status':'BLOCKED' if guarded['status'].startswith('BLOCKED') else 'REVIEW_REQUIRED' if guarded['status']=='SCREENING_ESTIMATE_WITH_CAVEATS' else 'LIMITED_EVIDENCE','evidence_policy':'REAL_ONLY_NO_SIMULATED_SCIENTIFIC_EVIDENCE'}
