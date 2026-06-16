import streamlit as st
import streamlit_app
import grad_config

st.set_page_config(page_title=grad_config.PAGE_TITLE, layout="wide")
dashboard_engine.render_dashboard(grad_config)