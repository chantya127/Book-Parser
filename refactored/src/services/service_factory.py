# src/services/service_factory.py
from typing import Dict, Any
from .chapter_service import ChapterService
from .folder_service import FolderService
from .project_service import ProjectService
from .pdf_service import PDFService
from ..core.session_manager import SessionManager

class ServiceFactory:
    """Factory for creating and managing services"""

    _instance = None
    _services = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ServiceFactory, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._services:
            self._initialize_services()

    def _initialize_services(self):
        """Initialize all services"""
        session_manager = SessionManager()

        self._services = {
            'chapter': ChapterService(session_manager),
            'folder': FolderService(session_manager),
            'project': ProjectService(session_manager),
            'pdf': PDFService(session_manager)
        }

    def get_service(self, service_name: str):
        """Get a service by name"""
        if service_name not in self._services:
            raise ValueError(f"Service '{service_name}' not found. Available services: {list(self._services.keys())}")

        return self._services[service_name]

    def get_chapter_service(self) -> ChapterService:
        """Get chapter service"""
        return self._services['chapter']

    def get_folder_service(self) -> FolderService:
        """Get folder service"""
        return self._services['folder']

    def get_project_service(self) -> ProjectService:
        """Get project service"""
        return self._services['project']

    def get_pdf_service(self) -> PDFService:
        """Get PDF service"""
        return self._services['pdf']

    def reset_services(self):
        """Reset all services (useful for testing)"""
        self._services.clear()
        self._initialize_services()

# Global service factory instance
service_factory = ServiceFactory()