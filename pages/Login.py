import streamlit as st
from services.auth import authenticate_user
from services.session_state import login
from services.router import guard_page, SIGNUP_PAGE, HOME_PAGE
from database import SessionLocal
from models.user import User
import os

guard_page("pages/Login.py")

def load_css(css_file):
    with open(css_file, 'r') as f:
        css = f.read()
    st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)

css_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'styles.css')
load_css(css_path)


st.title("Login")

with st.form("auth_form"):
    email = st.text_input("Email:")
    password = st.text_input("Password:", type="password")
    submitted = st.form_submit_button("Log In")
    if submitted:
        if not email or not password:
            st.error("Please fill in both email and password fields.")
        else:
            with SessionLocal() as db:
                user = db.query(User).filter(User.email == email).first()
                success, status = authenticate_user(email, password, redirect=False)
                if success:
                    login(email, user.id)
                    st.switch_page(HOME_PAGE)
                else:
                    if status == "invalid_email":
                        st.error("Invalid email format. Please enter a valid email address (e.g., user@example.com)")
                    elif status == "invalid_credentials":
                        st.error("Invalid credentials.")

st.markdown('<div class="auth-link">Don\'t have an account? <a href="/Signup" target="_self">Sign up here!</a></div>', unsafe_allow_html=True)
