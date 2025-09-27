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
        "Ninety-Four", "Ninety-Five", "Ninety-Six", "Ninety-Seven", "Ninety-Eight", "Ninety-Nine", "One Hundred",
        "One Hundred One", "One Hundred Two", "One Hundred Three", "One Hundred Four", "One Hundred Five", "One Hundred Six",
        "One Hundred Seven", "One Hundred Eight", "One Hundred Nine", "One Hundred Ten",
        "One Hundred Eleven", "One Hundred Twelve", "One Hundred Thirteen", "One Hundred Fourteen", "One Hundred Fifteen", "One Hundred Sixteen",
        "One Hundred Seventeen", "One Hundred Eighteen", "One Hundred Nineteen", "One Hundred Twenty",
        "One Hundred Twenty One", "One Hundred Twenty Two", "One Hundred Twenty Three", "One Hundred Twenty Four", "One Hundred Twenty Five", "One Hundred Twenty Six",
        "One Hundred Twenty Seven", "One Hundred Twenty Eight", "One Hundred Twenty Nine", "One Hundred Thirty",
        "One Hundred Thirty One", "One Hundred Thirty Two", "One Hundred Thirty Three", "One Hundred Thirty Four", "One Hundred Thirty Five", "One Hundred Thirty Six",
        "One Hundred Thirty Seven", "One Hundred Thirty Eight", "One Hundred Thirty Nine", "One Hundred Forty",
        "One Hundred Forty One", "One Hundred Forty Two", "One Hundred Forty Three", "One Hundred Forty Four", "One Hundred Forty Five", "One Hundred Forty Six",
        "One Hundred Forty Seven", "One Hundred Forty Eight", "One Hundred Forty Nine", "One Hundred Fifty",
        "One Hundred Fifty One", "One Hundred Fifty Two", "One Hundred Fifty Three", "One Hundred Fifty Four", "One Hundred Fifty Five", "One Hundred Fifty Six",
        "One Hundred Fifty Seven", "One Hundred Fifty Eight", "One Hundred Fifty Nine", "One Hundred Sixty",
        "One Hundred Sixty One", "One Hundred Sixty Two", "One Hundred Sixty Three", "One Hundred Sixty Four", "One Hundred Sixty Five", "One Hundred Sixty Six",
        "One Hundred Sixty Seven", "One Hundred Sixty Eight", "One Hundred Sixty Nine", "One Hundred Seventy",
        "One Hundred Seventy One", "One Hundred Seventy Two", "One Hundred Seventy Three", "One Hundred Seventy Four", "One Hundred Seventy Five", "One Hundred Seventy Six",
        "One Hundred Seventy Seven", "One Hundred Seventy Eight", "One Hundred Seventy Nine", "One Hundred Eighty",
        "One Hundred Eighty One", "One Hundred Eighty Two", "One Hundred Eighty Three", "One Hundred Eighty Four", "One Hundred Eighty Five", "One Hundred Eighty Six",
        "One Hundred Eighty Seven", "One Hundred Eighty Eight", "One Hundred Eighty Nine", "One Hundred Ninety",
        "One Hundred Ninety One", "One Hundred Ninety Two", "One Hundred Ninety Three", "One Hundred Ninety Four", "One Hundred Ninety Five", "One Hundred Ninety Six",
        "One Hundred Ninety Seven", "One Hundred Ninety Eight", "One Hundred Ninety Nine", "Two Hundred",
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
        "XCI", "XCII", "XCIII", "XCIV", "XCV", "XCVI", "XCVII", "XCVIII", "XCIX", "C",
        "CI", "CII", "CIII", "CIV", "CV", "CVI", "CVII", "CVIII", "CIX", "CX",
        "CXI", "CXII", "CXIII", "CXIV", "CXV", "CXVI", "CXVII", "CXVIII", "CXIX", "CXX",
        "CXXI", "CXXII", "CXXIII", "CXXIV", "CXXV", "CXXVI", "CXXVII", "CXXVIII", "CXXIX", "CXXX",
        "CXXXI", "CXXXII", "CXXXIII", "CXXXIV", "CXXXV", "CXXXVI", "CXXXVII", "CXXXVIII", "CXXXIX", "CXL",
        "CXLI", "CXLII", "CXLIII", "CXLIV", "CXLV", "CXLVI", "CXLVII", "CXLVIII", "CXLIX", "CL",
        "CLI", "CLII", "CLIII", "CLIV", "CLV", "CLVI", "CLVII", "CLVIII", "CLIX", "CLX",
        "CLXI", "CLXII", "CLXIII", "CLXIV", "CLXV", "CLXVI", "CLXVII", "CLXVIII", "CLXIX", "CLXX",
        "CLXXI", "CLXXII", "CLXXIII", "CLXXIV", "CLXXV", "CLXXVI", "CLXXVII", "CLXXVIII", "CLXXIX", "CLXXX",
        "CLXXXI", "CLXXXII", "CLXXXIII", "CLXXXIV", "CLXXXV", "CLXXXVI", "CLXXXVII", "CLXXXVIII", "CLXXXIX", "CXC",
        "CXCI", "CXCII", "CXCIII", "CXCIV", "CXCV", "CXCVI", "CXCVII", "CXCVIII", "CXCIX", "CC",
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