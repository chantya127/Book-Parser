# src/utils/file_utils.py - File operation utilities
import os
import shutil
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import streamlit as st

class FileUtils:
    """File operation utility functions"""

    @staticmethod
    def ensure_directory_exists(directory: str) -> bool:
        """Ensure directory exists, create if it doesn't"""
        try:
            Path(directory).mkdir(parents=True, exist_ok=True)
            return True
        except Exception:
            return False

    @staticmethod
    def copy_file(source: str, destination: str) -> bool:
        """Copy file from source to destination"""
        try:
            shutil.copy2(source, destination)
            return True
        except Exception:
            return False

    @staticmethod
    def move_file(source: str, destination: str) -> bool:
        """Move file from source to destination"""
        try:
            shutil.move(source, destination)
            return True
        except Exception:
            return False

    @staticmethod
    def delete_file(file_path: str) -> bool:
        """Delete file"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
            return False
        except Exception:
            return False

    @staticmethod
    def delete_directory(directory: str) -> bool:
        """Delete directory and all contents"""
        try:
            if os.path.exists(directory):
                shutil.rmtree(directory)
                return True
            return False
        except Exception:
            return False

    @staticmethod
    def get_file_size(file_path: str) -> int:
        """Get file size in bytes"""
        try:
            return os.path.getsize(file_path)
        except OSError:
            return 0

    @staticmethod
    def get_directory_size(directory: str) -> int:
        """Get directory size in bytes"""
        try:
            total_size = 0
            for dirpath, dirnames, filenames in os.walk(directory):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    try:
                        total_size += os.path.getsize(filepath)
                    except OSError:
                        pass
            return total_size
        except Exception:
            return 0

    @staticmethod
    def list_files(directory: str, extension: str = None) -> List[str]:
        """List files in directory"""
        try:
            files = []
            for item in os.listdir(directory):
                item_path = os.path.join(directory, item)
                if os.path.isfile(item_path):
                    if extension:
                        if item.lower().endswith(extension.lower()):
                            files.append(item_path)
                    else:
                        files.append(item_path)
            return files
        except Exception:
            return []

    @staticmethod
    def list_directories(directory: str) -> List[str]:
        """List directories in directory"""
        try:
            directories = []
            for item in os.listdir(directory):
                item_path = os.path.join(directory, item)
                if os.path.isdir(item_path):
                    directories.append(item_path)
            return directories
        except Exception:
            return []

    @staticmethod
    def find_files_by_pattern(directory: str, pattern: str) -> List[str]:
        """Find files matching pattern"""
        try:
            import glob
            search_pattern = os.path.join(directory, pattern)
            return glob.glob(search_pattern, recursive=True)
        except Exception:
            return []

    @staticmethod
    def get_file_info(file_path: str) -> Dict:
        """Get file information"""
        try:
            path = Path(file_path)
            if not path.exists():
                return {'exists': False}

            stat = path.stat()
            return {
                'exists': True,
                'name': path.name,
                'path': str(path.absolute()),
                'size': stat.st_size,
                'modified': stat.st_mtime,
                'is_file': path.is_file(),
                'is_directory': path.is_dir(),
                'extension': path.suffix,
                'parent': str(path.parent)
            }
        except Exception as e:
            return {'exists': False, 'error': str(e)}

    @staticmethod
    def create_temp_file(suffix: str = '', prefix: str = 'temp') -> str:
        """Create temporary file"""
        try:
            import tempfile
            fd, path = tempfile.mkstemp(suffix=suffix, prefix=prefix)
            os.close(fd)
            return path
        except Exception:
            return ""

    @staticmethod
    def create_temp_directory(suffix: str = '', prefix: str = 'temp') -> str:
        """Create temporary directory"""
        try:
            import tempfile
            return tempfile.mkdtemp(suffix=suffix, prefix=prefix)
        except Exception:
            return ""

    @staticmethod
    def is_file_locked(file_path: str) -> bool:
        """Check if file is locked"""
        try:
            with open(file_path, 'a'):
                pass
            return False
        except IOError:
            return True

    @staticmethod
    def safe_delete_file(file_path: str) -> bool:
        """Safely delete file with retry logic"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    return True
                return False
            except PermissionError:
                if attempt < max_retries - 1:
                    import time
                    time.sleep(0.1)  # Wait 100ms before retry
                else:
                    return False
            except Exception:
                return False
        return False

    @staticmethod
    def safe_delete_directory(directory: str) -> bool:
        """Safely delete directory with retry logic"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                if os.path.exists(directory):
                    shutil.rmtree(directory)
                    return True
                return False
            except PermissionError:
                if attempt < max_retries - 1:
                    import time
                    time.sleep(0.1)  # Wait 100ms before retry
                else:
                    return False
            except Exception:
                return False
        return False

    @staticmethod
    def backup_file(file_path: str, backup_suffix: str = '.bak') -> bool:
        """Create backup of file"""
        try:
            if os.path.exists(file_path):
                backup_path = file_path + backup_suffix
                shutil.copy2(file_path, backup_path)
                return True
            return False
        except Exception:
            return False

    @staticmethod
    def restore_backup(backup_path: str, original_path: str) -> bool:
        """Restore file from backup"""
        try:
            if os.path.exists(backup_path):
                shutil.copy2(backup_path, original_path)
                return True
            return False
        except Exception:
            return False

    @staticmethod
    def clean_empty_directories(directory: str) -> int:
        """Clean empty directories recursively"""
        cleaned_count = 0
        try:
            for root, dirs, files in os.walk(directory, topdown=False):
                for dir_name in dirs:
                    dir_path = os.path.join(root, dir_name)
                    try:
                        if not os.listdir(dir_path):  # Empty directory
                            os.rmdir(dir_path)
                            cleaned_count += 1
                    except OSError:
                        pass  # Directory not empty or permission denied
        except Exception:
            pass
        return cleaned_count

    @staticmethod
    def get_mime_type(file_path: str) -> str:
        """Get MIME type of file"""
        try:
            import mimetypes
            mime_type, _ = mimetypes.guess_type(file_path)
            return mime_type or 'application/octet-stream'
        except Exception:
            return 'application/octet-stream'

    @staticmethod
    def is_text_file(file_path: str) -> bool:
        """Check if file is a text file"""
        try:
            mime_type = FileUtils.get_mime_type(file_path)
            return mime_type and mime_type.startswith('text/')
        except Exception:
            return False

    @staticmethod
    def is_binary_file(file_path: str) -> bool:
        """Check if file is a binary file"""
        try:
            with open(file_path, 'rb') as f:
                chunk = f.read(1024)
                return b'\0' in chunk
        except Exception:
            return True

    @staticmethod
    def count_files_by_extension(directory: str, extension: str) -> int:
        """Count files with specific extension"""
        try:
            count = 0
            for root, dirs, files in os.walk(directory):
                for file in files:
                    if file.lower().endswith(extension.lower()):
                        count += 1
            return count
        except Exception:
            return 0