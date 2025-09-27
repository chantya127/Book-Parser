# core/folder_manager.py - Modified to support standalone chapters

from pathlib import Path
from typing import List, Tuple, Optional, Dict
import streamlit as st
import os

class FolderManager:
    """Manages folder structure creation and organization"""
    
    DEFAULT_FOLDERS = ['prologue', 'index', 'epilogue']
    
    @staticmethod
    def get_default_folder_options() -> List[Dict[str, str]]:
        """Get available default folder options with descriptions"""
        return [
        {'name': 'Prologue', 'description': 'Introduction or preface content'},
        {'name': 'Index', 'description': 'Table of contents, index, or reference pages'},
        {'name': 'Epilogue', 'description': 'Conclusion, appendix, or closing content'},
        {'name': 'Bibliography', 'description': 'References and citations'},
        {'name': 'Glossary', 'description': 'Terms and definitions'},
        {'name': 'Exercises', 'description': 'Practice problems and solutions'},
        {'name': 'Notes', 'description': 'Additional notes and annotations'},

        # New values
        {'name': 'Cover', 'description': 'Book cover page'},
        {'name': 'Whole Book', 'description': 'Entire content of the book'},
        {'name': 'Front Index', 'description': 'Index at the beginning of the book'},
        {'name': 'Back Index', 'description': 'Index at the end of the book'},
        {'name': 'Prologue_Name', 'description': 'Specific prologue title (e.g., Prologue_April 1942)'},
        {'name': 'Epilogue_Name', 'description': 'Specific epilogue title (e.g., Epilogue_April 1942)'},
        {'name': 'Preface', 'description': 'Introductory remarks before main text'},
        {'name': 'Timeline', 'description': 'Chronological events and timeline'},
        {'name': 'About The Author', 'description': 'Details about the author'},
        {'name': 'Author Note', 'description': 'Notes directly from the author'},
        {'name': "Author's Note", 'description': 'Author’s additional remarks'},
        {'name': 'Content', 'description': 'Main content of the book'},
        {'name': 'Contents', 'description': 'List of book contents'},
        {'name': 'Postscript', 'description': 'Additional message after the main content'},
        {'name': 'Introduction', 'description': 'Introductory content before chapters'},
        {'name': 'List Of Illustrations', 'description': 'Catalog of illustrations used'},
        {'name': 'List Of Maps', 'description': 'Catalog of maps included'},
        {'name': 'Acknowledgement', 'description': 'Credits and acknowledgements'},
        {'name': 'Acknowledgements', 'description': 'Acknowledgements to contributors'},
        {'name': 'Author Q&A', 'description': 'Questions and answers with the author'},
        {'name': 'Reading Group Questions', 'description': 'Questions for reading groups'},
        {'name': "Reader's Questions & Answers", 'description': 'Q&A from readers'},
        {'name': "Readers' Questions & Answers", 'description': 'Multiple readers’ Q&A'},
        {'name': 'Author And Translator Biographies', 'description': 'Biographies of author and translator'},
        {'name': "Author's Acknowledgements", 'description': 'Acknowledgements from the author'},
        {'name': 'Characters', 'description': 'List of characters'},
        {'name': 'Characters List', 'description': 'Detailed character list'},
        {'name': 'Map', 'description': 'Single map'},
        {'name': 'Maps', 'description': 'Multiple maps'},
        {'name': 'A Conversation With', 'description': 'Dialogue with the author or others'},
        {'name': 'A Guide For Reading Groups', 'description': 'Guide for reading group discussions'},
        {'name': 'Enhance Your Bookclub', 'description': 'Content to enrich book club experience'},
        {'name': 'Closing Credits', 'description': 'Closing acknowledgements and credits'},
        {'name': 'More From', 'description': 'More works from the author or publisher'},
        {'name': 'Coming Soon', 'description': 'Preview of upcoming works'},
        {'name': 'Extract From', 'description': 'Excerpt from another book or content'}
    ]

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
    def create_project_structure(code: str, book_name: str, selected_folders: List[str] = None) -> Tuple[Optional[Path], List[str]]:
        """
        Create the basic project folder structure with selected default folders in specified location
        """
        if not code or not book_name:
            return None, []
        
        try:
            # Lazy import to avoid circular dependency
            from core.text_formatter import TextFormatter
            from core.session_manager import SessionManager
            
            # Get font case and apply formatting
            font_case = st.session_state.get('selected_font_case', 'First Capital (Sentence case)')
            formatted_code = TextFormatter.format_project_code(code, font_case)
            formatted_book_name = TextFormatter.format_book_name(book_name, font_case)
            
            # Sanitize the code but keep book name as-is with only font formatting
            safe_code = FolderManager.sanitize_name(formatted_code)
            base_name = f"{safe_code}_{formatted_book_name}"
            
            # Get project destination - if set, use it; otherwise use current directory
            project_destination = SessionManager.get_project_destination()
            if project_destination and os.path.exists(project_destination):
                base_path = Path(project_destination)
            else:
                base_path = Path.cwd()
            
            # Create main project folder in the specified location
            project_path = base_path / base_name
            project_path.mkdir(exist_ok=True)
            
            created_folders = []
            
            # Create only selected default folders with formatting
            if selected_folders:
                for folder in selected_folders:
                    formatted_folder = TextFormatter.format_folder_name(folder, font_case)
                    folder_path = project_path / f"{base_name}_{formatted_folder}"
                    folder_path.mkdir(exist_ok=True)
                    created_folders.append(str(folder_path.absolute()))
            
            return project_path, created_folders
            
        except Exception as e:
            st.error(f"Error creating folder structure: {str(e)}")
            return None, []


    @staticmethod
    def create_custom_parts_folders(project_path: Path, base_name: str, custom_parts: Dict) -> List[str]:
        """Create custom named part folders with font formatting"""
        created_parts = []
        
        try:
            # Lazy import to avoid circular dependency
            from core.text_formatter import TextFormatter
            font_case = st.session_state.get('selected_font_case', 'First Capital (Sentence case)')
            
            for part_id, part_info in custom_parts.items():
                part_name = part_info['name']
                # Apply additional formatting if needed
                formatted_part_name = TextFormatter.format_part_name(part_name, font_case)
                
                # Create folder with format: {base_name}_{formatted_part_name}
                part_folder = project_path / f"{base_name}_{formatted_part_name}"
                part_folder.mkdir(exist_ok=True)
                created_parts.append(str(part_folder.absolute()))
            
            return created_parts
        except Exception as e:
            st.error(f"Error creating custom part folders: {str(e)}")
            return []


class ChapterManager:
    """Manages chapter creation and organization within parts and standalone"""
    
    
    @staticmethod
    def generate_chapter_folder_name(parent_folder: str, chapter_number: str = None, 
                                chapter_name: str = None) -> str:
        """
        Generate chapter folder name following the convention:
        {base_project_name}_Chapter {chapter_number}_{chapter_name}
        
        Args:
            parent_folder: Parent folder name
            chapter_number: Chapter number (can be None or NULL sequence format)
            chapter_name: Chapter name (can be None)
            
        Returns:
            Properly formatted chapter folder name with correct spacing
        """
        # Import here to avoid circular dependency
        import streamlit as st
        from core.text_formatter import TextFormatter
        
        # Get font case and format "Chapter" text
        font_case = st.session_state.get('selected_font_case', 'First Capital (Sentence case)')
        formatted_chapter_text = TextFormatter.format_text("Chapter", font_case)
        
        # Extract base name by removing the part suffix or use as-is for standalone
        if "_Part_" in parent_folder:
            base_name = parent_folder.split("_Part_")[0]
        else:
            # For custom parts or standalone chapters, find the base 
            parts = parent_folder.split("_")
            if len(parts) >= 3:
                base_name = "_".join(parts[:-1]) if not ChapterManager.is_project_root_folder(parent_folder) else parent_folder
            else:
                base_name = parent_folder
        
        # Handle missing values with improved formatting
        if chapter_number is None or chapter_number.strip() == "":
            # Apply font formatting to "Null" and create properly formatted null name
            formatted_null = TextFormatter.format_text("Null", font_case)
            chapter_num = f"{formatted_null} Null Name"
        else:
            chapter_num = chapter_number.strip()

        if chapter_name is None or chapter_name.strip() == "":
            # Apply font formatting to "Null Name" based on selected font case (space instead of underscore)
            chapter_nm = TextFormatter.format_text("Null Name", font_case)
        else:
            chapter_nm = chapter_name.strip()
        
        # Generate folder name with formatted "Chapter" text: {formatted_Chapter} {number}_{name}
        # Check if both are null values (now formatted according to font case)
        null_name_formatted = TextFormatter.format_text("Null Name", font_case)
        null_null_name_formatted = f"{TextFormatter.format_text('Null', font_case)} Null Name"

        if chapter_nm == null_name_formatted and chapter_num == null_null_name_formatted:
            import random
            random_num = random.randint(10000, 99999)
            return f"{base_name}_{formatted_chapter_text} {chapter_num}_{random_num}"

        return f"{base_name}_{formatted_chapter_text} {chapter_num}_{chapter_nm}"

    @staticmethod
    def is_project_root_folder(folder_path: str) -> bool:
        """Check if the folder is the project root (for standalone chapters)"""
        # Project root folders typically follow pattern: {code}_{book_name}
        # and don't contain _Part_ or other suffixes
        return "_Part_" not in folder_path and not any(suffix in folder_path for suffix in ["_prologue", "_index", "_epilogue"])
    
    @staticmethod
    def generate_unique_chapter_id(base_name: str, parent_identifier: str, is_standalone: bool = False) -> str:
        """Generate unique identifier for chapter - works with numbered, custom parts, and standalone"""
        from core.session_manager import SessionManager
        counter = SessionManager.get('unique_chapter_counter', 0) + 1
        SessionManager.set('unique_chapter_counter', counter)
        
        if is_standalone:
            return f"{base_name}_standalone_chapter_{counter}"
        else:
            return f"{base_name}_part_{parent_identifier}_chapter_{counter}"
    
    @staticmethod
    def create_standalone_chapter_folders(project_path: Path, base_name: str, chapters: List[Dict]) -> List[str]:
        """
        Create standalone chapter folders directly under project root
        
        Args:
            project_path: Main project path
            base_name: Base project name
            chapters: List of chapter dictionaries with 'number' and 'name'
            
        Returns:
            List of created chapter folder paths
        """
        from core.session_manager import SessionManager
        
        created_chapters = []
        
        try:
            # Ensure project folder exists
            project_path.mkdir(exist_ok=True)
            folder_metadata = SessionManager.get('folder_metadata', {})
            
            for chapter in chapters:
                # Generate unique ID for metadata tracking
                chapter_id = ChapterManager.generate_unique_chapter_id(
                    base_name, "standalone", is_standalone=True
                )
                
                # Generate proper chapter folder name using base project name
                chapter_folder_name = ChapterManager.generate_chapter_folder_name(
                    base_name,  # Use base_name directly for standalone chapters
                    chapter.get('number'),
                    chapter.get('name')
                )
                
                # Create actual folder with the complete naming convention
                chapter_path = project_path / chapter_folder_name
                chapter_path.mkdir(exist_ok=True)
                
                # Store metadata mapping
                display_name = f"Standalone → {chapter_folder_name}"
                folder_metadata[chapter_id] = {
                    'display_name': display_name,
                    'actual_path': str(chapter_path.absolute()),
                    'type': 'standalone_chapter',
                    'parent_type': 'standalone',
                    'chapter_number': chapter.get('number', ''),
                    'chapter_name': chapter.get('name', ''),
                    'naming_base': chapter_folder_name,  # Full name for file naming
                    'folder_name': chapter_folder_name   # Complete folder name
                }
                
                created_chapters.append(str(chapter_path.absolute()))
            
            SessionManager.set('folder_metadata', folder_metadata)
            return created_chapters
        except Exception as e:
            st.error(f"Error creating standalone chapter folders: {str(e)}")
            return []
    
    @staticmethod
    def create_chapter_folders_for_custom_part(project_path: Path, base_name: str, 
                                            part_name: str, chapters: List[Dict]) -> List[str]:
        """
        Create chapter folders within a custom named part
        
        Args:
            project_path: Main project path
            base_name: Base project name
            part_name: Custom part name (e.g., "India", "Iran")
            chapters: List of chapter dictionaries with 'number' and 'name'
            
        Returns:
            List of created chapter folder paths
        """
        from core.session_manager import SessionManager
        
        created_chapters = []
        part_folder_name = f"{base_name}_{part_name}"
        part_path = project_path / part_folder_name
        
        try:
            # Ensure part folder exists
            part_path.mkdir(exist_ok=True)
            folder_metadata = SessionManager.get('folder_metadata', {})
            
            for chapter in chapters:
                # Generate unique ID for metadata tracking
                chapter_id = ChapterManager.generate_unique_chapter_id(base_name, part_name.lower())
                
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
                display_name = f"{part_name} → {chapter_folder_name}"
                folder_metadata[chapter_id] = {
                    'display_name': display_name,
                    'actual_path': str(chapter_path.absolute()),
                    'type': 'chapter',
                    'parent_part_name': part_name,
                    'parent_part_type': 'custom',
                    'chapter_number': chapter.get('number', ''),
                    'chapter_name': chapter.get('name', ''),
                    'naming_base': chapter_folder_name,  # Full name for file naming
                    'folder_name': chapter_folder_name   # Complete folder name
                }
                
                created_chapters.append(str(chapter_path.absolute()))
            
            SessionManager.set('folder_metadata', folder_metadata)
            return created_chapters
        except Exception as e:
            st.error(f"Error creating chapter folders for {part_name}: {str(e)}")
            return []
    
    @staticmethod
    def create_chapter_folders(project_path: Path, base_name: str, part_number: int, 
                             chapters: List[Dict]) -> List[str]:
        """
        Create chapter folders within a part with proper naming convention
        KEPT FOR BACKWARD COMPATIBILITY - use create_chapter_folders_for_custom_part for new implementations
        
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
                chapter_id = ChapterManager.generate_unique_chapter_id(base_name, str(part_number))
                
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
                    'parent_part_type': 'numbered',
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
    def get_chapters_preview(base_name: str, parent_identifier: str, chapters: List[Dict], is_custom_part: bool = False, is_standalone: bool = False) -> List[str]:
        """Generate preview of chapter folder names - supports numbered, custom parts, and standalone chapters"""
        preview = []
        
        if is_standalone:
            parent_folder_name = base_name  # Use base name directly for standalone
        elif is_custom_part:
            parent_folder_name = f"{base_name}_{parent_identifier}"
        else:
            parent_folder_name = f"{base_name}_part_{parent_identifier}"
        
        for chapter in chapters:
            chapter_folder_name = ChapterManager.generate_chapter_folder_name(
                parent_folder_name,
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
        
        # Check for duplicate chapter numbers, but skip NULL sequence chapters
        # since they're supposed to have the same "NULL" number
        numbers_to_check = []
        for ch in chapters:
            chapter_number = ch.get('number')
            is_null_sequence = ch.get('is_null_sequence', False)
            
            # Only check for duplicates if:
            # 1. It's not a NULL sequence chapter
            # 2. The number is not empty/null
            # 3. The number is not literally "NULL"
            if (not is_null_sequence and 
                chapter_number and 
                chapter_number.strip() != '' and 
                not chapter_number.upper().startswith('NULL')):
                numbers_to_check.append(chapter_number)
        
        # Check for duplicates only among non-NULL sequence chapters
        if len(numbers_to_check) != len(set(numbers_to_check)):
            return False, "Duplicate chapter numbers found (excluding NULL sequence chapters)"
        
        return True, ""