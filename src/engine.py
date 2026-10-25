"""Read-only consolidated V1-V6 evidence engine; no network or production writes."""
from pathlib import Path
import hashlib,json,re,csv
ROOT=Path(__file__).resolve().parents[1]
EXPECTED_SHA='4b43634ec370b1a7b1dfc28e6fbb9458172ba8234959d6c5f5713ad05d6212bf'

def load():
    base=(ROOT/'data/baseline_kg_COPY.json').read_bytes()
    sha=hashlib.sha256(base).hexdigest()
    if sha!=EXPECTED_SHA: raise ValueError('Clinical KG baseline checksum mismatch')
    kg=json.loads(base)
    observations=json.loads((ROOT/'data/population_observations.json').read_text())
    with (ROOT/'data/clinical_link_adjudication.csv').open(newline='') as f: links=list(csv.DictReader(f))
    return {'baseline_sha256':sha,'kg':kg,'observations':observations,'links':links}

def ask(question, store=None):
    store=store or load(); q=question.lower().strip()
    evidence=[]
    if any(x in q for x in ('kerendia','finerenone','eligible','eligibility','prescrib','treatable','market size','addressable market')):
        return {'status':'BLOCKED_ELIGIBILITY','answer':'NHANES single-visit screening proxies do not establish confirmed disease, prescription eligibility, or treatment market size. Clinical validation required.','evidence_ids':[]}
    if any(x in q for x in ('trend','increase over time','decrease over time','change across','compare cycles','growth rate')):
        return {'status':'BLOCKED_TREND','answer':'Cross-period trends are not validated: laboratory comparability and other epidemiological review remain unresolved.','evidence_ids':[]}
    if any(x in q for x in ('ckd','kidney','diabet','nhanes','prevalence')):
        obs=store['observations']; period='2021-2023'
        for p in ('2015-2016','2017-2018','2021-2023'):
            if p in q: period=p
        chosen=next((o for o in obs if o.get('period')==period and o.get('scenario')=='primary'),None)
        if not chosen:return {'status':'NO_EVIDENCE','answer':'No matching primary observation.','evidence_ids':[]}
        n=chosen['estimated_adults']; ci=chosen.get('count_ci_95')
        phrase=f"NHANES {period}: approximately {n:,.0f} U.S. adults meet a single-visit CKD laboratory-screening and probable T2D proxy"
        if ci and all(v is not None for v in ci):phrase+=f" (reported 95% CI {ci[0]:,.0f}–{ci[1]:,.0f})"
        phrase+='; not confirmed diagnoses, treatment eligibility, or a validated trend.'
        return {'status':'SCREENING_ESTIMATE_WITH_CAVEATS','answer':phrase,'evidence_ids':[chosen['id']],'weight':chosen.get('survey_weight_variable') or chosen.get('weight')}
    return {'status':'OUT_OF_SCOPE','answer':'No supported population evidence for this question.','evidence_ids':[]}

def integrity():
    d=load();kg=d['kg'];nodes=kg.get('nodes',[]);edges=kg.get('links',kg.get('edges',[]))
    return {'baseline_sha256':d['baseline_sha256'],'nodes':len(nodes),'edges':len(edges),'observations':len(d['observations']),'links':len(d['links'])}
