# src/services/chapter_service.py
from typing import Dict, List, Optional
from pathlib import Path
import os
import shutil
from .base_service import ChapterService as BaseChapterService
from ..core.session_manager import SessionManager
from ..core.folder_manager import FolderManager, ChapterManager
from ..core.chapter_utils import ChapterUtils, ChapterConfigManager
from ..core.text_formatter import TextFormatter

class ChapterService(BaseChapterService):
    """Concrete implementation of ChapterService"""

    def validate_config(self, config: Dict) -> bool:
        """Validate chapter service configuration"""
        return bool(config.get('code') and config.get('book_name'))

    def create_chapter(self, config: Dict, context_key: str, chapter_data: Dict,
                      is_standalone: bool = False, create_only: bool = False,
                      chapter_index: int = None) -> bool:
        """
        Create a single chapter folder

        Args:
            create_only: If True, don't add to session (folder already in list, just creating physical folder)
            chapter_index: Index of chapter in list (used when create_only=True)
        """
        try:
            if not self.validate_config(config):
                return False

            safe_code = FolderManager.sanitize_name(config['code'])
            book_name = config['book_name']
            base_name = f"{safe_code}_{book_name}"

            project_destination = self.session_manager.get_project_destination()
            if project_destination and os.path.exists(project_destination):
                base_path = Path(project_destination)
            else:
                base_path = Path.cwd()

            project_path = base_path / base_name

            if not project_path.exists():
                project_path.mkdir(parents=True, exist_ok=True)

            with self.session_manager.spinner(f"Creating chapter folder..."):
                if is_standalone:
                    created_folders = ChapterManager.create_standalone_chapter_folders(
                        project_path, base_name, [chapter_data]
                    )
                else:
                    created_folders = ChapterManager.create_chapter_folders_for_custom_part(
                        project_path, base_name, context_key, [chapter_data]
                    )

            if created_folders:
                current_folders = self.session_manager.get('created_folders', [])
                current_folders.extend(created_folders)
                self.session_manager.set('created_folders', current_folders)
                self.session_manager.set('chapters_created', True)

                # Only add to session if not create_only (new chapter being added)
                if not create_only:
                    if is_standalone:
                        standalone_chapters = self.session_manager.get('standalone_chapters', [])
                        standalone_chapters.append(chapter_data)
                        self.session_manager.set('standalone_chapters', standalone_chapters)
                    else:
                        chapters_config = self.session_manager.get('chapters_config', {})
                        if context_key not in chapters_config:
                            chapters_config[context_key] = []
                        chapters_config[context_key].append(chapter_data)
                        self.session_manager.set('chapters_config', chapters_config)

                return True
            return False

        except Exception as e:
            self.session_manager.error(f"Error creating chapter: {str(e)}")
            return False

    def delete_chapter(self, config: Dict, context_key: str, chapter_index: int,
                      is_standalone: bool = False) -> bool:
        """Delete a single chapter folder and remove from session"""
        try:
            if not self.validate_config(config):
                return False

            # Get chapters list
            if is_standalone:
                chapters = self.session_manager.get('standalone_chapters', [])
            else:
                chapters_config = self.session_manager.get('chapters_config', {})
                chapters = chapters_config.get(context_key, [])

            if chapter_index >= len(chapters):
                self.session_manager.error("Invalid chapter index")
                return False

            chapter = chapters[chapter_index]

            # Build chapter folder path
            safe_code = FolderManager.sanitize_name(config['code'])
            book_name = config['book_name']
            base_name = f"{safe_code}_{book_name}"

            # Get project path
            project_destination = self.session_manager.get_project_destination()
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
                with self.session_manager.spinner(f"Deleting chapter folder..."):
                    shutil.rmtree(chapter_path)
            else:
                self.session_manager.warning(f"Chapter folder not found: {chapter_path.name}")

            # Remove from chapters list
            chapters.pop(chapter_index)

            # Update session state
            if is_standalone:
                self.session_manager.set('standalone_chapters', chapters)
            else:
                chapters_config = self.session_manager.get('chapters_config', {})
                chapters_config[context_key] = chapters
                self.session_manager.set('chapters_config', chapters_config)

            # Update created folders list
            current_folders = self.session_manager.get('created_folders', [])
            chapter_path_str = str(chapter_path.absolute())
            if chapter_path_str in current_folders:
                current_folders.remove(chapter_path_str)
            self.session_manager.set('created_folders', current_folders)

            # Remove from metadata
            folder_metadata = self.session_manager.get('folder_metadata', {})
            metadata_to_remove = []
            for folder_id, metadata in folder_metadata.items():
                if metadata.get('actual_path') == chapter_path_str:
                    metadata_to_remove.append(folder_id)

            for folder_id in metadata_to_remove:
                del folder_metadata[folder_id]

            self.session_manager.set('folder_metadata', folder_metadata)

            return True

        except PermissionError:
            self.session_manager.error(f"Permission denied. Cannot delete chapter folder.")
            return False
        except Exception as e:
            self.session_manager.error(f"Error deleting chapter: {str(e)}")
            return False

    def update_chapter(self, config: Dict, context_key: str, chapter_index: int,
                      old_folder_name: str, new_folder_name: str, is_standalone: bool,
                      new_number: str, new_name: str) -> bool:
        """Update chapter folder in backend when any field changes"""
        try:
            if not self.validate_config(config):
                return False

            safe_code = FolderManager.sanitize_name(config['code'])
            book_name = config['book_name']
            base_name = f"{safe_code}_{book_name}"

            # Get project path
            project_destination = self.session_manager.get_project_destination()
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
                    current_folders = self.session_manager.get('created_folders', [])
                    old_path_str = str(old_path.absolute())
                    new_path_str = str(new_path.absolute())

                    if old_path_str in current_folders:
                        current_folders.remove(old_path_str)
                        current_folders.append(new_path_str)
                        self.session_manager.set('created_folders', current_folders)

                    # Update metadata
                    folder_metadata = self.session_manager.get('folder_metadata', {})
                    for folder_id, metadata in folder_metadata.items():
                        if metadata.get('actual_path') == old_path_str:
                            metadata['actual_path'] = new_path_str
                            metadata['folder_name'] = new_folder_name
                            metadata['naming_base'] = new_folder_name
                            metadata['chapter_number'] = new_number
                            metadata['chapter_name'] = new_name
                            break
                    self.session_manager.set('folder_metadata', folder_metadata)

                    # Rename all PDF files inside the folder
                    for pdf_file in new_path.glob("*.pdf"):
                        old_file_name = pdf_file.name
                        if old_folder_name in old_file_name:
                            new_file_name = old_file_name.replace(old_folder_name, new_folder_name)
                            pdf_file.rename(new_path / new_file_name)
                else:
                    # Same folder name but update metadata anyway
                    folder_metadata = self.session_manager.get('folder_metadata', {})
                    path_str = str(old_path.absolute())
                    for folder_id, metadata in folder_metadata.items():
                        if metadata.get('actual_path') == path_str:
                            metadata['chapter_number'] = new_number
                            metadata['chapter_name'] = new_name
                            break
                    self.session_manager.set('folder_metadata', folder_metadata)

                # Update chapter in session state
                if is_standalone:
                    chapters = self.session_manager.get('standalone_chapters', [])
                    if chapter_index < len(chapters):
                        chapters[chapter_index]['number'] = new_number
                        chapters[chapter_index]['name'] = new_name
                        self.session_manager.set('standalone_chapters', chapters)
                else:
                    chapters_config = self.session_manager.get('chapters_config', {})
                    if context_key in chapters_config and chapter_index < len(chapters_config[context_key]):
                        chapters_config[context_key][chapter_index]['number'] = new_number
                        chapters_config[context_key][chapter_index]['name'] = new_name
                        self.session_manager.set('chapters_config', chapters_config)

                return True
            else:
                self.session_manager.error("Chapter folder not found")
                return False

        except PermissionError:
            self.session_manager.error("Permission denied. Cannot update chapter folder.")
            return False
        except Exception as e:
            self.session_manager.error(f"Error updating chapter: {str(e)}")
            return False

    def get_chapters_for_context(self, context_key: str) -> List[Dict]:
        """Get chapters for a specific context"""
        return ChapterConfigManager.get_chapters_for_context(context_key)

    def get_created_chapter_indices(self, config: Dict, context_key: str,
                                   chapters: List[Dict], is_standalone: bool) -> set:
        """Check which chapter folders actually exist on filesystem"""
        created_indices = set()

        if not self.validate_config(config):
            return created_indices

        safe_code = FolderManager.sanitize_name(config['code'])
        book_name = config['book_name']
        base_name = f"{safe_code}_{book_name}"

        project_destination = self.session_manager.get_project_destination()
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