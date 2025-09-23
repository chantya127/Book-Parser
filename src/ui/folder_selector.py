# ui/folder_selector.py - Streamlit-only destination folder selector

import streamlit as st
import os
from pathlib import Path
from core.session_manager import SessionManager


def render_destination_folder_selector():
    """Render destination folder selector in sidebar - simplified to only project destination"""
    
    st.markdown("---")
    st.subheader("📁 Project Destination")
    
    # Project destination section
    current_project_dest = SessionManager.get_project_destination()
    
    if current_project_dest:
        folder_name = Path(current_project_dest).name
        st.info(f"Project Base: **{folder_name}**")
        
        if os.path.exists(current_project_dest):
            st.success("✅ Accessible")
        else:
            st.warning("⚠️ Not found")
            
        if st.button("🗑️ Clear Project Location", key="clear_project_destination"):
            SessionManager.set_project_destination('')
            st.session_state['project_destination_selected'] = False
            st.rerun()
    else:
        st.info("Using current directory")
    
    # Set project destination - fix double-click issue
    if st.button("📂 Set Project Location", key="set_project_destination"):
        st.session_state['show_project_browser'] = True
        st.session_state['folder_browser_active'] = True  # Set both flags immediately
        st.session_state['folder_browser_context'] = 'project'
        st.rerun()  # Force immediate rerun

def show_folder_browser_overlay():
    """Show folder browser overlay in main content area"""
    
    # This will be rendered in the main content area
    st.session_state['folder_browser_active'] = True



def render_folder_browser_in_main():
    """Render folder browser in main content area when active"""
    
    if not st.session_state.get('folder_browser_active', False):
        return False
    
    context = st.session_state.get('folder_browser_context', 'project')
    
    if context == 'page_assignment':
        st.markdown("## 📂 Select Page Extraction Destination")
        st.markdown("Choose where to extract pages from your PDF.")
    else:
        st.markdown("## 📂 Select Project Base Location")
        st.markdown("Your entire project folder will be created inside the selected location.")
    
    st.markdown("---")
    
    # Initialize browser path
    if 'browser_path' not in st.session_state:
        st.session_state['browser_path'] = str(Path.home().absolute())
    
    current_path = Path(st.session_state['browser_path']).absolute()
    
    # Current location display
    st.info(f"📍 Current location: {current_path}")
    
    # Navigation controls
    col1, col2, col3, col4 = st.columns([1, 1, 2, 1])
    
    with col1:
        if st.button("🏠 Home", key="nav_home"):
            st.session_state['browser_path'] = str(Path.home().absolute())
            st.rerun()
    
    with col2:
        if current_path.parent != current_path:
            if st.button("⬆️ Up", key="nav_up"):
                st.session_state['browser_path'] = str(current_path.parent.absolute())
                st.rerun()
    
    with col3:
        if context == 'page_assignment':
            button_text = "✅ SELECT FOR EXTRACTION"
        else:
            button_text = "✅ SET PROJECT LOCATION"
            
        if st.button(button_text, key="select_folder", type="primary"):
            selected_path = str(current_path.absolute())
            
            if context == 'page_assignment':
                # Store the selection for page assignment
                st.session_state['selected_page_destination'] = selected_path
                st.session_state['selected_page_destination_name'] = current_path.name
                st.success(f"✅ Extraction destination selected: {current_path.name}")
                st.session_state['show_folder_browser'] = False
            else:
                SessionManager.set_project_destination(selected_path)
                st.success(f"✅ Project location set: {current_path.name}")
                st.session_state['show_project_browser'] = False
            
            # Close browser
            st.session_state['folder_browser_active'] = False
            st.rerun()
    
    with col4:
        if st.button("❌ Cancel", key="cancel_browser"):
            st.session_state['folder_browser_active'] = False
            st.session_state['show_folder_browser'] = False
            st.session_state['show_project_browser'] = False
            st.rerun()
    
    # Quick access buttons
    st.markdown("**Quick Access:**")
    quick_folders = get_quick_access_folders()
    
    if quick_folders:
        cols = st.columns(len(quick_folders))
        for i, (name, path) in enumerate(quick_folders.items()):
            with cols[i]:
                if st.button(name, key=f"quick_nav_{i}"):
                    st.session_state['browser_path'] = path
                    st.rerun()
    
    st.markdown("---")
    
    # CRITICAL: This is the folder listing section that was missing
    try:
        folders = [item for item in current_path.iterdir() 
                  if item.is_dir() and not item.name.startswith('.')]
        folders.sort(key=lambda x: x.name.lower())
        
        if folders:
            st.markdown("**📁 Available Folders:**")
            
            # Display folders in a grid
            cols_per_row = 3
            for i in range(0, len(folders), cols_per_row):
                cols = st.columns(cols_per_row)
                
                for j, folder in enumerate(folders[i:i+cols_per_row]):
                    if j < len(cols):
                        with cols[j]:
                            folder_name = folder.name
                            display_name = folder_name[:15] + "..." if len(folder_name) > 15 else folder_name
                            
                            if st.button(f"📁 {display_name}", 
                                       key=f"folder_nav_{i}_{j}",
                                       help=f"Navigate to: {folder_name}"):
                                st.session_state['browser_path'] = str(folder.absolute())
                                st.rerun()
        else:
            st.info("📂 No subfolders found in this directory")
            
    except PermissionError:
        st.error("❌ Permission denied accessing this folder")
    except Exception as e:
        st.error(f"❌ Error reading folder: {str(e)}")
    
    return True

def get_quick_access_folders():
    """Get quick access folder shortcuts"""
    
    home = Path.home()
    folders = {
        "Desktop": str(home / "Desktop"),
        "Documents": str(home / "Documents"),
        "Downloads": str(home / "Downloads"),
        "Current": str(Path.cwd())
    }
    
    return {name: path for name, path in folders.items() if os.path.exists(path)}


def render_destination_quick_selector():
    """Quick destination selector for page assignment"""
    
    # Check if we should show the browser
    if st.button("📂 Browse for Folder", key="open_browser_btn", type="primary"):
        st.session_state['show_folder_browser'] = True
        st.session_state['folder_browser_active'] = True
        st.session_state['folder_browser_context'] = 'page_assignment'
        st.rerun()
    
    # Quick selection options
    st.markdown("**Or select quickly:**")
    
    quick_folders = get_quick_access_folders()
    
    for name, path in quick_folders.items():
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write(f"📁 {name}")
            st.caption(path)
        with col2:
            if st.button("Select", key=f"select_{name.replace(' ', '_')}"):
                return (path, Path(path).name)
    
    # Manual input
    st.markdown("**Or enter path manually:**")
    manual_path = st.text_input(
        "Folder path:",
        placeholder="Enter full path to destination folder",
        key="manual_path_input"
    )
    
    if manual_path.strip():
        path = Path(manual_path.strip())
        if st.button("Use This Path", key="use_manual_path"):
            return (str(path.absolute()), path.name)
    
    return ("", "")