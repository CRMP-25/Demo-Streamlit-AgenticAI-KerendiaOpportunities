"""Offline release gates and immutable source manifest; run from project root."""
from pathlib import Path
import json,hashlib,csv,datetime,subprocess,sys
from .engine import ROOT,integrity,EXPECTED_SHA
from .v7 import population

def run_gates():
    i=integrity();checks={}
    checks['clinical_baseline_sha256']=i['baseline_sha256']==EXPECTED_SHA
    checks['baseline_nodes_293']=i['nodes']==293
    checks['baseline_edges_517']=i['edges']==517
    checks['population_observations_4']=i['observations']==4
    checks['clinical_mapping_candidates_88']=i['links']==88
    checks['correct_2021_2023_weight']=population('2021-2023')['survey_weight']=='WTPH2YR'
    checks['correct_2017_2018_weight']=population('2017-2018')['survey_weight']=='WTMEC2YR'
    with (ROOT/'data/clinical_link_adjudication.csv').open(newline='') as f:links=list(csv.DictReader(f))
    checks['no_human_approved_links']=not any(str(x.get('human_review_completed','')).lower()=='true' for x in links)
    return checks

def report():
    checks=run_gates()
    return {'timestamp_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'PASS_LOCAL_EVIDENCE_GATES' if all(checks.values()) else 'FAIL','checks':checks,'scientific_release':'NOT_APPROVED','open_scientific_gates':['Raw NHANES reprocessing not independently rerun','R survey cross-check not independently rerun','Cross-cycle creatinine comparability not established','Clinical mappings not human approved','External epidemiological validation pending'],'network_retrieval':'UNVERIFIED_IN_CURRENT_ENVIRONMENT','production_github_accessed_by_v7_code':False}
if __name__=='__main__':print(json.dumps(report(),indent=2))
