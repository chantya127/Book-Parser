# src/ui/part_management.py - Part management UI components
import streamlit as st
from typing import Dict, List
from datetime import datetime
from pathlib import Path
import os
from ..services.service_factory import service_factory
from ..core.text_formatter import TextFormatter
from ..core.folder_manager import FolderManager

class PartManagementUI:
    """UI components for part management"""

    def __init__(self):
        self.folder_service = service_factory.get_folder_service()

    def add_individual_custom_part(self, config: Dict, part_name: str) -> bool:
        """Add an individual custom part folder with proper font formatting"""
        try:
            # Get font case and format the part name
            font_case = self._get_font_case()
            formatted_part_name = TextFormatter.format_part_name(part_name, font_case)

            safe_code = FolderManager.sanitize_name(config['code'])
            book_name = config['book_name']
            base_name = f"{safe_code}_{book_name}"

            # Use project destination instead of current directory
            project_destination = self._get_project_destination()
            if project_destination and os.path.exists(project_destination):
                base_path = Path(project_destination)
            else:
                base_path = Path.cwd()

            project_path = base_path / base_name

            if not project_path.exists():
                project_path.mkdir(parents=True, exist_ok=True)
                st.info(f"Created project directory: {project_path.absolute()}")

            # Create part folder with formatted name
            part_folder = project_path / f"{base_name}_{formatted_part_name}"

            if part_folder.exists():
                st.error(f"Part '{formatted_part_name}' already exists!")
                return False

            part_folder.mkdir(exist_ok=True)

            # Add to custom parts
            success = self._add_part_to_session(part_name, formatted_part_name)
            if success:
                # Update created folders list
                self._update_created_folders(str(part_folder.absolute()))

                # Set operation completion flags
                st.session_state['part_operation_completed'] = True
                st.session_state['part_operation_info'] = {
                    'operation': 'add',
                    'part_name': formatted_part_name,
                    'location': str(part_folder.absolute())
                }

            return success

        except Exception as e:
            st.error(f"Error creating part: {str(e)}")
            return False

    def render_part_management_section(self, config: Dict):
        """Render part management section with optimized operations and font formatting"""

        col_opt1, col_opt2, col_opt3, col_opt4 = st.columns(4)

        # Show current font formatting
        font_case = self._get_font_case()
        st.caption(f"Font formatting: {font_case}")

        with col_opt2:
            part_name_input = st.text_input(
                "Part Name to Add",
                value="",
                placeholder="e.g., Mathematics, Science",
                key="individual_part_name_input",
                help=f"Enter the custom name for the new part (will be formatted as: {font_case})"
            )

        with col_opt1:
            if st.button("➕ Add Individual Part", type="secondary", key="add_part_btn"):
                if part_name_input.strip():
                    # Use the improved function with font formatting
                    success = self.add_individual_custom_part(config, part_name_input.strip())
                    if success:
                        st.rerun()
                    else:
                        formatted_name = TextFormatter.format_part_name(part_name_input.strip(), font_case)
                        st.error(f"Part '{formatted_name}' already exists!")
                else:
                    st.error("Please enter a part name first")

        # Delete part functionality
        current_parts = self._get_existing_custom_parts(config)

        with col_opt3:
            if current_parts:
                part_to_delete = st.selectbox(
                    "Select Part to Delete",
                    [part['name'] for part in current_parts],
                    key="part_to_delete_select",
                    help="Choose which part to delete (this will delete all contents)"
                )

        with col_opt4:
            if current_parts:
                if st.button("🗑️ Delete Selected Part", type="secondary", key="delete_part_btn"):
                    part_to_delete = st.session_state.get("part_to_delete_select")
                    if part_to_delete:
                        self._delete_individual_custom_part(config, part_to_delete)
                        st.rerun()

    def _get_font_case(self) -> str:
        """Get current font case from session"""
        from ..core.session_manager import SessionManager
        return SessionManager.get_font_case()

    def _get_project_destination(self) -> str:
        """Get project destination from session"""
        from ..core.session_manager import SessionManager
        return SessionManager.get_project_destination()

    def _add_part_to_session(self, original_name: str, formatted_name: str) -> bool:
        """Add part to session state"""
        try:
            from ..core.session_manager import SessionManager

            custom_parts = SessionManager.get('custom_parts', {})
            base_id = formatted_name.lower().replace(' ', '_').replace('-', '_')
            part_id = f"part_{len(custom_parts) + 1}_{base_id}"

            # Ensure unique ID
            counter = 1
            original_id = part_id
            while part_id in custom_parts:
                part_id = f"{original_id}_{counter}"
                counter += 1

            custom_parts[part_id] = {
                'name': formatted_name,
                'display_name': formatted_name,
                'original_name': original_name,
                'created_timestamp': datetime.now().isoformat()
            }

            SessionManager.set('custom_parts', custom_parts)
            return True

        except Exception as e:
            st.error(f"Error adding part to session: {str(e)}")
            return False

    def _update_created_folders(self, folder_path: str):
        """Update created folders list"""
        from ..core.session_manager import SessionManager

        current_folders = SessionManager.get('created_folders', [])
        if folder_path not in current_folders:
            current_folders.append(folder_path)
            SessionManager.set('created_folders', current_folders)

    def _get_existing_custom_parts(self, config: Dict) -> List[Dict]:
        """Get list of actually existing custom parts by checking filesystem first, then session state"""
        existing_parts = []

        safe_code = FolderManager.sanitize_name(config.get('code', ''))
        book_name = config.get('book_name', '')
        base_name = f"{safe_code}_{book_name}"

        # Get custom parts from session state
        from ..core.session_manager import SessionManager
        custom_parts = SessionManager.get('custom_parts', {})

        # Check filesystem directly to get the truth - use project destination
        try:
            project_destination = self._get_project_destination()
            if project_destination and os.path.exists(project_destination):
                base_path = Path(project_destination)
            else:
                base_path = Path.cwd()

            project_path = base_path / base_name

            if project_path.exists() and project_path.is_dir():
                # Check which custom parts actually exist on filesystem
                for part_id, part_info in custom_parts.items():
                    part_name = part_info['name']
                    part_folder = project_path / f"{base_name}_{part_name}"

                    if part_folder.exists():
                        existing_parts.append({
                            'id': part_id,
                            'name': part_name,
                            'path': str(part_folder.absolute()),
                            'display_name': part_info.get('display_name', part_name)
                        })
        except Exception:
            pass

        return existing_parts

    def _delete_individual_custom_part(self, config: Dict, part_name: str):
        """Delete an individual custom part folder and all its contents"""
        try:
            safe_code = FolderManager.sanitize_name(config['code'])
            book_name = config['book_name']
            base_name = f"{safe_code}_{book_name}"

            # Use project destination instead of current directory
            project_destination = self._get_project_destination()
            if project_destination and os.path.exists(project_destination):
                base_path = Path(project_destination)
            else:
                base_path = Path.cwd()

            project_path = base_path / base_name

            if not project_path.exists():
                st.error(f"Project folder not found. Cannot delete part '{part_name}'.")
                return

            # Find the part folder
            part_folder = project_path / f"{base_name}_{part_name}"

            if not part_folder.exists():
                st.error(f"Part '{part_name}' folder not found.")
                return

            # Delete the folder and all contents
            import shutil
            shutil.rmtree(part_folder)

            # Remove from session state
            from ..core.session_manager import SessionManager
            custom_parts = SessionManager.get('custom_parts', {})
            part_to_remove = None

            for part_id, part_info in custom_parts.items():
                if part_info['name'] == part_name:
                    part_to_remove = part_id
                    break

            if part_to_remove:
                del custom_parts[part_to_remove]
                SessionManager.set('custom_parts', custom_parts)

            # Update created folders list and remove related metadata
            current_folders = SessionManager.get('created_folders', [])
            part_path_str = str(part_folder.absolute())
            if part_path_str in current_folders:
                current_folders.remove(part_path_str)

            # Remove any chapter folders that were in this part
            folders_to_remove = []
            for folder_path in current_folders:
                if f"_{part_name}" in folder_path and base_name in folder_path:
                    folders_to_remove.append(folder_path)

            for folder_path in folders_to_remove:
                current_folders.remove(folder_path)

            SessionManager.set('created_folders', current_folders)

            # Remove chapter metadata for this part
            folder_metadata = SessionManager.get('folder_metadata', {})
            metadata_to_remove = []
            for folder_id, metadata in folder_metadata.items():
                if (metadata.get('type') == 'chapter' and
                    metadata.get('parent_part_name') == part_name):
                    metadata_to_remove.append(folder_id)
                elif (metadata.get('type') == 'custom' and
                      f"_{part_name}" in metadata.get('actual_path', '')):
                    metadata_to_remove.append(folder_id)

            for folder_id in metadata_to_remove:
                del folder_metadata[folder_id]

            SessionManager.set('folder_metadata', folder_metadata)

            # Remove chapters config for this part
            chapters_config = SessionManager.get('chapters_config', {})
            if part_name in chapters_config:
                del chapters_config[part_name]
                SessionManager.set('chapters_config', chapters_config)

            # Set success message for next render
            st.session_state['part_operation_completed'] = True
            st.session_state['part_operation_info'] = {
                'operation': 'delete',
                'part_name': part_name
            }

        except PermissionError:
            st.error(f"❌ Permission denied. Cannot delete part '{part_name}'. Please check folder permissions.")
        except Exception as e:
            st.error(f"❌ Error deleting part '{part_name}': {str(e)}")