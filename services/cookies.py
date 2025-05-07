import streamlit as st
from streamlit_cookies_manager import CookieManager

cookies = CookieManager()
if not cookies.ready():
    st.stop()
