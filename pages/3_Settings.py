import streamlit as st
from services.router import guard_page
from components.sidebar import render as sidebar
from components.budget_summary import show_budget_summary
from components.budget_settings import render_budget_settings
from components.category_settings import render_category_settings
import os

guard_page("pages/Settings.py")

if not st.session_state.logged_in:
    st.stop()

def load_css(css_file):
    with open(css_file, 'r') as f:
        css = f.read()
    st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)

css_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'category_settings_styles.css')
load_css(css_path)

sidebar()
show_budget_summary(st.session_state.user_id)
st.markdown("---")

render_budget_settings(st.session_state.user_id)

st.markdown("---")

render_category_settings(st.session_state.user_id)