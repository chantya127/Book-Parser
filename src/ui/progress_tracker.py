
# src/ui/progress_tracker.py
import streamlit as st
from typing import List, Tuple
from core.session_manager import SessionManager

def render_progress_tracker():
    """Render progress tracking section"""
    st.subheader("🗺️ Progress")
    
    progress_steps = get_progress_steps()
    
    for i, (step, completed) in enumerate(progress_steps, 1):
        status = "✅" if completed else "⭕"
        st.write(f"{status} Step {i}: {step}")

def get_progress_steps() -> List[Tuple[str, bool]]:
    """Get current progress steps and their completion status"""
    config = SessionManager.get('project_config', {})
    extraction_history = SessionManager.get('extraction_history', [])
    
    return [
        ("Upload PDF", SessionManager.get('pdf_uploaded')),
        ("Configure Project", bool(config.get('code') and config.get('book_name'))),
        ("Set Parts", config.get('num_parts', 0) > 0),
        ("Create Structure", SessionManager.get('folder_structure_created')),
        ("Configure Chapters", SessionManager.get('chapters_created')),
        ("Extract Pages", len(extraction_history) > 0)
    ]
