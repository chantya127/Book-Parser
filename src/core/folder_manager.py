
# src/core/folder_manager.py
from pathlib import Path
from typing import List, Tuple, Optional, Dict
import streamlit as st
import random
import os

class FolderManager:
    """Manages folder structure creation and organization"""
    
    DEFAULT_FOLDERS = ['Prologue', 'Index', 'Epilogue', 'Prologue']
    
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
