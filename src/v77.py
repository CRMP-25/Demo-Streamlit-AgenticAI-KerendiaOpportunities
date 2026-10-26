"""V7.7 bounded evidence-grounded intelligence; baseline graph and NHANES read-only.
No LLM or fabricated clinical outcomes. Summarizes abstract text as attributed excerpts, not validated efficacy.
"""
from __future__ import annotations
import re, xml.etree.ElementTree as ET, urllib.parse, urllib.request, urllib.error, time, threading, copy, email.utils, datetime
from .engine import load, integrity
from .v7 import pubmed_live, literature_refresh, EvidenceUnavailable, utc, _get_json, API
from .v761 import build_investigation, to_markdown as prior_markdown

PIVOTAL_QUERIES = {
    'FIDELIO-DKD': 'finerenone FIDELIO-DKD randomized trial',
    'FIGARO-DKD': 'finerenone FIGARO-DKD randomized trial',
    'FIDELITY': 'finerenone FIDELITY pooled analysis'
}

# In-process, time-bounded cache of actual API responses; never synthesizes evidence.
_CACHE={}
_CACHE_LOCK=threading.Lock()
CACHE_SECONDS=6*3600

def _cached(key, producer):
    with _CACHE_LOCK:
        entry=_CACHE.get(key)
        if entry and time.monotonic()-entry[0]<CACHE_SECONDS:
            result=copy.deepcopy(entry[1]); result['cache_status']='VERIFIED_RESPONSE_CACHED'; return result
    result=producer()
    if result.get('status')=='RETRIEVED':
        with _CACHE_LOCK:_CACHE[key]=(time.monotonic(),copy.deepcopy(result))
    return result

def _request_bytes(url, timeout=18, max_bytes=2_000_000, attempts=3, sleeper=None):
    """Allowlisted verified HTTPS; bounded retry only for 429/5xx; no TLS bypass."""
    parsed=urllib.parse.urlparse(url)
    if parsed.scheme!='https' or parsed.hostname!='eutils.ncbi.nlm.nih.gov':
        raise EvidenceUnavailable('Disallowed evidence host')
    if sleeper is None:sleeper=time.sleep
    last=None
    for i in range(attempts):
        req=urllib.request.Request(url,headers={'User-Agent':'Healthcare-KG-Research-V7.7.1/0.1 (public research demo)'})
        try:
            with urllib.request.urlopen(req,timeout=timeout) as response:
                if response.status!=200:raise EvidenceUnavailable('HTTP '+str(response.status))
                data=response.read(max_bytes+1)
                if len(data)>max_bytes:raise EvidenceUnavailable('Source response size limit exceeded')
                return data
        except urllib.error.HTTPError as exc:
            last=exc
            if exc.code not in (429,500,502,503,504) or i==attempts-1:break
            delay=min(8.0,1.5*(2**i))
            retry=exc.headers.get('Retry-After') if exc.headers else None
            if retry:
                try:delay=min(8.0,max(delay,float(retry)))
                except ValueError:pass
            sleeper(delay)
        except (OSError,ValueError) as exc:
            last=exc;break
    raise EvidenceUnavailable('Verified PubMed request failed: '+str(last))

def graph_connections(concepts, max_edges=16):
    """Rank existing edges by retrieved endpoints and finerenone/CKD/T2D relevance."""
    kg=load()['kg']; edges=kg.get('edges',kg.get('links',[]))
    selected={str(c['node_id']) for c in concepts[:8]}
    if not selected:return []
    node_desc={str(n.get('id')):str(n.get('description') or n.get('label') or '') for n in kg.get('nodes',[]) if isinstance(n,dict)}
    rows=[]
    for e in edges:
        if not isinstance(e,(list,tuple)) or len(e)<3:continue
        a,b,rel=map(str,e[:3])
        if a not in selected and b not in selected:continue
        description=' '.join((node_desc.get(a,''),node_desc.get(b,''))).lower()
        clinical_terms=sum(t in description for t in ('finerenone','kidney','renal','diabet','albumin','cardiovascular'))
        score=10*int(a in selected and b in selected)+3*clinical_terms+int(a in ('DR7','D34') or b in ('DR7','D34'))*6
        rows.append((score,{'source':a,'relation':rel,'target':b,'both_endpoints_retrieved':a in selected and b in selected,'ranking':'QUESTION_RELEVANCE_HEURISTIC_NOT_CLINICAL_VALIDATION'}))
    rows.sort(key=lambda x:(-x[0],x[1]['source'],x[1]['target']))
    return [r for _,r in rows[:max_edges]]

def retrieve_pivotal(max_results=12):
    """One batched PubMed search plus one batched summary; no unverified title->study assignment."""
    def producer():
        query='(FIDELIO-DKD[Title/Abstract] OR FIGARO-DKD[Title/Abstract] OR FIDELITY[Title/Abstract]) AND finerenone[Title/Abstract]'
        args=urllib.parse.urlencode({'db':'pubmed','term':query,'retmax':min(20,max_results),'retmode':'json','sort':'relevance'})
        import json
        try:
            raw=_request_bytes(API['pubmed']+'esearch.fcgi?'+args)
            ids=json.loads(raw).get('esearchresult',{}).get('idlist',[])
            if not ids:return {'status':'NO_EVIDENCE','records':[],'retrieved_utc':utc(),'query':query}
            args2=urllib.parse.urlencode({'db':'pubmed','id':','.join(ids),'retmode':'json'})
            summaries=json.loads(_request_bytes(API['pubmed']+'esummary.fcgi?'+args2))
            records=[]
            for pmid in ids:
                item=summaries.get('result',{}).get(pmid,{})
                title=item.get('title','')
                if not title:continue
                groups=[k for k in PIVOTAL_QUERIES if k.lower() in title.lower()]
                records.append({'pmid':pmid,'title':title,'url':'https://pubmed.ncbi.nlm.nih.gov/'+pmid+'/','study_tags_from_title':groups,'source':'PubMed'})
            return {'status':'RETRIEVED','records':records,'retrieved_utc':utc(),'query':query}
        except (EvidenceUnavailable,ValueError,KeyError) as exc:
            return {'status':'UNAVAILABLE','records':[],'error':str(exc),'retrieved_utc':utc()}
    return _cached('pivotal_batch_v771',producer)

def fetch_abstracts(pmids):
    """Single HTTPS EFetch call for distinct authentic PMIDs; six-hour in-process cache."""
    ids=list(dict.fromkeys(str(x) for x in pmids if re.fullmatch(r'\d{1,12}',str(x))))[:20]
    if not ids:return {'status':'NO_EVIDENCE','records':{},'retrieved_utc':utc()}
    def producer():
        url='https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?'+urllib.parse.urlencode({'db':'pubmed','id':','.join(ids),'rettype':'abstract','retmode':'xml'})
        try:
            root=ET.fromstring(_request_bytes(url,max_bytes=3_000_000));records={}
            for article in root.findall('.//PubmedArticle'):
                pmid=article.findtext('./MedlineCitation/PMID','')
                if pmid not in ids:continue
                sections=[]
                for el in article.findall('./MedlineCitation/Article/Abstract/AbstractText'):
                    t=' '.join(''.join(el.itertext()).split())
                    if t:sections.append({'label':el.get('Label') or el.get('NlmCategory') or 'Abstract','text':t})
                records[pmid]={'sections':sections,'abstract_available':bool(sections),'source_url':'https://pubmed.ncbi.nlm.nih.gov/'+pmid+'/'}
            return {'status':'RETRIEVED','records':records,'retrieved_utc':utc()}
        except (OSError,ValueError,ET.ParseError,EvidenceUnavailable) as exc:
            return {'status':'UNAVAILABLE','records':{},'error':str(exc),'retrieved_utc':utc()}
    return _cached('abstracts_'+','.join(sorted(ids)),producer)

def build_v77(question, *, fetch_live=True, external_results=None, pivotal_results=None, abstract_results=None):
    base=build_investigation(question,fetch_live=fetch_live,external_results=external_results)
    concepts=base['technical_trace']['clinical_kg_lexical_retrieval']
    edges=graph_connections(concepts)
    pertinent=any(x in question.lower() for x in ('finerenone','kerendia'))
    if pivotal_results is not None:pivotal=pivotal_results
    elif fetch_live and pertinent:
        batch=retrieve_pivotal()
        pivotal={key:{'status':batch['status'] if batch['status']!='RETRIEVED' else 'NO_EVIDENCE','records':[],'error':batch.get('error',''),'retrieved_utc':batch.get('retrieved_utc')} for key in PIVOTAL_QUERIES}
        if batch['status']=='RETRIEVED':
            for record in batch['records']:
                for group in record.get('study_tags_from_title',[]):
                    pivotal[group]['records'].append(record);pivotal[group]['status']='RETRIEVED'
    else:pivotal={}
    all_pmids=[]; primary=[]
    for r in base['external'].get('pubmed',{}).get('records',[]):
        if r.get('pmid'):all_pmids.append(str(r['pmid']))
    for group,entry in pivotal.items():
        if entry.get('status')=='RETRIEVED':
            for r in entry.get('records',[]):
                if r.get('pmid'):
                    ident=str(r['pmid']);primary.append({'group':group,'pmid':ident,'title':r.get('title',''),'url':r.get('url','')});all_pmids.append(ident)
    if abstract_results is not None:abstracts=abstract_results
    elif fetch_live and pertinent:abstracts=fetch_abstracts(all_pmids)
    else:abstracts={'status':'NOT_REQUESTED','records':{}}
    # No generated trial efficacy claims; evidence snippets are verbatim attributed source excerpts.
    snippets=[]
    for item in primary:
        rec=abstracts.get('records',{}).get(item['pmid'],{})
        sections=rec.get('sections',[])
        # Only Results/Conclusions when explicitly labelled; otherwise note missing appraisal.
        findings=[s for s in sections if any(k in s.get('label','').lower() for k in ('result','conclu'))]
        snippets.append({'group':item['group'],'pmid':item['pmid'],'title':item['title'],'url':item['url'],
                         'source_excerpt':(' '.join(s['text'] for s in findings))[:900] if findings else None,
                         'assessment':'ABSTRACT_EXCERPT_NOT_INDEPENDENTLY_APPRAISED' if findings else 'RESULTS_NOT_EXTRACTED'})
    statuses={k:v.get('status','UNKNOWN') for k,v in pivotal.items()}
    graph_text='\n'.join('• KG:'+x['source']+' —['+x['relation']+']→ KG:'+x['target']+(' (both retrieved)' if x['both_endpoints_retrieved'] else ' (neighbor)') for x in edges) if edges else 'No original KG edges adjacent to the retrieved concepts were found.'
    source_lines=[]
    for x in snippets:
        source_lines.append('• '+x['group']+' | PMID '+x['pmid']+' | '+x['title']+' | '+x['url'])
        source_lines.append('  '+('Attributed abstract excerpt (not critically appraised): '+x['source_excerpt'] if x['source_excerpt'] else 'Study outcomes not extracted; full study appraisal required.'))
    for key,entry in pivotal.items():
        if entry.get('status')!='RETRIEVED':source_lines.append('• '+key+': '+entry.get('status','UNAVAILABLE')+'; '+entry.get('error','no verified records'))
    if not source_lines:source_lines=['Pivotal-study retrieval not requested or no verified records available.']
    funnel=[
      ('A. Observed screening population','Previously derived NHANES single-visit CKD laboratory-screening + probable T2D proxy; NOT confirmed CKD.'),
      ('B. Disease confirmation','Requires longitudinal CKD criteria and validated T2D ascertainment; unavailable here.'),
      ('C. Label-aligned clinical criteria','Requires current indication, eGFR, serum potassium, albuminuria where relevant, contraindications and clinical exclusions; not adjudicated here.'),
      ('D. Current treatment and overlap','Requires existing use, competing/combination therapies, contraindications, access and prescribing patterns; unavailable here.'),
      ('E. Opportunity estimate','Blocked until denominators, criteria, missingness and validated assumptions are supplied. No percentage or market number inferred.')]
    base['sections'].insert(2,{'title':'Original KG relationship traversal','status':'BASELINE_EDGES_ONLY_NOT_CLINICALLY_ADJUDICATED','text':graph_text,'citations':['KG:'+x['source'] for x in edges]})
    base['sections'].insert(4,{'title':'Targeted pivotal evidence and attributed abstract excerpts','status':'ABSTRACTS_NOT_CRITICALLY_APPRAISED','text':'\n'.join(source_lines),'citations':[x['pmid'] for x in snippets]})
    base['sections'].insert(-1,{'title':'Population opportunity evidence funnel','status':'REQUIREMENTS_NOT_ELIGIBILITY_ESTIMATE','text':'\n'.join('• '+name+': '+desc for name,desc in funnel),'citations':[base['technical_trace']['population_observation']['evidence_id']] if base['technical_trace']['population_observation'] and base['technical_trace']['population_observation'].get('evidence_id') else []})
    for x in snippets:
        if not any(c['id']==x['pmid'] for c in base['citations']):base['citations'].append({'id':x['pmid'],'type':'PubMed targeted pivotal retrieval','url':x['url'],'verification':'ABSTRACT_NOT_CRITICALLY_APPRAISED'})
    base['version']='V7.7.1';base['pivotal_evidence']=pivotal;base['abstract_evidence']=abstracts;base['graph_edges']=edges;base['evidence_funnel']=funnel
    base['technical_trace']['pivotal_status']=statuses;base['technical_trace']['abstract_status']=abstracts.get('status')
    base['technical_trace']['baseline_integrity']=integrity()
    return base

def to_markdown(bundle):
    result=prior_markdown(bundle)
    return result.replace('Healthcare Intelligence — V7.6.1','Healthcare Intelligence — V7.7.1',1)
