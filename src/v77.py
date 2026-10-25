"""V7.7 bounded evidence-grounded intelligence; baseline graph and NHANES read-only.
No LLM or fabricated clinical outcomes. Summarizes abstract text as attributed excerpts, not validated efficacy.
"""
from __future__ import annotations
import re, xml.etree.ElementTree as ET, urllib.parse, urllib.request
from .engine import load, integrity
from .v7 import pubmed_live, literature_refresh, EvidenceUnavailable, utc, _get_json
from .v761 import build_investigation, to_markdown as prior_markdown

PIVOTAL_QUERIES = {
    'FIDELIO-DKD': 'finerenone FIDELIO-DKD randomized trial',
    'FIGARO-DKD': 'finerenone FIGARO-DKD randomized trial',
    'FIDELITY': 'finerenone FIDELITY pooled analysis'
}

def graph_connections(concepts, max_edges=16):
    """Only original edges, with relation strings retained. No new clinical mapping."""
    kg=load()['kg']; edges=kg.get('edges',kg.get('links',[]))
    selected={str(c['node_id']) for c in concepts[:8]}; rows=[]
    for e in edges:
        if not isinstance(e,(list,tuple)) or len(e)<3: continue
        a,b,rel=map(str,e[:3])
        if a in selected or b in selected:
            rows.append({'source':a,'relation':rel,'target':b,'both_endpoints_retrieved':a in selected and b in selected})
        if len(rows)>=max_edges:break
    return rows

def retrieve_pivotal(max_results=2):
    """Search real PubMed. Explicitly record failures and do not substitute known-looking IDs."""
    result={}
    for key,term in PIVOTAL_QUERIES.items():
        try:result[key]=pubmed_live(term,max_results=max_results)
        except (EvidenceUnavailable, OSError, ValueError) as exc:
            result[key]={'status':'UNAVAILABLE','records':[],'error':str(exc)}
    return result

def fetch_abstracts(pmids):
    """Verified HTTPS PubMed XML abstracts, no simulated text, bounded to 10 IDs."""
    ids=list(dict.fromkeys(str(x) for x in pmids if re.fullmatch(r'\d{1,12}',str(x))))[:10]
    if not ids:return {'status':'NO_EVIDENCE','records':{},'retrieved_utc':utc()}
    url='https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?'+urllib.parse.urlencode({'db':'pubmed','id':','.join(ids),'rettype':'abstract','retmode':'xml'})
    # Follow same HTTPS host allowlist and certificate verification as V7.
    req=urllib.request.Request(url,headers={'User-Agent':'Healthcare-KG-Research-V7.7/0.1'})
    try:
        with urllib.request.urlopen(req,timeout=18) as response:
            if response.status!=200:raise EvidenceUnavailable('HTTP '+str(response.status))
            raw=response.read(2_000_001)
            if len(raw)>2_000_000:raise EvidenceUnavailable('Abstract XML size limit exceeded')
        root=ET.fromstring(raw);records={}
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

def build_v77(question, *, fetch_live=True, external_results=None, pivotal_results=None, abstract_results=None):
    base=build_investigation(question,fetch_live=fetch_live,external_results=external_results)
    concepts=base['technical_trace']['clinical_kg_lexical_retrieval']
    edges=graph_connections(concepts)
    pertinent=any(x in question.lower() for x in ('finerenone','kerendia'))
    if pivotal_results is not None:pivotal=pivotal_results
    elif fetch_live and pertinent:pivotal=retrieve_pivotal()
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
    base['version']='V7.7';base['pivotal_evidence']=pivotal;base['abstract_evidence']=abstracts;base['graph_edges']=edges;base['evidence_funnel']=funnel
    base['technical_trace']['pivotal_status']=statuses;base['technical_trace']['abstract_status']=abstracts.get('status')
    base['technical_trace']['baseline_integrity']=integrity()
    return base

def to_markdown(bundle):
    result=prior_markdown(bundle)
    return result.replace('Healthcare Intelligence — V7.6.1','Healthcare Intelligence — V7.7',1)
