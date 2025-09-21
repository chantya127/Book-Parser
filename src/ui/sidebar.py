# src/ui/sidebar.py
import streamlit as st
import json
import os
from pathlib import Path
from datetime import datetime
from core.session_manager import SessionManager
from core.pdf_handler import PDFHandler
from core.folder_manager import FolderManager

def render_sidebar():
    """Render sidebar with project configuration"""
    
    with st.sidebar:
        st.header("🔧 Project Configuration")
        
        # Project management section
        render_project_management_section()
        
        render_pdf_upload_section()
        render_project_details_section()
        render_parts_configuration_section()

def render_project_management_section():
    """Render project management controls"""
    st.subheader("📁 Project Management")
    
    # Load existing projects list
    existing_projects = get_existing_projects()
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🆕 New Project", type="secondary"):
            create_new_project()
            st.rerun()
    
    with col2:
        if st.button("💾 Save Project", type="secondary"):
            save_current_project()
    
    # Load existing project dropdown
    if existing_projects:
        st.markdown("**Load Existing Project:**")
        
        # Create dropdown options with display names
        project_options = [""] + [p['display_name'] for p in existing_projects]
        project_filenames = [""] + [p['filename'] for p in existing_projects]
        
        selected_index = st.selectbox(
            "Select Project",
            range(len(project_options)),
            format_func=lambda x: "Choose a project..." if x == 0 else project_options[x],
            key="project_load_select"
        )
        
        if selected_index > 0:
            selected_filename = project_filenames[selected_index]
            selected_display = project_options[selected_index]
            
            col_load, col_delete = st.columns(2)
            
            with col_load:
                if st.button("📂 Load", key="load_project_btn"):
                    load_project(selected_filename)
                    st.success(f"✅ Loaded project: {selected_display}")
                    st.rerun()
            
            with col_delete:
                if st.button("🗑️ Delete", key="delete_project_btn"):
                    delete_project(selected_filename)
                    st.success(f"✅ Deleted project: {selected_display}")
                    st.rerun()
    
    # Show current project status
    current_project = SessionManager.get('current_project_name')
    if current_project:
        # Format current project name for display
        display_current = format_project_display_name(current_project)
        st.info(f"📋 Current: **{display_current}**")
    else:
        st.info("📋 No project loaded")
    
    st.markdown("---")

def get_projects_dir():
    """Get or create projects directory"""
    projects_dir = Path("saved_projects")
    projects_dir.mkdir(exist_ok=True)
    return projects_dir

def get_existing_projects():
    """Get list of existing project files with formatted display"""
    projects_dir = get_projects_dir()
    project_files = list(projects_dir.glob("*.json"))
    
    project_list = []
    for f in project_files:
        try:
            # Parse the filename to extract info
            parts = f.stem.split('_')
            
            # Find the timestamp part (starts with 4-digit year)
            timestamp_start = None
            for i, part in enumerate(parts):
                if len(part) >= 4 and part[:4].isdigit():
                    timestamp_start = i
                    break
            
            if timestamp_start:
                # Extract project info and timestamp
                project_info = '_'.join(parts[:timestamp_start])
                timestamp_str = '_'.join(parts[timestamp_start:])
                
                # Parse timestamp for display
                try:
                    timestamp = datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")
                    display_name = f"{project_info} ({timestamp.strftime('%Y-%m-%d %H:%M:%S')})"
                except ValueError:
                    # Fallback if timestamp parsing fails
                    display_name = f.stem
            else:
                # Old format or no timestamp
                display_name = f.stem
            
            project_list.append({
                'filename': f.stem,
                'display_name': display_name,
                'modified': f.stat().st_mtime
            })
            
        except Exception:
            # Fallback for any parsing issues
            project_list.append({
                'filename': f.stem,
                'display_name': f.stem,
                'modified': f.stat().st_mtime
            })
    
    # Sort by modification time (newest first)
    project_list.sort(key=lambda x: x['modified'], reverse=True)
    
    return project_list

def create_new_project():
    """Create a new project by clearing current session"""
    # Clear all session state except essential UI state
    keys_to_preserve = ['current_step']  # Add any UI state you want to preserve
    
    new_session = {}
    for key in keys_to_preserve:
        if key in st.session_state:
            new_session[key] = st.session_state[key]
    
    st.session_state.clear()
    
    # Restore preserved keys
    for key, value in new_session.items():
        st.session_state[key] = value
    
    # Initialize fresh session
    SessionManager.initialize_session()
    
    # Clear current project name
    SessionManager.set('current_project_name', None)

def format_project_display_name(project_name):
    """Format project name for display with timestamp parsing"""
    try:
        parts = project_name.split('_')
        
        # Find the timestamp part (starts with 4-digit year)
        timestamp_start = None
        for i, part in enumerate(parts):
            if len(part) >= 4 and part[:4].isdigit():
                timestamp_start = i
                break
        
        if timestamp_start:
            project_info = '_'.join(parts[:timestamp_start])
            timestamp_str = '_'.join(parts[timestamp_start:])
            
            try:
                timestamp = datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")
                return f"{project_info} ({timestamp.strftime('%Y-%m-%d %H:%M:%S')})"
            except ValueError:
                pass
        
        return project_name
        
    except Exception:
        return project_name

def save_current_project():
    """Save current project to file with timestamp"""
    config = SessionManager.get('project_config', {})
    
    if not config.get('code') or not config.get('book_name'):
        st.error("❌ Cannot save: Project code and book name are required")
        return
    
    # Create filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_name = f"{config['code']}_{config['book_name']}"
    project_name = f"{base_name}_{timestamp}"
    
    projects_dir = get_projects_dir()
    project_file = projects_dir / f"{project_name}.json"
    
    try:
        # Collect all project data
        project_data = {
            'project_config': SessionManager.get('project_config', {}),
            'pdf_uploaded': SessionManager.get('pdf_uploaded', False),
            'pdf_file_name': SessionManager.get('pdf_file').name if SessionManager.get('pdf_file') else None,
            'total_pages': SessionManager.get('total_pages', 0),
            'folder_structure_created': SessionManager.get('folder_structure_created', False),
            'created_folders': SessionManager.get('created_folders', []),
            'chapters_config': SessionManager.get('chapters_config', {}),
            'chapters_created': SessionManager.get('chapters_created', False),
            'folder_metadata': SessionManager.get('folder_metadata', {}),
            'numbering_systems': SessionManager.get('numbering_systems', {}),
            'extraction_history': SessionManager.get('extraction_history', []),
            'saved_timestamp': timestamp,
            'saved_datetime': datetime.now().isoformat()
        }
        
        # Save to JSON file
        with open(project_file, 'w') as f:
            json.dump(project_data, f, indent=2)
        
        # Update current project name
        SessionManager.set('current_project_name', project_name)
        
        # Format display name for success message
        display_name = format_project_display_name(project_name)
        st.success(f"✅ Project saved as: {display_name}")
        
    except Exception as e:
        st.error(f"❌ Error saving project: {str(e)}")

def load_project(project_name):
    """Load project from file"""
    projects_dir = get_projects_dir()
    project_file = projects_dir / f"{project_name}.json"
    
    if not project_file.exists():
        st.error(f"❌ Project file not found: {project_name}")
        return
    
    try:
        with open(project_file, 'r') as f:
            project_data = json.load(f)
        
        # Clear current session and load project data
        st.session_state.clear()
        SessionManager.initialize_session()
        
        # Restore project data
        for key, value in project_data.items():
            if key == 'pdf_file_name':
                # Handle PDF file separately - user will need to re-upload
                if value:
                    SessionManager.set('expected_pdf_name', value)
            else:
                SessionManager.set(key, value)
        
        # Set current project name
        SessionManager.set('current_project_name', project_name)
        
        # If PDF was previously uploaded, show message to re-upload
        if project_data.get('pdf_uploaded') and project_data.get('pdf_file_name'):
            st.warning(f"⚠️ Please re-upload your PDF file: {project_data['pdf_file_name']}")
            # Reset PDF-related flags until file is re-uploaded
            SessionManager.set('pdf_uploaded', False)
            SessionManager.set('pdf_file', None)
        
    except Exception as e:
        st.error(f"❌ Error loading project: {str(e)}")

def delete_project(project_name):
    """Delete project file"""
    projects_dir = get_projects_dir()
    project_file = projects_dir / f"{project_name}.json"
    
    try:
        if project_file.exists():
            os.remove(project_file)
        
        # If this was the current project, clear it
        if SessionManager.get('current_project_name') == project_name:
            SessionManager.set('current_project_name', None)
            
    except Exception as e:
        st.error(f"❌ Error deleting project: {str(e)}")

def render_pdf_upload_section():
    """Render PDF upload section"""
    st.subheader("Step 1: Upload PDF")
    
    # Show expected PDF name if loading a saved project
    expected_pdf = SessionManager.get('expected_pdf_name')
    if expected_pdf:
        st.info(f"📄 Expected PDF: {expected_pdf}")
    
    uploaded_file = st.file_uploader(
        "Choose a PDF file",
        type="pdf",
        help="Upload the main PDF book that you want to organize"
    )
    
    if uploaded_file is not None:
        # Check if this matches expected PDF name
        if expected_pdf and uploaded_file.name != expected_pdf:
            st.warning(f"⚠️ Uploaded PDF name '{uploaded_file.name}' doesn't match expected '{expected_pdf}'. This may cause issues.")
        
        if not SessionManager.get('pdf_uploaded'):
            handle_pdf_upload(uploaded_file)
        else:
            # Allow re-uploading different PDF
            if st.button("🔄 Use This PDF Instead"):
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
            
            # Clear expected PDF name if it was set
            if SessionManager.get('expected_pdf_name'):
                SessionManager.set('expected_pdf_name', None)
            
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
    if not SessionManager.get('pdf_uploaded') and not SessionManager.get('expected_pdf_name'):
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
        help="Book name (will be kept as-is in folder names)"
    )
    
    if code and book_name:
        SessionManager.update_config({'code': code, 'book_name': book_name})

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