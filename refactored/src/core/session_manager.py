# core/session_manager.py - Modified to avoid circular imports

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
            'pdf_content': None,
            'total_pages': 0,
            'folder_structure_created': False,
            'created_folders': [],
            'chapters_config': {},
            'standalone_chapters': [],
            'current_step': 1,
            'chapters_created': False,
            'page_assignments': {},
            'extraction_history': [],
            'folder_metadata': {},
            'unique_chapter_counter': 0,
            'numbering_systems': {},
            'chapter_suffixes': {},
            'custom_parts': {},
            'font_case_selected': True,
            'selected_font_case': 'First Capital (Title Case)',
            'project_destination_folder': '',  # NEW: For project structure location
            'project_destination_selected': False,  # NEW: Track if project destination is set
            'total_pages_generated': 0,  # NEW: Cache for generated pages count
            'pages_calculated_timestamp': None,  # NEW: Last calculation timestamp
            'authenticated': False,  # Authentication state (only used when auth is enabled)
        }
        
        for key, value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = value

    @staticmethod
    def get_chapter_suffix(context_key: str) -> str:
        """Get chapter suffix for a specific context"""
        chapter_suffixes = SessionManager.get('chapter_suffixes', {})
        return chapter_suffixes.get(context_key, "")

    @staticmethod
    def set_chapter_suffix(context_key: str, suffix: str):
        """Set chapter suffix for a specific context"""
        chapter_suffixes = SessionManager.get('chapter_suffixes', {})
        chapter_suffixes[context_key] = suffix
        SessionManager.set('chapter_suffixes', chapter_suffixes)
    
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
        """Update project configuration while preserving important state"""
        if 'project_config' not in st.session_state:
            st.session_state.project_config = {}
        
        # Preserve font case from session state if not in updates
        if 'selected_font_case' not in updates:
            current_font_case = st.session_state.get('selected_font_case')
            if current_font_case:
                updates['selected_font_case'] = current_font_case
        
        st.session_state.project_config.update(updates)
        
        # Sync font case to session state if it's in the updates
        if 'selected_font_case' in updates:
            st.session_state['selected_font_case'] = updates['selected_font_case']
    
    @staticmethod
    def get_font_case() -> str:
        """Get current font case setting"""
        return st.session_state.get('selected_font_case', 'First Capital (Sentence case)')
    
    @staticmethod
    def set_font_case(font_case: str):
        """Set font case and mark as selected"""
        st.session_state['selected_font_case'] = font_case
        st.session_state['font_case_selected'] = True
        # Also store in project config for persistence
        project_config = st.session_state.get('project_config', {})
        project_config['selected_font_case'] = font_case
        st.session_state['project_config'] = project_config

    @staticmethod
    def get_default_destination() -> str:
        """Get default destination folder"""
        return st.session_state.get('default_destination_folder', '')

    @staticmethod
    def set_default_destination(folder_path: str):
        """Set default destination folder"""
        st.session_state['default_destination_folder'] = folder_path
        st.session_state['destination_folder_selected'] = True

    @staticmethod
    def get_project_destination() -> str:
        """Get project destination folder"""
        return st.session_state.get('project_destination_folder', '')

    @staticmethod
    def set_project_destination(folder_path: str):
        """Set project destination folder"""
        st.session_state['project_destination_folder'] = folder_path
        st.session_state['project_destination_selected'] = True