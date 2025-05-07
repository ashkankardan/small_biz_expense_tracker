import streamlit as st
from services.router import guard_page
from components.sidebar import render as sidebar
from components.budget_summary import show_budget_summary

guard_page("pages/Reports.py")

if st.session_state.logged_in:
    sidebar()

    show_budget_summary(st.session_state.user_id)

    st.markdown("---")

else:
    st.stop()

