
# main.py - Entry point for the Streamlit application
import streamlit as st
import sys
from pathlib import Path

# Add src to path for imports
sys.path.append(str(Path(__file__).parent / "src"))

from src.core.session_manager import SessionManager
from src.ui.app_layout import setup_page_config, render_main_app


def main():
    """Main application entry point"""
    setup_page_config()
    SessionManager.initialize_session()
    render_main_app()

if __name__ == "__main__":
    main()