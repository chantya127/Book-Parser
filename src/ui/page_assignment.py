import streamlit as st
from typing import Dict, List, Tuple, Optional
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
    
    # Check if extraction just completed
    if st.session_state.get('extraction_just_completed'):
        extraction_info = st.session_state.get('last_extraction_info', {})
        st.success(f"✅ Successfully extracted {extraction_info.get('pages_count', 0)} pages!")
        st.info(f"📂 Files saved to: `{extraction_info.get('destination', 'Unknown')}`")
        # Clear the flag
        st.session_state['extraction_just_completed'] = False
    
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
    
    st.markdown("### 📂 Select Destination")
    
    # Single unified destination selection approach
    destination_mode = st.radio(
        "Choose destination method:",
        ["Select from project folders", "Browse for any folder"],
        help="Choose how to specify where pages should be extracted",
        key="destination_mode_radio"
    )
    
    if destination_mode == "Select from project folders":
        destination_info = render_project_folder_selection()
    else:
        destination_info = render_system_folder_browser()
    
    if destination_info and destination_info[0]:
        render_page_range_input(destination_info)

def render_project_folder_selection() -> Tuple[str, str]:
    """Render project folder selection with browse interface"""
    
    config = SessionManager.get('project_config', {})
    if not config.get('code') or not config.get('book_name'):
        st.error("Project configuration missing.")
        return ("", "")
    
    safe_code = FolderManager.sanitize_name(config['code'])
    book_name = config['book_name']
    base_name = f"{safe_code}_{book_name}"
    
    # Get project path
    project_path = get_project_path(base_name)
    
    if not project_path.exists():
        st.error("Project folder not found. Please create folder structure first.")
        return ("", "")
    
    st.markdown("**Browse project folders:**")
    
    # Get all folders in the project including metadata
    available_folders = get_project_folders_with_metadata(project_path)
    
    if not available_folders:
        st.info("No folders found in the project.")
        return ("", "")
    
    # Create folder browser interface
    folder_options = []
    folder_info_list = []
    
    for folder_info in available_folders:
        display_name, folder_path, folder_type, metadata = folder_info
        folder_options.append(display_name)
        folder_info_list.append((folder_path, metadata))
    
    # Use selectbox for folder selection with unique key
    selected_index = st.selectbox(
        "Choose destination folder:",
        range(len(folder_options)),
        format_func=lambda x: folder_options[x],
        help="Select the folder where you want to extract pages",
        key=f"page_dest_folder_{len(folder_options)}_{hash(str(folder_options)) % 10000}"
    )
    
    if selected_index is not None:
        selected_folder_path, selected_metadata = folder_info_list[selected_index]
        folder_name = selected_metadata.get('naming_base') if selected_metadata else Path(selected_folder_path).name
        
        # NEW FEATURE: Check if selected folder is a Part folder and show additional options
        selected_folder_display = folder_options[selected_index]
        if "📂" in selected_folder_display and "_Part_" in selected_folder_path:
            return render_part_folder_options(selected_folder_path, folder_name, selected_folder_display)
        
        return (selected_folder_path, folder_name)
    
    return ("", "")

def render_part_folder_options(part_folder_path: str, part_folder_name: str, part_display_name: str) -> Tuple[str, str]:
    """Render options when a Part folder is selected"""
    
    st.markdown("---")
    st.markdown("**📖 Part Folder Selected - Choose Destination:**")
    st.info(f"Selected: {part_display_name}")
    
    # Extract part number from folder path
    part_number = None
    try:
        if "_Part_" in part_folder_path:
            part_number = int(Path(part_folder_path).name.split("_Part_")[-1])
    except (ValueError, IndexError):
        pass
    
    # Option selection
    part_destination_option = st.radio(
        "Where do you want to extract pages?",
        ["📂 Directly into the Part folder", "📖 Into a specific chapter within this Part"],
        help="Choose whether to put pages directly in the Part folder or in a specific chapter",
        key=f"part_option_{part_number}"
    )
    
    if part_destination_option == "📂 Directly into the Part folder":
        # Return the part folder itself
        return (part_folder_path, part_folder_name)
    
    else:  # Into a specific chapter
        if part_number is None:
            st.error("Could not determine part number from folder path.")
            return ("", "")
        
        # Get chapters for this part
        chapters_info = get_chapters_for_part(part_number)
        
        if not chapters_info:
            st.warning(f"No chapters found in Part {part_number}. Create chapters first or choose direct insertion.")
            return ("", "")
        
        # Chapter selection dropdown
        chapter_options = [f"📖 {info['display_name']}" for info in chapters_info]
        
        selected_chapter_index = st.selectbox(
            f"Select chapter in Part {part_number}:",
            range(len(chapter_options)),
            format_func=lambda x: chapter_options[x],
            help="Choose which chapter to extract pages into",
            key=f"chapter_select_part_{part_number}_{len(chapters_info)}"
        )
        
        if selected_chapter_index is not None:
            selected_chapter_info = chapters_info[selected_chapter_index]
            return (selected_chapter_info['folder_path'], selected_chapter_info['naming_base'])
    
    return ("", "")

def get_chapters_for_part(part_number: int) -> List[Dict]:
    """Get all chapters for a specific part from metadata"""
    
    folder_metadata = SessionManager.get('folder_metadata', {})
    chapters_info = []
    
    for folder_id, metadata in folder_metadata.items():
        if (metadata.get('type') == 'chapter' and 
            metadata.get('parent_part') == part_number):
            
            # Create display name from folder name
            folder_name = metadata.get('folder_name', '')
            chapter_display = folder_name.replace(f"_Part_{part_number}_Chapter_", "Chapter ")
            
            chapters_info.append({
                'folder_id': folder_id,
                'display_name': chapter_display,
                'folder_path': metadata.get('actual_path'),
                'naming_base': metadata.get('naming_base'),
                'chapter_number': metadata.get('chapter_number', ''),
                'chapter_name': metadata.get('chapter_name', '')
            })
    
    # Sort chapters by number if possible
    def sort_key(chapter):
        try:
            # Try to extract number for sorting
            chapter_num = chapter.get('chapter_number', '')
            if chapter_num.isdigit():
                return (0, int(chapter_num))  # Numeric chapters first
            elif chapter_num.startswith('null_'):
                return (1, int(chapter_num.split('_')[-1]))  # null chapters second
            else:
                return (2, chapter_num)  # Other chapters last
        except (ValueError, AttributeError):
            return (3, chapter.get('display_name', ''))
    
    chapters_info.sort(key=sort_key)
    return chapters_info

def render_system_folder_browser() -> Tuple[str, str]:
    """Render system-wide folder browser with manual path input"""
    
    st.markdown("**Specify any folder on your system:**")
    
    # Get initial value (empty if extraction was just completed)
    initial_path = "" if st.session_state.get('extraction_just_completed') else ""
    
    # Direct path input with unique key
    path_input_key = f"custom_folder_path_{hash(str(st.session_state.get('last_extraction_info', {}))) % 10000}"
    custom_folder_path = st.text_input(
        "Destination Folder Path",
        value=initial_path,
        placeholder="e.g., C:\\Users\\YourName\\Documents\\MyFolder or /home/user/MyFolder",
        help="Enter the complete path where you want to extract pages",
        key=path_input_key
    )
    
    if custom_folder_path.strip():
        folder_path = Path(custom_folder_path.strip())
        
        # Validate path
        if folder_path.exists() and folder_path.is_dir():
            st.success(f"✅ Valid folder: {folder_path.absolute()}")
            return (str(folder_path.absolute()), folder_path.name)
        elif not folder_path.exists():
            st.warning("⚠️ Folder doesn't exist. It will be created during extraction.")
            return (str(folder_path.absolute()), folder_path.name)
        else:
            st.error("❌ Invalid path or not a directory")
    
    return ("", "")

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

def get_project_folders_with_metadata(project_path: Path) -> List[tuple]:
    """
    Get all folders within the project directory with metadata
    Returns list of (display_name, folder_path, folder_type, metadata) tuples
    """
    
    folders = []
    folder_metadata = SessionManager.get('folder_metadata', {})
    
    try:
        # Add project root
        folders.append((
            f"📂 {project_path.name} (Project Root)",
            str(project_path.absolute()),
            "root",
            {"naming_base": project_path.name}
        ))
        
        # Get all subfolders
        for item in project_path.rglob('*'):
            if item.is_dir() and item != project_path:
                relative_path = item.relative_to(project_path)
                depth = len(relative_path.parts) - 1
                
                # Check if this folder has metadata
                folder_metadata_info = None
                for folder_id, metadata in folder_metadata.items():
                    if metadata.get('actual_path') == str(item.absolute()):
                        folder_metadata_info = metadata
                        break
                
                # Generate display name with proper indentation and icons
                indent = "  " * depth
                folder_icon = "📁" if depth == 0 else "└─"
                folder_name = item.name
                
                # Enhanced display for special folder types
                if folder_metadata_info:
                    folder_type = folder_metadata_info.get('type', 'unknown')
                    if folder_type == 'chapter':
                        folder_icon = "📖"
                    elif folder_type == 'custom':
                        folder_icon = "🗂️"
                    display_name = f"{indent}{folder_icon} {folder_name}"
                else:
                    # Regular folder
                    if "Part_" in folder_name:
                        folder_icon = "📂"
                    display_name = f"{indent}{folder_icon} {folder_name}"
                
                folders.append((
                    display_name,
                    str(item.absolute()),
                    folder_metadata_info.get('type', 'regular') if folder_metadata_info else 'regular',
                    folder_metadata_info
                ))
        
        return folders
    
    except Exception:
        return []

def render_page_range_input(destination_info: Tuple[str, str]):
    """Render page range input and extraction controls"""
    
    destination_path, naming_base = destination_info
    
    st.markdown("### 📄 Page Range Assignment")
    st.markdown(f"**Selected Destination:** `{Path(destination_path).name}`")
    st.caption(f"📍 Full path: {destination_path}")
    
    total_pages = SessionManager.get('total_pages', 0)
    
    # Get initial value (empty if extraction was just completed)
    initial_ranges = "" if st.session_state.get('extraction_just_completed') else ""
    
    # Page range input with examples and unique key
    st.markdown("**Enter page ranges:**")
    ranges_input_key = f"page_ranges_{hash(destination_path) % 10000}"
    page_ranges_text = st.text_area(
        "Page Ranges",
        value=initial_ranges,
        placeholder=f"Examples:\n• Single pages: 1, 5, 10\n• Ranges: 1-5, 10-15\n• Mixed: 1-3, 7, 12-20\n\nTotal pages available: {total_pages}",
        help=f"Specify pages to extract (1-{total_pages})",
        height=120,
        key=ranges_input_key
    )
    
    # Show buttons
    col1, col2 = st.columns(2)
    
    with col1:
        preview_disabled = not page_ranges_text.strip()
        preview_key = f"preview_btn_{hash(destination_path + str(preview_disabled)) % 10000}"
        if st.button("📋 Preview Assignment", type="secondary", disabled=preview_disabled, key=preview_key):
            if page_ranges_text.strip():
                page_ranges = [r.strip() for r in page_ranges_text.split(',') if r.strip()]
                render_assignment_preview(Path(destination_path).name, page_ranges, total_pages, naming_base)
    
    with col2:
        extract_disabled = not page_ranges_text.strip()
        extract_key = f"extract_btn_{hash(destination_path + str(extract_disabled)) % 10000}"
        if st.button("🚀 Extract Pages", type="primary", disabled=extract_disabled, key=extract_key):
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

def render_assignment_preview(display_name: str, page_ranges: List[str], total_pages: int, naming_base: str):
    """Render preview of page assignment"""
    
    pages = PDFExtractor.parse_page_ranges(page_ranges, total_pages)
    
    if pages:
        st.success(f"Ready to extract {len(pages)} pages to: `{display_name}`")
        
        with st.expander("📋 Detailed Preview", expanded=True):
            st.markdown("**Files that will be created:**")
            safe_folder_name = PDFExtractor.sanitize_filename(naming_base)
            
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
    
    destination_path, naming_base = destination_info
    folder_path = Path(destination_path)
    
    try:
        # Check if destination folder already has PDF files
        if folder_path.exists():
            existing_pdfs = list(folder_path.glob("*.pdf"))
            if existing_pdfs:
                st.warning(f"⚠️ Destination folder already contains {len(existing_pdfs)} PDF files. New files will be added alongside existing ones.")
        
        # Ensure the folder exists
        folder_path.mkdir(parents=True, exist_ok=True)
        
        # Progress bar
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Execute extraction
        status_text.text(f"Extracting pages to {folder_path.name}...")
        progress_bar.progress(20)
        
        success, created_files, error_msg = PDFExtractor.extract_pages_to_folder(
            page_ranges, str(folder_path), naming_base, total_pages
        )
        
        progress_bar.progress(100)
        
        if success and created_files:
            # Update extraction history
            extraction_history = SessionManager.get('extraction_history', [])
            extraction_record = {
                'destination': folder_path.name,
                'destination_path': str(folder_path.absolute()),
                'pages_extracted': len(created_files),
                'page_ranges': page_ranges,
                'files_created': created_files,
                'naming_base': naming_base
            }
            extraction_history.append(extraction_record)
            SessionManager.set('extraction_history', extraction_history)
            
            # Store extraction info for success message
            st.session_state['last_extraction_info'] = {
                'pages_count': len(created_files),
                'destination': str(folder_path.absolute())
            }
            st.session_state['extraction_just_completed'] = True
            
            # Clear progress indicators
            progress_bar.empty()
            status_text.empty()
            
            # Force page refresh to show success message and clear inputs
            st.rerun()
            
        elif success and not created_files:
            progress_bar.empty()
            status_text.empty()
            st.warning("⚠️ No pages were extracted. Please check your page ranges.")
        else:
            progress_bar.empty()
            status_text.empty()
            st.error(f"❌ Extraction failed: {error_msg}")
    
    except FileExistsError:
        st.error(f"❌ Some files already exist in the destination folder. Please clean the folder or choose a different destination.")
    except PermissionError:
        st.error(f"❌ Permission denied. Cannot write to folder '{folder_path.name}'. Please check folder permissions.")
    except Exception as e:
        if "No space left" in str(e).lower():
            st.error(f"❌ Insufficient disk space to extract files. Please free up space and try again.")
        elif "access denied" in str(e).lower():
            st.error(f"❌ Access denied. Please check if the folder is open in another application.")
        else:
            st.error(f"❌ Extraction error: {str(e)}")

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
        st.success("✅ Extraction history cleared!")
        st.rerun()