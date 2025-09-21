# src/ui/custom_folder_management.py
import streamlit as st
from typing import Dict, List, Optional
from pathlib import Path

from core.session_manager import SessionManager

def render_custom_folder_management_page():
    """Render the custom folder management page"""
    
    # Import at function level to avoid circular imports
    from core.session_manager import SessionManager
    
    # Check prerequisites
    if not SessionManager.get('folder_structure_created'):
        render_prerequisites_warning()
        return
    
    st.subheader("🗂️ Custom Folder Management")
    st.markdown("Create custom folders within your existing project structure.")
    
    # Main layout
    col1, col2 = st.columns([2, 1])
    
    with col1:
        render_custom_folder_creation_interface()
    
    with col2:
        render_custom_folders_summary()

def render_prerequisites_warning():
    """Render warning when prerequisites are not met"""
    st.warning("⚠️ Please complete the project setup first!")
    st.markdown("""
    **Required steps:**
    1. Upload PDF file
    2. Configure project details
    3. Create folder structure
    """)

def render_custom_folder_creation_interface():
    """Render the custom folder creation interface"""
    
    st.markdown("### 📂 Create New Custom Folder")
    
    # Check if we just created a folder to show success message
    if st.session_state.get('custom_folder_just_created'):
        folder_name = st.session_state.get('last_created_folder_name', 'Unknown')
        folder_path = st.session_state.get('last_created_folder_path', 'Unknown')
        st.success(f"✅ Successfully created custom folder: '{folder_name}'")
        st.info(f"📂 Location: {folder_path}")
        # Clear the flag
        st.session_state['custom_folder_just_created'] = False
    
    # Step 1: Parent folder selection
    st.markdown("**Step 1: Select Parent Location**")
    
    parent_method = st.radio(
        "Choose parent location method:",
        ["Select from project folders", "Enter custom path"],
        help="Choose how to specify the parent folder",
        key="parent_method_radio"
    )
    
    selected_parent_path = None
    
    if parent_method == "Select from project folders":
        selected_parent_path = render_project_folder_dropdown()
    else:
        selected_parent_path = render_custom_path_input()
    
    # Step 2: Folder name input (only show if parent is selected)
    if selected_parent_path:
        st.markdown("---")
        st.markdown("**Step 2: Enter Folder Name**")
        
        # Show selected parent info
        parent_name = Path(selected_parent_path).name
        st.info(f"📁 Parent folder: **{parent_name}**")
        
        # Use session state to track the input value with unique key
        folder_input_key = f"custom_folder_name_{hash(selected_parent_path) % 10000}"
        
        custom_folder_name = st.text_input(
            "Custom Folder Name",
            value="",  # Always start with empty value
            placeholder="e.g., Solutions, Exercises, Notes, References",
            help="Enter the exact name for your custom folder (no modifications will be made)",
            key=folder_input_key
        )
        
        # Step 3: Preview and create (only show if name is entered)
        if custom_folder_name.strip():
            st.markdown("---")
            st.markdown("**Step 3: Preview and Create**")
            
            # Show preview - keep name exactly as entered
            final_folder_name = custom_folder_name.strip()
            
            st.markdown("**Preview:**")
            st.code(f"📁 {parent_name} → {final_folder_name}")
            
            # Create button with unique key
            create_button_key = f"create_folder_{hash(selected_parent_path + final_folder_name) % 10000}"
            if st.button("🏗️ Create Custom Folder", type="primary", key=create_button_key):
                success = create_custom_folder_simple(selected_parent_path, final_folder_name)
                if success:
                    # Set flags for success message and refresh
                    st.session_state['custom_folder_just_created'] = True
                    st.rerun()

def render_project_folder_dropdown() -> Optional[str]:
    """Render dropdown for project folder selection"""
    
    # Import at function level to avoid circular imports
    from core.session_manager import SessionManager
    from core.folder_manager import FolderManager
    
    config = SessionManager.get('project_config', {})
    if not config.get('code') or not config.get('book_name'):
        st.error("Project configuration missing.")
        return None
    
    safe_code = FolderManager.sanitize_name(config['code'])
    book_name = config['book_name']
    base_name = f"{safe_code}_{book_name}"
    
    # Get project path
    project_path = get_project_path(base_name)
    
    if not project_path.exists():
        st.error("Project folder not found. Please create folder structure first.")
        return None
    
    # Get fresh folder list every time to avoid duplicates
    available_folders = get_all_project_folders_fresh(project_path)
    
    if not available_folders:
        st.info("No folders found in the project.")
        return None
    
    # Create folder dropdown options
    folder_options = []
    folder_paths = []
    
    # Add project root as an option
    folder_options.append(f"📂 {project_path.name} (Project Root)")
    folder_paths.append(str(project_path.absolute()))
    
    # Add all subfolders with proper hierarchy display
    for folder_info in available_folders:
        folder_path, relative_path, depth = folder_info
        indent = "  " * depth
        folder_icon = "📁" if depth == 0 else "└─"
        folder_name = Path(folder_path).name
        display_name = f"{indent}{folder_icon} {folder_name}"
        folder_options.append(display_name)
        folder_paths.append(folder_path)
    
    # Use selectbox with dynamic key based on folder count
    selector_key = f"parent_folder_selector_{len(folder_options)}_{hash(str(folder_options)) % 10000}"
    selected_index = st.selectbox(
        "Choose parent folder:",
        range(len(folder_options)),
        format_func=lambda x: folder_options[x],
        help="Select the folder where you want to create the custom folder",
        key=selector_key
    )
    
    if selected_index is not None:
        return folder_paths[selected_index]
    
    return None

def get_all_project_folders_fresh(project_path: Path) -> List[tuple]:
    """Get all folders within the project directory - fresh scan every time"""
    
    folders = []
    
    try:
        # Get all directories, excluding the project root itself
        for item in project_path.rglob('*'):
            if item.is_dir() and item != project_path:
                relative_path = item.relative_to(project_path)
                depth = len(relative_path.parts) - 1
                folders.append((str(item.absolute()), str(relative_path), depth))
        
        # Sort by depth first, then by path for consistent ordering
        folders.sort(key=lambda x: (x[2], x[1]))
        
        # Remove duplicates if any
        seen_paths = set()
        unique_folders = []
        for folder_path, rel_path, depth in folders:
            if folder_path not in seen_paths:
                seen_paths.add(folder_path)
                unique_folders.append((folder_path, rel_path, depth))
        
        return unique_folders
    
    except Exception as e:
        st.error(f"Error scanning folders: {str(e)}")
        return []

def render_custom_path_input() -> Optional[str]:
    """Render custom path input"""
    
    custom_path = st.text_input(
        "Parent Folder Path",
        placeholder="e.g., C:\\Users\\YourName\\Documents\\MyFolder or /home/user/MyFolder",
        help="Enter the complete path where you want to create the custom folder",
        key="custom_path_input"
    )
    
    if custom_path.strip():
        path = Path(custom_path.strip())
        
        if path.exists() and path.is_dir():
            st.success(f"✅ Valid folder: {path.name}")
            return str(path.absolute())
        elif not path.exists():
            st.warning("⚠️ Folder doesn't exist. It will be created during custom folder creation.")
            return str(path.absolute())
        else:
            st.error("❌ Invalid path or not a directory")
    
    return None

def create_custom_folder_simple(parent_path: str, folder_name: str) -> bool:
    """Create a custom folder with parent folder prefix + custom name"""
    
    try:
        parent_folder = Path(parent_path)
        parent_folder_name = parent_folder.name
        final_folder_name = f"{parent_folder_name}_{folder_name}"
        custom_folder_path = parent_folder / final_folder_name
        
        # Check if folder already exists
        if custom_folder_path.exists():
            st.error(f"❌ Folder '{final_folder_name}' already exists in '{parent_folder_name}'. Please choose a different name.")
            return False
        
        with st.spinner(f"Creating custom folder '{final_folder_name}'..."):
            # Ensure parent folder exists
            parent_folder.mkdir(parents=True, exist_ok=True)
            
            # Create the custom folder with parent prefix + custom name
            custom_folder_path.mkdir(exist_ok=True)
            
            # Add to metadata
            add_folder_to_metadata(
                str(custom_folder_path.absolute()), 
                final_folder_name, 
                parent_path,
                folder_name  # Original name without prefix
            )
            
            # Store success information for next render
            st.session_state['last_created_folder_name'] = final_folder_name
            st.session_state['last_created_folder_path'] = str(custom_folder_path.absolute())
            
            return True
    
    except PermissionError:
        st.error(f"❌ Permission denied. Cannot create folder in '{parent_folder.name}'. Please check folder permissions.")
        return False
    except FileExistsError:
        st.error(f"❌ Folder '{final_folder_name}' already exists. Please choose a different name.")
        return False
    except OSError as e:
        if "Invalid argument" in str(e) or "cannot create" in str(e).lower():
            st.error(f"❌ Invalid folder name '{folder_name}'. Please avoid special characters and try a simpler name.")
        else:
            st.error(f"❌ System error creating folder: {str(e)}")
        return False
    except Exception as e:
        st.error(f"❌ Unexpected error creating custom folder: {str(e)}")
        return False

def add_folder_to_metadata(folder_path: str, folder_name: str, parent_path: str, original_name: str = None):
    """Add folder to metadata tracking"""
    
    # Import at function level to avoid circular imports
    from core.session_manager import SessionManager
    
    folder_metadata = SessionManager.get('folder_metadata', {})
    import random
    custom_folder_id = f"custom_{random.randint(10000, 99999)}"
    
    parent_name = Path(parent_path).name
    original_display_name = original_name or folder_name
    
    folder_metadata[custom_folder_id] = {
        'display_name': f"{parent_name} → {original_display_name}",
        'actual_path': folder_path,
        'type': 'custom',
        'parent_path': parent_path,
        'folder_name': folder_name,  # Full name with prefix
        'naming_base': folder_name   # Use full name for file naming
    }
    
    SessionManager.set('folder_metadata', folder_metadata)
    
    # Update created folders list
    current_folders = SessionManager.get('created_folders', [])
    if folder_path not in current_folders:
        current_folders.append(folder_path)
        SessionManager.set('created_folders', current_folders)

def get_project_path(base_name: str) -> Path:
    """Get the project path using consistent resolution"""
    current_dir = Path.cwd()
    
    possible_paths = [
        Path(base_name),
        current_dir / base_name,
        Path.cwd() / base_name
    ]
    
    for path in possible_paths:
        if path.exists():
            return path
    
    # Create if doesn't exist
    project_path = current_dir / base_name
    project_path.mkdir(parents=True, exist_ok=True)
    return project_path

def get_all_project_folders(project_path: Path) -> List[tuple]:
    """Get all folders within the project directory"""
    
    folders = []
    
    try:
        for item in project_path.rglob('*'):
            if item.is_dir() and item != project_path:
                relative_path = item.relative_to(project_path)
                depth = len(relative_path.parts) - 1
                folders.append((str(item.absolute()), str(relative_path), depth))
        
        folders.sort(key=lambda x: (x[2], x[1]))
        return folders
    
    except Exception:
        return []

def render_custom_folders_summary():
    """Render summary of created custom folders"""
    
    st.subheader("🗂️ Custom Folders")
    
    folder_metadata = SessionManager.get('folder_metadata', {})
    
    # Filter custom folders
    custom_folders = [
        (folder_id, metadata) for folder_id, metadata in folder_metadata.items()
        if metadata.get('type') == 'custom'
    ]
    
    if not custom_folders:
        st.info("No custom folders created yet")
        return
    
    # Statistics
    st.metric("Custom Folders Created", len(custom_folders))
    
    # List of custom folders
    st.markdown("**Created Custom Folders:**")
    
    for folder_id, metadata in custom_folders:
        folder_name = metadata.get('folder_name', 'Unknown')
        with st.expander(f"📁 {folder_name}", expanded=False):
            st.write(f"**Display Name:** {metadata.get('display_name', 'N/A')}")
            st.write(f"**Location:** {metadata.get('actual_path', 'N/A')}")
            st.write(f"**Naming Base:** {metadata.get('naming_base', 'N/A')}")
            
            # Use folder_id for unique key instead of folder_name
            if st.button(
                "🗑️ Delete Folder", 
                key=f"delete_custom_{folder_id}", 
                help="Delete this custom folder and its contents"
            ):
                delete_custom_folder(folder_id, metadata)

def delete_custom_folder(folder_id: str, metadata: Dict):
    """Delete a custom folder"""
    
    try:
        folder_path = Path(metadata['actual_path'])
        folder_name = metadata.get('folder_name', 'Unknown')
        
        if not folder_path.exists():
            st.warning(f"⚠️ Folder '{folder_name}' not found on filesystem. Removing from list.")
        else:
            import shutil
            shutil.rmtree(folder_path)
            st.success(f"✅ Deleted folder: '{folder_name}'")
        
        # Remove from metadata using folder_id
        folder_metadata = SessionManager.get('folder_metadata', {})
        if folder_id in folder_metadata:
            del folder_metadata[folder_id]
            SessionManager.set('folder_metadata', folder_metadata)
        
        # Remove from created folders list
        current_folders = SessionManager.get('created_folders', [])
        folder_path_str = str(folder_path.absolute())
        if folder_path_str in current_folders:
            current_folders.remove(folder_path_str)
            SessionManager.set('created_folders', current_folders)
        
        st.rerun()
        
    except PermissionError:
        st.error(f"❌ Permission denied. Cannot delete folder '{folder_name}'. Please check folder permissions.")
    except Exception as e:
        st.error(f"❌ Error deleting folder '{folder_name}': {str(e)}")