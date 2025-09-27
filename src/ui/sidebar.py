# src/ui/sidebar.py - Modified to use lazy imports
import streamlit as st
import json
import os
from pathlib import Path
from datetime import datetime
from core.session_manager import SessionManager
from core.pdf_handler import PDFHandler
from core.folder_manager import FolderManager
from ui.font_selector import render_font_case_changer

def render_sidebar():
    """Render sidebar with project configuration"""
    
    with st.sidebar:
        st.header("🔧 Project Configuration")
        
        # Project management section
        render_project_management_section()
        
        render_pdf_upload_section()
        render_project_details_section()
        render_custom_parts_configuration_section()
        
        # NEW: Add font case changer
        render_font_case_changer()

        from ui.folder_selector import render_destination_folder_selector

        render_destination_folder_selector()

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
    
    # Load existing project dropdown with delete options
    if existing_projects:
        st.markdown("**Existing Projects:**")
        
        # Show projects in a more compact format with delete buttons
        for project in existing_projects[:10]:  # Show only recent 10 projects
            col_name, col_load, col_delete = st.columns([3, 1, 1])
            
            with col_name:
                # Truncate long display names for better layout
                display_name = project['display_name']
                if len(display_name) > 40:
                    display_name = display_name[:37] + "..."
                st.write(f"📋 {display_name}")
            
            with col_load:
                if st.button("📂", key=f"load_{project['filename']}", 
                           help=f"Load project: {project['display_name']}"):
                    load_project(project['filename'])
                    st.success(f"✅ Loaded: {project['display_name'][:30]}...")
                    st.rerun()
            
            with col_delete:
                if st.button("❌", key=f"delete_{project['filename']}", 
                           help=f"Delete project: {project['display_name']}"):
                    # Add confirmation dialog
                    if st.session_state.get(f'confirm_delete_{project["filename"]}'):
                        delete_project(project['filename'])
                        st.success(f"✅ Deleted: {project['display_name'][:30]}...")
                        # Clear confirmation state
                        if f'confirm_delete_{project["filename"]}' in st.session_state:
                            del st.session_state[f'confirm_delete_{project["filename"]}']
                        st.rerun()
                    else:
                        # Set confirmation state
                        st.session_state[f'confirm_delete_{project["filename"]}'] = True
                        st.warning(f"Click ❌ again to confirm deletion of: {project['display_name'][:30]}...")
                        st.rerun()
        
        # Show count if there are more projects
        if len(existing_projects) > 10:
            st.caption(f"Showing 10 of {len(existing_projects)} projects")
        
        # Option to clear all confirmation states
        if any(key.startswith('confirm_delete_') for key in st.session_state.keys()):
            if st.button("🔄 Cancel All Deletions", type="secondary"):
                # Clear all confirmation states
                keys_to_remove = [key for key in st.session_state.keys() if key.startswith('confirm_delete_')]
                for key in keys_to_remove:
                    del st.session_state[key]
                st.rerun()
    
    # Show current project status
    current_project = SessionManager.get('current_project_name')
    if current_project:
        display_current = format_project_display_name(current_project)
        if len(display_current) > 50:
            display_current = display_current[:47] + "..."
        st.info(f"📋 Current: **{display_current}**")
    else:
        st.info("📋 No project loaded")
    
    st.markdown("---")

def clear_all_delete_confirmations():
    """Clear all delete confirmation states"""
    keys_to_remove = [key for key in st.session_state.keys() if key.startswith('confirm_delete_')]
    for key in keys_to_remove:
        del st.session_state[key]

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
        # Get current font case
        current_font_case = SessionManager.get_font_case()
        
        # Collect all project data including destinations
        project_data = {
            'project_config': config,
            'pdf_uploaded': SessionManager.get('pdf_uploaded', False),
            'pdf_file_name': SessionManager.get('pdf_file').name if SessionManager.get('pdf_file') else None,
            'total_pages': SessionManager.get('total_pages', 0),
            'folder_structure_created': SessionManager.get('folder_structure_created', False),
            'created_folders': SessionManager.get('created_folders', []),
            'chapters_config': SessionManager.get('chapters_config', {}),
            'standalone_chapters': SessionManager.get('standalone_chapters', []),  # ADD THIS LINE
            'chapters_created': SessionManager.get('chapters_created', False),
            'page_assignments': SessionManager.get('page_assignments', {}),  # ADD THIS LINE
            'folder_metadata': SessionManager.get('folder_metadata', {}),
            'unique_chapter_counter': SessionManager.get('unique_chapter_counter', 0),  # ADD THIS LINE
            'numbering_systems': SessionManager.get('numbering_systems', {}),
            'chapter_suffixes': SessionManager.get('chapter_suffixes', {}),
            'extraction_history': SessionManager.get('extraction_history', []),
            'custom_parts': SessionManager.get('custom_parts', {}),
            'font_case_selected': True,
            'selected_font_case': current_font_case,  # Use current font case
            'project_destination_folder': SessionManager.get('project_destination_folder', ''),
            'project_destination_selected': SessionManager.get('project_destination_selected', False),
            'total_pages_generated': SessionManager.get('total_pages_generated', 0),  # ADD THIS LINE
            'pages_calculated_timestamp': SessionManager.get('pages_calculated_timestamp', None),  # ADD THIS LINE
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
    """Handle PDF file upload and processing with improved large file handling"""
    file_size_mb = len(uploaded_file.getvalue()) / (1024 * 1024)
    
    with st.spinner(f"Loading PDF ({file_size_mb:.1f}MB)... This may take a moment for large files."):
        # Show progress for large files
        if file_size_mb > 100:
            progress_bar = st.progress(0)
            progress_bar.progress(25, "Reading PDF content...")
            
        pdf_reader, total_pages = PDFHandler.load_pdf_info(uploaded_file)
        
        if file_size_mb > 100:
            progress_bar.progress(75, "Processing PDF structure...")
        
        if pdf_reader and total_pages > 0:
            SessionManager.set('pdf_file', uploaded_file)
            SessionManager.set('total_pages', total_pages)
            SessionManager.set('pdf_uploaded', True)
            
            # Clear expected PDF name if it was set
            if SessionManager.get('expected_pdf_name'):
                SessionManager.set('expected_pdf_name', None)
            
            if file_size_mb > 100:
                progress_bar.progress(100, "PDF loaded successfully!")
                progress_bar.empty()
            
            st.success(f"PDF loaded successfully! Total pages: {total_pages}")
            
            # Show memory usage warning for very large files
            if file_size_mb > 200:
                st.warning(f"⚠️ Large file ({file_size_mb:.1f}MB) loaded. Page extraction may take longer than usual.")
            
            st.rerun()
        else:
            if file_size_mb > 100:
                progress_bar.empty()
            st.error("Failed to load PDF. Please check if the file is valid and not corrupted.")

def display_pdf_success():
    """Display success message for uploaded PDF"""
    pdf_file = SessionManager.get('pdf_file')
    total_pages = SessionManager.get('total_pages')
    
    if pdf_file:
        st.success(f"✅ PDF loaded: {pdf_file.name}")
        st.info(f"Total pages: {total_pages}")



def render_project_details_section():
    """Render project details input section with font formatting"""
    if not SessionManager.get('pdf_uploaded') and not SessionManager.get('expected_pdf_name'):
        return
    
    st.subheader("Step 2: Project Details")
    
    config = SessionManager.get('project_config', {})
    
    # Get font case from session state first, then from config as fallback
    font_case = st.session_state.get('selected_font_case') or config.get('selected_font_case', 'First Capital (Sentence case)')
    
    # Ensure font case is always in session state
    if 'selected_font_case' not in st.session_state and font_case:
        st.session_state['selected_font_case'] = font_case
    
    # Show current font formatting
    st.caption(f"Font formatting: {font_case}")
    
    code = st.text_input(
        "Project Code",
        value=config.get('original_code', config.get('code', '')),
        placeholder="e.g., CS101",
        help=f"Short code identifier (will be formatted as: {font_case})"
    )
    
    book_name = st.text_input(
        "Book Name",
        value=config.get('original_book_name', config.get('book_name', '')),
        placeholder="e.g., Data Structures and Algorithms",
        help=f"Book name (will be formatted as: {font_case}, no underscores added)"
    )
    
    if code and book_name:
        # Apply font formatting properly
        from core.text_formatter import TextFormatter
        
        formatted_code = TextFormatter.format_text(code, font_case)
        formatted_book_name = TextFormatter.format_text(book_name, font_case)
        
        # Store values without triggering rerun
        config_updates = {
            'code': formatted_code, 
            'book_name': formatted_book_name,
            'original_code': code,
            'original_book_name': book_name,
            'selected_font_case': font_case  # Always preserve font case
        }
        
        # Only update if values have changed to prevent unnecessary reruns
        current_config = SessionManager.get('project_config', {})
        if (current_config.get('code') != formatted_code or 
            current_config.get('book_name') != formatted_book_name or
            current_config.get('selected_font_case') != font_case):
            
            SessionManager.update_config(config_updates)
        
        # Show preview with proper formatting
        safe_code = FolderManager.sanitize_name(formatted_code)
        preview_name = f"{safe_code}_{formatted_book_name}"
        if preview_name != f"{code}_{book_name}":
            st.info(f"Preview: `{preview_name}`")


def render_custom_parts_configuration_section():
    """Render custom parts configuration section with individual part creation"""
    config = SessionManager.get('project_config', {})
    
    if not (config.get('code') and config.get('book_name')):
        return
    
    st.subheader("Step 3: Custom Parts Setup")
    st.markdown("Create custom-named parts for your book (e.g., 'India', 'Iran', 'History', etc.)")
    
    # Get existing custom parts
    custom_parts = SessionManager.get('custom_parts', {})
    
    # Add new custom part section
    st.markdown("**Add New Part:**")
    
    # Show current font case for reference
    font_case = SessionManager.get_font_case()
    st.caption(f"Font formatting: {font_case}")
    
    # Check if we just added a part to clear the input
    input_value = ""
    if st.session_state.get('part_just_added'):
        st.session_state['part_just_added'] = False
        input_value = ""
    else:
        input_value = st.session_state.get('part_input_value', "")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        new_part_name = st.text_input(
            "Part Name",
            value=input_value,
            placeholder="e.g., India, Iran, History, Mathematics",
            help=f"Enter a custom name for this part (will be formatted as: {font_case})",
            key="new_part_name_input"
        )
        
        # Store the current value
        st.session_state['part_input_value'] = new_part_name
    
    with col2:
        if st.button("➕ Add Part", type="primary", disabled=not new_part_name.strip()):
            if new_part_name.strip():
                add_custom_part(new_part_name.strip(), custom_parts)
                # Set flag to clear input on next render
                st.session_state['part_just_added'] = True
                st.session_state['part_input_value'] = ""
                st.rerun()
    
    # Display existing custom parts (READ-ONLY)
    if custom_parts:
        st.markdown("**Current Parts:**")
        st.info("💡 Use Chapter Management tab to modify or delete parts after folder structure is created.")
        
        # Display parts without delete functionality
        for part_id, part_info in custom_parts.items():
            formatted_name = part_info.get('name', part_info.get('display_name', 'Unknown'))
            original_name = part_info.get('original_name', '')
            
            st.write(f"📂 **{formatted_name}**")
            if original_name and original_name != formatted_name:
                st.caption(f"Original: {original_name}")
        
        # Update the total count in config for compatibility
        SessionManager.update_config({'num_parts': len(custom_parts)})
        
        st.info(f"Total parts configured: {len(custom_parts)}")
    else:
        st.info("No custom parts created yet. Add parts above to organize your book content.")
        # Reset num_parts to 0 if no custom parts
        SessionManager.update_config({'num_parts': 0})


def add_custom_part(part_name: str, custom_parts: dict):
    """Add a new custom part with font formatting"""
    from core.text_formatter import TextFormatter
    
    font_case = SessionManager.get_font_case()
    formatted_part_name = TextFormatter.format_text(part_name, font_case)
    
    # Generate unique ID for the part using formatted name
    base_id = formatted_part_name.lower().replace(' ', '_').replace('-', '_')
    part_id = f"part_{len(custom_parts) + 1}_{base_id}"
    
    # Ensure unique ID
    counter = 1
    original_id = part_id
    while part_id in custom_parts:
        part_id = f"{original_id}_{counter}"
        counter += 1
    
    # Add to custom parts
    custom_parts[part_id] = {
        'name': formatted_part_name,
        'display_name': formatted_part_name,
        'original_name': part_name,
        'created_timestamp': datetime.now().isoformat()
    }
    
    SessionManager.set('custom_parts', custom_parts)
    st.success(f"Added part: '{formatted_part_name}'")


def delete_custom_part(part_id: str, custom_parts: dict):
    """Delete a custom part"""
    if part_id in custom_parts:
        part_name = custom_parts[part_id]['name']
        del custom_parts[part_id]
        SessionManager.set('custom_parts', custom_parts)
        st.success(f"✅ Deleted part: '{part_name}'")