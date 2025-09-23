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
    3. **Configure Custom Parts**: Create custom-named parts (e.g., 'India', 'Iran', 'History')
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
        
        # Check if font case is selected before showing folder creation
        if SessionManager.get('font_case_selected'):
            render_folder_creation_button(config)
        else:
            st.info("Please select font formatting in the sidebar first.")
    else:
        st.warning("⚠️ Please complete the project configuration in the sidebar")


def is_project_configured(config: dict) -> bool:
    """Check if project is properly configured"""
    return bool(config.get('code') and config.get('book_name'))

def display_project_info(config: dict):
    """Display current project information"""
    pdf_file = SessionManager.get('pdf_file')
    total_pages = SessionManager.get('total_pages')
    custom_parts = SessionManager.get('custom_parts', {})
    
    if pdf_file:
        st.write(f"**Project:** {config['code']}_{config['book_name']}")
        st.write(f"**PDF:** {pdf_file.name}")
        st.write(f"**Total Pages:** {total_pages}")
        st.write(f"**Custom Parts:** {len(custom_parts)} parts configured")
        
        # Show part names if any exist
        if custom_parts:
            part_names = [part_info['name'] for part_info in custom_parts.values()]
            st.write(f"**Part Names:** {', '.join(part_names)}")

def render_folder_creation_button(config: dict):
    """Render folder creation interface with default folder selection"""
    if SessionManager.get('folder_structure_created'):
        st.success("✅ Folder structure already created!")
        
        # Show created folders
        created_folders = SessionManager.get('created_folders', [])
        with st.expander("📁 View Created Folders"):
            for folder in created_folders:
                st.write(f"📂 {folder}")
    else:
        render_default_folder_selection(config)


def render_default_folder_selection(config: dict):
    """Render default folder selection interface"""
    st.markdown("### 📂 Select Default Folders to Create")
    st.markdown("Choose which default folders you want to include in your project structure:")
    
    # Get available default folder options
    folder_options = FolderManager.get_default_folder_options()
    
    # Create checkboxes for each default folder
    col1, col2 = st.columns(2)
    selected_folders = []
    
    for i, folder_option in enumerate(folder_options):
        folder_name = folder_option['name']
        folder_desc = folder_option['description']
        
        # Alternate between columns
        target_col = col1 if i % 2 == 0 else col2
        
        with target_col:
            # Pre-select common folders
            default_selected = folder_name in ['prologue', 'index', 'epilogue']
            
            if st.checkbox(
                f"**{folder_name.title()}**",
                value=default_selected,
                key=f"default_folder_{folder_name}",
                help=folder_desc
            ):
                selected_folders.append(folder_name)
    
    # Show preview of selected folders
    if selected_folders:
        st.markdown("**Selected folders to create:**")
        safe_code = FolderManager.sanitize_name(config['code'])
        book_name = config['book_name']
        base_name = f"{safe_code}_{book_name}"
        
        # Apply font formatting to preview
        from core.text_formatter import TextFormatter
        font_case = SessionManager.get_font_case()
        
        for folder in selected_folders:
            formatted_folder = TextFormatter.format_folder_name(folder, font_case)
            preview_name = f"{base_name}_{formatted_folder}"
            st.write(f"📁 `{preview_name}`")
        
        st.markdown("---")
        
        # Create button
        col_create, col_skip = st.columns(2)
        
        with col_create:
            if st.button("🏗️ Create Folder Structure", type="primary"):
                create_folder_structure_with_selection(config, selected_folders)
        
        with col_skip:
            if st.button("⏭️ Skip Default Folders", type="secondary"):
                create_folder_structure_with_selection(config, [])
    else:
        st.info("No default folders selected. You can still create the project structure without default folders.")
        if st.button("🏗️ Create Project Structure Only", type="primary"):
            create_folder_structure_with_selection(config, [])


def create_folder_structure_with_selection(config: dict, selected_folders: List[str]):
    """Create the folder structure with selected default folders"""
    with st.spinner("Creating folder structure..."):
        code = config['code']
        book_name = config['book_name']
        custom_parts = SessionManager.get('custom_parts', {})
        
        project_path, created_folders = FolderManager.create_project_structure(
            code, book_name, selected_folders
        )
        
        if project_path:
            # Create custom parts folders if specified
            if custom_parts:
                safe_code = FolderManager.sanitize_name(code)
                base_name = f"{safe_code}_{book_name}"
                custom_parts_folders = FolderManager.create_custom_parts_folders(
                    project_path, base_name, custom_parts
                )
                created_folders.extend(custom_parts_folders)
            
            SessionManager.set('folder_structure_created', True)
            SessionManager.set('created_folders', created_folders)
            
            display_creation_success_with_selection(created_folders, custom_parts, selected_folders)
        else:
            st.error("Failed to create folder structure")


def display_creation_success_with_selection(created_folders: List[str], custom_parts: dict, selected_folders: List[str]):
    """Display success message with created folders including selection info"""
    st.success("✅ Folder structure created successfully!")
    
    # Show summary
    default_count = len(selected_folders)
    custom_parts_count = len(custom_parts)
    total_folders = len(created_folders)
    
    st.info(f"Created {total_folders} folders: {default_count} default folders + {custom_parts_count} custom parts")
    
    if selected_folders:
        st.markdown("**Created default folders:**")
        for folder in selected_folders:
            st.write(f"📁 {folder.title()}")
    
    if custom_parts:
        st.markdown("**Created custom parts:**")
        for part_info in custom_parts.values():
            st.write(f"🎯 {part_info['name']}")
    
    st.markdown("**All created folders:**")
    for folder in created_folders:
        folder_name = folder.split('/')[-1] if '/' in folder else folder.split('\\')[-1]
        if any(part_info['name'] in folder_name for part_info in custom_parts.values()):
            st.write(f"🎯 {folder}")  # Custom part folders
        else:
            st.write(f"📁 {folder}")  # Default folders

def create_folder_structure(config: dict):
    """Create the folder structure with custom parts"""
    with st.spinner("Creating folder structure..."):
        code = config['code']
        book_name = config['book_name']
        custom_parts = SessionManager.get('custom_parts', {})
        
        project_path, created_folders = FolderManager.create_project_structure(code, book_name)
        
        if project_path:
            # Create custom parts folders if specified
            if custom_parts:
                safe_code = FolderManager.sanitize_name(code)
                base_name = f"{safe_code}_{book_name}"
                custom_parts_folders = FolderManager.create_custom_parts_folders(
                    project_path, base_name, custom_parts
                )
                created_folders.extend(custom_parts_folders)
            
            SessionManager.set('folder_structure_created', True)
            SessionManager.set('created_folders', created_folders)
            
            display_creation_success(created_folders, custom_parts)
        else:
            st.error("Failed to create folder structure")

def display_creation_success(created_folders: List[str], custom_parts: dict):
    """Display success message with created folders"""
    st.success("✅ Folder structure created successfully!")
    
    # Show summary
    default_count = len(FolderManager.DEFAULT_FOLDERS)
    custom_parts_count = len(custom_parts)
    total_folders = len(created_folders)
    
    st.info(f"Created {total_folders} folders: {default_count} default folders + {custom_parts_count} custom parts")
    
    st.markdown("**Created folders:**")
    for folder in created_folders:
        folder_name = folder.split('/')[-1] if '/' in folder else folder.split('\\')[-1]
        if any(part_info['name'] in folder_name for part_info in custom_parts.values()):
            st.write(f"🎯 {folder}")  # Custom part folders
        else:
            st.write(f"📁 {folder}")  # Default folders

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
    custom_parts = SessionManager.get('custom_parts', {})
    
    st.metric("PDF Pages", total_pages)
    st.metric("Project Code", config.get('code', 'Not set'))
    st.metric("Custom Parts", len(custom_parts))
    
    # Chapter statistics
    total_chapters = sum(len(chapters) for chapters in chapters_config.values())
    if total_chapters > 0:
        st.metric("Total Chapters", total_chapters)
    
    if SessionManager.get('folder_structure_created'):
        created_folders = SessionManager.get('created_folders', [])
        st.metric("Folders Created", len(created_folders))
    
    # Show custom part names
    if custom_parts:
        st.markdown("**Custom Parts:**")
        for part_info in custom_parts.values():
            st.write(f"🎯 {part_info['name']}")