# src/core/auth_manager.py - Simple authentication for localhost use

import streamlit as st

class AuthManager:
    """Simple authentication manager for localhost use"""

    # Set to True to require password, False to disable authentication
    REQUIRE_AUTH = False

    # Simple password - change this to your desired password
    APP_PASSWORD = "admin123"

    @staticmethod
    def is_authenticated() -> bool:
        """Check if user is authenticated"""
        return st.session_state.get('authenticated', False)

    @staticmethod
    def login(password: str) -> bool:
        """Simple login check"""
        if password == AuthManager.APP_PASSWORD:
            st.session_state['authenticated'] = True
            return True
        return False

    @staticmethod
    def logout():
        """Logout user"""
        st.session_state['authenticated'] = False