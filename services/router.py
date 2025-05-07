import streamlit as st
from services.session_state import init_state

LOGIN_PAGE  = "pages/Login.py"
SIGNUP_PAGE = "pages/Signup.py"
HOME_PAGE   = "pages/1_Add_New.py" 

def hide_sidebar_if_logged_out():
    if not st.session_state.logged_in:
        st.markdown("""
            <style>
            [data-testid="stSidebar"], [data-testid="stSidebarNav"] {display: none;}
            </style>
        """, unsafe_allow_html=True)

def guard_page(current_page: str = "") -> None:
    init_state()
    hide_sidebar_if_logged_out()

    if current_page == "":
        st.switch_page(HOME_PAGE)
        st.stop()

    if not st.session_state.logged_in and current_page not in (LOGIN_PAGE, SIGNUP_PAGE):
        st.switch_page(LOGIN_PAGE)
        st.stop()

    if st.session_state.logged_in and current_page in (LOGIN_PAGE, SIGNUP_PAGE):
        st.switch_page(HOME_PAGE)
        st.stop()
