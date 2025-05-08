import streamlit as st
from services.router import guard_page
from components.sidebar import render as sidebar
from components.budget_summary import show_budget_summary
import os

guard_page("pages/Settings.py")

if not st.session_state.logged_in:
    st.stop()

def load_css(css_file):
    with open(css_file, 'r') as f:
        css = f.read()
    st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)

css_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'styles.css')
load_css(css_path)

sidebar()
show_budget_summary(st.session_state.user_id)
st.markdown("---")
