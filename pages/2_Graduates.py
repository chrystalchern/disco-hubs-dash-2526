import streamlit as st
import streamlit_app
import grad_config

st.set_page_config(page_title=grad_config.PAGE_TITLE, layout="wide")
streamlit_app.render_dashboard(grad_config)