import streamlit as st
from services.auth import register_user
from services.router import guard_page, LOGIN_PAGE
import os

guard_page("pages/Signup.py")

def load_css(css_file):
    with open(css_file, 'r') as f:
        css = f.read()
    st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)

css_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'styles.css')
load_css(css_path)


st.title("Sign Up")

with st.form("signup_form"):
    email = st.text_input("Email:")
    password = st.text_input("Password:", type="password")
    submitted = st.form_submit_button("Sign Up")
    if submitted:
        success, status = register_user(email, password)
        if success:
            st.switch_page(LOGIN_PAGE)
        else:
            if status == "invalid_email":
                st.error("Invalid email format. Please enter a valid email address (e.g., user@example.com)")
            elif status == "email_exists":
                st.error("Email already registered.")
            elif status == "missing_fields":
                st.error("Please fill in both email and password fields.")

st.markdown('<div class="auth-link">Already have an account? <a href="/Login" target="_self">Log in here!</a></div>', unsafe_allow_html=True)