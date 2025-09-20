
# src/ui/app_layout.py
import streamlit as st
from ui.sidebar import render_sidebar
from ui.main_content import render_main_content
from ui.progress_tracker import render_progress_tracker
from ui.chapter_management import render_chapter_management_page
from ui.page_assignment import render_page_assignment_page
from core.session_manager import SessionManager

def setup_page_config():
    """Configure Streamlit page settings"""
    st.set_page_config(
        page_title="PDF Page Organizer",
        page_icon="📚",
        layout="wide",
        initial_sidebar_state="expanded"
    )

def render_main_app():
    """Render the main application layout"""
    st.title("📚 PDF Page Organizer")
    
    # Navigation tabs
    tab1, tab2, tab3 = st.tabs(["📋 Project Setup", "📂 Chapter Management", "📄 Page Assignment"])
    
    with tab1:
        render_project_setup_tab()
    
    with tab2:
        render_chapter_management_page()
    
    with tab3:
        render_page_assignment_page()

def render_project_setup_tab():
    """Render the project setup tab"""
    st.markdown("---")
    render_sidebar()
    render_main_content()
