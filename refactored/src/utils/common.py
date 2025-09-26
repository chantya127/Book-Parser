# src/utils/common.py - Common utility functions
import streamlit as st
from typing import Dict, List, Any, Optional
from pathlib import Path
import os
from ..core.session_manager import SessionManager

class CommonUtils:
    """Common utility functions used across the application"""

    @staticmethod
    def get_project_config() -> Dict:
        """Get project configuration from session"""
        return SessionManager.get('project_config', {})

    @staticmethod
    def get_project_destination() -> str:
        """Get project destination from session"""
        return SessionManager.get_project_destination()

    @staticmethod
    def get_font_case() -> str:
        """Get current font case from session"""
        return SessionManager.get_font_case()

    @staticmethod
    def get_created_folders() -> List[str]:
        """Get list of created folders from session"""
        return SessionManager.get('created_folders', [])

    @staticmethod
    def get_folder_metadata() -> Dict:
        """Get folder metadata from session"""
        return SessionManager.get('folder_metadata', {})

    @staticmethod
    def get_chapters_config() -> Dict:
        """Get chapters configuration from session"""
        return SessionManager.get('chapters_config', {})

    @staticmethod
    def get_standalone_chapters() -> List[Dict]:
        """Get standalone chapters from session"""
        return SessionManager.get('standalone_chapters', [])

    @staticmethod
    def get_custom_parts() -> Dict:
        """Get custom parts from session"""
        return SessionManager.get('custom_parts', {})

    @staticmethod
    def get_extraction_history() -> List[Dict]:
        """Get extraction history from session"""
        return SessionManager.get('extraction_history', [])

    @staticmethod
    def is_pdf_uploaded() -> bool:
        """Check if PDF is uploaded"""
        return SessionManager.get('pdf_uploaded', False)

    @staticmethod
    def is_folder_structure_created() -> bool:
        """Check if folder structure is created"""
        return SessionManager.get('folder_structure_created', False)

    @staticmethod
    def are_chapters_created() -> bool:
        """Check if chapters are created"""
        return SessionManager.get('chapters_created', False)

    @staticmethod
    def get_total_pages() -> int:
        """Get total pages from session"""
        return SessionManager.get('total_pages', 0)

    @staticmethod
    def get_pdf_file():
        """Get PDF file from session"""
        return SessionManager.get('pdf_file')

    @staticmethod
    def show_success(message: str):
        """Show success message"""
        st.success(f"✅ {message}")

    @staticmethod
    def show_error(message: str):
        """Show error message"""
        st.error(f"❌ {message}")

    @staticmethod
    def show_warning(message: str):
        """Show warning message"""
        st.warning(f"⚠️ {message}")

    @staticmethod
    def show_info(message: str):
        """Show info message"""
        st.info(f"💡 {message}")

    @staticmethod
    def show_spinner(message: str):
        """Show spinner with message"""
        return st.spinner(message)

    @staticmethod
    def render_prerequisites_warning():
        """Render prerequisites warning"""
        st.warning("⚠️ Please complete the project setup first!")
        st.markdown("""
        **Required steps:**
        1. Upload PDF file
        2. Configure project details
        3. Create folder structure
        """)

    @staticmethod
    def validate_project_config(config: Dict) -> bool:
        """Validate project configuration"""
        return bool(config.get('code') and config.get('book_name'))

    @staticmethod
    def get_project_path(base_name: str) -> Path:
        """Get the project path using project destination"""
        project_destination = CommonUtils.get_project_destination()
        if project_destination and os.path.exists(project_destination):
            base_path = Path(project_destination)
        else:
            base_path = Path.cwd()

        project_path = base_path / base_name

        if not project_path.exists():
            project_path.mkdir(parents=True, exist_ok=True)

        return project_path

    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitize filename by removing invalid characters"""
        import re
        return re.sub(r'[<>:"/\\|?*]', '_', filename)

    @staticmethod
    def format_display_name(name: str, max_length: int = 50) -> str:
        """Format display name with length limit"""
        if len(name) > max_length:
            return name[:max_length-3] + "..."
        return name

    @staticmethod
    def create_unique_id(prefix: str, existing_ids: List[str]) -> str:
        """Create a unique ID with prefix"""
        import random
        while True:
            unique_id = f"{prefix}_{random.randint(10000, 99999)}"
            if unique_id not in existing_ids:
                return unique_id

    @staticmethod
    def get_file_size_mb(file_path: str) -> float:
        """Get file size in MB"""
        try:
            return os.path.getsize(file_path) / (1024 * 1024)
        except OSError:
            return 0.0

    @staticmethod
    def is_large_file(file_path: str, threshold_mb: int = 100) -> bool:
        """Check if file is large"""
        return CommonUtils.get_file_size_mb(file_path) > threshold_mb

    @staticmethod
    def format_file_size(size_bytes: int) -> str:
        """Format file size for display"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"

    @staticmethod
    def get_quick_access_folders() -> Dict[str, str]:
        """Get quick access folder shortcuts"""
        home = Path.home()
        folders = {
            "Desktop": str(home / "Desktop"),
            "Documents": str(home / "Documents"),
            "Downloads": str(home / "Downloads"),
            "Current": str(Path.cwd())
        }

        return {name: path for name, path in folders.items() if os.path.exists(path)}

    @staticmethod
    def handle_operation_completion(operation: str, entity_name: str, location: str = None):
        """Handle operation completion with success messages"""
        st.session_state['part_operation_completed'] = True
        st.session_state['part_operation_info'] = {
            'operation': operation,
            'part_name': entity_name,
            'location': location
        }

    @staticmethod
    def clear_operation_completion():
        """Clear operation completion flags"""
        if 'part_operation_completed' in st.session_state:
            st.session_state['part_operation_completed'] = False
        if 'part_operation_info' in st.session_state:
            st.session_state['part_operation_info'] = {}