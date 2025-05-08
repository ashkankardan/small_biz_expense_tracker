import streamlit as st
from streamlit_javascript import st_javascript

def get_browser_tz() -> str:
    if "tz" not in st.session_state:
        tz = st_javascript("Intl.DateTimeFormat().resolvedOptions().timeZone")
        st.session_state.tz = tz if tz else "UTC"
    return st.session_state.tz
