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
        ["Default Folders", "Parts", "Chapters"],
        help="Choose the type of folder to assign pages to"
    )
    
    destination_info = render_folder_selection(folder_type, available_folders)
    
    if destination_info and destination_info[0]:  # Check if destination is selected
        render_page_range_input(destination_info)

def get_available_folders() -> Dict[str, List[Tuple[str, str]]]:
    """Get all available folders with (display_name, folder_id) tuples"""
    config = SessionManager.get('project_config', {})
    folder_metadata = SessionManager.get('folder_metadata', {})
    
    if not config.get('code') or not config.get('book_name'):
        return {'default': [], 'parts': [], 'chapters': []}
    
    safe_code = FolderManager.sanitize_name(config['code'])
    safe_book_name = FolderManager.sanitize_name(config['book_name'])
    base_name = f"{safe_code}_{safe_book_name}"
    
    folders = {
        'default': [],
        'parts': [],
        'chapters': []
    }
    
    # Default folders
    for folder in FolderManager.DEFAULT_FOLDERS:
        folder_name = f"{base_name}_{folder}"
        folders['default'].append((folder_name, folder_name))
    
    # Part folders
    num_parts = config.get('num_parts', 0)
    for i in range(1, num_parts + 1):
        folder_name = f"{base_name}_part_{i}"
        folders['parts'].append((folder_name, folder_name))
    
    # Chapter folders from metadata
    for folder_id, metadata in folder_metadata.items():
        if metadata['type'] == 'chapter':
            folders['chapters'].append((metadata['display_name'], folder_id))
    
    return folders

def render_folder_selection(folder_type: str, available_folders: Dict[str, List[Tuple[str, str]]]) -> Tuple[str, str]:
    """Render folder selection based on type and return (display_name, folder_id)"""
    
    folder_mapping = {
        "Default Folders": "default",
        "Parts": "parts", 
        "Chapters": "chapters"
    }
    
    folder_key = folder_mapping[folder_type]
    folders = available_folders[folder_key]
    
    if not folders:
        st.info(f"No {folder_type.lower()} available.")
        return ("", "")
    
    # Create selectbox with display names but track IDs
    display_names = [folder[0] for folder in folders]
    selected_index = st.selectbox(
        f"Select {folder_type[:-1]}",
        range(len(display_names)),
        format_func=lambda x: display_names[x],
        help=f"Choose the specific {folder_type.lower()[:-1]} to assign pages to"
    )
    
    return folders[selected_index] if selected_index is not None else ("", "")

def render_page_range_input(destination_info: Tuple[str, str]):
    """Render page range input and extraction controls"""
    
    display_name, folder_id = destination_info
    
    st.markdown("### 📄 Page Range Assignment")
    
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
    
    # Show buttons even when text area is empty, but disable extract if no ranges
    col1, col2 = st.columns(2)
    
    with col1:
        preview_disabled = not page_ranges_text.strip()
        if st.button("📋 Preview Assignment", type="secondary", disabled=preview_disabled):
            if page_ranges_text.strip():
                page_ranges = [r.strip() for r in page_ranges_text.split(',') if r.strip()]
                render_assignment_preview(display_name, page_ranges, total_pages)
    
    with col2:
        extract_disabled = not page_ranges_text.strip()
        if st.button("🚀 Extract Pages", type="primary", disabled=extract_disabled):
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
            safe_folder_name = PDFExtractor.sanitize_filename(display_name)
            
            # Show first 10 files as preview
            preview_count = min(10, len(pages))
            for page in pages[:preview_count]:
                file_name = f"{safe_folder_name}_page_{page}.pdf"
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
        # Chapter folder - use stored path and naming base
        metadata = folder_metadata[folder_id]
        folder_path = Path(metadata['actual_path'])
        file_naming_base = metadata['naming_base']
    else:
        # Default or part folder - direct path
        safe_code = FolderManager.sanitize_name(config['code'])
        safe_book_name = FolderManager.sanitize_name(config['book_name'])
        base_name = f"{safe_code}_{safe_book_name}"
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