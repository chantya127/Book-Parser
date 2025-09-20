# src/ui/main_content.py
import streamlit as st
from typing import List
from core.session_manager import SessionManager
from core.folder_manager import FolderManager

def render_main_content():
    """Render main content area"""
    col1, col2 = st.columns([2, 1])
    
    with col1:
        render_main_section()
    
    with col2:
        render_stats_section()

def render_main_section():
    """Render main section content"""
    if not SessionManager.get('pdf_uploaded'):
        render_welcome_message()
    else:
        render_project_summary()

def render_welcome_message():
    """Render welcome message when no PDF is uploaded"""
    st.info("👈 Please upload a PDF file to get started")
    st.markdown("""
    ### How to use this tool:
    
    1. **Upload PDF**: Select your main book PDF file
    2. **Project Setup**: Enter project code and book name
    3. **Configure Parts**: Specify how many parts your book has
    4. **Create Folders**: Generate the folder structure
    5. **Setup Chapters**: Configure chapters within parts (optional)
    6. **Assign Pages**: Move page ranges to specific folders
    """)

def render_project_summary():
    """Render project summary and folder creation"""
    st.subheader("📋 Project Summary")
    
    config = SessionManager.get('project_config', {})
    
    if is_project_configured(config):
        display_project_info(config)
        render_folder_creation_button(config)
    else:
        st.warning("⚠️ Please complete the project configuration in the sidebar")

def is_project_configured(config: dict) -> bool:
    """Check if project is properly configured"""
    return bool(config.get('code') and config.get('book_name'))

def display_project_info(config: dict):
    """Display current project information"""
    pdf_file = SessionManager.get('pdf_file')
    total_pages = SessionManager.get('total_pages')
    
    if pdf_file:
        st.write(f"**Project:** {config['code']}_{config['book_name']}")
        st.write(f"**PDF:** {pdf_file.name}")
        st.write(f"**Total Pages:** {total_pages}")
        st.write(f"**Parts:** {config.get('num_parts', 0)}")

def render_folder_creation_button(config: dict):
    """Render folder creation button and handle creation"""
    if SessionManager.get('folder_structure_created'):
        st.success("✅ Folder structure already created!")
        
        # Show created folders
        created_folders = SessionManager.get('created_folders', [])
        with st.expander("📁 View Created Folders"):
            for folder in created_folders:
                st.write(f"📂 {folder}")
    else:
        if st.button("🏗️ Create Folder Structure", type="primary"):
            create_folder_structure(config)

def create_folder_structure(config: dict):
    """Create the folder structure"""
    with st.spinner("Creating folder structure..."):
        code = config['code']
        book_name = config['book_name']
        num_parts = config.get('num_parts', 0)
        
        project_path, created_folders = FolderManager.create_project_structure(code, book_name)
        
        if project_path:
            # Create parts folders if specified
            if num_parts > 0:
                safe_code = FolderManager.sanitize_name(code)
                safe_book_name = FolderManager.sanitize_name(book_name)
                base_name = f"{safe_code}_{safe_book_name}"
                parts_folders = FolderManager.create_parts_folders(project_path, base_name, num_parts)
                created_folders.extend(parts_folders)
            
            SessionManager.set('folder_structure_created', True)
            SessionManager.set('created_folders', created_folders)
            
            display_creation_success(created_folders)
        else:
            st.error("Failed to create folder structure")

def display_creation_success(created_folders: List[str]):
    """Display success message with created folders"""
    st.success("✅ Folder structure created successfully!")
    st.markdown("**Created folders:**")
    for folder in created_folders:
        st.write(f"📁 {folder}")

def render_stats_section():
    """Render statistics section"""
    st.subheader("📊 Quick Stats")
    
    if SessionManager.get('pdf_uploaded'):
        display_project_stats()
    else:
        st.info("Upload PDF to see stats")

def display_project_stats():
    """Display project statistics"""
    total_pages = SessionManager.get('total_pages')
    config = SessionManager.get('project_config', {})
    chapters_config = SessionManager.get('chapters_config', {})
    
    st.metric("PDF Pages", total_pages)
    st.metric("Project Code", config.get('code', 'Not set'))
    st.metric("Parts Planned", config.get('num_parts', 0))
    
    # Chapter statistics
    total_chapters = sum(len(chapters) for chapters in chapters_config.values())
    if total_chapters > 0:
        st.metric("Total Chapters", total_chapters)
    
    if SessionManager.get('folder_structure_created'):
        created_folders = SessionManager.get('created_folders', [])
        st.metric("Folders Created", len(created_folders))