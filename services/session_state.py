import streamlit as st
from services.auth import destroy_session_cookie, check_persistent_login
from models.user import User
from database import SessionLocal

def init_state() -> None:
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.email = ""

        user_id = check_persistent_login()
        if user_id:
            with SessionLocal() as db:
                user = db.get(User, user_id)
                if user:
                    st.session_state.logged_in = True
                    st.session_state.email = user.email

def login(email: str):
    st.session_state.logged_in = True
    st.session_state.email = email

def logout():
    destroy_session_cookie()
    st.session_state.logged_in = False
    st.session_state.email = ""
