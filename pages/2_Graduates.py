import streamlit as st
import dashboard_engine
import grad_config

st.set_page_config(page_title=grad_config.PAGE_TITLE, layout="wide")
dashboard_engine.render_dashboard(grad_config)