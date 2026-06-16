import streamlit as st
import streamlit_app
import ug_config

st.set_page_config(page_title=ug_config.PAGE_TITLE, layout="wide")
streamlit_app.render_dashboard(ug_config)