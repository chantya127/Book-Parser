# src/ui/login.py - Simple login UI component

import streamlit as st
from core.auth_manager import AuthManager

def render_login_form():
    """Render the login form"""
    st.title("🔐 Login to PDF Page Organizer")

    st.markdown("---")
    st.markdown("*Default password: admin123*")

    # Show authentication toggle info
    if AuthManager.REQUIRE_AUTH:
        st.info("🔒 Authentication is currently **ENABLED**")
    else:
        st.info("🔓 Authentication is currently **DISABLED**")

    # Center the login form
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("### Enter Password")

        password = st.text_input("Password", type="password", key="login_password")

        if st.button("Login", type="primary"):
            if AuthManager.login(password):
                st.success("Login successful!")
                st.rerun()
            else:
                st.error("Incorrect password. Please try again.")

        st.markdown("---")

def render_logout_button():
    """Render logout button in sidebar"""
    if st.sidebar.button("🚪 Logout", type="secondary"):
        AuthManager.logout()
        st.rerun()