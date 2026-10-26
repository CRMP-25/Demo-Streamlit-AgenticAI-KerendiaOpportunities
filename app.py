"""V7.7.10 local Streamlit demo. No repository access, no synthetic scientific evidence."""
import json
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import networkx as nx
from src.demo import SAFE_QUESTIONS, observations, graph_neighborhood
from src.v777 import build_v777 as build_investigation, to_markdown
from src.nhanes_compute import compute_screening_total, SurveyInputError
from src.nhanes_cdc import compute_official_nhanes
from src.version import APP_VERSION, download_name
from src.v7 import literature_refresh, population
from src.release import report
from src.engine import integrity

st.set_page_config(page_title=f'Healthcare Intelligence | {APP_VERSION}',layout='wide',page_icon='🧬')
st.markdown('''<style>.block-container{padding-top:1.7rem;max-width:1450px}.small-note{color:#52647a;font-size:0.87rem}.hero{padding:1.25rem 1.6rem;background:#102c45;color:white;border-radius:14px}.hero h1{color:white;margin:0;font-size:2rem}.hero p{color:#d5e5ee;margin:0.4rem 0 0}</style>''',unsafe_allow_html=True)
st.markdown(f'<div class="hero"><h1>Healthcare Intelligence · {APP_VERSION}</h1><p>Clinical knowledge graph + population intelligence + verifiable biomedical evidence</p></div>',unsafe_allow_html=True)
st.caption('CONTROLLED DEMONSTRATION · Authentic evidence only · Screening ≠ diagnosis · No clinical eligibility or validated population trends')
try:
    stats=integrity()
except Exception as exc:
    st.error('Baseline integrity failed. Application halted: '+str(exc));st.stop()
c1,c2,c3,c4=st.columns(4)
c1.metric('Clinical concepts',stats['nodes']);c2.metric('KG relationships',stats['edges']);c3.metric('Population observations',stats['observations']);c4.metric('Candidate links',stats['links'])
ask_tab,graph_tab,pop_tab,compute_tab,lit_tab,report_tab,gate_tab=st.tabs(['Ask the Agent','KG Explorer','Population Intelligence','NHANES Compute','Evidence Explorer','Intelligence Report','Validation'])
with ask_tab:
    st.subheader('Question-directed evidence-grounded investigation')
    sample=st.selectbox('Example investigations',SAFE_QUESTIONS + [
        'Investigate the clinical evidence, population characteristics, and potential treatment opportunity for finerenone (Kerendia) in patients with chronic kidney disease and type 2 diabetes. Identify what is established, what is uncertain, and what additional evidence would be required.'])
    question=st.text_area('Question',value=sample,height=105,key='question')
    fetch=st.checkbox('Retrieve live PubMed and ClinicalTrials.gov evidence',value=True,
        help='Uses verified HTTPS sources. A connection failure is reported, never filled with invented records.')
    if st.button('Investigate',type='primary',key='ask'):
        with st.spinner('Routing the question and retrieving only relevant evidence...'):
            try:st.session_state['v77_bundle']=build_investigation(question,fetch_live=fetch)
            except Exception as exc:st.error('Investigation could not complete: '+str(exc))
    if 'v77_bundle' in st.session_state:
        b=st.session_state['v77_bundle']
        st.info('Question intent: '+b.get('intent','INTEGRATED')+' | Status: '+b['status']+' — supported findings remain visible.')
        for section in b['sections']:
            st.markdown('### '+section['title'])
            st.markdown(section['text'])
            if section['citations']:st.caption('Evidence IDs: '+', '.join(section['citations']))
        with st.expander('Technical tool execution and full source provenance'):
            st.json(b['technical_trace'])
        st.download_button('Download investigation (.md)',to_markdown(b),download_name('Investigation','md'),'text/markdown')
    st.caption('Population-only questions bypass PubMed, ClinicalTrials.gov, and KG traversal even when live retrieval is checked. Transparent bounded tool orchestration, not an autonomous LLM. Only unsupported claims are blocked; supported findings remain visible.')
with graph_tab:
    st.subheader('Read-only clinical knowledge graph')
    term=st.text_input('Find concepts',value='kidney')
    try:
        graph=graph_neighborhood(term)
        if graph['nodes']:
            G=nx.Graph()
            for n in graph['nodes']:G.add_node(n['id'],label=n['label'])
            for e in graph['edges']:G.add_edge(e['source'],e['target'])
            pos=nx.spring_layout(G,seed=11)
            fig=go.Figure()
            for u,v in G.edges():
                fig.add_trace(go.Scatter(x=[pos[u][0],pos[v][0]],y=[pos[u][1],pos[v][1]],mode='lines',line=dict(width=1,color='#9ab0c2'),hoverinfo='skip',showlegend=False))
            fig.add_trace(go.Scatter(x=[pos[n][0] for n in G.nodes],y=[pos[n][1] for n in G.nodes],mode='markers+text',text=[n for n in G.nodes],textposition='top center',marker=dict(size=18,color='#0e7490',line=dict(width=1.5,color='#083344')),textfont=dict(color='#101010',size=13,family='Arial Black'),hovertext=[G.nodes[n]['label'] for n in G.nodes],hoverinfo='text',showlegend=False))
            fig.update_layout(height=410,margin=dict(l=10,r=10,t=15,b=10),xaxis=dict(visible=False),yaxis=dict(visible=False),plot_bgcolor='#ffffff',paper_bgcolor='#ffffff',font=dict(color='#111111'))
            st.plotly_chart(fig,use_container_width=True)
            st.markdown('<style>div[data-testid="stDataFrame"]{color:#111111} div[data-testid="stDataFrame"] a{color:#075985!important;text-decoration:underline!important}</style>',unsafe_allow_html=True)
            st.dataframe(pd.DataFrame(graph['nodes']),use_container_width=True,hide_index=True)
            st.caption('Only edges already in the original graph are shown; disconnected results are valid. Lexical search is not clinical adjudication.')
        else:st.info('No matching baseline concepts.')
    except Exception as exc:st.error(str(exc))
with pop_tab:
    st.subheader('NHANES population screening evidence')
    period=st.selectbox('Survey period',['2021-2023','2017-2018','2015-2016'])
    scenario=st.selectbox('Available observation', ['primary','urine_albumin_bridge_sensitivity'] if period=='2021-2023' else ['primary'])
    result=population(period,scenario)
    if result['status']=='NO_EVIDENCE':st.warning('No source observation for this selection.')
    else:
        st.metric('Estimated adults meeting screening proxy',f"{result['estimate']:,.0f}")
        ci=result.get('ci_95')
        if ci and len(ci)==2 and all(x is not None for x in ci):
            st.write(f"Reported 95% CI: **{ci[0]:,.0f}–{ci[1]:,.0f}**")
        st.write('**Survey weight:**',result['survey_weight'],' | **Unweighted cases:**',result['unweighted_cases'],' | **Complete records:**',result['unweighted_denominator'])
        st.info('Preliminary single-visit CKD laboratory screening + probable T2D proxy; NOT confirmed CKD, clinical eligibility, or addressable market.')
        with st.expander('Source provenance and definition'):st.json(result)
    st.caption('Cross-cycle trend comparisons are deliberately disabled. Period selection is descriptive only.')
with compute_tab:
    st.subheader('V7.7.10 · CDC NHANES auto-computation')
    st.info('No files needed from you. Retrieve five official CDC 2021–2023 SAS XPT modules, derive documented screening proxies, and calculate a survey-weighted estimate.')
    if st.button('Retrieve CDC data and compute screening estimate', type='primary', key='nhanes_cdc_compute'):
        with st.spinner('Downloading official CDC files, joining participant records and calculating survey-weighted estimate...'):
            try:
                st.session_state['v779_cdc_result'] = compute_official_nhanes()
            except Exception as exc:
                st.error('CDC computation unavailable; no estimate generated: '+str(exc))
    if 'v779_cdc_result' in st.session_state:
        cdc = st.session_state['v779_cdc_result']
        st.metric('Computed adult screening proxy (NOT diagnosed or eligible)', f"{cdc['estimate']:,.0f}")
        st.write('Unweighted positive / known:', cdc['unweighted_positive'], '/', cdc['unweighted_known'])
        if cdc.get('ci95_t_approx'):
            st.write('Approximate 95% Student-t CI:', f"{cdc['ci95_t_approx'][0]:,.0f} – {cdc['ci95_t_approx'][1]:,.0f}")
            st.caption(f"PSU Taylor SE: {cdc['standard_error']:,.0f}; design df: {cdc['design_degrees_freedom']}; t critical: {cdc['ci95_t_critical']:.3f}. Not independently CDC-certified.")
        else:
            st.warning('Confidence interval unavailable under current PSU design checks.')
        sensitivity = cdc.get('missing_status_sensitivity')
        if sensitivity:
            st.write('Missing-screening classification sensitivity (not a confidence interval):',
                     f"{sensitivity['all_missing_negative']:,.0f} – {sensitivity['all_missing_positive']:,.0f}")
            st.caption(f"Missing screening records: {cdc['missing_screening_rows']:,}; survey weight represented by these records: {cdc['missing_screening_weight']:,.0f}. These extreme cases do not correct selection bias.")
        st.write('Difference from historical 9,233,798 estimate:', f"{cdc['difference_from_historical']:,.0f}")
        st.warning(cdc['historical_comparability'] + ' ' + cdc['cautions'])
        with st.expander('Definitions, source URLs, file SHA-256 checksums and methods'):
            st.json(cdc)
        st.download_button('Download CDC computation audit (JSON)', json.dumps(cdc,indent=2),
                           file_name='Healthcare_Intelligence_CDC_NHANES_V7_7_10.json',mime='application/json')
    st.divider()
    st.subheader('Advanced: analyze your own prepared participant-level CSV')
    st.warning('Optional advanced workflow. Only upload authentic, de-identified data. This is a screening proxy, NOT confirmed disease or treatment eligibility.')
    st.caption('CSV must include a 0/1 screening flag derived by your documented rules, an appropriate survey weight, survey stratum and PSU. Optional 0/1 universe flag. Uploaded data are processed in this session; do not upload identifying information.')
    upload = st.file_uploader('Upload de-identified participant-level CSV', type=['csv'], key='nhanes_v778_upload')
    if upload is not None:
        try:
            df = pd.read_csv(upload)
            st.caption(f'{len(df):,} rows; {len(df.columns)} columns. Preview suppressed to reduce inadvertent disclosure.')
            cols = list(df.columns)
            if len(cols) < 4:
                st.error('At least four mapped columns are required.')
            else:
                flag = st.selectbox('Binary CKD/T2D screening-proxy flag (0/1)', cols, key='nhanes_flag')
                weight = st.selectbox('Correct NHANES survey weight', cols, index=min(1,len(cols)-1), key='nhanes_weight')
                strata = st.selectbox('Survey stratum (e.g. SDMVSTRA)', cols, index=min(2,len(cols)-1), key='nhanes_strata')
                psu = st.selectbox('Survey PSU (e.g. SDMVPSU)', cols, index=min(3,len(cols)-1), key='nhanes_psu')
                universe = st.selectbox('Universe restriction flag (optional)', ['None']+cols, key='nhanes_universe')
                cycle = st.text_input('NHANES cycle and weight derivation (required for audit)', placeholder='e.g. 2021–2023, WTPH2YR; cite source and exclusions', key='nhanes_cycle')
                definition = st.text_area('Screening flag definition and missingness rules (required for audit)', key='nhanes_definition')
                if st.button('Compute survey-weighted screening estimate', key='nhanes_compute_button'):
                    if not cycle.strip() or not definition.strip():
                        st.error('Document the survey cycle/weight derivation and screening definition first.')
                    else:
                        try:
                            result = compute_screening_total(df,flag=flag,weight=weight,strata=strata,psu=psu,universe=None if universe=='None' else universe)
                            result['user_cycle_and_weight_notes'] = cycle
                            result['user_screening_definition'] = definition
                            st.session_state['v778_computation'] = result
                        except SurveyInputError as exc:
                            st.error(str(exc))
        except Exception as exc:
            st.error('Could not parse CSV: '+str(exc))
    if 'v778_computation' in st.session_state:
        r=st.session_state['v778_computation']
        st.metric('Survey-weighted screening proxy total', f"{r['estimate']:,.0f}")
        st.write('Unweighted positive / known:', r['unweighted_positive'], '/', r['unweighted_known'])
        st.write('Missing screening values:', r['missing_screening_rows'])
        if r.get('ci95_t_approx'):
            st.write('Approximate 95% Student-t CI:', f"{r['ci95_t_approx'][0]:,.0f} – {r['ci95_t_approx'][1]:,.0f}")
        if r.get('missing_status_sensitivity'):
            st.write('Missing-status extreme-case sensitivity (not CI):', r['missing_status_sensitivity'])
        else:
            st.warning('CI unavailable: singleton strata or insufficient PSU degrees of freedom.')
        st.caption(r['limitations'])
        st.download_button('Download computation audit (JSON)',json.dumps(r,indent=2),file_name='Healthcare_Intelligence_NHANES_Computation_V7_7_10.json',mime='application/json')

with lit_tab:
    st.subheader('Authentic biomedical source retrieval')
    term=st.text_input('PubMed / ClinicalTrials.gov search',value='finerenone chronic kidney disease')
    st.caption('Only actual HTTPS API results are displayed. No cached fabricated papers, synthetic trials, or fallback citations.')
    if st.button('Retrieve live records',key='live'):
        with st.spinner('Requesting real records from biomedical sources...'):
            try:st.session_state['v76_literature']=literature_refresh(term)
            except Exception as exc:st.error(str(exc))
    if 'v76_literature' in st.session_state:
        for source,record in st.session_state['v76_literature'].items():
            st.markdown('#### '+source.title())
            if record['status']=='UNAVAILABLE':st.warning('Live source unavailable: '+record.get('error','Unknown error'))
            elif record['status']=='NO_EVIDENCE':st.info('No matching source records.')
            else:
                st.success('Retrieved from live source · '+record.get('retrieved_utc',''))
                for item in record['records']:st.markdown('- ['+item.get('title','Untitled').replace('[','').replace(']','')+']('+item['url']+') · '+(item.get('pmid') or item.get('nct_id','')))
            with st.expander('Retrieval provenance'):st.json(record)
with report_tab:
    st.subheader('Source-linked intelligence report')
    if 'v77_bundle' not in st.session_state:
        st.info('Use “Ask the Agent” to run an integrated investigation first.')
    else:
        bundle=st.session_state['v77_bundle']
        markdown=to_markdown(bundle)
        st.markdown(markdown)
        st.download_button('Download report (.md)',markdown,download_name('Report','md'),'text/markdown')
        st.download_button('Download evidence JSON',json.dumps(bundle,indent=2,default=str),download_name('Evidence','json'),'application/json')
with gate_tab:
    st.subheader('Validation and evidence limitations')
    st.json(report())
    st.warning(f'{APP_VERSION} is a controlled functional demonstration, not a research-validated or clinical-grade system. External API verification requires network access.')
    st.caption('No GitHub access, cloning, pushing, deployment, or original KG modification is performed by this application.')
