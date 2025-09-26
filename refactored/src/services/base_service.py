# src/services/base_service.py
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from pathlib import Path

class BaseService(ABC):
    """Base service class with common functionality"""

    def __init__(self, session_manager):
        self.session_manager = session_manager

    @abstractmethod
    def validate_config(self, config: Dict) -> bool:
        """Validate service configuration"""
        pass

class ChapterService(BaseService):
    """Service for chapter-related operations"""

    @abstractmethod
    def create_chapter(self, config: Dict, context_key: str, chapter_data: Dict,
                      is_standalone: bool = False) -> bool:
        """Create a single chapter"""
        pass

    @abstractmethod
    def delete_chapter(self, config: Dict, context_key: str, chapter_index: int,
                      is_standalone: bool = False) -> bool:
        """Delete a single chapter"""
        pass

    @abstractmethod
    def update_chapter(self, config: Dict, context_key: str, chapter_index: int,
                      old_folder_name: str, new_folder_name: str, is_standalone: bool,
                      new_number: str, new_name: str) -> bool:
        """Update chapter folder"""
        pass

    @abstractmethod
    def get_chapters_for_context(self, context_key: str) -> List[Dict]:
        """Get chapters for a specific context"""
        pass

class FolderService(BaseService):
    """Service for folder-related operations"""

    @abstractmethod
    def create_project_structure(self, config: Dict, selected_folders: List[str]) -> tuple:
        """Create project folder structure"""
        pass

    @abstractmethod
    def create_custom_folder(self, parent_path: str, folder_name: str) -> bool:
        """Create a custom folder"""
        pass

    @abstractmethod
    def delete_folder(self, folder_path: str) -> bool:
        """Delete a folder"""
        pass

    @abstractmethod
    def get_folder_info(self, folder_path: str) -> Dict:
        """Get folder information"""
        pass

class ProjectService(BaseService):
    """Service for project-related operations"""

    @abstractmethod
    def save_project(self, project_name: str, project_data: Dict) -> bool:
        """Save project to file"""
        pass

    @abstractmethod
    def load_project(self, project_name: str) -> Dict:
        """Load project from file"""
        pass

    @abstractmethod
    def delete_project(self, project_name: str) -> bool:
        """Delete project file"""
        pass

    @abstractmethod
    def get_project_list(self) -> List[Dict]:
        """Get list of saved projects"""
        pass

class PDFService(BaseService):
    """Service for PDF-related operations"""

    @abstractmethod
    def extract_pages(self, pdf_path: str, page_ranges: List[str],
                     destination_path: str, naming_base: str) -> tuple:
        """Extract pages from PDF"""
        pass

    @abstractmethod
    def validate_pdf(self, pdf_path: str) -> tuple:
        """Validate PDF file"""
        pass

    @abstractmethod
    def get_pdf_info(self, pdf_path: str) -> Dict:
        """Get PDF information"""
        pass