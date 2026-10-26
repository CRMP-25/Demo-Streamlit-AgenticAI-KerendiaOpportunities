"""V7.7.4: primary-trial verified retrieval, readable KG, source-grounded quantitative synthesis.

A curated PMID is only a search candidate until its PubMed title and abstract are
retrieved and verified. No synthetic outcomes, no clinical eligibility estimates.
"""
from __future__ import annotations
import re
from .v773 import build_v773, to_markdown as previous_markdown, complete_source_sections
from .v77 import fetch_abstracts, _request_bytes
from .engine import load
from .version import APP_VERSION
from .v772 import classify_intent
import json, urllib.parse

# Candidate identifiers: ALWAYS independently verify via PubMed ESummary and EFetch.
PRIMARY_CANDIDATES = {
 'FIDELIO-DKD': ('33264825', 'Effect of Finerenone on Chronic Kidney Disease Outcomes in Type 2 Diabetes'),
 'FIGARO-DKD': ('34449181', 'Cardiovascular and Kidney Outcomes with Finerenone in Type 2 Diabetes'),
}

def normalize_title(s):
    return re.sub(r'[^a-z0-9]+',' ',s.casefold()).strip()

def verify_primary_candidate(group, pmid, expected, summary):
    title=str(summary.get('title',''))
    if not title or normalize_title(expected) not in normalize_title(title):
        return None
    return {'study':group,'pmid':pmid,'title':title,'url':'https://pubmed.ncbi.nlm.nih.gov/'+pmid+'/',
            'publication_type':'PRIMARY_TRIAL_TITLE_VERIFIED_PUBMED',
            'verification':'PUBMED_TITLE_MATCH_NOT_FULL_TEXT_APPRAISAL'}

def retrieve_primary_papers():
    ids=[x[0] for x in PRIMARY_CANDIDATES.values()]
    url='https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?'+urllib.parse.urlencode({'db':'pubmed','id':','.join(ids),'retmode':'json'})
    try:
        response=json.loads(_request_bytes(url))['result']
        records=[];failures=[]
        for group,(pmid,expected) in PRIMARY_CANDIDATES.items():
            match=verify_primary_candidate(group,pmid,expected,response.get(pmid,{}))
            if match:records.append(match)
            else:failures.append(group+': PubMed title verification failed')
        return {'status':'RETRIEVED' if records else 'NO_VERIFIED_PRIMARY','records':records,'warnings':failures}
    except Exception as exc:
        return {'status':'UNAVAILABLE','records':[],'warnings':['Primary publication retrieval failed: '+str(exc)]}

def kg_node_map():
    nodes=load()['kg'].get('nodes',[])
    result={}
    for n in nodes:
        if isinstance(n,(list,tuple)) and len(n)>=3:
            result[str(n[0])]={'type':str(n[1]),'description':str(n[2])}
        elif isinstance(n,dict):
            result[str(n.get('id'))]={'type':str(n.get('type','')),'description':str(n.get('description') or n.get('label') or n.get('name') or '')}
    return result

def readable_graph_v774(bundle):
    nodes=kg_node_map(); lines=[]
    for edge in bundle.get('graph_edges',[])[:12]:
        a,b=str(edge['source']),str(edge['target'])
        def show(nid):
            n=nodes.get(nid)
            if not n:return f'Unresolved KG node (`KG:{nid}`)'
            desc=n['description'].replace('|','\\|').strip()
            if len(desc)>190:desc=desc[:187].rsplit(' ',1)[0]+'…'
            return f'{desc} (`KG:{nid}`, {n["type"]})'
        lines.append(f'- **{show(a)}** — **{edge["relation"]}** → **{show(b)}**. *Preserved graph assertion; not clinically adjudicated.*')
    return '\n'.join(lines) if lines else 'No relevant preserved graph edges retrieved.'

def quantitative_source_findings(record):
    """Source-attributed quantitative snippets only; no inferred denominators or endpoint labels."""
    result=[]
    for s in record.get('abstract_sections',[]):
        if 'result' not in s.get('label','').casefold() and 'method' not in s.get('label','').casefold():continue
        text=s.get('text','')
        # Extract complete source sentences containing explicitly reported effect measures.
        sentences=re.split(r'(?<=[.!?])\s+(?=[A-Z])',text)
        for sentence in sentences:
            if re.search(r'\b(?:hazard ratio|HR|confidence interval|95% CI|rate ratio)\b',sentence,re.I):
                result.append(sentence.strip())
    return result[:5]

def build_v774(question, *, fetch_live=True, external_results=None, pivotal_results=None, abstract_results=None, primary_results=None):
    b=build_v773(question,fetch_live=fetch_live,external_results=external_results,
                 pivotal_results=pivotal_results,abstract_results=abstract_results)
    b['version']=APP_VERSION
    b['technical_trace']['release_version']=APP_VERSION
    if b.get('intent')=='POPULATION_ONLY':return b
    b['sections']=[s for s in b['sections'] if s['title'] not in ('Executive evidence synthesis and decision gaps','Readable original KG relationships')]
    if b.get('intent') in ('INTEGRATED','KG_ONLY'):
        b['sections'].append({'title':'Clinically readable preserved KG relationships',
             'status':'KG_SOURCE_DESCRIPTIONS_NOT_INDEPENDENTLY_VERIFIED','text':readable_graph_v774(b),
             'citations':['KG:'+str(e['source']) for e in b.get('graph_edges',[])[:12]]})
    if b.get('intent') in ('INTEGRATED','CLINICAL_EVIDENCE_ONLY'):
        prim=primary_results if primary_results is not None else (retrieve_primary_papers() if fetch_live else {'status':'NOT_REQUESTED','records':[],'warnings':['Live primary retrieval not requested']})
        verified=[r for r in prim.get('records',[]) if r.get('verification')=='PUBMED_TITLE_MATCH_NOT_FULL_TEXT_APPRAISAL']
        if verified:
            pmids=[r['pmid'] for r in verified]
            abstracts=fetch_abstracts(pmids) if fetch_live else {'status':'NOT_REQUESTED','records':{}}
            for r in verified:
                r['abstract_sections']=complete_source_sections(abstracts.get('records',{}).get(r['pmid'],{}))
        b['primary_trial_evidence']={'status':prim.get('status','UNAVAILABLE'),'records':verified,'warnings':prim.get('warnings',[])}
        # Also retain prior FIDELITY/secondary evidence; avoid double-counting duplicates.
        rows=['| Trial | Verified publication | PubMed title check | Abstract |','|---|---|---|---|']
        for group in PRIMARY_CANDIDATES:
            rec=next((r for r in verified if r['study']==group),None)
            rows.append(f'| {group} | '+(f'[PMID {rec["pmid"]}]({rec["url"]}) | Title verified | '+('Retrieved' if rec.get('abstract_sections') else 'Unavailable') if rec else 'Unavailable | Not verified | Unavailable')+' |')
        b['sections'].insert(0,{'title':'Verified primary efficacy publication audit','status':'TITLE_VERIFIED_NOT_FULL_TEXT_APPRAISAL',
            'text':'\n'.join(rows)+'\n\nA verified title is not a full-text clinical appraisal. '+(' '.join(prim.get('warnings',[])) if prim.get('warnings') else ''),
            'citations':[r['pmid'] for r in verified]})
        comparison=[]
        all_records=verified+b.get('structured_evidence',[])
        for r in all_records:
            findings=quantitative_source_findings(r)
            if findings:
                comparison.append(f'**{r["study"]} — PMID {r["pmid"]}** ('+('verified primary candidate' if r in verified else 'other retrieved publication')+')')
                comparison.extend('- Source abstract: '+f for f in findings)
            else:comparison.append(f'**{r["study"]} — PMID {r["pmid"]}:** No source-attributed effect-measure sentence extracted; do not infer results.')
        b['sections'].insert(1,{'title':'Quantitative evidence interpretation — source-attributed',
           'status':'SOURCE_SENTENCES_NOT_INDEPENDENTLY_APPRAISED',
           'text':'\n\n'.join(comparison) if comparison else 'No quantitative results available from retrieved abstracts.',
           'citations':list(dict.fromkeys(r['pmid'] for r in all_records))})
        for r in verified:
            if not any(c['id']==r['pmid'] for c in b['citations']):
                b['citations'].append({'id':r['pmid'],'type':'PubMed verified primary publication title','url':r['url'],
                   'verification':'PUBMED_TITLE_MATCH_NOT_FULL_TEXT_APPRAISAL'})
        missing=[g for g in PRIMARY_CANDIDATES if not any(r['study']==g for r in verified)]
        summary=('**Primary evidence:** '+(', '.join(r['study']+' (PMID '+r['pmid']+')' for r in verified) if verified else 'No primary publication verified in this run')+'. '
                 +('Unverified: '+', '.join(missing)+'. ' if missing else '')+
                 '**Interpretation:** The clinical evidence is limited to attributed PubMed abstracts; full-text trial appraisal and current prescribing-label review remain necessary. '
                 '**Population applicability:** The historical 9.23-million NHANES laboratory-screening proxy is not a diagnosed or finerenone-eligible population. '
                 '**Next actions:** Compare endpoint definitions, safety, inclusion/exclusion criteria and available NHANES variables; do not estimate market size without validated inputs.')
        b['sections'].insert(0,{'title':'Executive evidence synthesis — V7.7.4','status':'PARTIAL_EVIDENCE_BOUNDED',
            'text':summary,'citations':[r['pmid'] for r in verified]})
    return b

def to_markdown(bundle):
    return re.sub(r'^# Healthcare Intelligence[^\n]*','# Healthcare Intelligence — '+APP_VERSION,previous_markdown(bundle),count=1)
