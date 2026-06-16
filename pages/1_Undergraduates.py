import streamlit as st
import dashboard_engine
import ug_config

st.set_page_config(page_title=ug_config.PAGE_TITLE, layout="wide")
dashboard_engine.render_dashboard(ug_config)