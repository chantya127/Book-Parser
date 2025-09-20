import streamlit as st
from typing import Dict, List, Tuple
from core.session_manager import SessionManager
from core.pdf_handler import PDFExtractor
from core.folder_manager import FolderManager, ChapterManager
from pathlib import Path
import os

def render_page_assignment_page():
    """Render the page assignment and extraction page"""
    
    # Check prerequisites
    if not SessionManager.get('folder_structure_created'):
        render_prerequisites_warning()
        return
    
    st.subheader("📄 Page Assignment & Extraction")
    st.markdown("Assign page ranges to specific folders and extract them from your PDF.")
    
    # Main layout
    col1, col2 = st.columns([2, 1])
    
    with col1:
        render_assignment_interface()
    
    with col2:
        render_assignment_summary()

def render_prerequisites_warning():
    """Render warning when prerequisites are not met"""
    st.warning("⚠️ Please complete the previous steps first!")
    st.markdown("""
    **Required steps:**
    1. Upload PDF file
    2. Configure project details
    3. Create folder structure
    """)

def render_assignment_interface():
    """Render the main page assignment interface"""
    
    # Folder selection
    available_folders = get_available_folders()
    
    if not any(available_folders.values()):
        st.error("No folders available. Please create folder structure first.")
        return
    
    st.markdown("### 📂 Select Destination")
    
    folder_type = st.selectbox(
        "Folder Type",
        ["Default Folders", "Parts", "Create Custom Folder"],  # Added custom folder option
        help="Choose the type of folder to assign pages to"
    )
    
    if folder_type == "Default Folders":
        destination_info = render_default_folder_selection(available_folders['default'])
    elif folder_type == "Parts":
        destination_info = render_parts_selection_interface(available_folders)
    else:  # Create Custom Folder
        destination_info = render_custom_folder_creation(available_folders)
    
    if destination_info and destination_info[0]:  # Check if destination is selected
        render_page_range_input(destination_info)

def get_available_folders() -> Dict[str, List[Tuple[str, str]]]:
    """Get all available folders with (display_name, folder_id) tuples"""
    config = SessionManager.get('project_config', {})
    folder_metadata = SessionManager.get('folder_metadata', {})
    
    if not config.get('code') or not config.get('book_name'):
        return {'default': [], 'parts': [], 'chapters': {}, 'custom': [], 'all_for_custom': []}
    
    safe_code = FolderManager.sanitize_name(config['code'])
    book_name = config['book_name']  # Book name kept as is
    base_name = f"{safe_code}_{book_name}"
    
    folders = {
        'default': [],
        'parts': [],
        'chapters': {},  # Organized by part number
        'custom': [],
        'all_for_custom': []  # All folders available as parents for custom folders
    }
    
    # Default folders
    for folder in FolderManager.DEFAULT_FOLDERS:
        folder_name = f"{base_name}_{folder}"
        folders['default'].append((folder_name, folder_name))
        folders['all_for_custom'].append((f"Default → {folder}", folder_name))
    
    # Part folders
    num_parts = config.get('num_parts', 0)
    for i in range(1, num_parts + 1):
        folder_name = f"{base_name}_Part_{i}"
        folders['parts'].append((folder_name, folder_name))
        folders['all_for_custom'].append((f"Part {i}", folder_name))
        
        # Initialize chapters list for this part
        folders['chapters'][i] = []
    
    # Chapter folders organized by part
    for folder_id, metadata in folder_metadata.items():
        if metadata['type'] == 'chapter':
            part_num = metadata['parent_part']
            if part_num in folders['chapters']:
                chapter_display_name = metadata['display_name'].split(" → ")[-1]  # Get just the chapter part
                folders['chapters'][part_num].append((chapter_display_name, folder_id))
                folders['all_for_custom'].append((metadata['display_name'], folder_id))
        elif metadata['type'] == 'custom':
            # Add custom folders to the list
            folders['custom'].append((metadata['display_name'], folder_id))
            folders['all_for_custom'].append((metadata['display_name'], folder_id))
    
    return folders

def render_custom_folder_creation(available_folders: Dict) -> Tuple[str, str]:
    """Render interface for creating custom folders"""
    
    all_folders = available_folders['all_for_custom']
    
    if not all_folders:
        st.info("No folders available to create custom folders in.")
        return ("", "")
    
    st.markdown("**Create a custom folder inside an existing folder:**")
    
    # Step 1: Select parent folder
    parent_display_names = [folder[0] for folder in all_folders]
    selected_parent_index = st.selectbox(
        "Select Parent Folder",
        range(len(parent_display_names)),
        format_func=lambda x: parent_display_names[x],
        help="Choose the parent folder to create the custom folder in",
        key="custom_parent_selection"
    )
    
    if selected_parent_index is None:
        return ("", "")
    
    selected_parent = all_folders[selected_parent_index]
    parent_display, parent_id = selected_parent
    
    # Step 2: Enter custom folder name
    custom_folder_name = st.text_input(
        "Custom Folder Name",
        placeholder="e.g., Solutions, Exercises, Notes",
        help="Enter a name for your custom folder",
        key="custom_folder_name"
    )
    
    if custom_folder_name.strip():
        # Step 3: Create folder button
        if st.button("🏗️ Create Custom Folder", type="primary", key="create_custom_folder"):
            config = SessionManager.get('project_config', {})
            safe_code = FolderManager.sanitize_name(config['code'])
            book_name = config['book_name']  # Book name kept as is
            base_name = f"{safe_code}_{book_name}"
            
            # FIXED: Use consistent path resolution
            import os
            current_dir = Path.cwd()
            
            possible_paths = [
                Path(base_name),
                current_dir / base_name,
                Path.cwd() / base_name
            ]
            
            project_path = None
            for path in possible_paths:
                if path.exists():
                    project_path = path
                    break
            
            if not project_path:
                project_path = current_dir / base_name
                project_path.mkdir(parents=True, exist_ok=True)
            
            created_folder_path = FolderManager.create_custom_folder(
                project_path, base_name, parent_id, custom_folder_name
            )
            
            if created_folder_path:
                st.success(f"✅ Created custom folder: {custom_folder_name}")
                st.info(f"📂 Location: {created_folder_path}")
                st.rerun()  # Refresh to show the new folder in the list
            else:
                st.error("❌ Failed to create custom folder")
        
        # Show preview of what will be created
        st.markdown("---")
        st.markdown("**Preview:**")
        safe_folder_name = FolderManager.sanitize_name(custom_folder_name)
        config = SessionManager.get('project_config', {})
        safe_code = FolderManager.sanitize_name(config['code'])
        book_name = config['book_name']  # Book name kept as is
        base_name = f"{safe_code}_{book_name}"
        preview_name = f"{base_name}_{safe_folder_name}"
        st.caption(f"📁 Will create: `{parent_display} → {preview_name}`")
        
        return (f"{parent_display} → {preview_name}", f"preview_{parent_id}_{safe_folder_name}")
    
    return ("", "")

def render_default_folder_selection(default_folders: List[Tuple[str, str]]) -> Tuple[str, str]:
    """Render selection for default folders"""
    if not default_folders:
        st.info("No default folders available.")
        return ("", "")
    
    display_names = [folder[0] for folder in default_folders]
    selected_index = st.selectbox(
        "Select Default Folder",
        range(len(display_names)),
        format_func=lambda x: display_names[x],
        help="Choose the specific default folder to assign pages to"
    )
    
    return default_folders[selected_index] if selected_index is not None else ("", "")

def render_parts_selection_interface(available_folders: Dict) -> Tuple[str, str]:
    """Render the parts selection interface with sub-options"""
    
    parts_folders = available_folders['parts']
    chapters_by_part = available_folders['chapters']
    custom_folders = available_folders.get('custom', [])
    
    if not parts_folders:
        st.info("No parts available.")
        return ("", "")
    
    # Step 1: Select Part
    part_display_names = [folder[0] for folder in parts_folders]
    selected_part_index = st.selectbox(
        "Select Part",
        range(len(part_display_names)),
        format_func=lambda x: part_display_names[x],
        help="Choose which part to work with"
    )
    
    if selected_part_index is None:
        return ("", "")
    
    selected_part = parts_folders[selected_part_index]
    part_number = selected_part_index + 1  # Parts are 1-indexed
    
    # Step 2: Choose destination within part
    st.markdown("---")
    
    options = ["Directly in Part folder", "In a Chapter within this Part"]
    
    # Add custom folders option if there are custom folders in this part
    part_custom_folders = [cf for cf in custom_folders if f"Part {part_number}" in cf[0]]
    if part_custom_folders:
        options.append("In a Custom folder within this Part")
    
    destination_option = st.radio(
        f"Where to place pages in Part {part_number}?",
        options,
        help="Choose whether to place pages directly in the part folder, in a specific chapter, or in a custom folder"
    )
    
    if destination_option == "Directly in Part folder":
        return selected_part
    
    elif destination_option == "In a Chapter within this Part":
        chapters_in_part = chapters_by_part.get(part_number, [])
        
        if not chapters_in_part:
            st.warning(f"No chapters found in Part {part_number}. Please create chapters first or choose 'Directly in Part folder'.")
            return ("", "")
        
        chapter_display_names = [chapter[0] for chapter in chapters_in_part]
        selected_chapter_index = st.selectbox(
            f"Select Chapter in Part {part_number}",
            range(len(chapter_display_names)),
            format_func=lambda x: chapter_display_names[x],
            help="Choose the specific chapter to assign pages to"
        )
        
        if selected_chapter_index is not None:
            selected_chapter = chapters_in_part[selected_chapter_index]
            chapter_display = f"Part {part_number} → {selected_chapter[0]}"
            return (chapter_display, selected_chapter[1])
        
        return ("", "")
    
    elif destination_option == "In a Custom folder within this Part":
        if not part_custom_folders:
            st.warning(f"No custom folders found in Part {part_number}.")
            return ("", "")
        
        custom_display_names = [cf[0] for cf in part_custom_folders]
        selected_custom_index = st.selectbox(
            f"Select Custom Folder in Part {part_number}",
            range(len(custom_display_names)),
            format_func=lambda x: custom_display_names[x],
            help="Choose the specific custom folder to assign pages to"
        )
        
        if selected_custom_index is not None:
            selected_custom = part_custom_folders[selected_custom_index]
            return selected_custom
        
        return ("", "")

def render_page_range_input(destination_info: Tuple[str, str]):
    """Render page range input and extraction controls"""
    
    display_name, folder_id = destination_info
    
    # Skip if this is a preview (not yet created)
    if folder_id.startswith("preview_"):
        st.info("Please create the custom folder first before assigning pages.")
        return
    
    st.markdown("### 📄 Page Range Assignment")
    st.markdown(f"**Selected Destination:** `{display_name}`")
    
    total_pages = SessionManager.get('total_pages', 0)
    
    # Page range input with examples
    st.markdown("**Enter page ranges:**")
    page_ranges_text = st.text_area(
        "Page Ranges",
        placeholder=f"Examples:\n• Single pages: 1, 5, 10\n• Ranges: 1-5, 10-15\n• Mixed: 1-3, 7, 12-20\n\nTotal pages available: {total_pages}",
        help=f"Specify pages to extract (1-{total_pages})",
        height=120,
        key="page_ranges_input"
    )
    
    # Show buttons - make them primary (red) from the start
    col1, col2 = st.columns(2)
    
    with col1:
        preview_disabled = not page_ranges_text.strip()
        if st.button("📋 Preview Assignment", type="primary", disabled=preview_disabled, key="preview_btn"):
            if page_ranges_text.strip():
                page_ranges = [r.strip() for r in page_ranges_text.split(',') if r.strip()]
                render_assignment_preview(display_name, page_ranges, total_pages)
    
    with col2:
        extract_disabled = not page_ranges_text.strip()
        if st.button("🚀 Extract Pages", type="primary", disabled=extract_disabled, key="extract_btn"):
            if page_ranges_text.strip():
                page_ranges = [r.strip() for r in page_ranges_text.split(',') if r.strip()]
                execute_page_extraction(destination_info, page_ranges, total_pages)
    
    # Show preview of page ranges if text is entered
    if page_ranges_text.strip():
        page_ranges = [r.strip() for r in page_ranges_text.split(',') if r.strip()]
        preview = PDFExtractor.preview_page_extraction(page_ranges, total_pages)
        
        if "No valid pages" in preview:
            st.error(preview)
        else:
            st.info(preview)

def render_assignment_preview(display_name: str, page_ranges: List[str], total_pages: int):
    """Render preview of page assignment"""
    
    pages = PDFExtractor.parse_page_ranges(page_ranges, total_pages)
    
    if pages:
        st.success(f"Ready to extract {len(pages)} pages to: `{display_name}`")
        
        with st.expander("📋 Detailed Preview", expanded=True):
            st.markdown("**Files that will be created:**")
            safe_folder_name = PDFExtractor.sanitize_filename(display_name.split(" → ")[-1])
            
            # Show first 10 files as preview
            preview_count = min(10, len(pages))
            for i in range(1, preview_count + 1):  # Sequential numbering from 1
                file_name = f"{safe_folder_name}_Page_{i}.pdf"
                st.write(f"📄 {file_name}")
            
            if len(pages) > preview_count:
                st.write(f"... and {len(pages) - preview_count} more files")
                
            st.markdown(f"**Destination:** `{display_name}`")
    else:
        st.error("No valid pages found in the specified ranges")

def execute_page_extraction(destination_info: Tuple[str, str], page_ranges: List[str], total_pages: int):
    """Execute the page extraction process with proper path resolution"""
    
    display_name, folder_id = destination_info
    config = SessionManager.get('project_config', {})
    folder_metadata = SessionManager.get('folder_metadata', {})
    
    if not config.get('code') or not config.get('book_name'):
        st.error("Project not configured properly. Please complete project setup.")
        return
    
    # Determine actual folder path and naming base
    if folder_id in folder_metadata:
        # Chapter or custom folder - use stored path and naming base
        metadata = folder_metadata[folder_id]
        folder_path = Path(metadata['actual_path'])
        file_naming_base = metadata['naming_base']
    else:
        # Default or part folder - direct path
        safe_code = FolderManager.sanitize_name(config['code'])
        book_name = config['book_name']  # Book name kept as is
        base_name = f"{safe_code}_{book_name}"
        folder_path = Path(base_name) / folder_id
        file_naming_base = folder_id
    
    # Ensure the folder exists
    if not folder_path.exists():
        st.error(f"Destination folder does not exist: {folder_path}")
        return
    
    # Progress bar
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        # Execute extraction
        status_text.text(f"Extracting pages to {display_name}...")
        progress_bar.progress(20)
        
        success, created_files, error_msg = PDFExtractor.extract_pages_to_folder(
            page_ranges, str(folder_path), file_naming_base, total_pages
        )
        
        progress_bar.progress(100)
        
        if success and created_files:
            status_text.text("Extraction completed successfully!")
            st.success(f"✅ Successfully extracted {len(created_files)} pages!")
            
            # Update extraction history
            extraction_history = SessionManager.get('extraction_history', [])
            extraction_record = {
                'destination': display_name,
                'destination_path': str(folder_path),
                'pages_extracted': len(created_files),
                'page_ranges': page_ranges,
                'files_created': created_files,
                'folder_id': folder_id
            }
            extraction_history.append(extraction_record)
            SessionManager.set('extraction_history', extraction_history)
            
            # Show created files
            with st.expander("📁 View Created Files", expanded=True):
                for file_path in created_files[:10]:  # Show first 10
                    st.write(f"📄 {os.path.basename(file_path)}")
                if len(created_files) > 10:
                    st.write(f"... and {len(created_files) - 10} more files")
            
            # Show folder location
            st.info(f"📂 Files saved to: `{folder_path.absolute()}`")
            
        elif success and not created_files:
            st.warning("⚠️ No pages were extracted. Please check your page ranges.")
        else:
            st.error(f"❌ Extraction failed: {error_msg}")
    
    except Exception as e:
        st.error(f"❌ Extraction error: {str(e)}")
    finally:
        progress_bar.empty()
        status_text.empty()

def render_assignment_summary():
    """Render summary of page assignments and extractions"""
    
    st.subheader("📊 Assignment Summary")
    
    extraction_history = SessionManager.get('extraction_history', [])
    
    if not extraction_history:
        st.info("No extractions completed yet")
        return
    
    # Statistics
    total_extractions = len(extraction_history)
    total_pages_extracted = sum(record['pages_extracted'] for record in extraction_history)
    
    st.metric("Total Extractions", total_extractions)
    st.metric("Pages Extracted", total_pages_extracted)
    
    # Recent extractions
    st.markdown("**Recent Extractions:**")
    recent_extractions = list(reversed(extraction_history[-5:]))  # Show last 5
    
    for i, record in enumerate(recent_extractions):
        with st.expander(f"📂 {record['destination']} ({record['pages_extracted']} pages)", 
                        expanded=i == 0):
            st.write(f"**Page Ranges:** {', '.join(record['page_ranges'])}")
            st.write(f"**Files Created:** {len(record['files_created'])}")
            st.write(f"**Location:** {record.get('destination_path', 'Unknown')}")
            
            # Show sample files
            if record['files_created']:
                st.write("**Sample Files:**")
                sample_files = record['files_created'][:3]
                for file_path in sample_files:
                    st.write(f"📄 {os.path.basename(file_path)}")
                if len(record['files_created']) > 3:
                    st.write(f"... and {len(record['files_created']) - 3} more")
    
    # Clear history option
    if st.button("🗑️ Clear History", help="Clear extraction history (files remain on disk)"):
        SessionManager.set('extraction_history', [])
        st.rerun()