# src/ui/sidebar.py
import streamlit as st
from core.session_manager import SessionManager
from core.pdf_handler import PDFHandler
from core.folder_manager import FolderManager

def render_sidebar():
    """Render sidebar with project configuration"""
    
    with st.sidebar:
        st.header("🔧 Project Configuration")
        
        render_pdf_upload_section()
        render_project_details_section()
        render_parts_configuration_section()

def render_pdf_upload_section():
    """Render PDF upload section"""
    st.subheader("Step 1: Upload PDF")
    
    uploaded_file = st.file_uploader(
        "Choose a PDF file",
        type="pdf",
        help="Upload the main PDF book that you want to organize"
    )
    
    if uploaded_file is not None and not SessionManager.get('pdf_uploaded'):
        handle_pdf_upload(uploaded_file)
    elif SessionManager.get('pdf_uploaded'):
        display_pdf_success()

def handle_pdf_upload(uploaded_file):
    """Handle PDF file upload and processing"""
    with st.spinner("Loading PDF..."):
        pdf_reader, total_pages = PDFHandler.load_pdf_info(uploaded_file)
        
        if pdf_reader and total_pages > 0:
            SessionManager.set('pdf_file', uploaded_file)
            SessionManager.set('total_pages', total_pages)
            SessionManager.set('pdf_uploaded', True)
            st.success(f"PDF loaded successfully! Total pages: {total_pages}")
            st.rerun()

def display_pdf_success():
    """Display success message for uploaded PDF"""
    pdf_file = SessionManager.get('pdf_file')
    total_pages = SessionManager.get('total_pages')
    
    if pdf_file:
        st.success(f"✅ PDF loaded: {pdf_file.name}")
        st.info(f"Total pages: {total_pages}")

def render_project_details_section():
    """Render project details input section"""
    if not SessionManager.get('pdf_uploaded'):
        return
    
    st.subheader("Step 2: Project Details")
    
    config = SessionManager.get('project_config', {})
    
    code = st.text_input(
        "Project Code",
        value=config.get('code', ''),
        placeholder="e.g., CS101",
        help="Short code identifier for the project"
    )
    
    book_name = st.text_input(
        "Book Name",
        value=config.get('book_name', ''),
        placeholder="e.g., Data Structures and Algorithms",
        help="Book name (will be kept as-is in folder names - no underscores added)"
    )
    
    if code and book_name:
        SessionManager.update_config({'code': code, 'book_name': book_name})
        display_folder_preview(code, book_name)

def display_folder_preview(code: str, book_name: str):
    """Display preview of folder naming convention"""
    preview_folders = FolderManager.get_folder_preview(code, book_name, 1)
    
    st.markdown("**Preview folder naming:**")
    preview_text = "\n".join(preview_folders[:3])  # Show first 3 as preview
    st.code(preview_text)

def render_parts_configuration_section():
    """Render parts configuration section"""
    config = SessionManager.get('project_config', {})
    
    if not (config.get('code') and config.get('book_name')):
        return
    
    st.subheader("Step 3: Parts Setup")
    
    num_parts = st.number_input(
        "Number of Parts",
        min_value=0,
        max_value=100,
        value=config.get('num_parts', 0),
        step=1,
        help="How many main parts does the book have?"
    )
    
    SessionManager.update_config({'num_parts': num_parts})
    
    if num_parts > 0:
        st.info(f"Will create {num_parts} part folders")