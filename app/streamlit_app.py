from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pandas as pd
import streamlit as st
from src.engine import analyze, load_incidents

st.set_page_config(page_title='IncidentIQ | AI Incident Triage', page_icon='🔎', layout='wide')
st.title('🔎 IncidentIQ')
st.caption('AI-assisted incident similarity search and explainable assignment-group suggestions · Works locally')

records = load_incidents()
st.metric('Indexed sample incidents', len(records))
st.info('Demonstration uses synthetic incidents. Similarity is not proof of duplication; review matches before taking action.')

with st.form('triage'):
    title = st.text_input('Incident short description', placeholder='VPN connection drops after MFA login')
    details = st.text_area('Detailed description', placeholder='Users cannot reconnect to the corporate VPN...')
    c1, c2 = st.columns(2)
    k = c1.slider('Maximum matches', 1, 15, 5)
    min_score = c2.slider('Minimum similarity', 0.0, 1.0, 0.10, 0.05)
    submitted = st.form_submit_button('Analyze incident', type='primary')

if submitted:
    if not title.strip():
        st.error('Enter a short description.')
    else:
        report = analyze(title, details, k, min_score)
        suggestion = report['suggested_assignment']
        left, right = st.columns(2)
        left.metric('Suggested assignment group', suggestion['assignment_group'])
        right.metric('Possible duplicate?', 'Review suggested' if report['possible_duplicate'] else 'Not flagged')
        st.caption(f"Routing explanation: {', '.join(suggestion['matched_keywords']) or 'No matching rules; defaulted to Service Desk'}")
        if report['similar_incidents']:
            df = pd.DataFrame(report['similar_incidents'])
            df['similarity'] = (df['similarity'] * 100).round(1).astype(str) + '%'
            st.subheader('Closest historical incidents')
            st.dataframe(df[['number', 'short_description', 'assignment_group', 'state', 'similarity']], hide_index=True, use_container_width=True)
            st.download_button('Download matches as CSV', df.to_csv(index=False).encode('utf-8'), 'incidentiq_matches.csv', 'text/csv')
        else:
            st.warning('No records match the chosen similarity threshold.')
        with st.expander('Why this result?'):
            st.write('TF-IDF (unigrams and bigrams) converts text to vectors; cosine similarity ranks historical incidents. Assignment suggestions use explicit keyword rules, not a learned classification model.')

with st.expander('Browse sample incident catalog'):
    st.dataframe(pd.DataFrame(records), hide_index=True, use_container_width=True)
