# src/utils/validation.py - Validation utility functions
import re
from typing import Dict, List, Tuple, Optional
from pathlib import Path

class ValidationUtils:
    """Validation utility functions"""

    @staticmethod
    def validate_project_code(code: str) -> Tuple[bool, str]:
        """Validate project code"""
        if not code:
            return False, "Project code cannot be empty"

        if len(code) < 2:
            return False, "Project code must be at least 2 characters long"

        if len(code) > 20:
            return False, "Project code must be less than 20 characters"

        # Allow alphanumeric characters, underscores, and hyphens
        if not re.match(r'^[a-zA-Z0-9_-]+$', code):
            return False, "Project code can only contain letters, numbers, underscores, and hyphens"

        return True, "Valid project code"

    @staticmethod
    def validate_book_name(name: str) -> Tuple[bool, str]:
        """Validate book name"""
        if not name:
            return False, "Book name cannot be empty"

        if len(name) < 2:
            return False, "Book name must be at least 2 characters long"

        if len(name) > 100:
            return False, "Book name must be less than 100 characters"

        return True, "Valid book name"

    @staticmethod
    def validate_part_name(name: str) -> Tuple[bool, str]:
        """Validate part name"""
        if not name:
            return False, "Part name cannot be empty"

        if len(name) < 2:
            return False, "Part name must be at least 2 characters long"

        if len(name) > 50:
            return False, "Part name must be less than 50 characters"

        return True, "Valid part name"

    @staticmethod
    def validate_chapter_number(number: str) -> Tuple[bool, str]:
        """Validate chapter number"""
        if not number:
            return True, "Empty chapter number is allowed"

        # Allow various formats: 1, 01, I, II, III, A, B, C, etc.
        if re.match(r'^[0-9]+$', number) or re.match(r'^[IVXLCDM]+$', number) or re.match(r'^[A-Z]$', number):
            return True, "Valid chapter number"

        return False, "Invalid chapter number format"

    @staticmethod
    def validate_chapter_name(name: str) -> Tuple[bool, str]:
        """Validate chapter name"""
        if not name:
            return False, "Chapter name cannot be empty"

        if len(name) < 2:
            return False, "Chapter name must be at least 2 characters long"

        if len(name) > 100:
            return False, "Chapter name must be less than 100 characters"

        return True, "Valid chapter name"

    @staticmethod
    def validate_file_path(path: str) -> Tuple[bool, str]:
        """Validate file path"""
        try:
            path_obj = Path(path)
            if path_obj.exists() and path_obj.is_file():
                return True, "Valid file path"
            elif path_obj.exists() and path_obj.is_dir():
                return False, "Path is a directory, not a file"
            else:
                return True, "Path does not exist but is valid"
        except Exception as e:
            return False, f"Invalid path: {str(e)}"

    @staticmethod
    def validate_directory_path(path: str) -> Tuple[bool, str]:
        """Validate directory path"""
        try:
            path_obj = Path(path)
            if path_obj.exists() and path_obj.is_dir():
                return True, "Valid directory path"
            elif path_obj.exists() and path_obj.is_file():
                return False, "Path is a file, not a directory"
            else:
                return True, "Directory does not exist but path is valid"
        except Exception as e:
            return False, f"Invalid directory path: {str(e)}"

    @staticmethod
    def validate_page_ranges(page_ranges: List[str], total_pages: int) -> Tuple[bool, str]:
        """Validate page ranges"""
        if not page_ranges:
            return False, "No page ranges provided"

        valid_pages = []
        for range_str in page_ranges:
            if not range_str.strip():
                continue

            # Handle single page
            if range_str.isdigit():
                page = int(range_str)
                if 1 <= page <= total_pages:
                    valid_pages.append(page)
                else:
                    return False, f"Page {page} is out of range (1-{total_pages})"
            # Handle range
            elif '-' in range_str:
                parts = range_str.split('-')
                if len(parts) != 2:
                    return False, f"Invalid range format: {range_str}"

                try:
                    start = int(parts[0].strip())
                    end = int(parts[1].strip())

                    if start > end:
                        return False, f"Invalid range: {start} > {end}"

                    if start < 1 or end > total_pages:
                        return False, f"Range {start}-{end} is out of bounds (1-{total_pages})"

                    valid_pages.extend(range(start, end + 1))
                except ValueError:
                    return False, f"Invalid number in range: {range_str}"
            else:
                return False, f"Invalid page specification: {range_str}"

        if not valid_pages:
            return False, "No valid pages found"

        return True, f"Valid: {len(valid_pages)} pages"

    @staticmethod
    def validate_pdf_file(file_path: str) -> Tuple[bool, str]:
        """Validate PDF file"""
        if not file_path:
            return False, "No file path provided"

        path = Path(file_path)
        if not path.exists():
            return False, "PDF file does not exist"

        if not path.is_file():
            return False, "Path is not a file"

        if path.suffix.lower() != '.pdf':
            return False, "File is not a PDF"

        # Check file size
        size_mb = path.stat().st_size / (1024 * 1024)
        if size_mb > 500:  # 500MB limit
            return False, f"PDF file is too large ({size_mb:.1f}MB). Maximum size is 500MB"

        return True, f"Valid PDF file ({size_mb:.1f}MB)"

    @staticmethod
    def validate_config(config: Dict) -> Tuple[bool, List[str]]:
        """Validate complete configuration"""
        errors = []

        # Validate project code
        is_valid, message = ValidationUtils.validate_project_code(config.get('code', ''))
        if not is_valid:
            errors.append(f"Project code: {message}")

        # Validate book name
        is_valid, message = ValidationUtils.validate_book_name(config.get('book_name', ''))
        if not is_valid:
            errors.append(f"Book name: {message}")

        return len(errors) == 0, errors

    @staticmethod
    def sanitize_input(text: str) -> str:
        """Sanitize user input"""
        if not text:
            return ""

        # Remove potentially dangerous characters
        dangerous_chars = ['<', '>', '&', '"', "'", '/', '\\', '|', '*', '?', '\0']
        sanitized = text
        for char in dangerous_chars:
            sanitized = sanitized.replace(char, '_')

        return sanitized.strip()

    @staticmethod
    def is_valid_email(email: str) -> bool:
        """Validate email address"""
        if not email:
            return False

        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))

    @staticmethod
    def is_valid_url(url: str) -> bool:
        """Validate URL"""
        if not url:
            return False

        pattern = r'^https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:\w*))*)?$'
        return bool(re.match(pattern, url))