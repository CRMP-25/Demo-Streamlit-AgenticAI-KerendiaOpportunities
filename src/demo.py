"""V7.6 demo composition. Read-only authentic stored evidence; live sources never simulated."""
import json,re,hashlib
from .engine import load,integrity,ROOT
from .v7 import investigate,population,concept_search,literature_refresh

SAFE_QUESTIONS=[
 'How many US adults meet the CKD screening and probable T2D proxy in NHANES 2021-2023?',
 'What clinical KG concepts are relevant to chronic kidney disease?',
 'What does the available evidence establish about Kerendia eligibility?',
 'Did the CKD population increase across NHANES cycles?',
 'Find PubMed literature and clinical trials on finerenone chronic kidney disease',
]

def observations():
    return [population(o['period'],o['scenario']) for o in load()['observations']]

def graph_neighborhood(search='kidney',limit=24):
    """Read-only baseline subgraph; nodes selected by lexical search, links only from baseline."""
    data=load()['kg']; nodes=data.get('nodes',[]); edges=data.get('links',data.get('edges',[]))
    selected=concept_search(search,limit=max(1,min(limit,40)))
    ids={str(n['node_id']) for n in selected}
    connections=[]
    for e in edges:
        if isinstance(e,dict):
            src=e.get('source',e.get('src'));tgt=e.get('target',e.get('tgt'));rel=e.get('relation',e.get('label','related'))
        elif isinstance(e,(list,tuple)) and len(e)>=3:
            src,tgt,rel=e[:3]
        else:continue
        if isinstance(src,dict):src=src.get('id')
        if isinstance(tgt,dict):tgt=tgt.get('id')
        if str(src) in ids and str(tgt) in ids:
            connections.append({'source':str(src),'target':str(tgt),'relation':str(rel)})
    return {'nodes':[{'id':str(n['node_id']),'label':n['description'][:90],'type':n['node_type'],'mapping_status':'UNREVIEWED_BASELINE_CONCEPT'} for n in selected], 'edges':connections,'baseline_sha256':integrity()['baseline_sha256'],'clinical_equivalence_approved':False}

def evidence_bundle(question,live=False):
    """Generate a source-linked report without claiming external records if unavailable."""
    investigation=investigate(question,external=False)
    obs=investigation['tools'].get('population_observation')
    concepts=investigation['tools'].get('clinical_kg_lexical_retrieval',[])
    external=literature_refresh('finerenone chronic kidney disease') if live else {'pubmed':{'status':'NOT_REQUESTED','records':[]},'trials':{'status':'NOT_REQUESTED','records':[]}}
    citations=[]
    if obs and obs.get('evidence_id'):
        citations.append({'evidence_id':obs['evidence_id'],'kind':'NHANES_SOURCE_OBSERVATION','source':'data/population_observations.json','status':'REVIEW_REQUIRED'})
    for source,entry in external.items():
        for record in entry.get('records',[]):
            citations.append({'evidence_id':record.get('pmid') or record.get('nct_id'),'kind':source,'source':record.get('url'),'status':'RETRIEVED'})
    response=investigation['response']
    sections=[{'heading':'Research question','text':question},
              {'heading':'Supported answer / safeguard','text':response['answer']},
              {'heading':'Population evidence','text':('Observation '+obs['evidence_id']+'; '+str(obs['estimate'])+' adults; single-visit screening proxy, not a confirmed diagnosis.' if obs and obs.get('evidence_id') else 'No applicable population estimate selected.')},
              {'heading':'Clinical KG context','text':str(len(concepts))+' lexical concept matches. These are NOT validated disease equivalences.'},
              {'heading':'External literature','text':'; '.join(k+': '+v['status'] for k,v in external.items())},
              {'heading':'Limits','text':'No confirmed diagnoses, clinical eligibility, market size, validated cross-cycle trends, or patient-specific advice.'}]
    return {'version':'V7.6','status':investigation['overall_status'],'sections':sections,'citations':citations,'external':external,'investigation':investigation,'source_integrity':integrity(),'evidence_policy':'REAL_ONLY','scientific_approval':False}

def report_markdown(bundle):
    lines=['# Healthcare Intelligence | Evidence-grounded demonstration','', '**Research prototype — not clinical advice.**','']
    for s in bundle['sections']:
        lines.extend(['## '+s['heading'],s['text'],''])
    lines.append('## Evidence identifiers')
    if not bundle['citations']:lines.append('No supporting external identifiers retrieved; do not infer source verification.')
    for c in bundle['citations']:lines.append('- '+str(c['evidence_id'])+' — '+c['kind']+' — '+c['source']+' ('+c['status']+')')
    lines.extend(['','## Scientific limitations','Existing NHANES outputs are preliminary single-visit screening proxies. Clinical mappings are unreviewed. Trend and eligibility conclusions are blocked.'])
    return '\n'.join(lines)+'\n'
