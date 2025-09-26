# src/repositories/repository_factory.py
from typing import Dict, Any
from .base_repository import BaseRepository, ProjectRepository, ChapterRepository, FolderRepository, PDFRepository
from ..core.session_manager import SessionManager

class RepositoryFactory:
    """Factory for creating and managing repositories"""

    _instance = None
    _repositories = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(RepositoryFactory, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._repositories:
            self._initialize_repositories()

    def _initialize_repositories(self):
        """Initialize all repositories"""
        session_manager = SessionManager()

        self._repositories = {
            'project': ProjectRepository(session_manager),
            'chapter': ChapterRepository(session_manager),
            'folder': FolderRepository(session_manager),
            'pdf': PDFRepository(session_manager)
        }

    def get_repository(self, repository_name: str) -> BaseRepository:
        """Get a repository by name"""
        if repository_name not in self._repositories:
            raise ValueError(f"Repository '{repository_name}' not found. Available repositories: {list(self._repositories.keys())}")

        return self._repositories[repository_name]

    def get_project_repository(self) -> ProjectRepository:
        """Get project repository"""
        return self._repositories['project']

    def get_chapter_repository(self) -> ChapterRepository:
        """Get chapter repository"""
        return self._repositories['chapter']

    def get_folder_repository(self) -> FolderRepository:
        """Get folder repository"""
        return self._repositories['folder']

    def get_pdf_repository(self) -> PDFRepository:
        """Get PDF repository"""
        return self._repositories['pdf']

    def reset_repositories(self):
        """Reset all repositories (useful for testing)"""
        self._repositories.clear()
        self._initialize_repositories()

# Global repository factory instance
repository_factory = RepositoryFactory()