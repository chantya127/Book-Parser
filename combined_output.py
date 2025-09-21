

# ===== File: main.py =====


# main.py - Entry point for the Streamlit application
import streamlit as st
import sys
from pathlib import Path

# Add src to path for imports
sys.path.append(str(Path(__file__).parent / "src"))

from ui.app_layout import setup_page_config, render_main_app
from core.session_manager import SessionManager

def main():
    """Main application entry point"""
    setup_page_config()
    SessionManager.initialize_session()
    render_main_app()

if __name__ == "__main__":
    main()


# ===== File: src/__init__.py =====




# ===== File: src/core/__init__.py =====




# ===== File: src/core/folder_manager.py =====

from pathlib import Path
from typing import List, Tuple, Optional, Dict
import streamlit as st
import random
import os

class FolderManager:
    """Manages folder structure creation and organization"""
    
    DEFAULT_FOLDERS = ['prologue', 'index', 'epilogue']
    
    @staticmethod
    def create_project_structure(code: str, book_name: str) -> Tuple[Optional[Path], List[str]]:
        """
        Create the basic project folder structure
        
        Args:
            code: Project code
            book_name: Book name (kept as is, no sanitization)
            
        Returns:
            Tuple of (project path, list of created folders)
        """
        if not code or not book_name:
            return None, []
        
        try:
            # Sanitize only the code, keep book name as is
            safe_code = FolderManager.sanitize_name(code)
            base_name = f"{safe_code}_{book_name}"  # Book name kept as is
            
            # Create main project folder
            project_path = Path(base_name)
            project_path.mkdir(exist_ok=True)
            
            created_folders = []
            
            # Create default folders
            for folder in FolderManager.DEFAULT_FOLDERS:
                folder_path = project_path / f"{base_name}_{folder}"
                folder_path.mkdir(exist_ok=True)
                created_folders.append(str(folder_path.absolute()))
            
            return project_path, created_folders
            
        except Exception as e:
            st.error(f"Error creating folder structure: {str(e)}")
            return None, []
    
    @staticmethod
    def create_parts_folders(project_path: Path, base_name: str, num_parts: int) -> List[str]:
        """Create part folders"""
        created_parts = []
        
        try:
            for i in range(1, num_parts + 1):
                part_folder = project_path / f"{base_name}_Part_{i}"
                part_folder.mkdir(exist_ok=True)
                created_parts.append(str(part_folder.absolute()))
            
            return created_parts
        except Exception as e:
            st.error(f"Error creating part folders: {str(e)}")
            return []
    
    @staticmethod
    def create_custom_folder(project_path: Path, base_name: str, parent_folder_path: str, custom_folder_name: str, session_manager=None) -> Optional[str]:
        """
        Create a custom folder inside any existing folder with parent prefix + custom name
        
        Args:
            project_path: Main project path
            base_name: Base project name
            parent_folder_path: Actual path of the parent folder
            custom_folder_name: Name for the new custom folder (will be prefixed with parent name)
            session_manager: SessionManager instance to avoid circular import
            
        Returns:
            Path of created folder or None if failed
        """
        try:
            # Import only when needed to avoid circular imports
            if session_manager is None:
                from core.session_manager import SessionManager
                session_manager = SessionManager
            
            parent_path = Path(parent_folder_path)
            parent_folder_name = parent_path.name
            
            # FIXED: Create folder with parent prefix + custom name (following project convention)
            final_folder_name = f"{parent_folder_name}_{custom_folder_name}"
            custom_folder_path = parent_path / final_folder_name
            custom_folder_path.mkdir(exist_ok=True)
            
            # Generate unique ID for the custom folder
            custom_folder_id = f"custom_{random.randint(10000, 99999)}"
            
            # Store metadata
            folder_metadata = session_manager.get('folder_metadata', {})
            folder_metadata[custom_folder_id] = {
                'display_name': f"{parent_folder_name} → {custom_folder_name}",
                'actual_path': str(custom_folder_path.absolute()),
                'type': 'custom',
                'parent_path': parent_folder_path,
                'folder_name': final_folder_name,  # Full name with prefix
                'naming_base': final_folder_name   # Use full name for file naming
            }
            
            session_manager.set('folder_metadata', folder_metadata)
            return str(custom_folder_path.absolute())
            
        except Exception as e:
            st.error(f"Error creating custom folder: {str(e)}")
            return None
    
    @staticmethod
    def sanitize_name(name: str) -> str:
        """Sanitize name for folder creation"""
        # Replace problematic characters
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            name = name.replace(char, '_')
        
        # Remove extra spaces and special characters
        name = ''.join(c if c.isalnum() or c in '-_' else '_' for c in name)
        name = '_'.join(name.split())  # Remove multiple underscores
        
        return name[:50]  # Limit length
    
    @staticmethod
    def get_folder_preview(code: str, book_name: str, num_parts: int = 0) -> List[str]:
        """Generate preview of folder structure"""
        if not code or not book_name:
            return []
        
        safe_code = FolderManager.sanitize_name(code)
        base_name = f"{safe_code}_{book_name}"  # Book name kept as is
        preview = []
        
        # Default folders
        for folder in FolderManager.DEFAULT_FOLDERS:
            preview.append(f"{base_name}_{folder}")
        
        # Part folders
        for i in range(1, num_parts + 1):
            preview.append(f"{base_name}_Part_{i}")
        
        return preview


class ChapterManager:
    """Manages chapter creation and organization within parts"""
    
    @staticmethod
    def generate_chapter_folder_name(parent_folder: str, chapter_number: str = None, 
                                   chapter_name: str = None) -> str:
        """
        Generate chapter folder name following the convention:
        {base_project_name}_Chapter_{chapter_number}_{chapter_name}
        
        Args:
            parent_folder: Parent folder name (e.g., CS101_DataStructures_Part_1)
            chapter_number: Chapter number (can be None)
            chapter_name: Chapter name (can be None)
            
        Returns:
            Properly formatted chapter folder name
        """
        # Extract base name by removing the part suffix
        if "_Part_" in parent_folder:
            base_name = parent_folder.split("_Part_")[0]
        else:
            base_name = parent_folder
        
        # Handle missing values with improved formatting
        if chapter_number is None or chapter_number.strip() == "":
            chapter_num = "null"
        else:
            chapter_num = chapter_number.strip()
        
        if chapter_name is None or chapter_name.strip() == "":
            chapter_nm = "Null_Name"  # Better formatting for null names
        else:
            # FIXED: Don't sanitize chapter name - keep it as is to avoid underscores
            chapter_nm = chapter_name.strip()
        
        # If both are null, add random number for uniqueness
        if chapter_num == "null" and chapter_nm == "Null_Name":
            random_num = random.randint(10000, 99999)
            return f"{base_name}_Chapter_{chapter_num}_{chapter_nm}_{random_num}"
        
        return f"{base_name}_Chapter_{chapter_num}_{chapter_nm}"
    
    @staticmethod
    def generate_unique_chapter_id(base_name: str, part_number: int) -> str:
        """Generate unique identifier for chapter"""
        from core.session_manager import SessionManager
        counter = SessionManager.get('unique_chapter_counter', 0) + 1
        SessionManager.set('unique_chapter_counter', counter)
        return f"{base_name}_part_{part_number}_chapter_{counter}"
    
    @staticmethod
    def create_chapter_folders(project_path: Path, base_name: str, part_number: int, 
                             chapters: List[Dict]) -> List[str]:
        """
        Create chapter folders within a part with proper naming convention
        
        Args:
            project_path: Main project path
            base_name: Base project name
            part_number: Part number
            chapters: List of chapter dictionaries with 'number' and 'name'
            
        Returns:
            List of created chapter folder paths
        """
        from core.session_manager import SessionManager
        
        created_chapters = []
        part_folder_name = f"{base_name}_Part_{part_number}"
        part_path = project_path / part_folder_name
        
        try:
            # Ensure part folder exists
            part_path.mkdir(exist_ok=True)
            folder_metadata = SessionManager.get('folder_metadata', {})
            
            for chapter in chapters:
                # Generate unique ID for metadata tracking
                chapter_id = ChapterManager.generate_unique_chapter_id(base_name, part_number)
                
                # Generate proper chapter folder name with full parent prefix
                chapter_folder_name = ChapterManager.generate_chapter_folder_name(
                    part_folder_name,
                    chapter.get('number'),
                    chapter.get('name')
                )
                
                # Create actual folder with the complete naming convention
                chapter_path = part_path / chapter_folder_name
                chapter_path.mkdir(exist_ok=True)
                
                # Store metadata mapping
                display_name = f"Part {part_number} → {chapter_folder_name}"
                folder_metadata[chapter_id] = {
                    'display_name': display_name,
                    'actual_path': str(chapter_path.absolute()),
                    'type': 'chapter',
                    'parent_part': part_number,
                    'chapter_number': chapter.get('number', ''),
                    'chapter_name': chapter.get('name', ''),
                    'naming_base': chapter_folder_name,  # Full name for file naming
                    'folder_name': chapter_folder_name   # Complete folder name
                }
                
                created_chapters.append(str(chapter_path.absolute()))
            
            SessionManager.set('folder_metadata', folder_metadata)
            return created_chapters
        except Exception as e:
            st.error(f"Error creating chapter folders: {str(e)}")
            return []
    
    @staticmethod
    def rename_chapter_files(chapter_id: str, new_naming_base: str) -> bool:
        """
        Rename all PDF files in a chapter and the chapter folder itself when chapter name changes
        """
        from core.session_manager import SessionManager
        
        try:
            folder_metadata = SessionManager.get('folder_metadata', {})
            if chapter_id not in folder_metadata:
                return False
            
            old_chapter_path = Path(folder_metadata[chapter_id]['actual_path'])
            if not old_chapter_path.exists():
                return False
            
            # Create new chapter folder path with updated name
            parent_path = old_chapter_path.parent
            new_chapter_path = parent_path / new_naming_base
            
            # Rename the chapter folder itself
            old_chapter_path.rename(new_chapter_path)
            
            # Find all PDF files in the renamed chapter folder
            pdf_files = list(new_chapter_path.glob("*.pdf"))
            
            for old_file in pdf_files:
                # Extract page number from filename
                filename = old_file.name
                if "_Page_" in filename:
                    page_part = filename.split("_Page_")[-1]  # "X.pdf"
                    new_filename = f"{new_naming_base}_Page_{page_part}"
                    new_file = new_chapter_path / new_filename
                    
                    # Rename the file
                    old_file.rename(new_file)
            
            # Update metadata with new paths and naming base
            folder_metadata[chapter_id]['actual_path'] = str(new_chapter_path.absolute())
            folder_metadata[chapter_id]['naming_base'] = new_naming_base
            folder_metadata[chapter_id]['folder_name'] = new_naming_base
            SessionManager.set('folder_metadata', folder_metadata)
            
            return True
        except Exception as e:
            st.error(f"Error renaming chapter folder and files: {str(e)}")
            return False
    
    @staticmethod
    def get_chapters_preview(base_name: str, part_number: int, chapters: List[Dict]) -> List[str]:
        """Generate preview of chapter folder names"""
        preview = []
        part_folder_name = f"{base_name}_part_{part_number}"
        
        for chapter in chapters:
            chapter_folder_name = ChapterManager.generate_chapter_folder_name(
                part_folder_name,
                chapter.get('number'),
                chapter.get('name')
            )
            preview.append(chapter_folder_name)
        
        return preview
    
    @staticmethod
    def validate_chapter_data(chapters: List[Dict]) -> Tuple[bool, str]:
        """
        Validate chapter configuration data
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not chapters:
            return False, "No chapters defined"
        
        # Check for duplicate chapter numbers (if provided and not null)
        numbers = [ch.get('number') for ch in chapters 
                  if ch.get('number') and ch.get('number') != '' and ch.get('number') != 'null']
        if len(numbers) != len(set(numbers)):
            return False, "Duplicate chapter numbers found"
        
        return True, ""


# ===== File: src/core/pdf_handler.py =====

import PyPDF2
from io import BytesIO
import streamlit as st
from typing import Tuple, Optional, List
from pathlib import Path
import os

class PDFHandler:
    """Handles PDF file operations"""
    
    @staticmethod
    def load_pdf_info(uploaded_file) -> Tuple[Optional[PyPDF2.PdfReader], int]:
        """
        Load PDF and extract basic information with memory optimization
        
        Args:
            uploaded_file: Streamlit uploaded file object
            
        Returns:
            Tuple of (PDF reader object, total pages)
        """
        try:
            # For large files, avoid storing full content in session
            # Instead, store file info and reload when needed
            file_content = uploaded_file.read()
            pdf_reader = PyPDF2.PdfReader(BytesIO(file_content))
            total_pages = len(pdf_reader.pages)
            
            # Store file info instead of full content for large files
            file_size_mb = len(file_content) / (1024 * 1024)
            if file_size_mb > 100:  # Only store content for files smaller than 100MB
                st.session_state.pdf_file_name = uploaded_file.name
                st.session_state.pdf_large_file = True
                st.info(f"Large PDF detected ({file_size_mb:.1f}MB). Using optimized memory handling.")
            else:
                st.session_state.pdf_content = file_content
                st.session_state.pdf_large_file = False
            
            return pdf_reader, total_pages
        except Exception as e:
            st.error(f"Error reading PDF: {str(e)}")
            return None, 0
    
    @staticmethod
    def get_pdf_reader() -> Optional[PyPDF2.PdfReader]:
        """Get PDF reader from stored content or reload from file"""
        try:
            # Check if we have content stored (for smaller files)
            pdf_content = st.session_state.get('pdf_content')
            if pdf_content:
                return PyPDF2.PdfReader(BytesIO(pdf_content))
            
            # For large files, get from the uploaded file directly
            pdf_file = st.session_state.get('pdf_file')
            if pdf_file:
                return PyPDF2.PdfReader(BytesIO(pdf_file.read()))
            
            return None
        except Exception as e:
            st.error(f"Error accessing PDF: {str(e)}")
            return None
    
    @staticmethod
    def validate_pdf(uploaded_file) -> bool:
        """Validate if uploaded file is a proper PDF"""
        try:
            uploaded_file.seek(0)  # Reset file pointer
            pdf_reader = PyPDF2.PdfReader(BytesIO(uploaded_file.read()))
            uploaded_file.seek(0)  # Reset for future reads
            return len(pdf_reader.pages) > 0
        except:
            return False


class PDFExtractor:
    """Handles PDF page extraction and file creation"""
    
    @staticmethod
    def extract_pages_to_folder(page_ranges: List[str], destination_folder: str, 
                              naming_base: str, total_pages: int) -> Tuple[bool, List[str], str]:
        """
        Extract specified pages from PDF and save to destination folder with sequential numbering
        
        Args:
            page_ranges: List of page range strings (e.g., ["1-5", "10", "15-20"])
            destination_folder: Target folder path
            naming_base: Base name for file naming (should include full hierarchy)
            total_pages: Total pages in PDF for validation
            
        Returns:
            Tuple of (success, list of created files, error message)
        """
        try:
            # Parse page ranges into individual page numbers
            pages_to_extract = PDFExtractor.parse_page_ranges(page_ranges, total_pages)
            
            if not pages_to_extract:
                return False, [], "No valid pages specified"
            
            # Get PDF reader
            pdf_reader = PDFHandler.get_pdf_reader()
            if not pdf_reader:
                return False, [], "Could not access PDF file"
            
            # Create destination folder if it doesn't exist
            dest_path = Path(destination_folder)
            dest_path.mkdir(parents=True, exist_ok=True)
            
            created_files = []
            failed_pages = []
            
            # Extract each page with sequential numbering (starting from 1)
            for sequential_num, actual_page_num in enumerate(pages_to_extract, 1):
                success, file_path = PDFExtractor.extract_single_page(
                    pdf_reader, actual_page_num, dest_path, naming_base, sequential_num
                )
                
                if success:
                    created_files.append(file_path)
                else:
                    failed_pages.append(actual_page_num)
            
            # Report results
            if failed_pages:
                warning_msg = f"Failed to extract pages: {', '.join(map(str, failed_pages))}"
                st.warning(warning_msg)
            
            success_status = len(created_files) > 0
            return success_status, created_files, ""
            
        except Exception as e:
            return False, [], f"Error extracting pages: {str(e)}"
    
    @staticmethod
    def extract_single_page(pdf_reader: PyPDF2.PdfReader, actual_page_num: int, 
                          dest_path: Path, naming_base: str, sequential_page_num: int = None) -> Tuple[bool, str]:
        """
        Extract a single page from PDF with proper naming convention and sequential numbering
        
        Args:
            pdf_reader: PDF reader object
            actual_page_num: Actual page number in PDF to extract (1-indexed)
            dest_path: Destination folder path
            naming_base: Complete naming base including parent folder hierarchy
            sequential_page_num: Sequential page number for file naming (starts from 1)
            
        Returns:
            Tuple of (success, file_path)
        """
        try:
            # Validate page number
            if actual_page_num < 1 or actual_page_num > len(pdf_reader.pages):
                return False, f"Page {actual_page_num} out of range"
            
            # Create new PDF with single page
            pdf_writer = PyPDF2.PdfWriter()
            pdf_writer.add_page(pdf_reader.pages[actual_page_num - 1])  # Convert to 0-indexed
            
            # Use sequential numbering if provided, otherwise use actual page number
            page_num_for_filename = sequential_page_num if sequential_page_num is not None else actual_page_num
            
            # Generate file name using the complete naming base with sequential numbering
            safe_naming_base = PDFExtractor.sanitize_filename(naming_base)
            file_name = f"{safe_naming_base}_Page_{page_num_for_filename}.pdf"
            file_path = dest_path / file_name
            
            # Write PDF file
            with open(file_path, 'wb') as output_file:
                pdf_writer.write(output_file)
            
            return True, str(file_path)
            
        except Exception as e:
            st.error(f"Error extracting page {actual_page_num}: {str(e)}")
            return False, ""
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitize filename for cross-platform compatibility"""
        # Remove/replace problematic characters
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        
        # Remove extra spaces and limit length
        filename = '_'.join(filename.split())
        return filename[:200]  # Limit filename length
    
    @staticmethod
    def parse_page_ranges(page_ranges: List[str], total_pages: int) -> List[int]:
        """
        Parse page range strings into list of individual page numbers
        
        Args:
            page_ranges: List of range strings (e.g., ["1-5", "10", "15-20"])
            total_pages: Total pages for validation
            
        Returns:
            List of individual page numbers
        """
        pages = set()
        
        for range_str in page_ranges:
            range_str = range_str.strip()
            if not range_str:
                continue
            
            if '-' in range_str:
                # Handle range (e.g., "1-5")
                try:
                    parts = range_str.split('-')
                    if len(parts) != 2:
                        st.warning(f"Invalid range format: {range_str}")
                        continue
                        
                    start, end = parts
                    start_page = int(start.strip())
                    end_page = int(end.strip())
                    
                    # Validate range
                    if start_page > 0 and end_page <= total_pages and start_page <= end_page:
                        pages.update(range(start_page, end_page + 1))
                    else:
                        st.warning(f"Invalid range: {range_str} (PDF has {total_pages} pages)")
                        
                except ValueError:
                    st.warning(f"Invalid range format: {range_str}")
            else:
                # Handle single page
                try:
                    page_num = int(range_str)
                    if 1 <= page_num <= total_pages:
                        pages.add(page_num)
                    else:
                        st.warning(f"Page {page_num} out of range (1-{total_pages})")
                        
                except ValueError:
                    st.warning(f"Invalid page number: {range_str}")
        
        return sorted(list(pages))
    
    @staticmethod
    def preview_page_extraction(page_ranges: List[str], total_pages: int) -> str:
        """
        Generate preview of what pages will be extracted
        
        Args:
            page_ranges: List of page range strings
            total_pages: Total pages for validation
            
        Returns:
            Preview string describing the extraction
        """
        pages = PDFExtractor.parse_page_ranges(page_ranges, total_pages)
        
        if not pages:
            return "No valid pages to extract"
        
        # Group consecutive pages for better display
        if len(pages) == 0:
            return "No pages selected"
        
        groups = []
        current_group = [pages[0]]
        
        for i in range(1, len(pages)):
            if pages[i] == pages[i-1] + 1:
                current_group.append(pages[i])
            else:
                groups.append(current_group)
                current_group = [pages[i]]
        
        groups.append(current_group)
        
        # Format groups
        formatted_groups = []
        for group in groups:
            if len(group) == 1:
                formatted_groups.append(str(group[0]))
            else:
                formatted_groups.append(f"{group[0]}-{group[-1]}")
        
        return f"Pages to extract: {', '.join(formatted_groups)} (Total: {len(pages)} pages)"


# ===== File: src/core/session_manager.py =====

import streamlit as st
from typing import Dict, Any

class SessionManager:
    """Manages application session state"""
    
    @staticmethod
    def initialize_session():
        """Initialize session state with default values"""
        defaults = {
            'project_config': {},
            'pdf_uploaded': False,
            'pdf_file': None,
            'pdf_content': None,  # Store PDF content to avoid re-reading
            'total_pages': 0,
            'folder_structure_created': False,
            'created_folders': [],
            'chapters_config': {},  # {part_1: [chapters], part_2: [chapters]}
            'current_step': 1,
            'chapters_created': False,
            'page_assignments': {},  # Track page assignments
            'extraction_history': [],  # Track completed extractions
            'folder_metadata': {},  # {folder_id: {display_name, actual_path, type}}
            'unique_chapter_counter': 0,  # For ensuring unique chapter identifiers
            'numbering_systems': {},  # {Part_1: numbering_system, Part_2: numbering_system}
        }
        
        for key, value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = value
    
    @staticmethod
    def get(key: str, default=None):
        """Get value from session state"""
        return st.session_state.get(key, default)
    
    @staticmethod
    def set(key: str, value: Any):
        """Set value in session state"""
        st.session_state[key] = value
    
    @staticmethod
    def update_config(updates: Dict[str, Any]):
        """Update project configuration"""
        if 'project_config' not in st.session_state:
            st.session_state.project_config = {}
        st.session_state.project_config.update(updates)


# ===== File: src/ui/__init__.py =====




# ===== File: src/ui/app_layout.py =====

# src/ui/app_layout.py
import streamlit as st
from ui.sidebar import render_sidebar
from ui.main_content import render_main_content
from ui.progress_tracker import render_progress_tracker
from ui.chapter_management import render_chapter_management_page
from ui.page_assignment import render_page_assignment_page
from ui.custom_folder_management import render_custom_folder_management_page
from core.session_manager import SessionManager

def setup_page_config():
    """Configure Streamlit page settings"""
    st.set_page_config(
        page_title="PDF Page Organizer",
        page_icon="📚",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS to ensure primary buttons are properly styled and all buttons are red
    st.markdown("""
    <style>
        /* Force all buttons to be red */
        div.stButton > button:first-child,
        .stButton > button[kind="primary"],
        .stButton > button[kind="secondary"] {
            background-color: #ff4b4b !important;
            color: white !important;
            border-color: #ff4b4b !important;
            border: 1px solid #ff4b4b !important;
        }
        
        /* Hover state for buttons */
        div.stButton > button:first-child:hover,
        .stButton > button[kind="primary"]:hover,
        .stButton > button[kind="secondary"]:hover {
            background-color: #ff6c6c !important;
            border-color: #ff6c6c !important;
        }
        
        /* Active/pressed state for buttons */
        div.stButton > button:first-child:active,
        .stButton > button[kind="primary"]:active,
        .stButton > button[kind="secondary"]:active {
            background-color: #ff2b2b !important;
            border-color: #ff2b2b !important;
        }
        
        /* Disabled buttons should be grayed out */
        div.stButton > button:first-child:disabled {
            background-color: #cccccc !important;
            color: #666666 !important;
            border-color: #cccccc !important;
        }
    </style>
    """, unsafe_allow_html=True)

def render_main_app():
    """Render the main application layout"""
    st.title("📚 PDF Page Organizer")
    
    # Navigation tabs - Added Custom Folders tab
    tab1, tab2, tab3, tab4 = st.tabs([
        "📋 Project Setup", 
        "📂 Chapter Management", 
        "🗂️ Custom Folders",
        "📄 Page Assignment"
    ])
    
    with tab1:
        render_project_setup_tab()
    
    with tab2:
        render_chapter_management_page()
    
    with tab3:
        render_custom_folder_management_page()
    
    with tab4:
        render_page_assignment_page()

def render_project_setup_tab():
    """Render the project setup tab"""
    st.markdown("---")
    render_sidebar()
    render_main_content()


# ===== File: src/ui/chapter_management.py =====

import streamlit as st
from typing import Dict, List
from core.session_manager import SessionManager
from core.folder_manager import ChapterManager, FolderManager
from pathlib import Path
import shutil

def render_chapter_management_page():
    """Render the chapter management page"""
    
    # Check prerequisites
    if not SessionManager.get('folder_structure_created'):
        render_prerequisites_warning()
        return
    
    config = SessionManager.get('project_config', {})
    
    st.subheader("📂 Chapter Management")
    st.markdown("Configure chapters within each part of your book.")
    
    # Add option to create individual parts
    st.markdown("### 🔧 Additional Options")
    col_opt1, col_opt2, col_opt3, col_opt4 = st.columns(4)
    
    # Get actual parts that exist (including individually created ones)
    actual_parts = get_existing_parts(config)
    max_part_num = max(actual_parts) if actual_parts else 0
    
    with col_opt1:
        if st.button("➕ Add Individual Part", type="secondary"):
            add_individual_part(config)
            st.rerun()  # Force refresh after adding part
    
    with col_opt2:
        individual_part_num = st.number_input(
            "Part Number to Add",
            min_value=1,
            value=max_part_num + 1,
            step=1,
            key="individual_part_input",
            help="Specify which part number to create individually"
        )
    
    with col_opt3:
        # Delete part option
        if actual_parts:
            part_to_delete = st.selectbox(
                "Select Part to Delete",
                actual_parts,
                key="part_to_delete_select",
                help="Choose which part to delete (this will delete all contents)"
            )
            
    with col_opt4:
        if actual_parts:
            if st.button("🗑️ Delete Selected Part", type="secondary", key="delete_part_btn"):
                part_to_delete = st.session_state.get("part_to_delete_select")
                if part_to_delete:
                    delete_individual_part(config, part_to_delete)
                    st.rerun()
    
    if not actual_parts:
        st.info("📝 No parts configured. You can add individual parts above or configure parts in Project Setup.")
        return
    
    st.markdown("---")
    st.info(f"Found {len(actual_parts)} existing parts: {', '.join(map(str, sorted(actual_parts)))}")
    
    # Chapter configuration for each part
    col1, col2 = st.columns([2, 1])
    
    with col1:
        render_chapter_configuration(config, actual_parts)
    
    with col2:
        render_chapter_preview(config)

def delete_individual_part(config: Dict, part_number: int):
    """Delete an individual part folder and all its contents"""
    try:
        safe_code = FolderManager.sanitize_name(config['code'])
        book_name = config['book_name']
        base_name = f"{safe_code}_{book_name}"
        
        # Use consistent path resolution
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
            st.error(f"Project folder not found. Cannot delete Part {part_number}.")
            return
        
        # Find the part folder
        part_folder = project_path / f"{base_name}_Part_{part_number}"
        
        if not part_folder.exists():
            st.error(f"Part {part_number} folder not found.")
            return
        
        # Confirmation dialog
        with st.spinner(f"Deleting Part {part_number} and all its contents..."):
            # Delete the folder and all contents
            shutil.rmtree(part_folder)
            
            # Update session state - remove from created folders
            current_folders = SessionManager.get('created_folders', [])
            part_path_str = str(part_folder.absolute())
            if part_path_str in current_folders:
                current_folders.remove(part_path_str)
            
            # Remove any chapter folders that were in this part
            folders_to_remove = []
            for folder_path in current_folders:
                if f"Part_{part_number}" in folder_path and part_folder.name in folder_path:
                    folders_to_remove.append(folder_path)
            
            for folder_path in folders_to_remove:
                current_folders.remove(folder_path)
            
            SessionManager.set('created_folders', current_folders)
            
            # Remove chapter metadata for this part
            folder_metadata = SessionManager.get('folder_metadata', {})
            metadata_to_remove = []
            for folder_id, metadata in folder_metadata.items():
                if metadata.get('type') == 'chapter' and metadata.get('parent_part') == part_number:
                    metadata_to_remove.append(folder_id)
                elif metadata.get('type') == 'custom' and f"Part_{part_number}" in metadata.get('actual_path', ''):
                    metadata_to_remove.append(folder_id)
            
            for folder_id in metadata_to_remove:
                del folder_metadata[folder_id]
            
            SessionManager.set('folder_metadata', folder_metadata)
            
            # Remove chapters config for this part
            chapters_config = SessionManager.get('chapters_config', {})
            part_key = f"Part_{part_number}"
            if part_key in chapters_config:
                del chapters_config[part_key]
                SessionManager.set('chapters_config', chapters_config)
            
            # Update num_parts if this was the highest numbered part
            current_num_parts = config.get('num_parts', 0)
            if part_number == current_num_parts:
                # Find the new highest part number
                existing_parts = get_existing_parts(config)
                new_max_parts = max(existing_parts) if existing_parts else 0
                SessionManager.update_config({'num_parts': new_max_parts})
            
            st.success(f"✅ Successfully deleted Part {part_number} and all its contents!")
            
    except PermissionError:
        st.error(f"❌ Permission denied. Cannot delete Part {part_number}. Please check folder permissions.")
    except Exception as e:
        st.error(f"❌ Error deleting Part {part_number}: {str(e)}")

def get_existing_parts(config: Dict) -> List[int]:
    """Get list of actually existing part numbers by checking folders and session state"""
    existing_parts = set()
    
    # Get from config num_parts
    config_parts = config.get('num_parts', 0)
    if config_parts > 0:
        existing_parts.update(range(1, config_parts + 1))
    
    # Check created folders for individual parts
    created_folders = SessionManager.get('created_folders', [])
    safe_code = FolderManager.sanitize_name(config.get('code', ''))
    book_name = config.get('book_name', '')
    base_name = f"{safe_code}_{book_name}"
    
    for folder_path in created_folders:
        folder_name = Path(folder_path).name
        # Look for pattern: base_name_Part_X
        if f"{base_name}_Part_" in folder_name:
            try:
                part_num_str = folder_name.split(f"{base_name}_Part_")[-1]
                part_num = int(part_num_str)
                existing_parts.add(part_num)
            except (ValueError, IndexError):
                continue
    
    # Also check filesystem directly
    try:
        current_dir = Path.cwd()
        possible_paths = [
            Path(base_name),
            current_dir / base_name,
            Path.cwd() / base_name
        ]
        
        for project_path in possible_paths:
            if project_path.exists() and project_path.is_dir():
                for item in project_path.iterdir():
                    if item.is_dir() and f"{base_name}_Part_" in item.name:
                        try:
                            part_num_str = item.name.split(f"{base_name}_Part_")[-1]
                            part_num = int(part_num_str)
                            existing_parts.add(part_num)
                        except (ValueError, IndexError):
                            continue
                break
    except Exception:
        pass  # If filesystem check fails, continue with what we have
    
    return sorted(list(existing_parts))

def add_individual_part(config: Dict):
    """Add an individual part folder"""
    try:
        individual_part_num = st.session_state.get('individual_part_input', 1)
        
        with st.spinner(f"Creating Part {individual_part_num}..."):
            safe_code = FolderManager.sanitize_name(config['code'])
            book_name = config['book_name']
            base_name = f"{safe_code}_{book_name}"
            
            # Use consistent path resolution
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
            
            # Create individual part folder
            part_folder = project_path / f"{base_name}_Part_{individual_part_num}"
            part_folder.mkdir(exist_ok=True)
            
            # Update session state
            current_folders = SessionManager.get('created_folders', [])
            new_part_path = str(part_folder.absolute())
            if new_part_path not in current_folders:
                current_folders.append(new_part_path)
                SessionManager.set('created_folders', current_folders)
            
            # Update num_parts if this part number is higher
            current_num_parts = config.get('num_parts', 0)
            if individual_part_num > current_num_parts:
                SessionManager.update_config({'num_parts': individual_part_num})
            
            st.success(f"✅ Created Part {individual_part_num} successfully!")
            st.info(f"📂 Location: {part_folder.absolute()}")
            
    except Exception as e:
        st.error(f"Error creating individual part: {str(e)}")

def render_prerequisites_warning():
    """Render warning when prerequisites are not met"""
    st.warning("⚠️ Please complete the project setup first!")
    st.markdown("""
    **Required steps:**
    1. Upload PDF file
    2. Configure project details
    3. Create folder structure
    """)

def render_chapter_configuration(config: Dict, existing_parts: List[int]):
    """Render chapter configuration interface"""
    
    chapters_config = SessionManager.get('chapters_config', {})
    
    for part_num in existing_parts:
        with st.expander(f"📖 Part {part_num} Chapters", expanded=part_num == existing_parts[0] if existing_parts else False):
            render_part_chapters(part_num, chapters_config, config)
    
    # Create chapters button
    if any(chapters_config.values()):  # Only show if chapters are configured
        if st.button("🏗️ Create All Chapters", type="primary"):
            create_all_chapters(config, chapters_config)

def get_chapter_number_format(part_num: int, chapter_index: int) -> str:
    """Get formatted chapter number based on numbering system"""
    numbering_config = SessionManager.get('numbering_systems', {})
    part_key = f"Part_{part_num}"
    numbering_system = numbering_config.get(part_key, "Numbers (1, 2, 3...)")
    
    chapter_num = chapter_index + 1  # Convert 0-based index to 1-based
    
    if numbering_system == "Words (One, Two, Three...)":
        word_numbers = ["One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine", "Ten",
                       "Eleven", "Twelve", "Thirteen", "Fourteen", "Fifteen", "Sixteen", "Seventeen", 
                       "Eighteen", "Nineteen", "Twenty", "Twenty-One", "Twenty-Two", "Twenty-Three",
                       "Twenty-Four", "Twenty-Five", "Twenty-Six", "Twenty-Seven", "Twenty-Eight",
                       "Twenty-Nine", "Thirty", "Thirty-One", "Thirty-Two", "Thirty-Three", "Thirty-Four",
                       "Thirty-Five", "Thirty-Six", "Thirty-Seven", "Thirty-Eight", "Thirty-Nine", "Forty",
                       "Forty-One", "Forty-Two", "Forty-Three", "Forty-Four", "Forty-Five", "Forty-Six",
                       "Forty-Seven", "Forty-Eight", "Forty-Nine", "Fifty"]
        return word_numbers[chapter_num - 1] if chapter_num <= len(word_numbers) else str(chapter_num)
    
    elif numbering_system == "Roman (I, II, III...)":
        roman_numerals = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X",
                         "XI", "XII", "XIII", "XIV", "XV", "XVI", "XVII", "XVIII", "XIX", "XX",
                         "XXI", "XXII", "XXIII", "XXIV", "XXV", "XXVI", "XXVII", "XXVIII", "XXIX", "XXX",
                         "XXXI", "XXXII", "XXXIII", "XXXIV", "XXXV", "XXXVI", "XXXVII", "XXXVIII", "XXXIX", "XL",
                         "XLI", "XLII", "XLIII", "XLIV", "XLV", "XLVI", "XLVII", "XLVIII", "XLIX", "L"]
        return roman_numerals[chapter_num - 1] if chapter_num <= len(roman_numerals) else str(chapter_num)
    
    elif numbering_system == "Null (null_1, null_2...)":
        return f"null_{chapter_num}"
    
    else:  # Default to numbers
        return str(chapter_num)

def render_part_chapters(part_num: int, chapters_config: Dict, config: Dict):
    """Render chapter configuration for a specific part"""
    
    part_key = f"Part_{part_num}"
    part_chapters = chapters_config.get(part_key, [])
    
    # Number of chapters input
    current_count = len(part_chapters)
    num_chapters = st.number_input(
        f"Number of chapters in Part {part_num}",
        min_value=0,
        value=current_count,
        step=1,
        key=f"chapters_count_{part_num}",
        help="Enter any number of chapters (no limit)"
    )
    
    # Chapter numbering system selection
    if num_chapters > 0:
        numbering_config = SessionManager.get('numbering_systems', {})
        current_system = numbering_config.get(part_key, "Numbers (1, 2, 3...)")
        
        numbering_options = [
            "Numbers (1, 2, 3...)", 
            "Words (One, Two, Three...)", 
            "Roman (I, II, III...)",
            "Null (null_1, null_2...)"
        ]
        
        numbering_system = st.selectbox(
            f"Chapter Numbering System for Part {part_num}",
            numbering_options,
            index=numbering_options.index(current_system) if current_system in numbering_options else 0,
            key=f"numbering_system_{part_num}",
            help="Choose how chapters should be numbered. 'Null' will create null_(1), null_(2) format."
        )
        
        # Check if numbering system changed
        if current_system != numbering_system:
            numbering_config[part_key] = numbering_system
            SessionManager.set('numbering_systems', numbering_config)
            update_chapter_numbering_system(part_num)
            st.rerun()
        
        # Store numbering system in config
        numbering_config[part_key] = numbering_system
        SessionManager.set('numbering_systems', numbering_config)
    
    # Update chapters list based on count
    if num_chapters != current_count:
        update_chapters_count(part_key, num_chapters, part_chapters, part_num)
        st.rerun()
    
    # Chapter details configuration
    if num_chapters > 0:
        render_chapter_details(part_num, part_chapters, config)
        
        # Individual create button for this part
        part_button_col1, part_button_col2 = st.columns(2)
        with part_button_col1:
            if st.button(f"🏗️ Create Part {part_num} Chapters", key=f"create_part_{part_num}"):
                create_chapters_for_part(config, part_num, part_chapters)
        
        with part_button_col2:
            if SessionManager.get('chapters_created') and any(part_chapters):
                if st.button(f"🔄 Update Part {part_num} Chapters", key=f"update_part_{part_num}"):
                    update_existing_chapters_for_part(config, part_num, part_chapters)

def update_chapters_count(part_key: str, num_chapters: int, current_chapters: List, part_num: int):
    """Update the number of chapters for a part with auto-numbering"""
    chapters_config = SessionManager.get('chapters_config', {})
    
    if num_chapters > len(current_chapters):
        # Add new chapters with auto-generated numbers
        for i in range(len(current_chapters), num_chapters):
            auto_number = get_chapter_number_format(part_num, i)
            current_chapters.append({'number': auto_number, 'name': ''})
    else:
        # Remove extra chapters
        current_chapters = current_chapters[:num_chapters]
    
    chapters_config[part_key] = current_chapters
    SessionManager.set('chapters_config', chapters_config)

def update_chapter_numbering_system(part_num: int):
    """Update all chapter numbers when numbering system changes"""
    part_key = f"Part_{part_num}"
    chapters_config = SessionManager.get('chapters_config', {})
    current_chapters = chapters_config.get(part_key, [])
    
    if current_chapters:
        # Update all chapter numbers based on new system
        for i, chapter in enumerate(current_chapters):
            new_number = get_chapter_number_format(part_num, i)
            current_chapters[i]['number'] = new_number
        
        chapters_config[part_key] = current_chapters
        SessionManager.set('chapters_config', chapters_config)

def render_chapter_details(part_num: int, chapters: List[Dict], config: Dict):
    """Render detailed configuration for each chapter with rename detection"""
    
    st.markdown(f"**Configure chapters for Part {part_num}:**")
    
    # Get old chapters config for comparison
    old_chapters_config = SessionManager.get('chapters_config', {})
    old_chapters = old_chapters_config.get(f"Part_{part_num}", [])
    
    updated_chapters = []
    safe_code = FolderManager.sanitize_name(config['code'])
    book_name = config['book_name']
    base_name = f"{safe_code}_{book_name}"
    
    for i, chapter in enumerate(chapters):
        col1, col2 = st.columns(2)
        
        with col1:
            auto_number = get_chapter_number_format(part_num, i)
            chapter_number = st.text_input(
                "Number",
                value=chapter.get('number', auto_number),
                placeholder=f"e.g., {auto_number}",
                key=f"chapter_num_{part_num}_{i}",
                help="Chapter number will auto-populate based on selected system"
            )
        
        with col2:
            chapter_name = st.text_input(
                "Name",
                value=chapter.get('name', ''),
                placeholder="e.g., Introduction, Basics (leave empty for 'Null Name')",
                key=f"chapter_name_{part_num}_{i}",
                help="Leave empty to use 'Null Name' in folder naming"
            )
        
        updated_chapters.append({
            'number': chapter_number,
            'name': chapter_name
        })
        
        # Show preview of folder name
        preview_name = ChapterManager.generate_chapter_folder_name(
            f"{base_name}_Part_{part_num}",
            chapter_number or None,
            chapter_name or None
        )
        st.caption(f"📁 Folder: `{preview_name}`")
        
        if i < len(chapters) - 1:
            st.markdown("---")
    
    # Check for chapter name/number changes and handle file renaming
    if len(old_chapters) == len(updated_chapters) and SessionManager.get('chapters_created'):
        handle_chapter_renaming(part_num, old_chapters, updated_chapters, config)
    
    # Update session state
    chapters_config = SessionManager.get('chapters_config', {})
    chapters_config[f"Part_{part_num}"] = updated_chapters
    SessionManager.set('chapters_config', chapters_config)

def handle_chapter_renaming(part_num: int, old_chapters: List[Dict], new_chapters: List[Dict], config: Dict):
    """Handle renaming of chapter files when chapter details change"""
    folder_metadata = SessionManager.get('folder_metadata', {})
    safe_code = FolderManager.sanitize_name(config['code'])
    book_name = config['book_name']
    base_name = f"{safe_code}_{book_name}"
    part_folder_name = f"{base_name}_Part_{part_num}"
    
    for i, (old_chapter, new_chapter) in enumerate(zip(old_chapters, new_chapters)):
        # Check if chapter name/number changed
        old_name = old_chapter.get('name', '').strip()
        old_number = old_chapter.get('number', '').strip()
        new_name = new_chapter.get('name', '').strip()
        new_number = new_chapter.get('number', '').strip()
        
        if old_name != new_name or old_number != new_number:
            # Find corresponding chapter folder and rename files
            for folder_id, metadata in folder_metadata.items():
                if (metadata['type'] == 'chapter' and 
                    metadata['parent_part'] == part_num and
                    metadata['chapter_number'] == old_number and
                    metadata['chapter_name'] == old_name):
                    
                    # Update metadata
                    metadata['chapter_number'] = new_number
                    metadata['chapter_name'] = new_name
                    
                    # Generate new naming base
                    new_naming_base = ChapterManager.generate_chapter_folder_name(
                        part_folder_name, new_number or None, new_name or None
                    )
                    
                    # Rename files and folder
                    if ChapterManager.rename_chapter_files(folder_id, new_naming_base):
                        st.success(f"📝 Renamed files in chapter {i+1}")
                    
                    # Update display name and naming base
                    display_chapter_name = new_naming_base.split(f'{part_folder_name}_')[-1]
                    metadata['display_name'] = f"Part {part_num} → {display_chapter_name}"
                    metadata['naming_base'] = new_naming_base
                    break
    
    SessionManager.set('folder_metadata', folder_metadata)

def render_chapter_preview(config: Dict):
    """Render chapter structure preview"""
    st.subheader("📋 Structure Preview")
    
    chapters_config = SessionManager.get('chapters_config', {})
    
    if not any(chapters_config.values()):
        st.info("Configure chapters to see preview")
        return
    
    safe_code = FolderManager.sanitize_name(config['code'])
    book_name = config['book_name']
    base_name = f"{safe_code}_{book_name}"
    
    for part_key, chapters in chapters_config.items():
        if chapters:
            part_num = part_key.split('_')[1]
            st.markdown(f"**Part {part_num}:**")
            
            preview_chapters = ChapterManager.get_chapters_preview(
                base_name, int(part_num), chapters
            )
            
            for chapter_folder in preview_chapters:
                st.write(f"📂 {chapter_folder}")
            
            st.markdown("---")

def create_chapters_for_part(config: Dict, part_num: int, chapters: List[Dict]):
    """Create chapters for a specific part only"""
    if not chapters or not any(ch.get('number') or ch.get('name') for ch in chapters):
        st.warning(f"No chapters configured for Part {part_num}!")
        return
    
    try:
        with st.spinner(f"Creating chapters for Part {part_num}..."):
            safe_code = FolderManager.sanitize_name(config['code'])
            book_name = config['book_name']
            base_name = f"{safe_code}_{book_name}"
            
            # Use consistent path resolution
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
                st.info(f"Created project directory: {project_path.absolute()}")
            
            # Validate chapters before creating
            is_valid, error_msg = ChapterManager.validate_chapter_data(chapters)
            if not is_valid:
                st.error(f"Error in Part {part_num}: {error_msg}")
                return
            
            created_chapters = ChapterManager.create_chapter_folders(
                project_path, base_name, part_num, chapters
            )
            
            if created_chapters:
                SessionManager.set('chapters_created', True)
                # Update created folders list
                current_folders = SessionManager.get('created_folders', [])
                current_folders.extend(created_chapters)
                SessionManager.set('created_folders', current_folders)
                
                st.success(f"✅ Created {len(created_chapters)} chapters for Part {part_num}!")
                
                # Show created chapters
                with st.expander(f"📂 View Created Chapters for Part {part_num}"):
                    for chapter in created_chapters:
                        st.write(f"📂 {chapter}")
    
    except Exception as e:
        st.error(f"Error creating chapters for Part {part_num}: {str(e)}")
        st.error(f"Debug info: Tried to find project at {base_name}")
        st.error(f"Current working directory: {Path.cwd()}")

def create_all_chapters(config: Dict, chapters_config: Dict):
    """Create all configured chapters with unique IDs and metadata tracking"""
    
    if not any(chapters_config.values()):
        st.warning("No chapters configured!")
        return
    
    try:
        with st.spinner("Creating chapter folders..."):
            safe_code = FolderManager.sanitize_name(config['code'])
            book_name = config['book_name']
            base_name = f"{safe_code}_{book_name}"
            
            # Use consistent path resolution
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
                st.info(f"Created project directory: {project_path.absolute()}")
            
            all_created_chapters = []
            
            for part_key, chapters in chapters_config.items():
                if chapters and any(ch.get('number') or ch.get('name') for ch in chapters):
                    part_num = int(part_key.split('_')[1])
                    
                    # Validate chapters before creating
                    is_valid, error_msg = ChapterManager.validate_chapter_data(chapters)
                    if not is_valid:
                        st.error(f"Error in Part {part_num}: {error_msg}")
                        continue
                    
                    created_chapters = ChapterManager.create_chapter_folders(
                        project_path, base_name, part_num, chapters
                    )
                    all_created_chapters.extend(created_chapters)
            
            if all_created_chapters:
                SessionManager.set('chapters_created', True)
                # Update created folders list
                current_folders = SessionManager.get('created_folders', [])
                current_folders.extend(all_created_chapters)
                SessionManager.set('created_folders', current_folders)
                
                st.success(f"✅ Created {len(all_created_chapters)} chapter folders successfully!")
                
                # Show created chapters
                with st.expander("📂 View Created Chapters"):
                    for chapter in all_created_chapters:
                        st.write(f"📂 {chapter}")
            else:
                st.warning("No chapter folders created. Please configure chapters first.")
    
    except Exception as e:
        st.error(f"Error creating chapters: {str(e)}")
        st.error(f"Debug info: Tried to find project at {base_name}")
        st.error(f"Current working directory: {Path.cwd()}")

def update_existing_chapters_for_part(config: Dict, part_num: int, chapters: List[Dict]):
    """Update existing chapters for a specific part"""
    try:
        with st.spinner(f"Updating chapters for Part {part_num}..."):
            st.success(f"✅ Updated chapters for Part {part_num}!")
            st.info("Chapter updates are handled automatically when you modify names/numbers.")
    except Exception as e:
        st.error(f"Error updating chapters for Part {part_num}: {str(e)}")


# ===== File: src/ui/custom_folder_management.py =====

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


# ===== File: src/ui/main_content.py =====

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
                # FIXED: Keep book name as-is instead of sanitizing
                base_name = f"{safe_code}_{book_name}"
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


# ===== File: src/ui/page_assignment.py =====

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


# ===== File: src/ui/progress_tracker.py =====


# src/ui/progress_tracker.py
import streamlit as st
from typing import List, Tuple
from core.session_manager import SessionManager

def render_progress_tracker():
    """Render progress tracking section"""
    st.subheader("🗺️ Progress")
    
    progress_steps = get_progress_steps()
    
    for i, (step, completed) in enumerate(progress_steps, 1):
        status = "✅" if completed else "⭕"
        st.write(f"{status} Step {i}: {step}")

def get_progress_steps() -> List[Tuple[str, bool]]:
    """Get current progress steps and their completion status"""
    config = SessionManager.get('project_config', {})
    extraction_history = SessionManager.get('extraction_history', [])
    
    return [
        ("Upload PDF", SessionManager.get('pdf_uploaded')),
        ("Configure Project", bool(config.get('code') and config.get('book_name'))),
        ("Set Parts", config.get('num_parts', 0) > 0),
        ("Create Structure", SessionManager.get('folder_structure_created')),
        ("Configure Chapters", SessionManager.get('chapters_created')),
        ("Extract Pages", len(extraction_history) > 0)
    ]



# ===== File: src/ui/sidebar.py =====

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
