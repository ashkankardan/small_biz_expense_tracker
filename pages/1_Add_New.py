import streamlit as st
from services.router import guard_page
from components.sidebar import render as sidebar

guard_page("pages/Add_New.py")

if st.session_state.logged_in:
    sidebar()

st.title("Add New")


