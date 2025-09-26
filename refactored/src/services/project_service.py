# src/services/project_service.py
from typing import Dict, List
from pathlib import Path
import json
import os
from datetime import datetime
from .base_service import ProjectService as BaseProjectService
from ..core.session_manager import SessionManager

class ProjectService(BaseProjectService):
    """Concrete implementation of ProjectService"""

    def validate_config(self, config: Dict) -> bool:
        """Validate project service configuration"""
        return bool(config.get('code') and config.get('book_name'))

    def save_project(self, project_name: str, project_data: Dict) -> bool:
        """Save project to file with timestamp"""
        try:
            if not self.validate_config(project_data.get('project_config', {})):
                self.session_manager.error("❌ Cannot save: Project code and book name are required")
                return False

            # Create filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            base_name = f"{project_data['project_config']['code']}_{project_data['project_config']['book_name']}"
            full_project_name = f"{base_name}_{timestamp}"

            projects_dir = self._get_projects_dir()
            project_file = projects_dir / f"{full_project_name}.json"

            # Get current font case
            current_font_case = self.session_manager.get_font_case()

            # Collect all project data including destinations
            complete_project_data = {
                'project_config': project_data.get('project_config', {}),
                'pdf_uploaded': self.session_manager.get('pdf_uploaded', False),
                'pdf_file_name': self.session_manager.get('pdf_file').name if self.session_manager.get('pdf_file') else None,
                'total_pages': self.session_manager.get('total_pages', 0),
                'folder_structure_created': self.session_manager.get('folder_structure_created', False),
                'created_folders': self.session_manager.get('created_folders', []),
                'chapters_config': self.session_manager.get('chapters_config', {}),
                'chapters_created': self.session_manager.get('chapters_created', False),
                'folder_metadata': self.session_manager.get('folder_metadata', {}),
                'numbering_systems': self.session_manager.get('numbering_systems', {}),
                'chapter_suffixes': self.session_manager.get('chapter_suffixes', {}),
                'extraction_history': self.session_manager.get('extraction_history', []),
                'custom_parts': self.session_manager.get('custom_parts', {}),
                'font_case_selected': True,
                'selected_font_case': current_font_case,  # Use current font case
                'project_destination_folder': self.session_manager.get('project_destination_folder', ''),
                'project_destination_selected': self.session_manager.get('project_destination_selected', False),
                'saved_timestamp': timestamp,
                'saved_datetime': datetime.now().isoformat()
            }

            # Save to JSON file
            with open(project_file, 'w') as f:
                json.dump(complete_project_data, f, indent=2)

            # Update current project name
            self.session_manager.set('current_project_name', full_project_name)

            # Format display name for success message
            display_name = self._format_project_display_name(full_project_name)
            self.session_manager.success(f"✅ Project saved as: {display_name}")

            return True

        except Exception as e:
            self.session_manager.error(f"❌ Error saving project: {str(e)}")
            return False

    def load_project(self, project_name: str) -> Dict:
        """Load project from file"""
        projects_dir = self._get_projects_dir()
        project_file = projects_dir / f"{project_name}.json"

        if not project_file.exists():
            self.session_manager.error(f"❌ Project file not found: {project_name}")
            return {}

        try:
            with open(project_file, 'r') as f:
                project_data = json.load(f)

            # Clear current session and load project data
            # Note: In a real implementation, you'd want to be more careful about this
            # For now, we'll just return the data and let the caller handle it

            return project_data

        except Exception as e:
            self.session_manager.error(f"❌ Error loading project: {str(e)}")
            return {}

    def delete_project(self, project_name: str) -> bool:
        """Delete project file"""
        projects_dir = self._get_projects_dir()
        project_file = projects_dir / f"{project_name}.json"

        try:
            if project_file.exists():
                os.remove(project_file)

            # If this was the current project, clear it
            if self.session_manager.get('current_project_name') == project_name:
                self.session_manager.set('current_project_name', None)

            return True

        except Exception as e:
            self.session_manager.error(f"❌ Error deleting project: {str(e)}")
            return False

    def get_project_list(self) -> List[Dict]:
        """Get list of saved projects"""
        projects_dir = self._get_projects_dir()
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
                    'modified': f.stat().st_mtime,
                    'path': str(f.absolute())
                })

            except Exception:
                # Fallback for any parsing issues
                project_list.append({
                    'filename': f.stem,
                    'display_name': f.stem,
                    'modified': f.stat().st_mtime,
                    'path': str(f.absolute())
                })

        # Sort by modification time (newest first)
        project_list.sort(key=lambda x: x['modified'], reverse=True)

        return project_list

    def _get_projects_dir(self) -> Path:
        """Get or create projects directory"""
        projects_dir = Path("saved_projects")
        projects_dir.mkdir(exist_ok=True)
        return projects_dir

    def _format_project_display_name(self, project_name: str) -> str:
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