# src/services/folder_service.py
from typing import Dict, List, Tuple
from pathlib import Path
import os
import shutil
import random
from datetime import datetime
from .base_service import FolderService as BaseFolderService
from ..core.session_manager import SessionManager
from ..core.folder_manager import FolderManager
from ..core.text_formatter import TextFormatter

class FolderService(BaseFolderService):
    """Concrete implementation of FolderService"""

    def validate_config(self, config: Dict) -> bool:
        """Validate folder service configuration"""
        return bool(config.get('code') and config.get('book_name'))

    def create_project_structure(self, config: Dict, selected_folders: List[str]) -> Tuple[Path, List[str]]:
        """Create project folder structure"""
        if not self.validate_config(config):
            return None, []

        code = config['code']
        book_name = config['book_name']
        custom_parts = self.session_manager.get('custom_parts', {})

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

            self.session_manager.set('folder_structure_created', True)
            self.session_manager.set('created_folders', created_folders)

        return project_path, created_folders

    def create_custom_folder(self, parent_path: str, folder_name: str) -> bool:
        """Create a custom folder with parent folder prefix + custom name and font formatting"""
        try:
            # Lazy import for font formatting
            font_case = self.session_manager.get_font_case()

            parent_folder = Path(parent_path)
            parent_folder_name = parent_folder.name

            # Apply font formatting to the custom folder name
            formatted_folder_name = TextFormatter.format_custom_folder_name(folder_name, font_case)
            final_folder_name = f"{parent_folder_name}_{formatted_folder_name}"

            custom_folder_path = parent_folder / final_folder_name

            # Check if folder already exists
            if custom_folder_path.exists():
                self.session_manager.error(f"❌ Folder '{final_folder_name}' already exists in '{parent_folder_name}'. Please choose a different name.")
                return False

            with self.session_manager.spinner(f"Creating custom folder '{final_folder_name}'..."):
                # Ensure parent folder exists
                parent_folder.mkdir(parents=True, exist_ok=True)

                # Create the custom folder with parent prefix + formatted custom name
                custom_folder_path.mkdir(exist_ok=True)

                # Add to metadata
                self._add_folder_to_metadata(
                    str(custom_folder_path.absolute()),
                    final_folder_name,
                    parent_path,
                    folder_name  # Original name for reference
                )

                return True

        except PermissionError:
            self.session_manager.error(f"❌ Permission denied. Cannot create folder in '{parent_folder.name}'. Please check folder permissions.")
            return False
        except FileExistsError:
            self.session_manager.error(f"❌ Folder '{final_folder_name}' already exists. Please choose a different name.")
            return False
        except OSError as e:
            if "Invalid argument" in str(e) or "cannot create" in str(e).lower():
                self.session_manager.error(f"❌ Invalid folder name '{folder_name}'. Please avoid special characters and try a simpler name.")
            else:
                self.session_manager.error(f"❌ System error creating folder: {str(e)}")
            return False
        except Exception as e:
            self.session_manager.error(f"❌ Unexpected error creating custom folder: {str(e)}")
            return False

    def delete_folder(self, folder_path: str) -> bool:
        """Delete a folder"""
        try:
            folder_path_obj = Path(folder_path)

            if not folder_path_obj.exists():
                self.session_manager.warning(f"⚠️ Folder not found on filesystem.")
                return False

            folder_name = folder_path_obj.name

            import shutil
            shutil.rmtree(folder_path_obj)
            self.session_manager.success(f"✅ Deleted folder: '{folder_name}'")

            # Remove from metadata
            folder_metadata = self.session_manager.get('folder_metadata', {})
            folder_path_str = str(folder_path_obj.absolute())

            # Find and remove metadata entry
            folder_id_to_remove = None
            for folder_id, metadata in folder_metadata.items():
                if metadata.get('actual_path') == folder_path_str:
                    folder_id_to_remove = folder_id
                    break

            if folder_id_to_remove:
                del folder_metadata[folder_id_to_remove]
                self.session_manager.set('folder_metadata', folder_metadata)

            # Remove from created folders list
            current_folders = self.session_manager.get('created_folders', [])
            if folder_path_str in current_folders:
                current_folders.remove(folder_path_str)
                self.session_manager.set('created_folders', current_folders)

            return True

        except PermissionError:
            self.session_manager.error(f"❌ Permission denied. Cannot delete folder '{folder_name}'. Please check folder permissions.")
            return False
        except Exception as e:
            self.session_manager.error(f"❌ Error deleting folder: {str(e)}")
            return False

    def get_folder_info(self, folder_path: str) -> Dict:
        """Get folder information"""
        try:
            path = Path(folder_path)

            if not path.exists():
                return {'exists': False, 'error': 'Folder not found'}

            folder_metadata = self.session_manager.get('folder_metadata', {})
            metadata = None

            # Find metadata for this folder
            for folder_id, folder_data in folder_metadata.items():
                if folder_data.get('actual_path') == str(path.absolute()):
                    metadata = folder_data
                    break

            return {
                'exists': True,
                'name': path.name,
                'path': str(path.absolute()),
                'parent': str(path.parent),
                'is_directory': path.is_dir(),
                'metadata': metadata
            }

        except Exception as e:
            return {'exists': False, 'error': str(e)}

    def get_project_path(self, base_name: str) -> Path:
        """Get the project path using project destination"""
        # Use project destination instead of current directory
        project_destination = self.session_manager.get_project_destination()
        if project_destination and os.path.exists(project_destination):
            base_path = Path(project_destination)
        else:
            base_path = Path.cwd()

        project_path = base_path / base_name

        if not project_path.exists():
            # Create if doesn't exist
            project_path.mkdir(parents=True, exist_ok=True)

        return project_path

    def get_all_project_folders(self, project_path: Path) -> List[Tuple[str, str, int]]:
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

    def _add_folder_to_metadata(self, folder_path: str, folder_name: str,
                               parent_path: str, original_name: str = None):
        """Add folder to metadata tracking"""
        folder_metadata = self.session_manager.get('folder_metadata', {})
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

        self.session_manager.set('folder_metadata', folder_metadata)

        # Update created folders list
        current_folders = self.session_manager.get('created_folders', [])
        if folder_path not in current_folders:
            current_folders.append(folder_path)
            self.session_manager.set('created_folders', current_folders)