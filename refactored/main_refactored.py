# refactored/main_refactored.py - Entry point for the refactored application
import streamlit as st
import sys
from pathlib import Path

# Add src to path for imports
sys.path.append(str(Path(__file__).parent / "src"))

from src.core.session_manager import SessionManager
from src.ui.chapter_management_refactored import ChapterManagementRefactored

def main():
    """Main application entry point for refactored version"""
    # Setup page configuration
    st.set_page_config(
        page_title="PDF Page Organizer (Refactored)",
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

    # Initialize session
    SessionManager.initialize_session()

    # Render the refactored chapter management
    chapter_management = ChapterManagementRefactored()
    chapter_management.render_chapter_management_page()

if __name__ == "__main__":
    main()