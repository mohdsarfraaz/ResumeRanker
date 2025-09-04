import streamlit as st
from datetime import datetime
from header import render_header
from jd_input import job_description_section
from resume_processing import process_resumes
from results import render_results
from sidebar import render_sidebar

# Reset at midnight
today = datetime.now().date()
if "last_run_date" not in st.session_state or st.session_state["last_run_date"] != today:
    st.session_state.clear()
    st.session_state["last_run_date"] = today

st.set_page_config(page_title="📄 Resume Ranker", layout="wide")

# Layout
render_header()
jd_text, filters = job_description_section()
resume_files, results = process_resumes(jd_text, filters)

if results:
    render_results(results)

render_sidebar()
