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


# src/__init__.py
# Empty file to make src a Python package


# src/core/__init__.py  
# Empty file to make core a Python package


# src/ui/__init__.py
# Empty file to make ui a Python package


# src/core/session_manager.py
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
            'extraction_history': []  # Track completed extractions
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


# src/core/pdf_handler.py
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
        Load PDF and extract basic information
        
        Args:
            uploaded_file: Streamlit uploaded file object
            
        Returns:
            Tuple of (PDF reader object, total pages)
        """
        try:
            # Read file content once and store
            file_content = uploaded_file.read()
            pdf_reader = PyPDF2.PdfReader(BytesIO(file_content))
            total_pages = len(pdf_reader.pages)
            
            # Store content in session for reuse
            st.session_state.pdf_content = file_content
            
            return pdf_reader, total_pages
        except Exception as e:
            st.error(f"Error reading PDF: {str(e)}")
            return None, 0
    
    @staticmethod
    def get_pdf_reader() -> Optional[PyPDF2.PdfReader]:
        """Get PDF reader from stored content"""
        try:
            pdf_content = st.session_state.get('pdf_content')
            if pdf_content:
                return PyPDF2.PdfReader(BytesIO(pdf_content))
            return None
        except Exception as e:
            st.error(f"Error accessing PDF: {str(e)}")
            return None
    
    @staticmethod
    def validate_pdf(uploaded_file) -> bool:
        """Validate if uploaded file is a proper PDF"""
        try:
            pdf_reader = PyPDF2.PdfReader(BytesIO(uploaded_file.read()))
            return len(pdf_reader.pages) > 0
        except:
            return False


class PDFExtractor:
    """Handles PDF page extraction and file creation"""
    
    @staticmethod
    def extract_pages_to_folder(page_ranges: List[str], destination_folder: str, 
                              folder_name: str, total_pages: int) -> Tuple[bool, List[str], str]:
        """
        Extract specified pages from PDF and save to destination folder
        
        Args:
            page_ranges: List of page range strings (e.g., ["1-5", "10", "15-20"])
            destination_folder: Target folder path
            folder_name: Folder name for file naming
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
            
            # Extract each page
            for page_num in pages_to_extract:
                success, file_path = PDFExtractor.extract_single_page(
                    pdf_reader, page_num, dest_path, folder_name
                )
                
                if success:
                    created_files.append(file_path)
                else:
                    failed_pages.append(page_num)
            
            # Report results
            if failed_pages:
                warning_msg = f"Failed to extract pages: {', '.join(map(str, failed_pages))}"
                st.warning(warning_msg)
            
            success_status = len(created_files) > 0
            return success_status, created_files, ""
            
        except Exception as e:
            return False, [], f"Error extracting pages: {str(e)}"
    
    @staticmethod
    def extract_single_page(pdf_reader: PyPDF2.PdfReader, page_num: int, 
                          dest_path: Path, folder_name: str) -> Tuple[bool, str]:
        """
        Extract a single page from PDF
        
        Args:
            pdf_reader: PDF reader object
            page_num: Page number to extract (1-indexed)
            dest_path: Destination folder path
            folder_name: Base folder name for file naming
            
        Returns:
            Tuple of (success, file_path)
        """
        try:
            # Validate page number
            if page_num < 1 or page_num > len(pdf_reader.pages):
                return False, f"Page {page_num} out of range"
            
            # Create new PDF with single page
            pdf_writer = PyPDF2.PdfWriter()
            pdf_writer.add_page(pdf_reader.pages[page_num - 1])  # Convert to 0-indexed
            
            # Generate file name (sanitize folder name)
            safe_folder_name = PDFExtractor.sanitize_filename(folder_name)
            file_name = f"{safe_folder_name}_page_{page_num}.pdf"
            file_path = dest_path / file_name
            
            # Write PDF file
            with open(file_path, 'wb') as output_file:
                pdf_writer.write(output_file)
            
            return True, str(file_path)
            
        except Exception as e:
            st.error(f"Error extracting page {page_num}: {str(e)}")
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


# src/core/folder_manager.py
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
            book_name: Book name
            
        Returns:
            Tuple of (project path, list of created folders)
        """
        if not code or not book_name:
            return None, []
        
        try:
            # Sanitize names for folder creation
            safe_code = FolderManager.sanitize_name(code)
            safe_book_name = FolderManager.sanitize_name(book_name)
            base_name = f"{safe_code}_{safe_book_name}"
            
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
                part_folder = project_path / f"{base_name}_part_{i}"
                part_folder.mkdir(exist_ok=True)
                created_parts.append(str(part_folder.absolute()))
            
            return created_parts
        except Exception as e:
            st.error(f"Error creating part folders: {str(e)}")
            return []
    
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
        safe_book_name = FolderManager.sanitize_name(book_name)
        base_name = f"{safe_code}_{safe_book_name}"
        preview = []
        
        # Default folders
        for folder in FolderManager.DEFAULT_FOLDERS:
            preview.append(f"{base_name}_{folder}")
        
        # Part folders
        for i in range(1, num_parts + 1):
            preview.append(f"{base_name}_part_{i}")
        
        return preview


class ChapterManager:
    """Manages chapter creation and organization within parts"""
    
    @staticmethod
    def generate_chapter_folder_name(parent_folder: str, chapter_number: str = None, 
                                   chapter_name: str = None) -> str:
        """
        Generate chapter folder name following the convention:
        {parent_folder_name}_chapter_{chapter_number}_{chapter_name}
        
        Args:
            parent_folder: Parent folder name
            chapter_number: Chapter number (can be None)
            chapter_name: Chapter name (can be None)
            
        Returns:
            Properly formatted chapter folder name
        """
        # Handle missing values
        chapter_num = chapter_number if chapter_number else "null"
        chapter_nm = FolderManager.sanitize_name(chapter_name) if chapter_name else "null"
        
        # If both are null, add random number for uniqueness
        if chapter_num == "null" and chapter_nm == "null":
            random_num = random.randint(10000, 99999)
            return f"{parent_folder}_chapter_{chapter_num}_{chapter_nm}_{random_num}"
        
        return f"{parent_folder}_chapter_{chapter_num}_{chapter_nm}"
    
    @staticmethod
    def create_chapter_folders(project_path: Path, base_name: str, part_number: int, 
                             chapters: List[Dict]) -> List[str]:
        """
        Create chapter folders within a part
        
        Args:
            project_path: Main project path
            base_name: Base project name
            part_number: Part number
            chapters: List of chapter dictionaries with 'number' and 'name'
            
        Returns:
            List of created chapter folder paths
        """
        created_chapters = []
        part_folder_name = f"{base_name}_part_{part_number}"
        part_path = project_path / part_folder_name
        
        try:
            # Ensure part folder exists
            part_path.mkdir(exist_ok=True)
            
            for chapter in chapters:
                chapter_folder_name = ChapterManager.generate_chapter_folder_name(
                    part_folder_name,
                    chapter.get('number'),
                    chapter.get('name')
                )
                
                # Create chapter folder inside the part folder
                chapter_path = part_path / chapter_folder_name.split(f"{part_folder_name}_")[-1]
                chapter_path.mkdir(exist_ok=True)
                created_chapters.append(str(chapter_path.absolute()))
            
            return created_chapters
        except Exception as e:
            st.error(f"Error creating chapter folders: {str(e)}")
            return []
    
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
        
        # Check for duplicate chapter numbers (if provided)
        numbers = [ch.get('number') for ch in chapters if ch.get('number') and ch.get('number') != '']
        if len(numbers) != len(set(numbers)):
            return False, "Duplicate chapter numbers found"
        
        return True, ""


# src/ui/app_layout.py
import streamlit as st
from ui.sidebar import render_sidebar
from ui.main_content import render_main_content
from ui.progress_tracker import render_progress_tracker
from ui.chapter_management import render_chapter_management_page
from ui.page_assignment import render_page_assignment_page
from core.session_manager import SessionManager

def setup_page_config():
    """Configure Streamlit page settings"""
    st.set_page_config(
        page_title="PDF Page Organizer",
        page_icon="📚",
        layout="wide",
        initial_sidebar_state="expanded"
    )

def render_main_app():
    """Render the main application layout"""
    st.title("📚 PDF Page Organizer")
    
    # Navigation tabs
    tab1, tab2, tab3 = st.tabs(["📋 Project Setup", "📂 Chapter Management", "📄 Page Assignment"])
    
    with tab1:
        render_project_setup_tab()
    
    with tab2:
        render_chapter_management_page()
    
    with tab3:
        render_page_assignment_page()

def render_project_setup_tab():
    """Render the project setup tab"""
    st.markdown("---")
    render_sidebar()
    render_main_content()


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
        placeholder="e.g., DataStructures",
        help="Book name (will be used in folder names)"
    )
    
    if code and book_name:
        SessionManager.update_config({'code': code, 'book_name': book_name})
        display_folder_preview(code, book_name)

def display_folder_preview(code: str, book_name: str):
    """Display preview of folder naming convention"""
    preview_folders = FolderManager.get_folder_preview(code, book_name, 1)
    
    st.markdown("**Preview folder naming:**")
    preview_text = "\n".join(preview_folders[:3])  # Show first 3 as preview
    st.code(preview_text)

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


# src/ui/chapter_management.py
import streamlit as st
from typing import Dict, List
from core.session_manager import SessionManager
from core.folder_manager import ChapterManager, FolderManager
from pathlib import Path

def render_chapter_management_page():
    """Render the chapter management page"""
    
    # Check prerequisites
    if not SessionManager.get('folder_structure_created'):
        render_prerequisites_warning()
        return
    
    config = SessionManager.get('project_config', {})
    num_parts = config.get('num_parts', 0)
    
    if num_parts == 0:
        st.info("📝 No parts configured. Chapters are only needed when you have parts defined.")
        return
    
    st.subheader("📂 Chapter Management")
    st.markdown("Configure chapters within each part of your book.")
    
    # Chapter configuration for each part
    col1, col2 = st.columns([2, 1])
    
    with col1:
        render_chapter_configuration(config, num_parts)
    
    with col2:
        render_chapter_preview(config)

def render_prerequisites_warning():
    """Render warning when prerequisites are not met"""
    st.warning("⚠️ Please complete the project setup first!")
    st.markdown("""
    **Required steps:**
    1. Upload PDF file
    2. Configure project details
    3. Create folder structure
    """)

def render_chapter_configuration(config: Dict, num_parts: int):
    """Render chapter configuration interface"""
    
    chapters_config = SessionManager.get('chapters_config', {})
    
    for part_num in range(1, num_parts + 1):
        with st.expander(f"📖 Part {part_num} Chapters", expanded=part_num == 1):
            render_part_chapters(part_num, chapters_config, config)
    
    # Create chapters button
    if any(chapters_config.values()):  # Only show if chapters are configured
        if st.button("🏗️ Create All Chapters", type="primary"):
            create_all_chapters(config, chapters_config)

def render_part_chapters(part_num: int, chapters_config: Dict, config: Dict):
    """Render chapter configuration for a specific part"""
    
    part_key = f"part_{part_num}"
    part_chapters = chapters_config.get(part_key, [])
    
    # Number of chapters input
    num_chapters = st.number_input(
        f"Number of chapters in Part {part_num}",
        min_value=0,
        max_value=100,
        value=len(part_chapters),
        step=1,
        key=f"chapters_count_{part_num}"
    )
    
    # Update chapters list based on count
    if num_chapters != len(part_chapters):
        update_chapters_count(part_key, num_chapters, part_chapters)
        st.rerun()
    
    # Chapter details configuration
    if num_chapters > 0:
        render_chapter_details(part_num, part_chapters, config)

def update_chapters_count(part_key: str, num_chapters: int, current_chapters: List):
    """Update the number of chapters for a part"""
    chapters_config = SessionManager.get('chapters_config', {})
    
    if num_chapters > len(current_chapters):
        # Add new chapters
        for i in range(len(current_chapters), num_chapters):
            current_chapters.append({'number': str(i + 1), 'name': ''})
    else:
        # Remove extra chapters
        current_chapters = current_chapters[:num_chapters]
    
    chapters_config[part_key] = current_chapters
    SessionManager.set('chapters_config', chapters_config)

def render_chapter_details(part_num: int, chapters: List[Dict], config: Dict):
    """Render detailed configuration for each chapter"""
    
    st.markdown(f"**Configure chapters for Part {part_num}:**")
    
    updated_chapters = []
    safe_code = FolderManager.sanitize_name(config['code'])
    safe_book_name = FolderManager.sanitize_name(config['book_name'])
    base_name = f"{safe_code}_{safe_book_name}"
    
    for i, chapter in enumerate(chapters):
        col1, col2 = st.columns(2)
        
        with col1:
            chapter_number = st.text_input(
                "Number",
                value=chapter.get('number', ''),
                placeholder="e.g., 1, 1.1, A",
                key=f"chapter_num_{part_num}_{i}"
            )
        
        with col2:
            chapter_name = st.text_input(
                "Name",
                value=chapter.get('name', ''),
                placeholder="e.g., Introduction, Basics",
                key=f"chapter_name_{part_num}_{i}"
            )
        
        updated_chapters.append({
            'number': chapter_number,
            'name': chapter_name
        })
        
        # Show preview of folder name
        preview_name = ChapterManager.generate_chapter_folder_name(
            f"{base_name}_part_{part_num}",
            chapter_number or None,
            chapter_name or None
        )
        st.caption(f"📁 Folder: `{preview_name}`")
        
        if i < len(chapters) - 1:  # Don't show separator after last chapter
            st.markdown("---")
    
    # Update session state
    chapters_config = SessionManager.get('chapters_config', {})
    chapters_config[f"part_{part_num}"] = updated_chapters
    SessionManager.set('chapters_config', chapters_config)

def render_chapter_preview(config: Dict):
    """Render chapter structure preview"""
    st.subheader("📋 Structure Preview")
    
    chapters_config = SessionManager.get('chapters_config', {})
    
    if not any(chapters_config.values()):
        st.info("Configure chapters to see preview")
        return
    
    safe_code = FolderManager.sanitize_name(config['code'])
    safe_book_name = FolderManager.sanitize_name(config['book_name'])
    base_name = f"{safe_code}_{safe_book_name}"
    
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

def create_all_chapters(config: Dict, chapters_config: Dict):
    """Create all configured chapters"""
    
    if not any(chapters_config.values()):
        st.warning("No chapters configured!")
        return
    
    try:
        with st.spinner("Creating chapter folders..."):
            safe_code = FolderManager.sanitize_name(config['code'])
            safe_book_name = FolderManager.sanitize_name(config['book_name'])
            base_name = f"{safe_code}_{safe_book_name}"
            project_path = Path(base_name)
            
            if not project_path.exists():
                st.error("Project folder not found. Please create folder structure first.")
                return
            
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


# src/ui/page_assignment.py
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
    
    destination_folder = render_folder_selection(folder_type, available_folders)
    
    if destination_folder:
        render_page_range_input(destination_folder)

def get_available_folders() -> Dict[str, List[str]]:
    """Get all available folders organized by type"""
    config = SessionManager.get('project_config', {})
    chapters_config = SessionManager.get('chapters_config', {})
    
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
        folders['default'].append(f"{base_name}_{folder}")
    
    # Part folders
    num_parts = config.get('num_parts', 0)
    for i in range(1, num_parts + 1):
        folders['parts'].append(f"{base_name}_part_{i}")
    
    # Chapter folders (updated to show they are inside parts)
    for part_key, chapters in chapters_config.items():
        if chapters:
            part_num = int(part_key.split('_')[1])
            for chapter in chapters:
                if chapter.get('number') or chapter.get('name'):  # Only include configured chapters
                    chapter_folder = ChapterManager.generate_chapter_folder_name(
                        f"{base_name}_part_{part_num}",
                        chapter.get('number'),
                        chapter.get('name')
                    )
                    # Extract just the chapter part for display (it will be inside the part folder)
                    chapter_name_only = chapter_folder.split(f"{base_name}_part_{part_num}_")[-1]
                    folders['chapters'].append(f"Part {part_num} → {chapter_name_only}")
    
    return folders

def render_folder_selection(folder_type: str, available_folders: Dict[str, List[str]]) -> str:
    """Render folder selection based on type"""
    
    folder_mapping = {
        "Default Folders": "default",
        "Parts": "parts", 
        "Chapters": "chapters"
    }
    
    folder_key = folder_mapping[folder_type]
    folders = available_folders[folder_key]
    
    if not folders:
        st.info(f"No {folder_type.lower()} available.")
        return ""
    
    selected_folder = st.selectbox(
        f"Select {folder_type[:-1]}",
        folders,
        help=f"Choose the specific {folder_type.lower()[:-1]} to assign pages to"
    )
    
    return selected_folder

def render_page_range_input(destination_folder: str):
    """Render page range input and extraction controls"""
    
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
                render_assignment_preview(destination_folder, page_ranges, total_pages)
    
    with col2:
        extract_disabled = not page_ranges_text.strip()
        if st.button("🚀 Extract Pages", type="primary", disabled=extract_disabled):
            if page_ranges_text.strip():
                page_ranges = [r.strip() for r in page_ranges_text.split(',') if r.strip()]
                execute_page_extraction(destination_folder, page_ranges, total_pages)
    
    # Show preview of page ranges if text is entered
    if page_ranges_text.strip():
        page_ranges = [r.strip() for r in page_ranges_text.split(',') if r.strip()]
        preview = PDFExtractor.preview_page_extraction(page_ranges, total_pages)
        
        if "No valid pages" in preview:
            st.error(preview)
        else:
            st.info(preview)

def render_assignment_preview(destination_folder: str, page_ranges: List[str], total_pages: int):
    """Render preview of page assignment"""
    
    pages = PDFExtractor.parse_page_ranges(page_ranges, total_pages)
    
    if pages:
        st.success(f"Ready to extract {len(pages)} pages to: `{destination_folder}`")
        
        with st.expander("📋 Detailed Preview", expanded=True):
            st.markdown("**Files that will be created:**")
            safe_folder_name = PDFExtractor.sanitize_filename(destination_folder)
            
            # Show first 10 files as preview
            preview_count = min(10, len(pages))
            for page in pages[:preview_count]:
                file_name = f"{safe_folder_name}_page_{page}.pdf"
                st.write(f"📄 {file_name}")
            
            if len(pages) > preview_count:
                st.write(f"... and {len(pages) - preview_count} more files")
                
            st.markdown(f"**Destination:** `{destination_folder}`")
    else:
        st.error("No valid pages found in the specified ranges")

def execute_page_extraction(destination_folder: str, page_ranges: List[str], total_pages: int):
    """Execute the page extraction process"""
    
    config = SessionManager.get('project_config', {})
    
    if not config.get('code') or not config.get('book_name'):
        st.error("Project not configured properly. Please complete project setup.")
        return
    
    # Handle chapter folder path determination
    safe_code = FolderManager.sanitize_name(config['code'])
    safe_book_name = FolderManager.sanitize_name(config['book_name'])
    base_name = f"{safe_code}_{safe_book_name}"
    
    # Check if this is a chapter folder (contains "Part X →")
    if "Part " in destination_folder and " → " in destination_folder:
        # Extract part number and chapter name
        part_info, chapter_info = destination_folder.split(" → ")
        part_num = part_info.split("Part ")[-1]
        
        # Build the actual folder path: base/part/chapter
        part_folder = f"{base_name}_part_{part_num}"
        chapter_folder = f"chapter_{chapter_info}"
        folder_path = Path(base_name) / part_folder / chapter_folder
        
        # For naming, use the full chapter name
        file_naming_base = f"{part_folder}_chapter_{chapter_info}"
    else:
        # Regular folder (default or part)
        folder_path = Path(base_name) / destination_folder
        file_naming_base = destination_folder
    
    # Progress bar
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        # Execute extraction
        status_text.text(f"Extracting pages to {destination_folder}...")
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
                'destination': destination_folder,
                'pages_extracted': len(created_files),
                'page_ranges': page_ranges,
                'files_created': created_files
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