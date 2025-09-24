

# ===== File: main.py =====


# main.py - Entry point for the Streamlit application
import streamlit as st
import sys
from pathlib import Path

# Add src to path for imports
sys.path.append(str(Path(__file__).parent / "src"))

from src.core.session_manager import SessionManager
from src.ui.app_layout import setup_page_config, render_main_app


def main():
    """Main application entry point"""
    setup_page_config()
    SessionManager.initialize_session()
    render_main_app()

if __name__ == "__main__":
    main()


# ===== File: src/__init__.py =====




# ===== File: src/core/__init__.py =====




# ===== File: src/core/chapter_utils.py =====

# core/chapter_utils.py - Centralized chapter management utilities

from typing import List, Dict, Tuple, Optional
from enum import Enum
import streamlit as st
from core.text_formatter import TextFormatter  # NEW IMPORT
from core.session_manager import SessionManager

class NumberingSystem(Enum):
    """Enumeration for chapter numbering systems"""
    NUMBERS = "Numbers (1, 2, 3...)"
    WORDS = "Words (One, Two, Three...)"
    ROMAN = "Roman (I, II, III...)"
    NULL_SEQUENCE = "Null Sequence (Chapter Null_Null Name, Chapter Null_Null Name (1)...)"


class ChapterUtils:
    """Centralized utilities for chapter management"""
    
    # Pre-computed lookup tables for performance

    # Keep existing lookup tables
    WORD_NUMBERS = [
        "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine", "Ten",
        "Eleven", "Twelve", "Thirteen", "Fourteen", "Fifteen", "Sixteen", "Seventeen", 
        "Eighteen", "Nineteen", "Twenty", "Twenty-One", "Twenty-Two", "Twenty-Three",
        "Twenty-Four", "Twenty-Five", "Twenty-Six", "Twenty-Seven", "Twenty-Eight",
        "Twenty-Nine", "Thirty", "Thirty-One", "Thirty-Two", "Thirty-Three", "Thirty-Four",
        "Thirty-Five", "Thirty-Six", "Thirty-Seven", "Thirty-Eight", "Thirty-Nine", "Forty",
        "Forty-One", "Forty-Two", "Forty-Three", "Forty-Four", "Forty-Five", "Forty-Six",
        "Forty-Seven", "Forty-Eight", "Forty-Nine", "Fifty", "Fifty-One", "Fifty-Two", "Fifty-Three",
        "Fifty-Four", "Fifty-Five", "Fifty-Six", "Fifty-Seven", "Fifty-Eight", "Fifty-Nine", "Sixty",
        "Sixty-One", "Sixty-Two", "Sixty-Three", "Sixty-Four", "Sixty-Five", "Sixty-Six",
        "Sixty-Seven", "Sixty-Eight", "Sixty-Nine", "Seventy", "Seventy-One", "Seventy-Two", "Seventy-Three",
        "Seventy-Four", "Seventy-Five", "Seventy-Six", "Seventy-Seven", "Seventy-Eight", "Seventy-Nine", "Eighty",
        "Eighty-One", "Eighty-Two", "Eighty-Three", "Eighty-Four", "Eighty-Five", "Eighty-Six",
        "Eighty-Seven", "Eighty-Eight", "Eighty-Nine", "Ninety", "Ninety-One", "Ninety-Two", "Ninety-Three",
        "Ninety-Four", "Ninety-Five", "Ninety-Six", "Ninety-Seven", "Ninety-Eight", "Ninety-Nine", "One Hundred"
    ]
    
    ROMAN_NUMERALS = [
        "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X",
        "XI", "XII", "XIII", "XIV", "XV", "XVI", "XVII", "XVIII", "XIX", "XX",
        "XXI", "XXII", "XXIII", "XXIV", "XXV", "XXVI", "XXVII", "XXVIII", "XXIX", "XXX",
        "XXXI", "XXXII", "XXXIII", "XXXIV", "XXXV", "XXXVI", "XXXVII", "XXXVIII", "XXXIX", "XL",
        "XLI", "XLII", "XLIII", "XLIV", "XLV", "XLVI", "XLVII", "XLVIII", "XLIX", "L",
        "LI", "LII", "LIII", "LIV", "LV", "LVI", "LVII", "LVIII", "LIX", "LX",
        "LXI", "LXII", "LXIII", "LXIV", "LXV", "LXVI", "LXVII", "LXVIII", "LXIX", "LXX",
        "LXXI", "LXXII", "LXXIII", "LXXIV", "LXXV", "LXXVI", "LXXVII", "LXXVIII", "LXXIX", "LXXX",
        "LXXXI", "LXXXII", "LXXXIII", "LXXXIV", "LXXXV", "LXXXVI", "LXXXVII", "LXXXVIII", "LXXXIX", "XC",
        "XCI", "XCII", "XCIII", "XCIV", "XCV", "XCVI", "XCVII", "XCVIII", "XCIX", "C"
    ]
    
    @staticmethod
    def get_numbering_options() -> List[str]:
        """Get all available numbering system options"""
        return [system.value for system in NumberingSystem]
    
    @staticmethod
    def format_chapter_number(chapter_index: int, numbering_system: str, suffix: str = "") -> str:
        """
        Format chapter number based on numbering system with optional suffix
        
        Args:
            chapter_index: 0-based chapter index
            numbering_system: Numbering system string
            suffix: Optional suffix to append to chapter number (e.g., "&")
            
        Returns:
            Formatted chapter number with suffix
        """
        chapter_num = chapter_index + 1  # Convert to 1-based
        
        # Get font case properly
        import streamlit as st
        font_case = st.session_state.get('selected_font_case', 'First Capital (Sentence case)')
        
        if numbering_system == NumberingSystem.WORDS.value:
            result = ChapterUtils.WORD_NUMBERS[chapter_num - 1] if chapter_num <= len(ChapterUtils.WORD_NUMBERS) else str(chapter_num)
        elif numbering_system == NumberingSystem.ROMAN.value:
            result = ChapterUtils.ROMAN_NUMERALS[chapter_num - 1] if chapter_num <= len(ChapterUtils.ROMAN_NUMERALS) else str(chapter_num)
        elif numbering_system == NumberingSystem.NULL_SEQUENCE.value:
            result = "NULL"
        else:  # Default to numbers
            result = str(chapter_num)
        
        # Apply suffix if provided
        if suffix and suffix.strip():
            result = f"{result}{suffix.strip()}"
        
        # Apply font formatting - import here to avoid circular dependency
        from core.text_formatter import TextFormatter
        return TextFormatter.format_text(result, font_case)


        @staticmethod
        def generate_null_sequence_name(chapter_index: int, font_case: str) -> str:
            """
            Generate NULL sequence chapter name: "Name", "Name (1)", "Name (2)", etc.
            
            Args:
                chapter_index: 0-based chapter index
                font_case: Font case setting
                
            Returns:
                Formatted chapter name for NULL sequence
            """
            from core.text_formatter import TextFormatter
            
            if chapter_index == 0:
                base_name = "Name"
            else:
                base_name = f"Name ({chapter_index})"
            
            return TextFormatter.format_chapter_name(base_name, font_case)
        
    @staticmethod
    def update_chapters_with_numbering(chapters: List[Dict], numbering_system: str, suffix: str = "") -> List[Dict]:
            """
            Update chapter numbers based on new numbering system and suffix
            
            Args:
                chapters: List of chapter dictionaries
                numbering_system: New numbering system
                suffix: Optional suffix for chapter numbers
                
            Returns:
                Updated chapters list
            """
            updated_chapters = []
            font_case = st.session_state.get('selected_font_case', 'First Capital (Sentence case)')
            
            for i, chapter in enumerate(chapters):
                new_number = ChapterUtils.format_chapter_number(i, numbering_system, suffix)
                updated_chapter = chapter.copy()
                updated_chapter['number'] = new_number
                
                # Handle NULL sequence names
                if numbering_system == NumberingSystem.NULL_SEQUENCE.value:
                    updated_chapter['name'] = ChapterUtils.generate_null_sequence_name(i, font_case)
                    updated_chapter['is_null_sequence'] = True
                else:
                    # Preserve existing name if not null sequence, or clear if switching from null sequence
                    if chapter.get('is_null_sequence'):
                        updated_chapter['name'] = ''
                    updated_chapter['is_null_sequence'] = False
                    
                updated_chapters.append(updated_chapter)
        
            return updated_chapters
        
    @staticmethod
    def create_chapters_list(count: int, numbering_system: str, suffix: str = "") -> List[Dict]:
            """
            Create a new list of chapters with proper numbering and suffix
            
            Args:
                count: Number of chapters to create
                numbering_system: Numbering system to use
                suffix: Optional suffix for chapter numbers
                
            Returns:
                List of chapter dictionaries
            """
            chapters = []
            
            # Get font case from session state (import here to avoid circular dependency)
            import streamlit as st
            font_case = st.session_state.get('selected_font_case', 'First Capital (Sentence case)')
            
            for i in range(count):
                is_null_sequence = numbering_system == NumberingSystem.NULL_SEQUENCE.value
                
                chapter_number = ChapterUtils.format_chapter_number(i, numbering_system, suffix)
                
                # Handle NULL sequence chapter names specially
                if is_null_sequence:
                    chapter_name = ChapterUtils.generate_null_sequence_name(i, font_case)
                else:
                    chapter_name = ''
                
                chapters.append({
                    'number': chapter_number, 
                    'name': chapter_name,
                    'is_null_sequence': is_null_sequence
                })
            
            return chapters    

    @staticmethod
    def render_numbering_system_selector(context_key: str, current_system: str = None, 
                                        help_text: str = None, suffix: str = "") -> tuple:
            """
            Render numbering system selector with suffix input
            
            Args:
                context_key: Unique key for this selector
                current_system: Currently selected system
                help_text: Help text for the selector
                suffix: Current suffix value
                
            Returns:
                Tuple of (selected_numbering_system, chapter_suffix)
            """
            options = ChapterUtils.get_numbering_options()
            
            if current_system is None:
                current_system = NumberingSystem.NUMBERS.value
            
            default_index = options.index(current_system) if current_system in options else 0
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                selected_system = st.selectbox(
                    "Chapter Numbering System",
                    options,
                    index=default_index,
                    key=f"numbering_system_{context_key}",
                    help=help_text or "Choose how chapters should be numbered"
                )
            
            with col2:
                chapter_suffix = st.text_input(
                    "Number Suffix",
                    value=suffix,
                    placeholder="e.g., &, -, :",
                    key=f"chapter_suffix_{context_key}",
                    help="Optional text to append to chapter numbers (e.g., '&' → 'Chapter 1&_Name')"
                )
            
            return selected_system, chapter_suffix

    @staticmethod
    def generate_null_sequence_name(chapter_index: int, font_case: str) -> str:
        """
        Generate NULL sequence chapter name: "Name", "Name (1)", "Name (2)", etc.
        """
        from core.text_formatter import TextFormatter
        
        if chapter_index == 0:
            base_name = "Name"
        else:
            base_name = f"Name ({chapter_index})"
        
        return TextFormatter.format_text(base_name, font_case)

class ChapterConfigManager:
    """Manages chapter configuration state and operations"""
    
    @staticmethod
    def get_session_manager():
        """Get SessionManager to avoid circular imports"""
        from core.session_manager import SessionManager
        return SessionManager
    
    @staticmethod
    def update_chapter_count(context_key: str, target_count: int, current_chapters: List[Dict], 
                            numbering_system: str, suffix: str = ""):
        """
        Update chapter count with proper state management including suffix
        
        Args:
            context_key: Context identifier (part name or 'standalone')
            target_count: Target number of chapters
            current_chapters: Current chapters list
            numbering_system: Current numbering system
            suffix: Chapter number suffix
        """
        SessionManager = ChapterConfigManager.get_session_manager()
        
        if target_count > len(current_chapters):
            # Add new chapters
            font_case = st.session_state.get('selected_font_case', 'First Capital (Sentence case)')
            for i in range(len(current_chapters), target_count):
                chapter_number = ChapterUtils.format_chapter_number(i, numbering_system, suffix)
                
                if numbering_system == NumberingSystem.NULL_SEQUENCE.value:
                    chapter_name = ChapterUtils.generate_null_sequence_name(i, font_case)
                    is_null_sequence = True
                else:
                    chapter_name = ''
                    is_null_sequence = False
                    
                current_chapters.append({
                    'number': chapter_number, 
                    'name': chapter_name,
                    'is_null_sequence': is_null_sequence
                })
        else:
            # Remove extra chapters
            current_chapters = current_chapters[:target_count]
        
        # Update session state based on context
        if context_key == 'standalone':
            SessionManager.set('standalone_chapters', current_chapters)
        else:
            chapters_config = SessionManager.get('chapters_config', {})
            chapters_config[context_key] = current_chapters
            SessionManager.set('chapters_config', chapters_config)
        
        return current_chapters
    
    @staticmethod
    def update_numbering_system(context_key: str, new_system: str):
        """
        Update numbering system and refresh all chapter numbers
        
        Args:
            context_key: Context identifier (part name or 'standalone')
            new_system: New numbering system
        """
        SessionManager = ChapterConfigManager.get_session_manager()
        
        # Update numbering systems config
        numbering_config = SessionManager.get('numbering_systems', {})
        numbering_config[context_key] = new_system
        SessionManager.set('numbering_systems', numbering_config)
        
        # Get current suffix for this context
        current_suffix = SessionManager.get_chapter_suffix(context_key)
        
        # Update chapter numbers based on context
        if context_key == 'standalone':
            current_chapters = SessionManager.get('standalone_chapters', [])
            if current_chapters:
                updated_chapters = ChapterUtils.update_chapters_with_numbering(current_chapters, new_system, current_suffix)
                SessionManager.set('standalone_chapters', updated_chapters)
        else:
            chapters_config = SessionManager.get('chapters_config', {})
            if context_key in chapters_config and chapters_config[context_key]:
                updated_chapters = ChapterUtils.update_chapters_with_numbering(chapters_config[context_key], new_system, current_suffix)
                chapters_config[context_key] = updated_chapters
                SessionManager.set('chapters_config', chapters_config)

    @staticmethod
    def get_current_numbering_system(context_key: str) -> str:
        """Get current numbering system for a context"""
        SessionManager = ChapterConfigManager.get_session_manager()
        numbering_config = SessionManager.get('numbering_systems', {})
        return numbering_config.get(context_key, NumberingSystem.NUMBERS.value)
    
    @staticmethod
    def get_chapters_for_context(context_key: str) -> List[Dict]:
        """Get chapters list for a specific context"""
        SessionManager = ChapterConfigManager.get_session_manager()
        
        if context_key == 'standalone':
            return SessionManager.get('standalone_chapters', [])
        else:
            chapters_config = SessionManager.get('chapters_config', {})
            return chapters_config.get(context_key, [])


class PartManager:
    """Manages part creation and deletion operations"""
    
    @staticmethod
    def add_part_with_immediate_sync(config: Dict, part_name: str) -> bool:
        """
        Add part with immediate session state synchronization and font formatting
        """
        try:
            from core.folder_manager import FolderManager
            from core.text_formatter import TextFormatter  # Add this import
            from pathlib import Path
            from datetime import datetime
            
            SessionManager = ChapterConfigManager.get_session_manager()
            
            # Apply font formatting to part name
            font_case = SessionManager.get_font_case()
            formatted_part_name = TextFormatter.format_part_name(part_name, font_case)
            
            safe_code = FolderManager.sanitize_name(config['code'])
            book_name = config['book_name']
            base_name = f"{safe_code}_{book_name}"
            
            # Path resolution
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
            
            # Create part folder with formatted name
            part_folder = project_path / f"{base_name}_{formatted_part_name}"
            
            if part_folder.exists():
                return False  # Part already exists
            
            part_folder.mkdir(exist_ok=True)
            
            # Update session state immediately with formatted name
            custom_parts = SessionManager.get('custom_parts', {})
            base_id = formatted_part_name.lower().replace(' ', '_').replace('-', '_')
            part_id = f"part_{len(custom_parts) + 1}_{base_id}"
            
            # Ensure unique ID
            counter = 1
            original_id = part_id
            while part_id in custom_parts:
                part_id = f"{original_id}_{counter}"
                counter += 1
            
            custom_parts[part_id] = {
                'name': formatted_part_name,  # Use formatted name
                'display_name': formatted_part_name,
                'original_name': part_name,  # Keep original
                'created_timestamp': datetime.now().isoformat()
            }
            
            SessionManager.set('custom_parts', custom_parts)
            
            # Update created folders list
            current_folders = SessionManager.get('created_folders', [])
            new_part_path = str(part_folder.absolute())
            if new_part_path not in current_folders:
                current_folders.append(new_part_path)
                SessionManager.set('created_folders', current_folders)
            
            # Set operation completion flags
            st.session_state['part_operation_completed'] = True
            st.session_state['part_operation_info'] = {
                'operation': 'add',
                'part_name': formatted_part_name,  # Show formatted name in success message
                'location': str(part_folder.absolute())
            }
            
            return True
            
        except Exception as e:
            st.error(f"Error creating part: {str(e)}")
            return False


# ===== File: src/core/folder_manager.py =====

# core/folder_manager.py - Modified to support standalone chapters

from pathlib import Path
from typing import List, Tuple, Optional, Dict
import streamlit as st
import random
import os

class FolderManager:
    """Manages folder structure creation and organization"""
    
    DEFAULT_FOLDERS = ['prologue', 'index', 'epilogue']
    
    @staticmethod
    def get_default_folder_options() -> List[Dict[str, str]]:
        """Get available default folder options with descriptions"""
        return [
            {'name': 'prologue', 'description': 'Introduction or preface content'},
            {'name': 'index', 'description': 'Table of contents, index, or reference pages'},
            {'name': 'epilogue', 'description': 'Conclusion, appendix, or closing content'},
            {'name': 'bibliography', 'description': 'References and citations'},
            {'name': 'glossary', 'description': 'Terms and definitions'},
            {'name': 'exercises', 'description': 'Practice problems and solutions'},
            {'name': 'notes', 'description': 'Additional notes and annotations'}
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
            chapter_num = "Null_Null Name"
        else:
            chapter_num = chapter_number.strip()
        
        if chapter_name is None or chapter_name.strip() == "":
            chapter_nm = "Null_Name"
        else:
            chapter_nm = chapter_name.strip()
        
        # Generate folder name with proper spacing: Chapter {number}_{name}
        # Note: Single space after "Chapter", underscore before chapter name
        if chapter_nm == "Null_Name" and chapter_num == "Null_Null Name":
            import random
            random_num = random.randint(10000, 99999)
            return f"{base_name}_Chapter {chapter_num}_{random_num}"
        
        return f"{base_name}_Chapter {chapter_num}_{chapter_nm}"

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
        Load PDF and extract basic information with optimized memory handling
        
        Args:
            uploaded_file: Streamlit uploaded file object
            
        Returns:
            Tuple of (PDF reader object, total pages)
        """
        try:
            # Always read and store the full content for reliability
            # Reset file pointer to beginning
            uploaded_file.seek(0)
            file_content = uploaded_file.read()
            
            # Validate we actually got content
            if not file_content or len(file_content) == 0:
                st.error("PDF file appears to be empty or corrupted")
                return None, 0
            
            pdf_reader = PyPDF2.PdfReader(BytesIO(file_content))
            total_pages = len(pdf_reader.pages)
            
            # Store file content in session state for ALL files
            # For memory management, we'll handle this differently
            file_size_mb = len(file_content) / (1024 * 1024)
            
            if file_size_mb > 100:
                st.info(f"Large PDF detected ({file_size_mb:.1f}MB). Processing may take longer.")
                # Still store content but warn about memory usage
                st.session_state.pdf_content = file_content
                st.session_state.pdf_large_file = True
            else:
                st.session_state.pdf_content = file_content
                st.session_state.pdf_large_file = False
            
            # Also store file name for reference
            st.session_state.pdf_file_name = uploaded_file.name
            
            return pdf_reader, total_pages
            
        except Exception as e:
            st.error(f"Error reading PDF: {str(e)}")
            return None, 0
    
    @staticmethod
    def get_pdf_reader() -> Optional[PyPDF2.PdfReader]:
        """Get PDF reader from stored content"""
        try:
            # Always try to get from stored content first
            pdf_content = st.session_state.get('pdf_content')
            if pdf_content:
                return PyPDF2.PdfReader(BytesIO(pdf_content))
            
            # Fallback: try to get from uploaded file (may not work for large files)
            pdf_file = st.session_state.get('pdf_file')
            if pdf_file:
                try:
                    pdf_file.seek(0)
                    file_content = pdf_file.read()
                    if file_content:
                        return PyPDF2.PdfReader(BytesIO(file_content))
                except:
                    pass
            
            # If all else fails, show helpful error
            st.error("PDF content not available. Please re-upload your PDF file.")
            return None
            
        except Exception as e:
            st.error(f"Error accessing PDF: {str(e)}")
            return None
    
    @staticmethod
    def validate_pdf(uploaded_file) -> bool:
        """Validate if uploaded file is a proper PDF"""
        try:
            uploaded_file.seek(0)  # Reset file pointer
            content = uploaded_file.read()
            uploaded_file.seek(0)  # Reset for future reads
            
            if not content or len(content) == 0:
                return False
                
            pdf_reader = PyPDF2.PdfReader(BytesIO(content))
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
        """
        try:
            # Parse page ranges into individual page numbers
            pages_to_extract = PDFExtractor.parse_page_ranges(page_ranges, total_pages)
            
            if not pages_to_extract:
                return False, [], "No valid pages specified"
            
            # Get PDF reader
            pdf_reader = PDFHandler.get_pdf_reader()
            if not pdf_reader:
                pdf_content = st.session_state.get('pdf_content')
                if pdf_content:
                    try:
                        from io import BytesIO
                        import PyPDF2
                        pdf_reader = PyPDF2.PdfReader(BytesIO(pdf_content))
                    except Exception as e:
                        return False, [], f"Could not access PDF file: {str(e)}"
                
                if not pdf_reader:
                    return False, [], "Could not access PDF file. Please re-upload your PDF."
            
            # Use the destination_folder exactly as provided
            dest_path = Path(destination_folder)
            
            # Create destination folder if it doesn't exist
            dest_path.mkdir(parents=True, exist_ok=True)
            
            created_files = []
            failed_pages = []
            
            # Extract each page
            for idx, (sequential_num, actual_page_num) in enumerate(enumerate(pages_to_extract, 1)):
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
        Extract a single page from PDF with proper naming convention and correct spacing
        """
        try:
            # Validate page number
            if actual_page_num < 1 or actual_page_num > len(pdf_reader.pages):
                return False, f"Page {actual_page_num} out of range"
            
            # Create new PDF with single page
            pdf_writer = PyPDF2.PdfWriter()
            pdf_writer.add_page(pdf_reader.pages[actual_page_num - 1])
            
            # Use sequential numbering if provided, otherwise use actual page number
            page_num_for_filename = sequential_page_num if sequential_page_num is not None else actual_page_num
            
            # Apply font formatting to the page number text
            import streamlit as st
            from core.text_formatter import TextFormatter
            font_case = st.session_state.get('selected_font_case', 'First Capital (Title Case)')
            formatted_page_num = TextFormatter.format_text(str(page_num_for_filename), font_case)
            
            # Generate file name with proper spacing - KEEP THE SPACE
            # Don't sanitize the naming_base if it already has proper formatting
            file_name = f"{naming_base}_Page {formatted_page_num}.pdf"
            
            # Use the exact dest_path provided
            file_path = dest_path / file_name
            
            # Write PDF file
            with open(file_path, 'wb') as output_file:
                pdf_writer.write(output_file)
            
            return True, str(file_path.absolute())
            
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

# core/session_manager.py - Modified to avoid circular imports

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
            'pdf_content': None,
            'total_pages': 0,
            'folder_structure_created': False,
            'created_folders': [],
            'chapters_config': {},
            'standalone_chapters': [],
            'current_step': 1,
            'chapters_created': False,
            'page_assignments': {},
            'extraction_history': [],
            'folder_metadata': {},
            'unique_chapter_counter': 0,
            'numbering_systems': {},
            'chapter_suffixes': {},
            'custom_parts': {},
            'font_case_selected': True,
            'selected_font_case': 'First Capital (Title Case)',
            'project_destination_folder': '',  # NEW: For project structure location
            'project_destination_selected': False,  # NEW: Track if project destination is set
            'total_pages_generated': 0,  # NEW: Cache for generated pages count
            'pages_calculated_timestamp': None,  # NEW: Last calculation timestamp
        }
        
        for key, value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = value

    @staticmethod
    def get_chapter_suffix(context_key: str) -> str:
        """Get chapter suffix for a specific context"""
        chapter_suffixes = SessionManager.get('chapter_suffixes', {})
        return chapter_suffixes.get(context_key, "")

    @staticmethod
    def set_chapter_suffix(context_key: str, suffix: str):
        """Set chapter suffix for a specific context"""
        chapter_suffixes = SessionManager.get('chapter_suffixes', {})
        chapter_suffixes[context_key] = suffix
        SessionManager.set('chapter_suffixes', chapter_suffixes)
    
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
    
    @staticmethod
    def get_font_case() -> str:
        """Get current font case setting"""
        return st.session_state.get('selected_font_case', 'First Capital (Sentence case)')
    
    @staticmethod
    def set_font_case(font_case: str):
        """Set font case and mark as selected"""
        st.session_state['selected_font_case'] = font_case
        st.session_state['font_case_selected'] = True

    @staticmethod
    def get_default_destination() -> str:
        """Get default destination folder"""
        return st.session_state.get('default_destination_folder', '')

    @staticmethod
    def set_default_destination(folder_path: str):
        """Set default destination folder"""
        st.session_state['default_destination_folder'] = folder_path
        st.session_state['destination_folder_selected'] = True

    @staticmethod
    def get_project_destination() -> str:
        """Get project destination folder"""
        return st.session_state.get('project_destination_folder', '')

    @staticmethod
    def set_project_destination(folder_path: str):
        """Set project destination folder"""
        st.session_state['project_destination_folder'] = folder_path
        st.session_state['project_destination_selected'] = True


# ===== File: src/core/text_formatter.py =====

# core/text_formatter.py - Text formatting utilities

from enum import Enum
from typing import Any, Dict, Optional

class FontCase(Enum):
    """Font case formatting options"""
    ALL_CAPS = "All Caps (UPPERCASE)"
    ALL_SMALL = "All Small (lowercase)" 
    FIRST_CAPITAL = "First Capital (Sentence case)"

class TextFormatter:
    """Centralized text formatting based on selected font case"""
    
    @staticmethod
    def format_text(text: str, font_case: str) -> str:
        """
        Format text according to the selected font case
        
        Args:
            text: Original text to format
            font_case: Font case option from FontCase enum
            
        Returns:
            Formatted text
        """
        if not text or not isinstance(text, str):
            return text
        
        text = str(text).strip()
        
        # Debug: Check what font_case value we're getting
        if font_case == FontCase.ALL_CAPS.value or font_case == "All Caps (UPPERCASE)":
            return text.upper()
        elif font_case == FontCase.ALL_SMALL.value or font_case == "All Small (lowercase)":
            return text.lower()
        elif font_case == FontCase.FIRST_CAPITAL.value or font_case == "First Capital (Sentence case)":
            return text.capitalize()
        else:
            # Default to original text if unknown format
            return text
    
    @staticmethod
    def get_font_case_options() -> list:
        """Get all available font case options"""
        return [case.value for case in FontCase]
    
    @staticmethod
    def format_project_code(code: str, font_case: str) -> str:
        """Format project code"""
        return TextFormatter.format_text(code, font_case)
    
    @staticmethod
    def format_book_name(book_name: str, font_case: str) -> str:
        """Format book name"""
        return TextFormatter.format_text(book_name, font_case)
    
    @staticmethod
    def format_part_name(part_name: str, font_case: str) -> str:
        """Format part name"""
        return TextFormatter.format_text(part_name, font_case)
    
    @staticmethod
    def format_chapter_name(chapter_name: str, font_case: str) -> str:
        """Format chapter name"""
        return TextFormatter.format_text(chapter_name, font_case)
    
    @staticmethod
    def format_chapter_number(chapter_number: str, font_case: str) -> str:
        """Format chapter number"""
        return TextFormatter.format_text(chapter_number, font_case)
    
    @staticmethod
    def format_folder_name(folder_name: str, font_case: str) -> str:
        """Format folder name"""
        return TextFormatter.format_text(folder_name, font_case)
    
    @staticmethod
    def format_custom_folder_name(custom_name: str, font_case: str) -> str:
        """Format custom folder name"""
        return TextFormatter.format_text(custom_name, font_case)
    
    @staticmethod
    def get_current_font_case():
        """Get current font case from session - using lazy import"""
        import streamlit as st
        return st.session_state.get('selected_font_case', 'First Capital (Sentence case)')


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
from ui.font_selector import render_font_case_selector  # NEW IMPORT
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

    # Check if folder browser should be shown
    from ui.folder_selector import render_folder_browser_in_main
    
    if render_folder_browser_in_main():
        return  # Show only folder browser when active
    
    # Remove the font case check - go directly to tabs
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

# ui/chapter_management.py - Optimized with centralized utilities

from datetime import datetime
import streamlit as st
from typing import Dict, List
from core.session_manager import SessionManager
from core.folder_manager import ChapterManager, FolderManager
from core.chapter_utils import ChapterUtils, ChapterConfigManager, NumberingSystem, PartManager
from pathlib import Path
import shutil
import os


class ChapterOperations:
    """Generic chapter operations for both standalone and part chapters"""
    

    @staticmethod
    def create_single_chapter(config: Dict, context_key: str, chapter_data: Dict, is_standalone: bool = False, create_only: bool = False, chapter_index: int = None) -> bool:
        """
        Create a single chapter folder
        
        Args:
            create_only: If True, don't add to session (folder already in list, just creating physical folder)
            chapter_index: Index of chapter in list (used when create_only=True)
        """
        try:
            safe_code = FolderManager.sanitize_name(config['code'])
            book_name = config['book_name']
            base_name = f"{safe_code}_{book_name}"
            
            project_destination = SessionManager.get_project_destination()
            if project_destination and os.path.exists(project_destination):
                base_path = Path(project_destination)
            else:
                base_path = Path.cwd()
            
            project_path = base_path / base_name
            
            if not project_path.exists():
                project_path.mkdir(parents=True, exist_ok=True)
            
            with st.spinner(f"Creating chapter folder..."):
                if is_standalone:
                    created_folders = ChapterManager.create_standalone_chapter_folders(
                        project_path, base_name, [chapter_data]
                    )
                else:
                    created_folders = ChapterManager.create_chapter_folders_for_custom_part(
                        project_path, base_name, context_key, [chapter_data]
                    )
            
            if created_folders:
                current_folders = SessionManager.get('created_folders', [])
                current_folders.extend(created_folders)
                SessionManager.set('created_folders', current_folders)
                SessionManager.set('chapters_created', True)
                
                # Only add to session if not create_only (new chapter being added)
                if not create_only:
                    if is_standalone:
                        standalone_chapters = SessionManager.get('standalone_chapters', [])
                        standalone_chapters.append(chapter_data)
                        SessionManager.set('standalone_chapters', standalone_chapters)
                    else:
                        chapters_config = SessionManager.get('chapters_config', {})
                        if context_key not in chapters_config:
                            chapters_config[context_key] = []
                        chapters_config[context_key].append(chapter_data)
                        SessionManager.set('chapters_config', chapters_config)
                
                return True
            return False
            
        except Exception as e:
            st.error(f"Error creating chapter: {str(e)}")
            return False

    @staticmethod
    def delete_single_chapter(config: Dict, context_key: str, chapter_index: int, is_standalone: bool = False) -> bool:
        """
        Delete a single chapter folder and remove from session
        """
        try:
            # Get chapters list
            if is_standalone:
                chapters = SessionManager.get('standalone_chapters', [])
            else:
                chapters_config = SessionManager.get('chapters_config', {})
                chapters = chapters_config.get(context_key, [])
            
            if chapter_index >= len(chapters):
                st.error("Invalid chapter index")
                return False
            
            chapter = chapters[chapter_index]
            
            # Build chapter folder path
            safe_code = FolderManager.sanitize_name(config['code'])
            book_name = config['book_name']
            base_name = f"{safe_code}_{book_name}"
            
            # Get project path
            project_destination = SessionManager.get_project_destination()
            if project_destination and os.path.exists(project_destination):
                base_path = Path(project_destination)
            else:
                base_path = Path.cwd()
            
            project_path = base_path / base_name
            
            # Generate chapter folder name
            if is_standalone:
                parent_folder_name = base_name
                chapter_folder_name = ChapterManager.generate_chapter_folder_name(
                    parent_folder_name,
                    chapter.get('number'),
                    chapter.get('name')
                )
                chapter_path = project_path / chapter_folder_name
            else:
                parent_folder_name = f"{base_name}_{context_key}"
                chapter_folder_name = ChapterManager.generate_chapter_folder_name(
                    parent_folder_name,
                    chapter.get('number'),
                    chapter.get('name')
                )
                part_path = project_path / parent_folder_name
                chapter_path = part_path / chapter_folder_name
            
            # Delete the physical folder
            if chapter_path.exists():
                with st.spinner(f"Deleting chapter folder..."):
                    shutil.rmtree(chapter_path)
            else:
                st.warning(f"Chapter folder not found: {chapter_path.name}")
            
            # Remove from chapters list
            chapters.pop(chapter_index)
            
            # Update session state
            if is_standalone:
                SessionManager.set('standalone_chapters', chapters)
            else:
                chapters_config = SessionManager.get('chapters_config', {})
                chapters_config[context_key] = chapters
                SessionManager.set('chapters_config', chapters_config)
            
            # Update created folders list
            current_folders = SessionManager.get('created_folders', [])
            chapter_path_str = str(chapter_path.absolute())
            if chapter_path_str in current_folders:
                current_folders.remove(chapter_path_str)
            SessionManager.set('created_folders', current_folders)
            
            # Remove from metadata
            folder_metadata = SessionManager.get('folder_metadata', {})
            metadata_to_remove = []
            for folder_id, metadata in folder_metadata.items():
                if metadata.get('actual_path') == chapter_path_str:
                    metadata_to_remove.append(folder_id)
            
            for folder_id in metadata_to_remove:
                del folder_metadata[folder_id]
            
            SessionManager.set('folder_metadata', folder_metadata)
            
            return True
            
        except PermissionError:
            st.error(f"Permission denied. Cannot delete chapter folder.")
            return False
        except Exception as e:
            st.error(f"Error deleting chapter: {str(e)}")
            return False

def render_chapter_management_page():
    """Render the chapter management page"""
    
    # Check prerequisites
    if not SessionManager.get('folder_structure_created'):
        render_prerequisites_warning()
        return
    
    config = SessionManager.get('project_config', {})
    
    st.subheader("📂 Chapter Management")
    st.markdown("Configure chapters within each custom part of your book, or create standalone chapters.")
    
    # Check for operation completion messages
    if st.session_state.get('part_operation_completed'):
        operation_info = st.session_state.get('part_operation_info', {})
        if operation_info.get('operation') == 'add':
            st.success(f"✅ Successfully created part '{operation_info.get('part_name')}'!")
            st.info(f"📂 Location: {operation_info.get('location', 'Unknown')}")
        elif operation_info.get('operation') == 'delete':
            st.success(f"✅ Successfully deleted part '{operation_info.get('part_name')}' and all its contents!")
        
        # Clear the flags
        st.session_state['part_operation_completed'] = False
        st.session_state['part_operation_info'] = {}
    
    # Standalone Chapters Section
    st.markdown("### 📖 Standalone Chapters")
    render_standalone_chapters_section(config)
    
    st.markdown("---")
    
    # Part Management Section
    st.markdown("### 🔧 Part Management")
    render_part_management_section(config)
    
    # Chapter configuration for parts
    updated_parts = get_existing_custom_parts(config)
    
    if not updated_parts:
        st.info("📝 No custom parts configured. You can add individual parts above or configure parts in Project Setup.")
    else:
        st.markdown("---")
        part_names = [part['name'] for part in updated_parts]
        st.info(f"Found {len(updated_parts)} existing parts: {', '.join(part_names)}")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            render_chapter_configuration(config, updated_parts)
        
        with col2:
            render_chapter_preview(config)


def render_standalone_chapters_section(config: Dict):
    """Render standalone chapters configuration section with optimized state management"""
    
    st.markdown("Create chapters directly under the project root (not inside any part).")
    
    context_key = 'standalone'
    
    # Get current state
    current_chapters = ChapterConfigManager.get_chapters_for_context(context_key)
    current_count = len(current_chapters)
    current_system = ChapterConfigManager.get_current_numbering_system(context_key)
    current_suffix = SessionManager.get_chapter_suffix(context_key)
    
    # Number of standalone chapters input
    target_count = st.number_input(
        "Number of standalone chapters",
        min_value=0,
        value=current_count,
        step=1,
        key="standalone_chapters_count",
        help="Enter number of chapters to create directly under project root"
    )
    
    # Numbering system selector with suffix
    if target_count > 0:
        new_system, new_suffix = ChapterUtils.render_numbering_system_selector(
            context_key,
            current_system,
            "Choose how standalone chapters should be numbered",
            current_suffix
        )
        
        # Handle system or suffix change with immediate update
        system_changed = new_system != current_system
        suffix_changed = new_suffix != current_suffix
        
        if system_changed or suffix_changed:
            if system_changed:
                ChapterConfigManager.update_numbering_system(context_key, new_system)
            if suffix_changed:
                SessionManager.set_chapter_suffix(context_key, new_suffix)
                # Update existing chapters with new suffix
                if current_chapters:
                    updated_chapters = ChapterUtils.update_chapters_with_numbering(
                        current_chapters, new_system, new_suffix
                    )
                    SessionManager.set('standalone_chapters', updated_chapters)
            
            current_system = new_system
            current_suffix = new_suffix
            # Force rerun to update UI
            st.rerun()
    
    # Handle count change
    if target_count != current_count:
        current_chapters = ChapterConfigManager.update_chapter_count(
            context_key, target_count, current_chapters, current_system, current_suffix
        )
        st.rerun()
    
    # Render chapter details
    if target_count > 0:
        render_chapter_details_optimized(context_key, current_chapters, config, is_standalone=True)
        
        # Action buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🏗️ Create Standalone Chapters", key="create_standalone_chapters"):
                create_standalone_chapters(config, current_chapters)
        
        with col2:
            if SessionManager.get('chapters_created') and any(current_chapters):
                if st.button("🔄 Update Standalone Chapters", key="update_standalone_chapters"):
                    update_existing_standalone_chapters(config, current_chapters)


def add_individual_custom_part(config: Dict, part_name: str):
    """Add an individual custom part folder with proper font formatting"""
    try:
        from core.text_formatter import TextFormatter
        from core.folder_manager import FolderManager
        from pathlib import Path
        import shutil
        
        # Get font case and format the part name
        font_case = SessionManager.get_font_case()
        formatted_part_name = TextFormatter.format_part_name(part_name, font_case)
        
        safe_code = FolderManager.sanitize_name(config['code'])
        book_name = config['book_name']
        base_name = f"{safe_code}_{book_name}"
        
        # Use project destination instead of current directory
        project_destination = SessionManager.get_project_destination()
        if project_destination and os.path.exists(project_destination):
            base_path = Path(project_destination)
        else:
            base_path = Path.cwd()
        
        project_path = base_path / base_name
        
        if not project_path.exists():
            project_path.mkdir(parents=True, exist_ok=True)
            st.info(f"Created project directory: {project_path.absolute()}")
        
        # Create part folder with formatted name
        part_folder = project_path / f"{base_name}_{formatted_part_name}"
        
        if part_folder.exists():
            st.error(f"Part '{formatted_part_name}' already exists!")
            return False
        
        part_folder.mkdir(exist_ok=True)
        
        # Rest remains the same...
        custom_parts = SessionManager.get('custom_parts', {})
        base_id = formatted_part_name.lower().replace(' ', '_').replace('-', '_')
        part_id = f"part_{len(custom_parts) + 1}_{base_id}"
        
        # Ensure unique ID
        counter = 1
        original_id = part_id
        while part_id in custom_parts:
            part_id = f"{original_id}_{counter}"
            counter += 1
        
        custom_parts[part_id] = {
            'name': formatted_part_name,
            'display_name': formatted_part_name,
            'original_name': part_name,
            'created_timestamp': datetime.now().isoformat()
        }
        
        SessionManager.set('custom_parts', custom_parts)
        
        # Update created folders list
        current_folders = SessionManager.get('created_folders', [])
        new_part_path = str(part_folder.absolute())
        if new_part_path not in current_folders:
            current_folders.append(new_part_path)
            SessionManager.set('created_folders', current_folders)
        
        # Set operation completion flags
        st.session_state['part_operation_completed'] = True
        st.session_state['part_operation_info'] = {
            'operation': 'add',
            'part_name': formatted_part_name,
            'location': str(part_folder.absolute())
        }
        
        return True
        
    except Exception as e:
        st.error(f"Error creating part: {str(e)}")
        return False


def render_part_management_section(config: Dict):
    """Render part management section with optimized operations and font formatting"""
    
    col_opt1, col_opt2, col_opt3, col_opt4 = st.columns(4)
    
    # Show current font formatting
    font_case = SessionManager.get_font_case()
    st.caption(f"Font formatting: {font_case}")
    
    with col_opt2:
        part_name_input = st.text_input(
            "Part Name to Add",
            value="",
            placeholder="e.g., Mathematics, Science",
            key="individual_part_name_input",
            help=f"Enter the custom name for the new part (will be formatted as: {font_case})"
        )
    
    with col_opt1:
        if st.button("➕ Add Individual Part", type="secondary", key="add_part_btn"):
            if part_name_input.strip():
                # Use the improved function with font formatting
                success = add_individual_custom_part(config, part_name_input.strip())
                if success:
                    st.rerun()
                else:
                    from core.text_formatter import TextFormatter
                    formatted_name = TextFormatter.format_part_name(part_name_input.strip(), font_case)
                    st.error(f"Part '{formatted_name}' already exists!")
            else:
                st.error("Please enter a part name first")
    
    # Delete part functionality
    current_parts = get_existing_custom_parts(config)
    
    with col_opt3:
        if current_parts:
            part_to_delete = st.selectbox(
                "Select Part to Delete",
                [part['name'] for part in current_parts],
                key="part_to_delete_select",
                help="Choose which part to delete (this will delete all contents)"
            )
    
    with col_opt4:
        if current_parts:
            if st.button("🗑️ Delete Selected Part", type="secondary", key="delete_part_btn"):
                part_to_delete = st.session_state.get("part_to_delete_select")
                if part_to_delete:
                    delete_individual_custom_part(config, part_to_delete)
                    st.rerun()


def render_chapter_details_optimized(context_key: str, chapters: List[Dict], config: Dict, is_standalone: bool = False):
    """Optimized chapter details rendering with proper state management and font formatting"""
    
    if is_standalone:
        st.markdown("**Configure standalone chapters:**")
    else:
        st.markdown(f"**Configure chapters for {context_key}:**")
    
    # Lazy import for font formatting
    from core.text_formatter import TextFormatter
    font_case = st.session_state.get('selected_font_case', 'First Capital (Sentence case)')
    
    safe_code = FolderManager.sanitize_name(config['code'])
    book_name = config['book_name']
    base_name = f"{safe_code}_{book_name}"
    
    # Check which chapters already have folders created
    created_chapter_indices = get_created_chapter_indices(config, context_key, chapters, is_standalone)
    
    updated_chapters = []
    
    for i, chapter in enumerate(chapters):
        # Chapter number and name inputs with action buttons
        col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
        
        with col1:
            if chapter.get('is_null_sequence'):
                st.text_input(
                    "Number",
                    value=chapter.get('number', ''),
                    key=f"{context_key}_chapter_num_{i}",
                    disabled=True,
                    help="NULL sequence number (auto-generated)"
                )
                chapter_number = chapter.get('number', '')
            else:
                chapter_number = st.text_input(
                    "Number",
                    value=chapter.get('number', ''),
                    placeholder=f"e.g., {chapter.get('number', '')}",
                    key=f"{context_key}_chapter_num_{i}",
                    help="Chapter number"
                )
        
        with col2:
            if chapter.get('is_null_sequence'):
                st.text_input(
                    "Name",
                    value=chapter.get('name', ''),
                    key=f"{context_key}_chapter_name_{i}",
                    disabled=True,
                    help="NULL sequence name (auto-generated)"
                )
                chapter_name = chapter.get('name', '')
            else:
                chapter_name = st.text_input(
                    "Name",
                    value=chapter.get('name', ''),
                    placeholder="e.g., Introduction, Overview",
                    key=f"{context_key}_chapter_name_{i}",
                    help="Chapter name"
                )
        
        # Apply font formatting to current input values
        if not chapter.get('is_null_sequence'):
            formatted_chapter_number = TextFormatter.format_chapter_number(chapter_number, font_case) if chapter_number else ''
            formatted_chapter_name = TextFormatter.format_chapter_name(chapter_name, font_case) if chapter_name else ''
        else:
            formatted_chapter_number = chapter_number
            formatted_chapter_name = chapter_name
        
        with col3:
            st.write("")
            st.write("")
            # Create button - only show if folder doesn't exist
            if i not in created_chapter_indices:
                if st.button("💾", key=f"create_chapter_{context_key}_{i}", help="Create this chapter folder"):
                    chapter_to_create = {
                        'number': formatted_chapter_number,
                        'name': formatted_chapter_name,
                        'is_null_sequence': chapter.get('is_null_sequence', False)
                    }
                    if ChapterOperations.create_single_chapter(config, context_key, chapter_to_create, is_standalone, create_only=True, chapter_index=i):
                        st.success(f"Chapter folder created!")
                        st.rerun()
            else:
                st.write("✅")  # Just show checkmark, no individual update
        
        with col4:
            st.write("")
            st.write("")
            # Delete button - only show if folder exists
            if i in created_chapter_indices:
                if st.button("🗑️", key=f"delete_chapter_{context_key}_{i}", help="Delete this chapter folder"):
                    if ChapterOperations.delete_single_chapter(config, context_key, i, is_standalone):
                        st.success("Chapter deleted!")
                        st.rerun()
        
        # Store updated chapter data
        updated_chapters.append({
            'number': formatted_chapter_number,
            'name': formatted_chapter_name,
            'original_number': chapter_number if not chapter.get('is_null_sequence') else '',
            'original_name': chapter_name if not chapter.get('is_null_sequence') else '',
            'is_null_sequence': chapter.get('is_null_sequence', False)
        })
        
        # Show preview and status
        if is_standalone:
            preview_name = ChapterManager.generate_chapter_folder_name(
                base_name,
                formatted_chapter_number or None,
                formatted_chapter_name or None
            )
        else:
            preview_name = ChapterManager.generate_chapter_folder_name(
                f"{base_name}_{context_key}",
                formatted_chapter_number or None,
                formatted_chapter_name or None
            )
        
        status_text = "✅ Created" if i in created_chapter_indices else "⏳ Not created"
        st.caption(f"📁 Folder: `{preview_name}` | {status_text}")
        
        if i < len(chapters) - 1:
            st.markdown("---")
    
    # Update session state with new values
    if is_standalone:
        SessionManager.set('standalone_chapters', updated_chapters)
    else:
        chapters_config = SessionManager.get('chapters_config', {})
        chapters_config[context_key] = updated_chapters
        SessionManager.set('chapters_config', chapters_config)

def update_chapter_in_backend(config: Dict, context_key: str, chapter_index: int, old_folder_name: str, new_folder_name: str, is_standalone: bool, new_number: str, new_name: str) -> bool:
    """Update chapter folder in backend when any field changes"""
    try:
        safe_code = FolderManager.sanitize_name(config['code'])
        book_name = config['book_name']
        base_name = f"{safe_code}_{book_name}"
        
        # Get project path
        project_destination = SessionManager.get_project_destination()
        if project_destination and os.path.exists(project_destination):
            base_path = Path(project_destination)
        else:
            base_path = Path.cwd()
        
        project_path = base_path / base_name
        
        # Determine paths
        if is_standalone:
            old_path = project_path / old_folder_name
            new_path = project_path / new_folder_name
        else:
            part_path = project_path / f"{base_name}_{context_key}"
            old_path = part_path / old_folder_name
            new_path = part_path / new_folder_name
        
        # Rename folder if names are different
        if old_path.exists():
            if old_path != new_path:
                old_path.rename(new_path)
                
                # Update created folders list
                current_folders = SessionManager.get('created_folders', [])
                old_path_str = str(old_path.absolute())
                new_path_str = str(new_path.absolute())
                
                if old_path_str in current_folders:
                    current_folders.remove(old_path_str)
                    current_folders.append(new_path_str)
                    SessionManager.set('created_folders', current_folders)
                
                # Update metadata
                folder_metadata = SessionManager.get('folder_metadata', {})
                for folder_id, metadata in folder_metadata.items():
                    if metadata.get('actual_path') == old_path_str:
                        metadata['actual_path'] = new_path_str
                        metadata['folder_name'] = new_folder_name
                        metadata['naming_base'] = new_folder_name
                        metadata['chapter_number'] = new_number
                        metadata['chapter_name'] = new_name
                        break
                SessionManager.set('folder_metadata', folder_metadata)
                
                # Rename all PDF files inside the folder
                for pdf_file in new_path.glob("*.pdf"):
                    old_file_name = pdf_file.name
                    if old_folder_name in old_file_name:
                        new_file_name = old_file_name.replace(old_folder_name, new_folder_name)
                        pdf_file.rename(new_path / new_file_name)
            else:
                # Same folder name but update metadata anyway
                folder_metadata = SessionManager.get('folder_metadata', {})
                path_str = str(old_path.absolute())
                for folder_id, metadata in folder_metadata.items():
                    if metadata.get('actual_path') == path_str:
                        metadata['chapter_number'] = new_number
                        metadata['chapter_name'] = new_name
                        break
                SessionManager.set('folder_metadata', folder_metadata)
            
            # Update chapter in session state
            if is_standalone:
                chapters = SessionManager.get('standalone_chapters', [])
                if chapter_index < len(chapters):
                    chapters[chapter_index]['number'] = new_number
                    chapters[chapter_index]['name'] = new_name
                    SessionManager.set('standalone_chapters', chapters)
            else:
                chapters_config = SessionManager.get('chapters_config', {})
                if context_key in chapters_config and chapter_index < len(chapters_config[context_key]):
                    chapters_config[context_key][chapter_index]['number'] = new_number
                    chapters_config[context_key][chapter_index]['name'] = new_name
                    SessionManager.set('chapters_config', chapters_config)
            
            return True
        else:
            st.error("Chapter folder not found")
            return False
        
    except PermissionError:
        st.error("Permission denied. Cannot update chapter folder.")
        return False
    except Exception as e:
        st.error(f"Error updating chapter: {str(e)}")
        return False

def get_created_chapter_indices(config: Dict, context_key: str, chapters: List[Dict], is_standalone: bool) -> set:
    """Check which chapter folders actually exist on filesystem"""
    created_indices = set()
    
    safe_code = FolderManager.sanitize_name(config['code'])
    book_name = config['book_name']
    base_name = f"{safe_code}_{book_name}"
    
    project_destination = SessionManager.get_project_destination()
    if project_destination and os.path.exists(project_destination):
        base_path = Path(project_destination)
    else:
        base_path = Path.cwd()
    
    project_path = base_path / base_name
    
    if not project_path.exists():
        return created_indices
    
    for i, chapter in enumerate(chapters):
        if is_standalone:
            parent_folder_name = base_name
            chapter_folder_name = ChapterManager.generate_chapter_folder_name(
                parent_folder_name,
                chapter.get('number'),
                chapter.get('name')
            )
            chapter_path = project_path / chapter_folder_name
        else:
            parent_folder_name = f"{base_name}_{context_key}"
            chapter_folder_name = ChapterManager.generate_chapter_folder_name(
                parent_folder_name,
                chapter.get('number'),
                chapter.get('name')
            )
            part_path = project_path / parent_folder_name
            chapter_path = part_path / chapter_folder_name
        
        if chapter_path.exists():
            created_indices.add(i)
    
    return created_indices


def render_chapter_configuration(config: Dict, existing_parts: List[Dict]):
    """Render chapter configuration interface for custom parts"""
    
    for part_info in existing_parts:
        part_name = part_info['name']
        with st.expander(f"📖 {part_name} Chapters", expanded=part_info == existing_parts[0] if existing_parts else False):
            render_part_chapters_optimized(part_name, config)
    
    # Create all chapters button
    chapters_config = SessionManager.get('chapters_config', {})
    if any(chapters_config.values()):
        if st.button("🏗️ Create All Chapters", type="primary"):
            create_all_chapters(config, chapters_config)

def render_part_chapters_optimized(part_name: str, config: Dict):
    """Optimized part chapters rendering"""
    
    context_key = part_name
    
    # Get current state
    current_chapters = ChapterConfigManager.get_chapters_for_context(context_key)
    current_count = len(current_chapters)
    current_system = ChapterConfigManager.get_current_numbering_system(context_key)
    current_suffix = SessionManager.get_chapter_suffix(context_key)
    
    # Number of chapters input
    target_count = st.number_input(
        f"Number of chapters in {part_name}",
        min_value=0,
        value=current_count,
        step=1,
        key=f"chapters_count_{part_name}",
        help="Enter any number of chapters (no limit)"
    )
    
    # Numbering system selector with suffix
    if target_count > 0:
        new_system, new_suffix = ChapterUtils.render_numbering_system_selector(
            f"part_{context_key}",
            current_system,
            f"Choose how chapters should be numbered for {part_name}",
            current_suffix
        )
        
        # Handle system or suffix change
        system_changed = new_system != current_system
        suffix_changed = new_suffix != current_suffix
        
        if system_changed or suffix_changed:
            if system_changed:
                ChapterConfigManager.update_numbering_system(context_key, new_system)
            if suffix_changed:
                SessionManager.set_chapter_suffix(context_key, new_suffix)
                # Update existing chapters with new suffix
                if current_chapters:
                    updated_chapters = ChapterUtils.update_chapters_with_numbering(
                        current_chapters, new_system, new_suffix
                    )
                    chapters_config = SessionManager.get('chapters_config', {})
                    chapters_config[context_key] = updated_chapters
                    SessionManager.set('chapters_config', chapters_config)
            
            st.rerun()
    
    # Handle count change
    if target_count != current_count:
        current_chapters = ChapterConfigManager.update_chapter_count(
            context_key, target_count, current_chapters, current_system, current_suffix
        )
        st.rerun()
    
    # Render chapter details
    if target_count > 0:
        render_chapter_details_optimized(context_key, current_chapters, config, is_standalone=False)
        
        # Action buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button(f"🏗️ Create {part_name} Chapters", key=f"create_part_{part_name}"):
                create_chapters_for_custom_part(config, part_name, current_chapters)
        
        with col2:
            if SessionManager.get('chapters_created') and any(current_chapters):
                if st.button(f"🔄 Update {part_name} Chapters", key=f"update_part_{part_name}"):
                    update_existing_chapters_for_part(config, part_name, current_chapters)

def render_chapter_preview(config: Dict):
    """Render chapter structure preview"""
    st.subheader("📋 Structure Preview")
    
    chapters_config = SessionManager.get('chapters_config', {})
    standalone_chapters = SessionManager.get('standalone_chapters', [])
    
    if not any(chapters_config.values()) and not standalone_chapters:
        st.info("Configure chapters to see preview")
        return
    
    safe_code = FolderManager.sanitize_name(config['code'])
    book_name = config['book_name']
    base_name = f"{safe_code}_{book_name}"
    
    # Show standalone chapters first
    if standalone_chapters:
        st.markdown("**Standalone Chapters:**")
        preview_chapters = ChapterManager.get_chapters_preview(
            base_name, "standalone", standalone_chapters, is_standalone=True
        )
        
        for chapter_folder in preview_chapters:
            st.write(f"📖 {chapter_folder}")
        
        st.markdown("---")
    
    # Show part chapters
    for part_name, chapters in chapters_config.items():
        if chapters:
            st.markdown(f"**{part_name}:**")
            
            preview_chapters = ChapterManager.get_chapters_preview(
                base_name, part_name, chapters, is_custom_part=True
            )
            
            for chapter_folder in preview_chapters:
                st.write(f"📂 {chapter_folder}")
            
            st.markdown("---")

# Keep existing functions but optimize them
def get_existing_custom_parts(config: Dict) -> List[Dict]:
    """Get list of actually existing custom parts by checking filesystem first, then session state"""
    existing_parts = []
    
    safe_code = FolderManager.sanitize_name(config.get('code', ''))
    book_name = config.get('book_name', '')
    base_name = f"{safe_code}_{book_name}"
    
    # Get custom parts from session state
    custom_parts = SessionManager.get('custom_parts', {})
    
    # Check filesystem directly to get the truth - use project destination
    try:
        project_destination = SessionManager.get_project_destination()
        if project_destination and os.path.exists(project_destination):
            base_path = Path(project_destination)
        else:
            base_path = Path.cwd()
        
        project_path = base_path / base_name
        
        if project_path.exists() and project_path.is_dir():
            # Check which custom parts actually exist on filesystem
            for part_id, part_info in custom_parts.items():
                part_name = part_info['name']
                part_folder = project_path / f"{base_name}_{part_name}"
                
                if part_folder.exists():
                    existing_parts.append({
                        'id': part_id,
                        'name': part_name,
                        'path': str(part_folder.absolute()),
                        'display_name': part_info.get('display_name', part_name)
                    })
    except Exception:
        pass
    
    return existing_parts

def delete_individual_custom_part(config: Dict, part_name: str):
    """Delete an individual custom part folder and all its contents"""
    try:
        safe_code = FolderManager.sanitize_name(config['code'])
        book_name = config['book_name']
        base_name = f"{safe_code}_{book_name}"
        
        # Use project destination instead of current directory
        project_destination = SessionManager.get_project_destination()
        if project_destination and os.path.exists(project_destination):
            base_path = Path(project_destination)
        else:
            base_path = Path.cwd()
        
        project_path = base_path / base_name
        
        if not project_path.exists():
            st.error(f"Project folder not found. Cannot delete part '{part_name}'.")
            return
        
        # Find the part folder
        part_folder = project_path / f"{base_name}_{part_name}"
        
        if not part_folder.exists():
            st.error(f"Part '{part_name}' folder not found.")
            return
        
        # Delete the folder and all contents
        shutil.rmtree(part_folder)
        
        # Rest of the cleanup logic remains the same...
        custom_parts = SessionManager.get('custom_parts', {})
        part_to_remove = None
        
        for part_id, part_info in custom_parts.items():
            if part_info['name'] == part_name:
                part_to_remove = part_id
                break
        
        if part_to_remove:
            del custom_parts[part_to_remove]
            SessionManager.set('custom_parts', custom_parts)
        
        # Update created folders list and remove related metadata
        current_folders = SessionManager.get('created_folders', [])
        part_path_str = str(part_folder.absolute())
        if part_path_str in current_folders:
            current_folders.remove(part_path_str)
        
        # Remove any chapter folders that were in this part
        folders_to_remove = []
        for folder_path in current_folders:
            if f"_{part_name}" in folder_path and base_name in folder_path:
                folders_to_remove.append(folder_path)
        
        for folder_path in folders_to_remove:
            current_folders.remove(folder_path)
        
        SessionManager.set('created_folders', current_folders)
        
        # Remove chapter metadata for this part
        folder_metadata = SessionManager.get('folder_metadata', {})
        metadata_to_remove = []
        for folder_id, metadata in folder_metadata.items():
            if (metadata.get('type') == 'chapter' and 
                metadata.get('parent_part_name') == part_name):
                metadata_to_remove.append(folder_id)
            elif (metadata.get('type') == 'custom' and 
                  f"_{part_name}" in metadata.get('actual_path', '')):
                metadata_to_remove.append(folder_id)
        
        for folder_id in metadata_to_remove:
            del folder_metadata[folder_id]
        
        SessionManager.set('folder_metadata', folder_metadata)
        
        # Remove chapters config for this part
        chapters_config = SessionManager.get('chapters_config', {})
        if part_name in chapters_config:
            del chapters_config[part_name]
            SessionManager.set('chapters_config', chapters_config)
        
        # Set success message for next render
        st.session_state['part_operation_completed'] = True
        st.session_state['part_operation_info'] = {
            'operation': 'delete',
            'part_name': part_name
        }
        
    except PermissionError:
        st.error(f"❌ Permission denied. Cannot delete part '{part_name}'. Please check folder permissions.")
    except Exception as e:
        st.error(f"❌ Error deleting part '{part_name}': {str(e)}")

def render_prerequisites_warning():
    """Render warning when prerequisites are not met"""
    st.warning("⚠️ Please complete the project setup first!")
    st.markdown("""
    **Required steps:**
    1. Upload PDF file
    2. Configure project details
    3. Create folder structure
    """)

# Keep existing creation functions (they work fine)
def create_standalone_chapters(config: Dict, chapters: List[Dict]):
    """Create standalone chapters directly under project root"""
    if not chapters or not any(ch.get('number') or ch.get('name') for ch in chapters):
        st.warning("No standalone chapters configured!")
        return
    
    try:
        with st.spinner("Creating standalone chapters..."):
            safe_code = FolderManager.sanitize_name(config['code'])
            book_name = config['book_name']
            base_name = f"{safe_code}_{book_name}"
            
            # Use project destination instead of current directory
            project_destination = SessionManager.get_project_destination()
            if project_destination and os.path.exists(project_destination):
                base_path = Path(project_destination)
            else:
                base_path = Path.cwd()
            
            project_path = base_path / base_name
            
            if not project_path.exists():
                project_path.mkdir(parents=True, exist_ok=True)
                st.info(f"Created project directory: {project_path.absolute()}")
            
            # Validate chapters before creating
            is_valid, error_msg = ChapterManager.validate_chapter_data(chapters)
            if not is_valid:
                st.error(f"Error in standalone chapters: {error_msg}")
                return
            
            created_chapters = ChapterManager.create_standalone_chapter_folders(
                project_path, base_name, chapters
            )
            
            if created_chapters:
                SessionManager.set('chapters_created', True)
                # Update created folders list
                current_folders = SessionManager.get('created_folders', [])
                current_folders.extend(created_chapters)
                SessionManager.set('created_folders', current_folders)
                
                st.success(f"✅ Created {len(created_chapters)} standalone chapters!")
                
                # Show created chapters
                with st.expander("📂 View Created Standalone Chapters"):
                    for chapter in created_chapters:
                        st.write(f"📂 {chapter}")
    
    except Exception as e:
        st.error(f"Error creating standalone chapters: {str(e)}")



def update_existing_standalone_chapters(config: Dict, chapters: List[Dict]):
    """Update existing standalone chapters in backend"""
    try:
        with st.spinner("Updating standalone chapters..."):
            safe_code = FolderManager.sanitize_name(config['code'])
            book_name = config['book_name']
            base_name = f"{safe_code}_{book_name}"
            
            # Get project path
            project_destination = SessionManager.get_project_destination()
            if project_destination and os.path.exists(project_destination):
                base_path = Path(project_destination)
            else:
                base_path = Path.cwd()
            
            project_path = base_path / base_name
            
            if not project_path.exists():
                st.error("Project folder not found")
                return
            
            # Get existing chapter folders from metadata
            folder_metadata = SessionManager.get('folder_metadata', {})
            existing_chapters = []
            
            for folder_id, metadata in folder_metadata.items():
                if metadata.get('type') == 'standalone_chapter':
                    existing_chapters.append({
                        'id': folder_id,
                        'path': metadata.get('actual_path'),
                        'old_name': metadata.get('folder_name'),
                        'metadata': metadata
                    })
            
            # Match and update each chapter
            updated_count = 0
            for i, chapter in enumerate(chapters):
                if i < len(existing_chapters):
                    existing = existing_chapters[i]
                    old_path = Path(existing['path'])
                    
                    if old_path.exists():
                        # Generate new folder name
                        new_folder_name = ChapterManager.generate_chapter_folder_name(
                            base_name,
                            chapter.get('number'),
                            chapter.get('name')
                        )
                        
                        new_path = project_path / new_folder_name
                        
                        # Rename if different
                        if old_path != new_path:
                            # First, rename all subfolders and their contents
                            rename_subfolders_with_new_prefix(old_path, existing['old_name'], new_folder_name)
                            
                            # Then rename the main chapter folder
                            old_path.rename(new_path)
                            
                            # Update metadata
                            folder_metadata[existing['id']]['actual_path'] = str(new_path.absolute())
                            folder_metadata[existing['id']]['folder_name'] = new_folder_name
                            folder_metadata[existing['id']]['naming_base'] = new_folder_name
                            folder_metadata[existing['id']]['chapter_number'] = chapter.get('number', '')
                            folder_metadata[existing['id']]['chapter_name'] = chapter.get('name', '')
                            
                            # Update created folders list
                            current_folders = SessionManager.get('created_folders', [])
                            old_path_str = str(old_path.absolute())
                            new_path_str = str(new_path.absolute())
                            
                            if old_path_str in current_folders:
                                current_folders.remove(old_path_str)
                                current_folders.append(new_path_str)
                                SessionManager.set('created_folders', current_folders)
                            
                            # Rename PDF files inside
                            for pdf_file in new_path.glob("*.pdf"):
                                old_file_name = pdf_file.name
                                if existing['old_name'] in old_file_name:
                                    new_file_name = old_file_name.replace(existing['old_name'], new_folder_name)
                                    pdf_file.rename(new_path / new_file_name)
                            
                            updated_count += 1
            
            SessionManager.set('folder_metadata', folder_metadata)
            
            if updated_count > 0:
                st.success(f"✅ Updated {updated_count} standalone chapters!")
            else:
                st.info("No changes to update")
                
    except Exception as e:
        st.error(f"Error updating standalone chapters: {str(e)}")


def rename_subfolders_with_new_prefix(parent_folder: Path, old_prefix: str, new_prefix: str):
    """Rename all subfolders inside a chapter to use new parent prefix"""
    try:
        # Get all immediate subfolders
        if not parent_folder.exists():
            return
        
        subfolders = [item for item in parent_folder.iterdir() if item.is_dir()]
        
        for subfolder in subfolders:
            old_subfolder_name = subfolder.name
            
            # Check if subfolder name starts with old prefix
            if old_subfolder_name.startswith(old_prefix):
                # Replace old prefix with new prefix
                new_subfolder_name = old_subfolder_name.replace(old_prefix, new_prefix, 1)
                new_subfolder_path = subfolder.parent / new_subfolder_name
                
                # Rename subfolder
                subfolder.rename(new_subfolder_path)
                
                # Rename all files inside the subfolder
                for file in new_subfolder_path.rglob("*"):
                    if file.is_file():
                        old_file_name = file.name
                        if old_prefix in old_file_name:
                            new_file_name = old_file_name.replace(old_prefix, new_prefix)
                            file.rename(file.parent / new_file_name)
                
                # Update metadata for this subfolder
                folder_metadata = SessionManager.get('folder_metadata', {})
                old_subfolder_str = str(subfolder.absolute())
                new_subfolder_str = str(new_subfolder_path.absolute())
                
                for folder_id, metadata in folder_metadata.items():
                    if metadata.get('actual_path') == old_subfolder_str:
                        metadata['actual_path'] = new_subfolder_str
                        metadata['folder_name'] = new_subfolder_name
                        metadata['naming_base'] = new_subfolder_name
                        break
                
                SessionManager.set('folder_metadata', folder_metadata)
                
                # Update created folders list
                current_folders = SessionManager.get('created_folders', [])
                if old_subfolder_str in current_folders:
                    current_folders.remove(old_subfolder_str)
                    current_folders.append(new_subfolder_str)
                    SessionManager.set('created_folders', current_folders)
                
    except Exception as e:
        st.error(f"Error renaming subfolders: {str(e)}")


def create_chapters_for_custom_part(config: Dict, part_name: str, chapters: List[Dict]):
    """Create chapters for a specific custom part only"""
    if not chapters or not any(ch.get('number') or ch.get('name') for ch in chapters):
        st.warning(f"No chapters configured for {part_name}!")
        return
    
    try:
        with st.spinner(f"Creating chapters for {part_name}..."):
            safe_code = FolderManager.sanitize_name(config['code'])
            book_name = config['book_name']
            base_name = f"{safe_code}_{book_name}"
            
            # Use project destination instead of current directory
            project_destination = SessionManager.get_project_destination()
            if project_destination and os.path.exists(project_destination):
                base_path = Path(project_destination)
            else:
                base_path = Path.cwd()
            
            project_path = base_path / base_name
            
            if not project_path.exists():
                project_path.mkdir(parents=True, exist_ok=True)
                st.info(f"Created project directory: {project_path.absolute()}")
            
            # Validate chapters before creating
            is_valid, error_msg = ChapterManager.validate_chapter_data(chapters)
            if not is_valid:
                st.error(f"Error in {part_name}: {error_msg}")
                return
            
            created_chapters = ChapterManager.create_chapter_folders_for_custom_part(
                project_path, base_name, part_name, chapters
            )
            
            if created_chapters:
                SessionManager.set('chapters_created', True)
                # Update created folders list
                current_folders = SessionManager.get('created_folders', [])
                current_folders.extend(created_chapters)
                SessionManager.set('created_folders', current_folders)
                
                st.success(f"✅ Created {len(created_chapters)} chapters for {part_name}!")
                
                # Show created chapters
                with st.expander(f"📂 View Created Chapters for {part_name}"):
                    for chapter in created_chapters:
                        st.write(f"📂 {chapter}")
    
    except Exception as e:
        st.error(f"Error creating chapters for {part_name}: {str(e)}")

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
            
            # Use project destination instead of current directory
            project_destination = SessionManager.get_project_destination()
            if project_destination and os.path.exists(project_destination):
                base_path = Path(project_destination)
            else:
                base_path = Path.cwd()
            
            project_path = base_path / base_name
            
            if not project_path.exists():
                project_path.mkdir(parents=True, exist_ok=True)
                st.info(f"Created project directory: {project_path.absolute()}")
            
            all_created_chapters = []
            
            for part_name, chapters in chapters_config.items():
                if chapters and any(ch.get('number') or ch.get('name') for ch in chapters):
                    
                    # Validate chapters before creating
                    is_valid, error_msg = ChapterManager.validate_chapter_data(chapters)
                    if not is_valid:
                        st.error(f"Error in {part_name}: {error_msg}")
                        continue
                    
                    created_chapters = ChapterManager.create_chapter_folders_for_custom_part(
                        project_path, base_name, part_name, chapters
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



def update_existing_chapters_for_part(config: Dict, part_name: str, chapters: List[Dict]):
    """Update existing chapters for a specific custom part"""
    try:
        with st.spinner(f"Updating chapters for {part_name}..."):
            safe_code = FolderManager.sanitize_name(config['code'])
            book_name = config['book_name']
            base_name = f"{safe_code}_{book_name}"
            
            # Get project path
            project_destination = SessionManager.get_project_destination()
            if project_destination and os.path.exists(project_destination):
                base_path = Path(project_destination)
            else:
                base_path = Path.cwd()
            
            project_path = base_path / base_name
            part_path = project_path / f"{base_name}_{part_name}"
            
            if not part_path.exists():
                st.error(f"Part folder not found: {part_name}")
                return
            
            # Get existing chapter folders from metadata
            folder_metadata = SessionManager.get('folder_metadata', {})
            existing_chapters = []
            
            for folder_id, metadata in folder_metadata.items():
                if (metadata.get('type') == 'chapter' and 
                    metadata.get('parent_part_name') == part_name):
                    existing_chapters.append({
                        'id': folder_id,
                        'path': metadata.get('actual_path'),
                        'old_name': metadata.get('folder_name'),
                        'metadata': metadata
                    })
            
            # Match and update each chapter
            updated_count = 0
            parent_folder_name = f"{base_name}_{part_name}"
            
            for i, chapter in enumerate(chapters):
                if i < len(existing_chapters):
                    existing = existing_chapters[i]
                    old_path = Path(existing['path'])
                    
                    if old_path.exists():
                        # Generate new folder name
                        new_folder_name = ChapterManager.generate_chapter_folder_name(
                            parent_folder_name,
                            chapter.get('number'),
                            chapter.get('name')
                        )
                        
                        new_path = part_path / new_folder_name
                        
                        # Rename if different
                        if old_path != new_path:
                            # First, rename all subfolders and their contents
                            rename_subfolders_with_new_prefix(old_path, existing['old_name'], new_folder_name)
                            
                            # Then rename the main chapter folder
                            old_path.rename(new_path)
                            
                            # Update metadata
                            folder_metadata[existing['id']]['actual_path'] = str(new_path.absolute())
                            folder_metadata[existing['id']]['folder_name'] = new_folder_name
                            folder_metadata[existing['id']]['naming_base'] = new_folder_name
                            folder_metadata[existing['id']]['chapter_number'] = chapter.get('number', '')
                            folder_metadata[existing['id']]['chapter_name'] = chapter.get('name', '')
                            
                            # Update created folders list
                            current_folders = SessionManager.get('created_folders', [])
                            old_path_str = str(old_path.absolute())
                            new_path_str = str(new_path.absolute())
                            
                            if old_path_str in current_folders:
                                current_folders.remove(old_path_str)
                                current_folders.append(new_path_str)
                                SessionManager.set('created_folders', current_folders)
                            
                            # Rename PDF files inside
                            for pdf_file in new_path.glob("*.pdf"):
                                old_file_name = pdf_file.name
                                if existing['old_name'] in old_file_name:
                                    new_file_name = old_file_name.replace(existing['old_name'], new_folder_name)
                                    pdf_file.rename(new_path / new_file_name)
                            
                            updated_count += 1
            
            SessionManager.set('folder_metadata', folder_metadata)
            
            if updated_count > 0:
                st.success(f"✅ Updated {updated_count} chapters for {part_name}!")
            else:
                st.info("No changes to update")
                
    except Exception as e:
        st.error(f"Error updating chapters for {part_name}: {str(e)}")


# ===== File: src/ui/custom_folder_management.py =====

# src/ui/custom_folder_management.py
import streamlit as st
from typing import Dict, List, Optional
from pathlib import Path

from core.session_manager import SessionManager
import os

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
    """Create a custom folder with parent folder prefix + custom name and font formatting"""
    
    try:
        # Lazy import for font formatting
        from core.text_formatter import TextFormatter
        font_case = st.session_state.get('selected_font_case', 'First Capital (Sentence case)')
        
        parent_folder = Path(parent_path)
        parent_folder_name = parent_folder.name
        
        # Apply font formatting to the custom folder name
        formatted_folder_name = TextFormatter.format_custom_folder_name(folder_name, font_case)
        final_folder_name = f"{parent_folder_name}_{formatted_folder_name}"
        
        custom_folder_path = parent_folder / final_folder_name
        
        # Check if folder already exists
        if custom_folder_path.exists():
            st.error(f"❌ Folder '{final_folder_name}' already exists in '{parent_folder_name}'. Please choose a different name.")
            return False
        
        with st.spinner(f"Creating custom folder '{final_folder_name}'..."):
            # Ensure parent folder exists
            parent_folder.mkdir(parents=True, exist_ok=True)
            
            # Create the custom folder with parent prefix + formatted custom name
            custom_folder_path.mkdir(exist_ok=True)
            
            # Add to metadata - FIXED: Use correct number of arguments
            add_folder_to_metadata(
                str(custom_folder_path.absolute()), 
                final_folder_name, 
                parent_path,
                folder_name  # Original name for reference
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
    """Add folder to metadata tracking - FIXED signature"""
    
    folder_metadata = SessionManager.get('folder_metadata', {})
    import random
    custom_folder_id = f"custom_{random.randint(10000, 99999)}"
    
    parent_name = Path(parent_path).name
    display_original_name = original_name or folder_name
    
    folder_metadata[custom_folder_id] = {
        'display_name': f"{parent_name} → {display_original_name}",
        'actual_path': folder_path,
        'type': 'custom',
        'parent_path': parent_path,
        'folder_name': folder_name,  # Full name with prefix and formatting
        'naming_base': folder_name,   # Use full formatted name for file naming
        'original_name': original_name  # Keep original input
    }
    
    SessionManager.set('folder_metadata', folder_metadata)
    
    # Update created folders list
    current_folders = SessionManager.get('created_folders', [])
    if folder_path not in current_folders:
        current_folders.append(folder_path)
        SessionManager.set('created_folders', current_folders)

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
    """Get the project path using project destination"""
    # Use project destination instead of current directory  
    project_destination = SessionManager.get_project_destination()
    if project_destination and os.path.exists(project_destination):
        base_path = Path(project_destination)
    else:
        base_path = Path.cwd()
    
    project_path = base_path / base_name
    
    if not project_path.exists():
        # Create if doesn't exist
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


# ===== File: src/ui/folder_selector.py =====

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
    st.info(f"📍 **Current:** `{current_path}`")
    
    # Navigation controls
    col1, col2, col3, col4 = st.columns([1, 1, 3, 1])
    
    with col1:
        if st.button("🏠 Home", key="nav_home", use_container_width=True):
            st.session_state['browser_path'] = str(Path.home().absolute())
            st.rerun()
    
    with col2:
        if current_path.parent != current_path:
            if st.button("⬆️ Up", key="nav_up", use_container_width=True):
                st.session_state['browser_path'] = str(current_path.parent.absolute())
                st.rerun()
    
    with col3:
        if context == 'page_assignment':
            button_text = "✅ SELECT FOR EXTRACTION"
        else:
            button_text = "✅ SET PROJECT LOCATION"
            
        if st.button(button_text, key="select_folder", type="primary", use_container_width=True):
            selected_path = str(current_path.absolute())
            
            if context == 'page_assignment':
                st.session_state['selected_page_destination'] = selected_path
                st.session_state['selected_page_destination_name'] = current_path.name
                st.success(f"Extraction destination selected: {current_path.name}")
                st.session_state['show_folder_browser'] = False
            else:
                SessionManager.set_project_destination(selected_path)
                st.success(f"Project location set: {current_path.name}")
                st.session_state['show_project_browser'] = False
            
            st.session_state['folder_browser_active'] = False
            st.rerun()
    
    with col4:
        if st.button("❌ Cancel", key="cancel_browser", use_container_width=True):
            st.session_state['folder_browser_active'] = False
            st.session_state['show_folder_browser'] = False
            st.session_state['show_project_browser'] = False
            st.rerun()
    
    st.markdown("---")
    
    # Quick access in expander
    with st.expander("⚡ Quick Access", expanded=False):
        quick_folders = get_quick_access_folders()
        
        if quick_folders:
            quick_cols = st.columns(len(quick_folders))
            for i, (name, path) in enumerate(quick_folders.items()):
                with quick_cols[i]:
                    if st.button(name, key=f"quick_nav_{i}", use_container_width=True):
                        st.session_state['browser_path'] = path
                        st.rerun()
    
    # Folder listing with full names visible
    try:
        folders = [item for item in current_path.iterdir() 
                  if item.is_dir() and not item.name.startswith('.')]
        folders.sort(key=lambda x: x.name.lower())
        
        if folders:
            st.markdown(f"**📁 Folders ({len(folders)}):**")
            
            # Display folders in 3-column grid with full names
            cols_per_row = 3
            for i in range(0, len(folders), cols_per_row):
                cols = st.columns(cols_per_row)
                
                for j, folder in enumerate(folders[i:i+cols_per_row]):
                    if j < len(cols):
                        with cols[j]:
                            folder_name = folder.name
                            
                            # Show full folder name as button text (no truncation)
                            # Button will auto-wrap text if needed
                            if st.button(f"📁 {folder_name}", 
                                       key=f"folder_nav_{i}_{j}",
                                       use_container_width=True):
                                st.session_state['browser_path'] = str(folder.absolute())
                                st.rerun()
        else:
            st.info("📂 No subfolders in this directory")
            
    except PermissionError:
        st.error("❌ Permission denied")
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
    
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


# ===== File: src/ui/font_selector.py =====

# ui/font_selector.py - Font case selection interface

import streamlit as st

def render_font_case_selector():
    """Render font case selection interface"""
    # Lazy import to avoid circular dependency
    from core.text_formatter import TextFormatter
    
    st.subheader("🎨 Text Formatting Setup")
    st.markdown("Choose how all text elements (codes, names, chapters, etc.) should be formatted throughout the application.")
    
    # Center the content
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("### Select Font Case Style")
        
        # Get font case options
        font_options = TextFormatter.get_font_case_options()
        current_selection = st.session_state.get('selected_font_case', font_options[2])  # Default to First Capital
        
        # Find current index
        try:
            current_index = font_options.index(current_selection)
        except ValueError:
            current_index = 2  # Default to First Capital
        
        selected_font_case = st.radio(
            "Choose formatting style:",
            font_options,
            index=current_index,
            key="font_case_radio",
            help="This formatting will be applied to all text elements including book codes, names, chapters, and folder names"
        )
        
        # Show preview examples
        st.markdown("---")
        st.markdown("### Preview Examples")
        
        # Example texts
        example_code = "CS101"
        example_book = "Data Structures and Algorithms"
        example_part = "Advanced Topics"
        example_chapter = "Binary Search Trees"
        
        # Format examples
        formatted_code = TextFormatter.format_project_code(example_code, selected_font_case)
        formatted_book = TextFormatter.format_book_name(example_book, selected_font_case)
        formatted_part = TextFormatter.format_part_name(example_part, selected_font_case)
        formatted_chapter = TextFormatter.format_chapter_name(example_chapter, selected_font_case)
        
        # Display examples in a nice format
        st.markdown(f"**Project Code:** `{formatted_code}`")
        st.markdown(f"**Book Name:** `{formatted_book}`")
        st.markdown(f"**Part Name:** `{formatted_part}`")
        st.markdown(f"**Chapter Name:** `{formatted_chapter}`")
        
        st.markdown("---")
        
        # Confirmation button
        col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
        
        with col_btn2:
            if st.button("✅ Confirm Selection", type="primary", key="confirm_font_case"):
                st.session_state['selected_font_case'] = selected_font_case
                st.session_state['font_case_selected'] = True
                st.success(f"✅ Font case set to: {selected_font_case}")
                st.rerun()
        
        # Option to change later
        st.markdown("---")
        st.info("💡 You can change the font formatting later from the sidebar settings.")


def render_font_case_changer():
    """Render font case changer for sidebar with radio buttons"""
    from core.text_formatter import TextFormatter
    from src.core.session_manager import SessionManager
    
    if st.session_state.get('font_case_selected'):
        st.markdown("---")
        st.subheader("🎨 Text Format")
        
        current_font_case = st.session_state.get('selected_font_case', 'First Capital (Title Case)')
        font_options = TextFormatter.get_font_case_options()
        
        try:
            current_index = font_options.index(current_font_case)
        except ValueError:
            current_index = 2
        
        # Initialize the previous selection in session state if not exists
        if 'previous_font_selection' not in st.session_state:
            st.session_state['previous_font_selection'] = current_font_case
        
        # Simple radio button selection
        selected_font_case = st.radio(
            "Select font format:",
            font_options,
            index=current_index,
            key="font_case_radio_selection",
            help="Choose how all text elements are formatted"
        )
        
        # Only process change if it's actually different from previous selection
        if selected_font_case != st.session_state['previous_font_selection']:
            st.markdown("**Preview:**")
            sample_texts = ["CS101", "Data Structures", "Advanced Topics"]
            
            for sample in sample_texts:
                formatted = TextFormatter.format_text(sample, selected_font_case)
                st.write(f"`{formatted}`")
            
            # Update both current and previous selections
            st.session_state['selected_font_case'] = selected_font_case
            st.session_state['previous_font_selection'] = selected_font_case
            st.success(f"Font format updated to: {selected_font_case}")
            
            # FIXED: Don't rerun if folder structure is already created
            # Only rerun if we're still in setup phase
            if not SessionManager.get('folder_structure_created'):
                st.rerun()


# ===== File: src/ui/main_content.py =====

# src/ui/main_content.py
import os
import streamlit as st
from typing import Dict, List
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
    3. **Configure Custom Parts**: Create custom-named parts (e.g., 'India', 'Iran', 'History')
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
        
        # Check if font case is selected before showing folder creation
        if SessionManager.get('font_case_selected'):
            render_folder_creation_button(config)
        else:
            st.info("Please select font formatting in the sidebar first.")
    else:
        st.warning("⚠️ Please complete the project configuration in the sidebar")


def is_project_configured(config: dict) -> bool:
    """Check if project is properly configured"""
    return bool(config.get('code') and config.get('book_name'))

def display_project_info(config: dict):
    """Display current project information"""
    pdf_file = SessionManager.get('pdf_file')
    total_pages = SessionManager.get('total_pages')
    custom_parts = SessionManager.get('custom_parts', {})
    
    if pdf_file:
        st.write(f"**Project:** {config['code']}_{config['book_name']}")
        st.write(f"**PDF:** {pdf_file.name}")
        st.write(f"**Total Pages:** {total_pages}")
        st.write(f"**Custom Parts:** {len(custom_parts)} parts configured")
        
        # Show part names if any exist
        if custom_parts:
            part_names = [part_info['name'] for part_info in custom_parts.values()]
            st.write(f"**Part Names:** {', '.join(part_names)}")

def render_folder_creation_button(config: dict):
    """Render folder creation interface with default folder selection"""
    if SessionManager.get('folder_structure_created'):
        st.success("✅ Folder structure already created!")
        
        # Show created folders
        created_folders = SessionManager.get('created_folders', [])
        with st.expander("📁 View Created Folders"):
            for folder in created_folders:
                st.write(f"📂 {folder}")
    else:
        render_default_folder_selection(config)


def render_default_folder_selection(config: dict):
    """Render default folder selection interface"""
    st.markdown("### 📂 Select Default Folders to Create")
    st.markdown("Choose which default folders you want to include in your project structure:")
    
    # Get available default folder options
    folder_options = FolderManager.get_default_folder_options()
    
    # Create checkboxes for each default folder
    col1, col2 = st.columns(2)
    selected_folders = []
    
    for i, folder_option in enumerate(folder_options):
        folder_name = folder_option['name']
        folder_desc = folder_option['description']
        
        # Alternate between columns
        target_col = col1 if i % 2 == 0 else col2
        
        with target_col:
            # Pre-select common folders
            default_selected = folder_name in ['prologue', 'index', 'epilogue']
            
            if st.checkbox(
                f"**{folder_name.title()}**",
                value=default_selected,
                key=f"default_folder_{folder_name}",
                help=folder_desc
            ):
                selected_folders.append(folder_name)
    
    # Show preview of selected folders
    if selected_folders:
        st.markdown("**Selected folders to create:**")
        safe_code = FolderManager.sanitize_name(config['code'])
        book_name = config['book_name']
        base_name = f"{safe_code}_{book_name}"
        
        # Apply font formatting to preview
        from core.text_formatter import TextFormatter
        font_case = SessionManager.get_font_case()
        
        for folder in selected_folders:
            formatted_folder = TextFormatter.format_folder_name(folder, font_case)
            preview_name = f"{base_name}_{formatted_folder}"
            st.write(f"📁 `{preview_name}`")
        
        st.markdown("---")
        
        # Create button
        col_create, col_skip = st.columns(2)
        
        with col_create:
            if st.button("🏗️ Create Folder Structure", type="primary"):
                create_folder_structure_with_selection(config, selected_folders)
        
        with col_skip:
            if st.button("⏭️ Skip Default Folders", type="secondary"):
                create_folder_structure_with_selection(config, [])
    else:
        st.info("No default folders selected. You can still create the project structure without default folders.")
        if st.button("🏗️ Create Project Structure Only", type="primary"):
            create_folder_structure_with_selection(config, [])


def create_folder_structure_with_selection(config: dict, selected_folders: List[str]):
    """Create the folder structure with selected default folders"""
    with st.spinner("Creating folder structure..."):
        code = config['code']
        book_name = config['book_name']
        custom_parts = SessionManager.get('custom_parts', {})
        
        project_path, created_folders = FolderManager.create_project_structure(
            code, book_name, selected_folders
        )
        
        if project_path:
            # Create custom parts folders if specified
            if custom_parts:
                safe_code = FolderManager.sanitize_name(code)
                base_name = f"{safe_code}_{book_name}"
                custom_parts_folders = FolderManager.create_custom_parts_folders(
                    project_path, base_name, custom_parts
                )
                created_folders.extend(custom_parts_folders)
            
            SessionManager.set('folder_structure_created', True)
            SessionManager.set('created_folders', created_folders)
            
            display_creation_success_with_selection(created_folders, custom_parts, selected_folders)
        else:
            st.error("Failed to create folder structure")


def display_creation_success_with_selection(created_folders: List[str], custom_parts: dict, selected_folders: List[str]):
    """Display success message with created folders including selection info"""
    st.success("✅ Folder structure created successfully!")
    
    # Show summary
    default_count = len(selected_folders)
    custom_parts_count = len(custom_parts)
    total_folders = len(created_folders)
    
    st.info(f"Created {total_folders} folders: {default_count} default folders + {custom_parts_count} custom parts")
    
    if selected_folders:
        st.markdown("**Created default folders:**")
        for folder in selected_folders:
            st.write(f"📁 {folder.title()}")
    
    if custom_parts:
        st.markdown("**Created custom parts:**")
        for part_info in custom_parts.values():
            st.write(f"🎯 {part_info['name']}")
    
    st.markdown("**All created folders:**")
    for folder in created_folders:
        folder_name = folder.split('/')[-1] if '/' in folder else folder.split('\\')[-1]
        if any(part_info['name'] in folder_name for part_info in custom_parts.values()):
            st.write(f"🎯 {folder}")  # Custom part folders
        else:
            st.write(f"📁 {folder}")  # Default folders

def create_folder_structure(config: dict):
    """Create the folder structure with custom parts"""
    with st.spinner("Creating folder structure..."):
        code = config['code']
        book_name = config['book_name']
        custom_parts = SessionManager.get('custom_parts', {})
        
        project_path, created_folders = FolderManager.create_project_structure(code, book_name)
        
        if project_path:
            # Create custom parts folders if specified
            if custom_parts:
                safe_code = FolderManager.sanitize_name(code)
                base_name = f"{safe_code}_{book_name}"
                custom_parts_folders = FolderManager.create_custom_parts_folders(
                    project_path, base_name, custom_parts
                )
                created_folders.extend(custom_parts_folders)
            
            SessionManager.set('folder_structure_created', True)
            SessionManager.set('created_folders', created_folders)
            
            display_creation_success(created_folders, custom_parts)
        else:
            st.error("Failed to create folder structure")

def display_creation_success(created_folders: List[str], custom_parts: dict):
    """Display success message with created folders"""
    st.success("✅ Folder structure created successfully!")
    
    # Show summary
    default_count = len(FolderManager.DEFAULT_FOLDERS)
    custom_parts_count = len(custom_parts)
    total_folders = len(created_folders)
    
    st.info(f"Created {total_folders} folders: {default_count} default folders + {custom_parts_count} custom parts")
    
    st.markdown("**Created folders:**")
    for folder in created_folders:
        folder_name = folder.split('/')[-1] if '/' in folder else folder.split('\\')[-1]
        if any(part_info['name'] in folder_name for part_info in custom_parts.values()):
            st.write(f"🎯 {folder}")  # Custom part folders
        else:
            st.write(f"📁 {folder}")  # Default folders

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
    custom_parts = SessionManager.get('custom_parts', {})
    
    st.metric("PDF Pages", total_pages)
    st.metric("Project Code", config.get('code', 'Not set'))
    st.metric("Custom Parts", len(custom_parts))
    
    # Chapter statistics
    total_chapters = sum(len(chapters) for chapters in chapters_config.values())
    if total_chapters > 0:
        st.metric("Total Chapters", total_chapters)
    
    if SessionManager.get('folder_structure_created'):
        created_folders = SessionManager.get('created_folders', [])
        st.metric("Folders Created", len(created_folders))
    
    # Pages generated metric with manual calculation button
    if SessionManager.get('folder_structure_created'):
        # Get cached count or show 0
        pages_generated = SessionManager.get('total_pages_generated', 0)
        last_calculated = SessionManager.get('pages_calculated_timestamp', None)
        
        st.metric("Pages Generated", pages_generated)
        from datetime import datetime
        if last_calculated:
            
            calc_time = datetime.fromisoformat(last_calculated)
            st.caption(f"Last calculated: {calc_time.strftime('%H:%M:%S')}")
        
        if st.button("🔄 Calculate Pages", key="calc_pages_btn", help="Count all PDF files in project folders"):
            with st.spinner("Counting generated pages..."):
                total_count = calculate_total_pages_generated(config)
                SessionManager.set('total_pages_generated', total_count)
                SessionManager.set('pages_calculated_timestamp', datetime.now().isoformat())
                st.success(f"Found {total_count} generated pages")
                st.rerun()
    
    # Show custom part names
    if custom_parts:
        st.markdown("**Custom Parts:**")
        for part_info in custom_parts.values():
            st.write(f"🎯 {part_info['name']}")


def calculate_total_pages_generated(config: Dict) -> int:
    """Calculate total number of PDF pages generated in all folders"""
    from pathlib import Path
    
    safe_code = FolderManager.sanitize_name(config.get('code', ''))
    book_name = config.get('book_name', '')
    base_name = f"{safe_code}_{book_name}"
    
    # Get project path
    project_destination = SessionManager.get_project_destination()
    if project_destination and os.path.exists(project_destination):
        base_path = Path(project_destination)
    else:
        base_path = Path.cwd()
    
    project_path = base_path / base_name
    
    if not project_path.exists():
        return 0
    
    # Count all PDF files recursively
    try:
        pdf_files = list(project_path.rglob("*.pdf"))
        return len(pdf_files)
    except Exception:
        return 0


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
    
    # Check if folder browser returned a selection
    if st.session_state.get('selected_page_destination'):
        selected_path = st.session_state['selected_page_destination']
        selected_name = st.session_state['selected_page_destination_name']
        
        st.success(f"Folder selected from browser: {selected_name}")
        
        # Clear the browser selection
        del st.session_state['selected_page_destination']
        del st.session_state['selected_page_destination_name']
        
        # Proceed with this destination
        destination_info = (selected_path, selected_name)
        render_page_range_input(destination_info)
        return
    
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
    
    # Show only 2 destination selection options
    destination_mode = st.radio(
        "Choose destination method:",
        ["Select from project folders", "Enter manual path"],
        help="Choose how to specify where pages should be extracted",
        key="destination_mode_radio"
    )
    
    destination_info = None
    
    if destination_mode == "Select from project folders":
        destination_info = render_project_folder_selection()
    else:  # Enter manual path
        destination_info = render_manual_path_input()
    
    # Only show page range input if we have a valid destination
    if destination_info and destination_info[0]:
        render_page_range_input(destination_info)
    else:
        st.info("Please select a destination folder first")

def render_manual_path_input() -> Tuple[str, str]:
    """Render simple manual path input"""
    
    st.markdown("**Enter destination path:**")
    
    manual_path = st.text_input(
        "Folder path:",
        placeholder="e.g., /Users/username/Documents/MyFolder",
        key="manual_path_input",
        help="Enter the complete path to destination folder"
    )
    
    if manual_path.strip():
        path = Path(manual_path.strip())
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            # Show path validation status
            if path.exists() and path.is_dir():
                st.success(f"✅ Valid folder: {path.name}")
            elif not path.exists():
                st.info(f"📁 Will be created: {path.name}")
            else:
                st.error("❌ Invalid path")
        
        with col2:
            if st.button("Use Path", key="use_manual_path", type="primary", use_container_width=True):
                return (str(path.absolute()), path.name)
    
    return ("", "")

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
    
    # Get all folders in the project including metadata
    available_folders = get_project_folders_with_metadata(project_path)
    
    if not available_folders:
        st.info("No folders found in the project.")
        return ("", "")
    
    # Create folder browser interface with better styling
    st.markdown("**Select destination from project folders:**")
    
    folder_options = []
    folder_info_list = []
    
    # Add project root as an option
    folder_options.append(f"📂 {project_path.name} (Project Root)")
    folder_info_list.append((str(project_path.absolute()), {"naming_base": project_path.name}))
    
    # Add all subfolders with proper hierarchy display
    for folder_info in available_folders:
        display_name, folder_path, folder_type, metadata = folder_info
        folder_options.append(display_name)
        folder_info_list.append((folder_path, metadata))
    
    # Use selectbox with better label
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
        
        # Show selected folder info
        st.success(f"Selected: {folder_name}")
        st.caption(f"Path: `{selected_folder_path}`")
        
        # Check if selected folder is a Part folder and show additional options
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

# def render_system_folder_browser() -> Tuple[str, str]:
#     """Render system-wide folder browser for page extraction"""
    
#     st.markdown("**Browse or enter destination:**")
    
#     # Create tabs for better organization
#     tab1, tab2, tab3 = st.tabs(["🔍 Browse", "⚡ Quick Access", "⌨️ Manual Path"])
    
#     with tab1:
#         # Browse button
#         if st.button("📂 Open Folder Browser", key="open_browser_btn", type="primary", use_container_width=True):
#             st.session_state['show_folder_browser'] = True
#             st.session_state['folder_browser_active'] = True
#             st.session_state['folder_browser_context'] = 'page_assignment'
#             st.rerun()
        
#         st.caption("Opens a visual folder browser to navigate and select destination")
    
#     with tab2:
#         # Quick selection options
#         from src.ui.folder_selector import get_quick_access_folders
#         quick_folders = get_quick_access_folders()
        
#         if quick_folders:
#             for name, path in quick_folders.items():
#                 if st.button(f"📁 {name}", key=f"select_{name.replace(' ', '_')}", use_container_width=True):
#                     return (path, Path(path).name)
#                 st.caption(f"`{path}`")
#         else:
#             st.info("No quick access folders available")
    
#     with tab3:
#         # Manual input
#         manual_path = st.text_input(
#             "Enter folder path:",
#             placeholder="e.g., /Users/username/Documents/MyFolder",
#             key="manual_path_input",
#             help="Enter the complete path to destination folder"
#         )
        
#         if manual_path.strip():
#             path = Path(manual_path.strip())
            
#             # Show path validation status
#             if path.exists() and path.is_dir():
#                 st.success(f"✅ Valid folder: {path.name}")
#             elif not path.exists():
#                 st.info(f"📁 Will be created: {path.name}")
#             else:
#                 st.error("❌ Invalid path")
            
#             if st.button("Use This Path", key="use_manual_path", type="primary", use_container_width=True):
#                 return (str(path.absolute()), path.name)
    
#     return ("", "")


def get_project_path(base_name: str) -> Path:
    """Get the project path using project destination"""
    # Use project destination instead of current directory
    project_destination = SessionManager.get_project_destination()
    if project_destination and os.path.exists(project_destination):
        base_path = Path(project_destination)
    else:
        base_path = Path.cwd()
    
    project_path = base_path / base_name
    
    if not project_path.exists():
        # Create if doesn't exist
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
    
    st.markdown("### Page Range Assignment")
    st.markdown(f"**Selected Destination:** `{Path(destination_path).name}`")
    st.caption(f"Full path: {destination_path}")
    
    # Verify the destination exists and show status
    if os.path.exists(destination_path):
        st.success("Destination folder is accessible")
    else:
        st.info("Destination folder will be created during extraction")
    
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
        if st.button("Preview Assignment", type="secondary", disabled=preview_disabled, key=preview_key):
            if page_ranges_text.strip():
                page_ranges = [r.strip() for r in page_ranges_text.split(',') if r.strip()]
                render_assignment_preview(Path(destination_path).name, page_ranges, total_pages, naming_base)
    
    with col2:
        extract_disabled = not page_ranges_text.strip()
        extract_key = f"extract_btn_{hash(destination_path + str(extract_disabled)) % 10000}"
        if st.button("Extract Pages", type="primary", disabled=extract_disabled, key=extract_key):
            if page_ranges_text.strip():
                page_ranges = [r.strip() for r in page_ranges_text.split(',') if r.strip()]
                # Debug: Confirm destination before extraction
                st.info(f"Starting extraction to: {destination_path}")
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
    """Execute the page extraction process"""
    
    destination_path, naming_base = destination_info
    folder_path = Path(destination_path)
    
    try:
        # Check if destination folder already has PDF files
        if folder_path.exists():
            existing_pdfs = list(folder_path.glob("*.pdf"))
            if existing_pdfs:
                st.warning(f"Destination folder already contains {len(existing_pdfs)} PDF files. New files will be added alongside existing ones.")
        
        # Ensure the folder exists
        folder_path.mkdir(parents=True, exist_ok=True)
        
        # Progress bar
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Execute extraction
        status_text.text(f"Extracting pages to {folder_path.name}...")
        progress_bar.progress(20)
        
        # Pass the exact path without any modification
        success, created_files, error_msg = PDFExtractor.extract_pages_to_folder(
            page_ranges, destination_path, naming_base, total_pages
        )
        
        progress_bar.progress(100)
        
        if success and created_files:
            # Update extraction history
            extraction_history = SessionManager.get('extraction_history', [])
            extraction_record = {
                'destination': folder_path.name,
                'destination_path': destination_path,
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
                'destination': destination_path
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
            st.warning("No pages were extracted. Please check your page ranges.")
        else:
            progress_bar.empty()
            status_text.empty()
            st.error(f"Extraction failed: {error_msg}")
    
    except Exception as e:
        st.error(f"Extraction error: {str(e)}")


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
        # Collect all project data including destinations
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
            'chapter_suffixes': SessionManager.get('chapter_suffixes', {}),
            'extraction_history': SessionManager.get('extraction_history', []),
            'custom_parts': SessionManager.get('custom_parts', {}),
            'font_case_selected': SessionManager.get('font_case_selected', False),
            'selected_font_case': SessionManager.get('selected_font_case', 'First Capital (Sentence case)'),
            'default_destination_folder': SessionManager.get('default_destination_folder', ''),
            'destination_folder_selected': SessionManager.get('destination_folder_selected', False),
            'project_destination_folder': SessionManager.get('project_destination_folder', ''),  # NEW
            'project_destination_selected': SessionManager.get('project_destination_selected', False),  # NEW
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
    font_case = SessionManager.get_font_case()
    
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
        
        SessionManager.update_config({
            'code': formatted_code, 
            'book_name': formatted_book_name,
            'original_code': code,
            'original_book_name': book_name
        })
        
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
