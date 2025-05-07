import streamlit as st

st.set_page_config(
    page_title="SmallBiz Expense Tracker",
    page_icon="SBET",
    layout="wide",
    initial_sidebar_state="collapsed",
)

if hasattr(st, "cache"):
    st.cache = st.cache_data

from services.session_state import init_state, logout
from services.router import guard_page
from database import init_db

init_db()
init_state()
guard_page("")

if st.session_state.logged_in:
    st.sidebar.success(f"👤 {st.session_state.email}")
    if st.sidebar.button("Log Out"):
        logout()
        st.experimental_rerun()

st.title("SmallBiz Expense Tracker")
