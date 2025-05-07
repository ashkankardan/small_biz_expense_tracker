import streamlit as st
from pathlib import Path
from services.session_state import logout

LOGO_PATH = Path("assets/sbet_logo.png")


def render() -> None:
    with st.sidebar:

        if LOGO_PATH.exists():
            st.image(str(LOGO_PATH), use_column_width=True)

        st.markdown("---")

        st.page_link("pages/1_Add_New.py", label="Add New")
        st.page_link("pages/2_Reports.py", label="Reports")
        st.page_link("pages/3_Settings.py", label="Settings")

        st.markdown("---")

        if st.button("Log out", use_container_width=True):
            logout()
            st.switch_page("pages/Login.py")
