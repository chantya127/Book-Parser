# src/ui/chapter_management_refactored.py - Refactored chapter management using modular components
import streamlit as st
from typing import Dict, List
from ..services.service_factory import service_factory
from .standalone_chapters import StandaloneChaptersUI
from .part_management import PartManagementUI
from .chapter_configuration import ChapterConfigurationUI

class ChapterManagementRefactored:
    """Refactored chapter management using modular components and dependency injection"""

    def __init__(self):
        self.standalone_chapters_ui = StandaloneChaptersUI()
        self.part_management_ui = PartManagementUI()
        self.chapter_configuration_ui = ChapterConfigurationUI()

    def render_chapter_management_page(self):
        """Render the chapter management page using modular components"""

        # Check prerequisites
        if not self._check_prerequisites():
            self._render_prerequisites_warning()
            return

        config = self._get_project_config()

        st.subheader("📂 Chapter Management")
        st.markdown("Configure chapters within each custom part of your book, or create standalone chapters.")

        # Check for operation completion messages
        self._handle_operation_completion_messages()

        # Standalone Chapters Section
        st.markdown("### 📖 Standalone Chapters")
        self.standalone_chapters_ui.render_standalone_chapters_section(config)

        st.markdown("---")

        # Part Management Section
        st.markdown("### 🔧 Part Management")
        self.part_management_ui.render_part_management_section(config)

        # Chapter configuration for parts
        updated_parts = self._get_existing_custom_parts(config)

        if not updated_parts:
            st.info("📝 No custom parts configured. You can add individual parts above or configure parts in Project Setup.")
        else:
            st.markdown("---")
            part_names = [part['name'] for part in updated_parts]
            st.info(f"Found {len(updated_parts)} existing parts: {', '.join(part_names)}")

            col1, col2 = st.columns([2, 1])

            with col1:
                self.chapter_configuration_ui.render_chapter_configuration(config, updated_parts)

            with col2:
                self.chapter_configuration_ui.render_chapter_preview(config)

    def _check_prerequisites(self) -> bool:
        """Check if prerequisites are met"""
        from ..core.session_manager import SessionManager
        return SessionManager.get('folder_structure_created', False)

    def _render_prerequisites_warning(self):
        """Render warning when prerequisites are not met"""
        st.warning("⚠️ Please complete the project setup first!")
        st.markdown("""
        **Required steps:**
        1. Upload PDF file
        2. Configure project details
        3. Create folder structure
        """)

    def _get_project_config(self) -> Dict:
        """Get project configuration"""
        from ..core.session_manager import SessionManager
        return SessionManager.get('project_config', {})

    def _handle_operation_completion_messages(self):
        """Handle operation completion messages"""
        if st.session_state.get('part_operation_completed'):
            operation_info = st.session_state.get('part_operation_info', {})
            if operation_info.get('operation') == 'add':
                st.success(f"✅ Successfully created part '{operation_info.get('part_name')}'!")
                st.info(f"📂 Location: {operation_info.get('location', 'Unknown')}")
            elif operation_info.get('operation') == 'delete':
                st.success(f"✅ Successfully deleted part '{operation_info.get('part_name')}' and all its contents!")

            # Clear the flags
            st.session_state['part_operation_completed'] = False
            st.session_state['part_operation_info'] = {}

    def _get_existing_custom_parts(self, config: Dict) -> List[Dict]:
        """Get list of actually existing custom parts"""
        from ..core.folder_manager import FolderManager
        from ..core.session_manager import SessionManager
        from pathlib import Path
        import os

        existing_parts = []

        safe_code = FolderManager.sanitize_name(config.get('code', ''))
        book_name = config.get('book_name', '')
        base_name = f"{safe_code}_{book_name}"

        # Get custom parts from session state
        custom_parts = SessionManager.get('custom_parts', {})

        # Check filesystem directly to get the truth - use project destination
        try:
            project_destination = SessionManager.get_project_destination()
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

# Create a singleton instance
chapter_management = ChapterManagementRefactored()

def render_chapter_management_page():
    """Render the chapter management page - backward compatibility function"""
    chapter_management.render_chapter_management_page()