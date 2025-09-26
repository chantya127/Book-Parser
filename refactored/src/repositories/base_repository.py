# src/repositories/base_repository.py
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, TypeVar, Generic
from pathlib import Path

T = TypeVar('T')

class BaseRepository(ABC, Generic[T]):
    """Base repository class with common CRUD operations"""

    def __init__(self, session_manager):
        self.session_manager = session_manager

    @abstractmethod
    def create(self, entity: T) -> bool:
        """Create a new entity"""
        pass

    @abstractmethod
    def read(self, id: str) -> Optional[T]:
        """Read entity by ID"""
        pass

    @abstractmethod
    def update(self, id: str, entity: T) -> bool:
        """Update entity by ID"""
        pass

    @abstractmethod
    def delete(self, id: str) -> bool:
        """Delete entity by ID"""
        pass

    @abstractmethod
    def list(self) -> List[T]:
        """List all entities"""
        pass

    @abstractmethod
    def exists(self, id: str) -> bool:
        """Check if entity exists"""
        pass

class ProjectRepository(BaseRepository[Dict]):
    """Repository for project data"""

    def create(self, entity: Dict) -> bool:
        """Create a new project"""
        try:
            project_name = entity.get('name', '')
            if not project_name:
                return False

            # Save project data
            self.session_manager.set('project_config', entity)
            return True
        except Exception:
            return False

    def read(self, id: str) -> Optional[Dict]:
        """Read project by ID"""
        try:
            return self.session_manager.get('project_config', {})
        except Exception:
            return None

    def update(self, id: str, entity: Dict) -> bool:
        """Update project"""
        try:
            self.session_manager.set('project_config', entity)
            return True
        except Exception:
            return False

    def delete(self, id: str) -> bool:
        """Delete project"""
        try:
            self.session_manager.set('project_config', {})
            return True
        except Exception:
            return False

    def list(self) -> List[Dict]:
        """List all projects"""
        try:
            config = self.session_manager.get('project_config', {})
            return [config] if config else []
        except Exception:
            return []

    def exists(self, id: str) -> bool:
        """Check if project exists"""
        try:
            config = self.session_manager.get('project_config', {})
            return bool(config.get('code') and config.get('book_name'))
        except Exception:
            return False

class ChapterRepository(BaseRepository[Dict]):
    """Repository for chapter data"""

    def create(self, entity: Dict) -> bool:
        """Create a new chapter"""
        try:
            context_key = entity.get('context_key', '')
            if not context_key:
                return False

            chapters_config = self.session_manager.get('chapters_config', {})
            if context_key not in chapters_config:
                chapters_config[context_key] = []

            chapters_config[context_key].append(entity)
            self.session_manager.set('chapters_config', chapters_config)
            return True
        except Exception:
            return False

    def read(self, id: str) -> Optional[Dict]:
        """Read chapter by ID"""
        try:
            chapters_config = self.session_manager.get('chapters_config', {})
            for context_key, chapters in chapters_config.items():
                for chapter in chapters:
                    if chapter.get('id') == id:
                        return chapter
            return None
        except Exception:
            return None

    def update(self, id: str, entity: Dict) -> bool:
        """Update chapter"""
        try:
            chapters_config = self.session_manager.get('chapters_config', {})
            for context_key, chapters in chapters_config.items():
                for i, chapter in enumerate(chapters):
                    if chapter.get('id') == id:
                        chapters[i] = entity
                        self.session_manager.set('chapters_config', chapters_config)
                        return True
            return False
        except Exception:
            return False

    def delete(self, id: str) -> bool:
        """Delete chapter"""
        try:
            chapters_config = self.session_manager.get('chapters_config', {})
            for context_key, chapters in chapters_config.items():
                for i, chapter in enumerate(chapters):
                    if chapter.get('id') == id:
                        chapters.pop(i)
                        self.session_manager.set('chapters_config', chapters_config)
                        return True
            return False
        except Exception:
            return False

    def list(self) -> List[Dict]:
        """List all chapters"""
        try:
            chapters_config = self.session_manager.get('chapters_config', {})
            all_chapters = []
            for chapters in chapters_config.values():
                all_chapters.extend(chapters)
            return all_chapters
        except Exception:
            return []

    def exists(self, id: str) -> bool:
        """Check if chapter exists"""
        return self.read(id) is not None

class FolderRepository(BaseRepository[Dict]):
    """Repository for folder data"""

    def create(self, entity: Dict) -> bool:
        """Create a new folder"""
        try:
            folder_path = entity.get('path', '')
            if not folder_path:
                return False

            created_folders = self.session_manager.get('created_folders', [])
            if folder_path not in created_folders:
                created_folders.append(folder_path)
                self.session_manager.set('created_folders', created_folders)

            # Add to metadata
            folder_metadata = self.session_manager.get('folder_metadata', {})
            folder_id = entity.get('id', f"folder_{len(folder_metadata)}")
            folder_metadata[folder_id] = entity
            self.session_manager.set('folder_metadata', folder_metadata)

            return True
        except Exception:
            return False

    def read(self, id: str) -> Optional[Dict]:
        """Read folder by ID"""
        try:
            folder_metadata = self.session_manager.get('folder_metadata', {})
            return folder_metadata.get(id)
        except Exception:
            return None

    def update(self, id: str, entity: Dict) -> bool:
        """Update folder"""
        try:
            folder_metadata = self.session_manager.get('folder_metadata', {})
            if id in folder_metadata:
                folder_metadata[id] = entity
                self.session_manager.set('folder_metadata', folder_metadata)
                return True
            return False
        except Exception:
            return False

    def delete(self, id: str) -> bool:
        """Delete folder"""
        try:
            folder_metadata = self.session_manager.get('folder_metadata', {})
            if id in folder_metadata:
                del folder_metadata[id]
                self.session_manager.set('folder_metadata', folder_metadata)

                # Remove from created folders list
                created_folders = self.session_manager.get('created_folders', [])
                folder_path = folder_metadata.get('path')
                if folder_path and folder_path in created_folders:
                    created_folders.remove(folder_path)
                    self.session_manager.set('created_folders', created_folders)

                return True
            return False
        except Exception:
            return False

    def list(self) -> List[Dict]:
        """List all folders"""
        try:
            folder_metadata = self.session_manager.get('folder_metadata', {})
            return list(folder_metadata.values())
        except Exception:
            return []

    def exists(self, id: str) -> bool:
        """Check if folder exists"""
        return self.read(id) is not None

class PDFRepository(BaseRepository[Dict]):
    """Repository for PDF data"""

    def create(self, entity: Dict) -> bool:
        """Create a new PDF record"""
        try:
            pdf_id = entity.get('id', f"pdf_{len(self.list())}")
            entity['id'] = pdf_id

            # Store PDF info
            self.session_manager.set('pdf_file', entity.get('file'))
            self.session_manager.set('total_pages', entity.get('pages', 0))
            self.session_manager.set('pdf_uploaded', True)

            return True
        except Exception:
            return False

    def read(self, id: str) -> Optional[Dict]:
        """Read PDF by ID"""
        try:
            pdf_file = self.session_manager.get('pdf_file')
            if pdf_file:
                return {
                    'id': id,
                    'file': pdf_file,
                    'pages': self.session_manager.get('total_pages', 0),
                    'uploaded': self.session_manager.get('pdf_uploaded', False)
                }
            return None
        except Exception:
            return None

    def update(self, id: str, entity: Dict) -> bool:
        """Update PDF"""
        try:
            if 'file' in entity:
                self.session_manager.set('pdf_file', entity['file'])
            if 'pages' in entity:
                self.session_manager.set('total_pages', entity['pages'])
            return True
        except Exception:
            return False

    def delete(self, id: str) -> bool:
        """Delete PDF"""
        try:
            self.session_manager.set('pdf_file', None)
            self.session_manager.set('total_pages', 0)
            self.session_manager.set('pdf_uploaded', False)
            return True
        except Exception:
            return False

    def list(self) -> List[Dict]:
        """List all PDFs"""
        try:
            pdf_file = self.session_manager.get('pdf_file')
            if pdf_file:
                return [{
                    'file': pdf_file,
                    'pages': self.session_manager.get('total_pages', 0),
                    'uploaded': self.session_manager.get('pdf_uploaded', False)
                }]
            return []
        except Exception:
            return []

    def exists(self, id: str) -> bool:
        """Check if PDF exists"""
        return self.session_manager.get('pdf_uploaded', False)