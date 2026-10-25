"""V7.7.3 evidence-bound clinical synthesis over authentic retrieved records.

No independent efficacy claims: evidence classifications are transparent title heuristics;
quantitative results are displayed only as verbatim complete source abstract sections.
"""
from __future__ import annotations
import re
from .v772 import build_v772, classify_intent
from .v761 import to_markdown as base_markdown
from .engine import load

APP_VERSION = 'V7.7.3'


def classify_study(title, group):
    t = (title or '').casefold()
    if group == 'FIDELITY' and ('pooled analysis' in t or 'pooled' in t):
        return 'POOLED_ANALYSIS_TITLE_HEURISTIC'
    if 'post hoc' in t or 'subgroup' in t or 'secondary' in t or 'an analysis' in t or 'hyperkalemia risk' in t:
        return 'SECONDARY_OR_SAFETY_ANALYSIS_TITLE_HEURISTIC'
    if 'randomized' in t or 'randomised' in t or 'effect of finerenone' in t or 'finerenone in patients' in t:
        return 'POTENTIAL_PRIMARY_TRIAL_TITLE_HEURISTIC_REVIEW_REQUIRED'
    return 'PUBLICATION_TYPE_UNRESOLVED'


def complete_source_sections(abstract):
    """Never cut a source statement mid-sentence; preserve whole attributed sections."""
    if not abstract or not abstract.get('abstract_available'):
        return []
    return [{'label': str(s.get('label','Abstract')), 'text': str(s.get('text','')).strip()}
            for s in abstract.get('sections',[]) if str(s.get('text','')).strip()]


def evidence_table(bundle):
    records = []
    abstracts = bundle.get('abstract_evidence',{}).get('records',{})
    seen = set()
    for group, entry in bundle.get('pivotal_evidence',{}).items():
        for item in entry.get('records',[]):
            pmid = str(item.get('pmid',''))
            if not re.fullmatch(r'\d{1,12}',pmid) or (group,pmid) in seen:
                continue
            seen.add((group,pmid))
            sections=complete_source_sections(abstracts.get(pmid,{}))
            records.append({'study':group,'pmid':pmid,'title':item.get('title',''),
                            'publication_type':classify_study(item.get('title',''),group),
                            'abstract_sections':sections,'url':item.get('url') or 'https://pubmed.ncbi.nlm.nih.gov/'+pmid+'/',
                            'appraisal':'NOT_INDEPENDENTLY_APPRAISED'})
    return sorted(records,key=lambda r:(r['study'], 0 if r['publication_type'].startswith('POTENTIAL_PRIMARY') else 1,r['pmid']))


def readable_graph(bundle):
    nodes={str(n.get('id')):n for n in load()['kg'].get('nodes',[]) if isinstance(n,dict)}
    lines=[]
    for edge in bundle.get('graph_edges',[])[:12]:
        a,b=edge['source'],edge['target']
        left=nodes.get(a,{});right=nodes.get(b,{})
        # Graph descriptions may be verbose: retain source text and identifiers in trace.
        def label(n,ident):
            value=str(n.get('label') or n.get('name') or n.get('description') or ident).strip()
            return value if len(value)<=135 else value[:132].rsplit(' ',1)[0]+'…'
        lines.append(f"- **{label(left,a)}** (`KG:{a}`) — **{edge['relation']}** → **{label(right,b)}** (`KG:{b}`). *Existing graph assertion; not clinically adjudicated.*")
    return '\n'.join(lines) if lines else 'No adjacent preserved graph relationships were retrieved.'


def build_v773(question, *, fetch_live=True, external_results=None, pivotal_results=None, abstract_results=None):
    b=build_v772(question,fetch_live=fetch_live,external_results=external_results,
                 pivotal_results=pivotal_results,abstract_results=abstract_results)
    b['version']=APP_VERSION
    b['technical_trace']['release_version']=APP_VERSION
    intent=b.get('intent') or classify_intent(question)
    if intent=='POPULATION_ONLY':
        return b
    # Replace legacy mid-sentence truncated excerpts with complete source sections below.
    b['sections']=[s for s in b['sections'] if s['title']!='Targeted pivotal evidence and attributed abstract excerpts']
    records=evidence_table(b)
    b['structured_evidence']=records
    if intent in ('INTEGRATED','CLINICAL_EVIDENCE_ONLY'):
        lines=['| Study | PMID | Publication type (title-based) | Abstract |', '|---|---|---|---|']
        for r in records:
            lines.append(f"| {r['study']} | [{r['pmid']}]({r['url']}) | {r['publication_type']} | {'Available' if r['abstract_sections'] else 'Unavailable'} |")
        if not records:lines=['No verified targeted pivotal-study records were available for classification.']
        b['sections'].append({'title':'Structured pivotal evidence comparison',
                              'status':'TITLE_HEURISTICS_AND_SOURCE_ABSTRACTS_NOT_CLINICAL_APPRAISAL',
                              'text':'\n'.join(lines)+'\n\nA title-based category is **not** confirmation of publication design or trial primacy. Verify the full study before interpreting effects.',
                              'citations':[r['pmid'] for r in records]})
        for r in records:
            source_parts=[f"**{r['study']} — PMID {r['pmid']}** ({r['publication_type']}; [PubMed]({r['url']}))"]
            selected=[s for s in r['abstract_sections'] if any(x in s['label'].casefold() for x in ('result','conclu','method','background'))]
            if not selected:selected=r['abstract_sections']
            for s in selected:
                source_parts.append(f"**Source abstract — {s['label']}:** {s['text']}")
            if not selected:source_parts.append('Abstract not available; study outcomes cannot be extracted.')
            b['sections'].append({'title':f"Source-attributed study record: {r['study']} ({r['pmid']})",
                                  'status':'COMPLETE_SOURCE_ABSTRACT_SECTIONS_NOT_INDEPENDENTLY_APPRAISED',
                                  'text':'\n\n'.join(source_parts),'citations':[r['pmid']]})
        primary={g:any(r['study']==g and r['publication_type'].startswith('POTENTIAL_PRIMARY') for r in records)
                 for g in ('FIDELIO-DKD','FIGARO-DKD')}
        synthesis=('**What the sources establish in this run:** Identifiable PubMed records and trial registrations were retrieved where available. '
                   'The source-attributed abstract sections above are evidence for further appraisal, not independently verified trial conclusions.\n\n'
                   '**Primary-trial evidence gap:** '+', '.join(g+(' has a candidate primary publication (verify full text)' if ok else ' lacks an identified primary efficacy publication') for g,ok in primary.items())+'.\n\n'
                   '**Clinical interpretation:** A study outcome cannot be extrapolated to all NHANES screening-positive adults. '
                   'Trial inclusion criteria, endpoint definitions, comparator treatment, adverse events, and applicability to the US population require appraisal.\n\n'
                   '**Next analysis:** Verify primary efficacy reports, extract outcome definitions and effect estimates with denominators and uncertainty, '
                   'then assess which trial/label criteria are observable in the NHANES data. Missing criteria remain unavailable; do not infer eligibility.')
        b['sections'].insert(0,{'title':'Executive evidence synthesis and decision gaps','status':'EVIDENCE_BOUNDED_NOT_CLINICAL_APPRAISAL',
                                'text':synthesis,'citations':[r['pmid'] for r in records]})
    if intent in ('INTEGRATED','KG_ONLY'):
        b['sections'].append({'title':'Readable original KG relationships','status':'GRAPH_ASSERTIONS_NOT_CLINICALLY_ADJUDICATED',
                              'text':readable_graph(b),'citations':['KG:'+e['source'] for e in b.get('graph_edges',[])[:12]]})
    if intent=='INTEGRATED':
        b['sections'].append({'title':'NHANES-to-clinical-evidence applicability matrix','status':'NO_ELIGIBILITY_EXTRAPOLATION',
          'text':('| Question | Available in this demonstration | Next requirement |\n|---|---|---|\n'
                  '| Screening population size | Historical NHANES proxy estimate | Independent survey replication |\n'
                  '| Confirmed CKD and T2D | Not established by single-visit proxy | Longitudinal diagnosis ascertainment |\n'
                  '| eGFR, albuminuria, potassium segmentation | Not estimated in this report | Analyze authentic participant-level survey variables and missingness |\n'
                  '| Trial inclusion/exclusion criteria | Not adjudicated | Verify primary trial protocols and endpoints |\n'
                  '| Label-aligned eligibility | Not established | Current label criteria and clinical review |\n'
                  '| Treated/untreated opportunity | Not established | Prescribing, contraindications, coverage, and overlap data |\n\n'
                  'No conversion percentage or market size is computed from unsupported assumptions.'),
          'citations':['NHANES_2021_2023_PRIMARY']})
    return b


def to_markdown(bundle):
    text=base_markdown(bundle)
    return re.sub(r'^# Healthcare Intelligence[^\n]*', '# Healthcare Intelligence — '+APP_VERSION, text, count=1)
