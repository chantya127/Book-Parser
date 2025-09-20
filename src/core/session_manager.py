import streamlit as st
from typing import Dict, Any

class SessionManager:
    """Manages application session state"""
    
    @staticmethod
    def initialize_session():
        """Initialize session state with default values"""
        defaults = {
            'project_config': {},
            'pdf_uploaded': False,
            'pdf_file': None,
            'pdf_content': None,  # Store PDF content to avoid re-reading
            'total_pages': 0,
            'folder_structure_created': False,
            'created_folders': [],
            'chapters_config': {},  # {part_1: [chapters], part_2: [chapters]}
            'current_step': 1,
            'chapters_created': False,
            'page_assignments': {},  # Track page assignments
            'extraction_history': [],  # Track completed extractions
            'folder_metadata': {},  # {folder_id: {display_name, actual_path, type}}
            'unique_chapter_counter': 0,  # For ensuring unique chapter identifiers
            'numbering_systems': {},  # {Part_1: numbering_system, Part_2: numbering_system}
        }
        
        for key, value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = value
    
    @staticmethod
    def get(key: str, default=None):
        """Get value from session state"""
        return st.session_state.get(key, default)
    
    @staticmethod
    def set(key: str, value: Any):
        """Set value in session state"""
        st.session_state[key] = value
    
    @staticmethod
    def update_config(updates: Dict[str, Any]):
        """Update project configuration"""
        if 'project_config' not in st.session_state:
            st.session_state.project_config = {}
        st.session_state.project_config.update(updates)