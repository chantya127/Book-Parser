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
    def create_custom_folder(project_path: Path, base_name: str, parent_folder_id: str, custom_folder_name: str) -> Optional[str]:
        """
        Create a custom folder inside any existing folder
        
        Args:
            project_path: Main project path
            base_name: Base project name
            parent_folder_id: ID of the parent folder
            custom_folder_name: Name for the new custom folder
            
        Returns:
            Path of created folder or None if failed
        """
        try:
            from core.session_manager import SessionManager
            
            # Sanitize the custom folder name
            safe_folder_name = FolderManager.sanitize_name(custom_folder_name)
            folder_metadata = SessionManager.get('folder_metadata', {})
            
            # Determine parent folder path
            if parent_folder_id in folder_metadata:
                # Parent is a tracked folder (chapter, etc.)
                parent_path = Path(folder_metadata[parent_folder_id]['actual_path'])
                parent_display = folder_metadata[parent_folder_id]['display_name']
            else:
                # Parent is a direct folder (part, default folder)
                parent_path = project_path / parent_folder_id
                parent_display = parent_folder_id
            
            # Create the custom folder
            custom_folder_path = parent_path / f"{base_name}_{safe_folder_name}"
            custom_folder_path.mkdir(exist_ok=True)
            
            # Generate unique ID for the custom folder
            import random
            custom_folder_id = f"custom_{safe_folder_name}_{random.randint(10000, 99999)}"
            
            # Store metadata
            folder_metadata[custom_folder_id] = {
                'display_name': f"{parent_display} → {safe_folder_name}",
                'actual_path': str(custom_folder_path.absolute()),
                'type': 'custom',
                'parent_id': parent_folder_id,
                'folder_name': safe_folder_name,
                'naming_base': f"{base_name}_{safe_folder_name}"
            }
            
            SessionManager.set('folder_metadata', folder_metadata)
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