# src/ui/app_layout.py
import streamlit as st
from ui.sidebar import render_sidebar
from ui.main_content import render_main_content
from ui.progress_tracker import render_progress_tracker
from ui.chapter_management import render_chapter_management_page
from ui.page_assignment import render_page_assignment_page
from ui.custom_folder_management import render_custom_folder_management_page
from ui.font_selector import render_font_case_selector  # NEW IMPORT
from core.session_manager import SessionManager

def setup_page_config():
    """Configure Streamlit page settings"""
    st.set_page_config(
        page_title="PBS Organizer",
        page_icon="📚",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS to ensure primary buttons are properly styled and all buttons are red
    st.markdown("""
    <style>
        /* Force all buttons to be red */
        div.stButton > button:first-child,
        .stButton > button[kind="primary"],
        .stButton > button[kind="secondary"] {
            background-color: #ff4b4b !important;
            color: white !important;
            border-color: #ff4b4b !important;
            border: 1px solid #ff4b4b !important;
        }
        
        /* Hover state for buttons */
        div.stButton > button:first-child:hover,
        .stButton > button[kind="primary"]:hover,
        .stButton > button[kind="secondary"]:hover {
            background-color: #ff6c6c !important;
            border-color: #ff6c6c !important;
        }
        
        /* Active/pressed state for buttons */
        div.stButton > button:first-child:active,
        .stButton > button[kind="primary"]:active,
        .stButton > button[kind="secondary"]:active {
            background-color: #ff2b2b !important;
            border-color: #ff2b2b !important;
        }
        
        /* Disabled buttons should be grayed out */
        div.stButton > button:first-child:disabled {
            background-color: #cccccc !important;
            color: #666666 !important;
            border-color: #cccccc !important;
        }
    </style>
    """, unsafe_allow_html=True)

def render_main_app():
    """Render the main application layout"""
    from core.auth_manager import AuthManager
    from ui.login import render_login_form, render_logout_button

    # Check if authentication is required
    if AuthManager.REQUIRE_AUTH:
        # Check authentication first
        if not AuthManager.is_authenticated():
            render_login_form()
            return

        # Add logout button to sidebar
        render_logout_button()

    st.title("📚 PBS Organizer")

    # Show authentication status in main app
    if not AuthManager.REQUIRE_AUTH:
        st.info("🔓 Authentication is disabled - no password required")

    # Check if folder browser should be shown
    from ui.folder_selector import render_folder_browser_in_main

    if render_folder_browser_in_main():
        return  # Show only folder browser when active
    
    # Remove the font case check - go directly to tabs
    # Navigation tabs - Added Custom Folders tab
    tab1, tab2, tab3, tab4 = st.tabs([
        "📋 Project Setup", 
        "📂 Chapter Management", 
        "🗂️ Custom Folders",
        "📄 Page Assignment"
    ])
    
    with tab1:
        render_project_setup_tab()
    
    with tab2:
        render_chapter_management_page()
    
    with tab3:
        render_custom_folder_management_page()
    
    with tab4:
        render_page_assignment_page()

def render_project_setup_tab():
    """Render the project setup tab"""
    st.markdown("---")
    render_sidebar()
    render_main_content()