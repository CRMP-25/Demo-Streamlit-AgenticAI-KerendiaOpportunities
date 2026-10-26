"""V7.7.5 local Streamlit demo. No repository access, no synthetic scientific evidence."""
import json
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import networkx as nx
from src.demo import SAFE_QUESTIONS, observations, graph_neighborhood
from src.v777 import build_v777 as build_investigation, to_markdown
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
ask_tab,graph_tab,pop_tab,lit_tab,report_tab,gate_tab=st.tabs(['Ask the Agent','KG Explorer','Population Intelligence','Evidence Explorer','Intelligence Report','Validation'])
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
