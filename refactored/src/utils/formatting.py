# src/utils/formatting.py - Formatting utility functions
from typing import Dict, List, Optional
from pathlib import Path

class FormattingUtils:
    """Formatting utility functions"""

    @staticmethod
    def format_project_code(code: str, font_case: str) -> str:
        """Format project code based on font case"""
        from ..core.text_formatter import TextFormatter
        return TextFormatter.format_project_code(code, font_case)

    @staticmethod
    def format_book_name(name: str, font_case: str) -> str:
        """Format book name based on font case"""
        from ..core.text_formatter import TextFormatter
        return TextFormatter.format_book_name(name, font_case)

    @staticmethod
    def format_part_name(name: str, font_case: str) -> str:
        """Format part name based on font case"""
        from ..core.text_formatter import TextFormatter
        return TextFormatter.format_part_name(name, font_case)

    @staticmethod
    def format_chapter_number(number: str, font_case: str) -> str:
        """Format chapter number based on font case"""
        from ..core.text_formatter import TextFormatter
        return TextFormatter.format_chapter_number(number, font_case)

    @staticmethod
    def format_chapter_name(name: str, font_case: str) -> str:
        """Format chapter name based on font case"""
        from ..core.text_formatter import TextFormatter
        return TextFormatter.format_chapter_name(name, font_case)

    @staticmethod
    def format_custom_folder_name(name: str, font_case: str) -> str:
        """Format custom folder name based on font case"""
        from ..core.text_formatter import TextFormatter
        return TextFormatter.format_custom_folder_name(name, font_case)

    @staticmethod
    def format_text(text: str, font_case: str) -> str:
        """Format text based on font case"""
        from ..core.text_formatter import TextFormatter
        return TextFormatter.format_text(text, font_case)

    @staticmethod
    def get_font_case_options() -> List[str]:
        """Get available font case options"""
        from ..core.text_formatter import TextFormatter
        return TextFormatter.get_font_case_options()

    @staticmethod
    def format_file_path(path: str) -> str:
        """Format file path for display"""
        try:
            path_obj = Path(path)
            return str(path_obj.absolute())
        except Exception:
            return path

    @staticmethod
    def format_folder_name(name: str, font_case: str) -> str:
        """Format folder name based on font case"""
        from ..core.text_formatter import TextFormatter
        return TextFormatter.format_folder_name(name, font_case)

    @staticmethod
    def format_display_name(name: str, max_length: int = 50) -> str:
        """Format display name with length limit"""
        if len(name) > max_length:
            return name[:max_length-3] + "..."
        return name

    @staticmethod
    def format_number_with_suffix(number: int, suffix: str) -> str:
        """Format number with suffix"""
        if suffix:
            return f"{number:02d}{suffix}"
        return str(number)

    @staticmethod
    def format_timestamp(timestamp_str: str) -> str:
        """Format timestamp for display"""
        from datetime import datetime
        try:
            timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            return timestamp.strftime('%Y-%m-%d %H:%M:%S')
        except Exception:
            return timestamp_str

    @staticmethod
    def format_duration(seconds: float) -> str:
        """Format duration in seconds to human readable format"""
        if seconds < 60:
            return f"{seconds:.1f}s"
        elif seconds < 3600:
            minutes = seconds / 60
            return f"{minutes:.1f}m"
        else:
            hours = seconds / 3600
            return f"{hours:.1f}h"

    @staticmethod
    def format_percentage(value: float, total: float) -> str:
        """Format percentage"""
        if total == 0:
            return "0.0%"
        percentage = (value / total) * 100
        return f"{percentage:.1f}%"

    @staticmethod
    def format_list(items: List[str], separator: str = ", ") -> str:
        """Format list of items"""
        return separator.join(items)

    @staticmethod
    def format_dict(data: Dict, separator: str = ", ") -> str:
        """Format dictionary as string"""
        return separator.join(f"{k}: {v}" for k, v in data.items())

    @staticmethod
    def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
        """Truncate text to max length"""
        if len(text) <= max_length:
            return text
        return text[:max_length-len(suffix)] + suffix

    @staticmethod
    def format_bytes(size_bytes: int) -> str:
        """Format bytes to human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"

    @staticmethod
    def format_path_for_display(path: str) -> str:
        """Format path for display in UI"""
        try:
            path_obj = Path(path)
            # Show only the last few components for readability
            parts = path_obj.parts
            if len(parts) > 3:
                return f"...{Path(*parts[-3:]).as_posix()}"
            return path_obj.as_posix()
        except Exception:
            return path

    @staticmethod
    def format_status_message(success: bool, message: str) -> str:
        """Format status message with emoji"""
        if success:
            return f"✅ {message}"
        else:
            return f"❌ {message}"

    @staticmethod
    def format_progress_message(current: int, total: int, item_name: str = "items") -> str:
        """Format progress message"""
        percentage = (current / total) * 100 if total > 0 else 0
        return f"Progress: {current}/{total} {item_name} ({percentage:.1f}%)"