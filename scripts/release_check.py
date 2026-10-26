"""Offline fail-closed release checks. No network, writes only to output directory."""
from pathlib import Path
import hashlib,json,re,sys
from src.engine import integrity
from src.version import APP_VERSION,download_name
from src.v775 import build_v775,to_markdown

ROOT=Path(__file__).resolve().parents[1]
EXPECTED='4b43634ec370b1a7b1dfc28e6fbb9458172ba8234959d6c5f5713ad05d6212bf'

def check(outdir):
    report=integrity()
    assert report['baseline_sha256']==EXPECTED, 'KG checksum mismatch'
    assert (report['nodes'],report['edges'],report['observations'],report['links'])==(293,517,4,88)
    assert re.fullmatch(r'V\d+\.\d+\.\d+',APP_VERSION)
    app=(ROOT/'app.py').read_text()
    assert 'from src.v775 import build_v775 as build_investigation' in app
    assert 'from src.version import APP_VERSION, download_name' in app
    assert 'V7.7.4 local' not in app
    assert download_name('Investigation','md').endswith(APP_VERSION.replace('.','_')+'.md')
    questions=[
      'How many US adults meet the CKD screening and probable T2D proxy in NHANES 2021-2023?',
      'Investigate finerenone CKD T2D clinical evidence, NHANES population and treatment opportunity',
    ]
    outdir.mkdir(parents=True,exist_ok=True)
    manifest={'version':APP_VERSION,'mode':'OFFLINE_MOCK_FREE_NO_LIVE_API','kg_integrity':report,'investigations':[]}
    for index,q in enumerate(questions,1):
        b=build_v775(q,fetch_live=False,
          external_results={'pubmed':{'status':'UNAVAILABLE','records':[]},'trials':{'status':'UNAVAILABLE','records':[]}},
          pivotal_results={},abstract_results={'status':'NOT_REQUESTED','records':{}},
          primary_results={'status':'NOT_REQUESTED','records':[],'warnings':['offline test']})
        md=to_markdown(b)
        assert md.startswith('# Healthcare Intelligence — '+APP_VERSION)
        assert b['version']==APP_VERSION
        name=f'Offline_Regression_{index}_{APP_VERSION.replace(".","_")}.md'
        (outdir/name).write_text(md)
        manifest['investigations'].append({'question':q,'filename':name,'status':b.get('status'),
           'sha256':hashlib.sha256(md.encode()).hexdigest()})
    (outdir/'manifest.json').write_text(json.dumps(manifest,indent=2))
    print(json.dumps({'version':APP_VERSION,'checks':'PASS','offline_reports':len(questions)},indent=2))

if __name__=='__main__':
    check(Path(sys.argv[1] if len(sys.argv)>1 else 'release_artifacts'))
