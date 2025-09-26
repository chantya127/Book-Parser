# src/services/pdf_service.py
from typing import Dict, List, Tuple
from pathlib import Path
import os
from .base_service import PDFService as BasePDFService
from ..core.session_manager import SessionManager
from ..core.pdf_handler import PDFExtractor

class PDFService(BasePDFService):
    """Concrete implementation of PDFService"""

    def validate_config(self, config: Dict) -> bool:
        """Validate PDF service configuration"""
        return bool(config.get('code') and config.get('book_name'))

    def extract_pages(self, pdf_path: str, page_ranges: List[str],
                     destination_path: str, naming_base: str) -> Tuple[bool, List[str], str]:
        """Extract pages from PDF"""
        try:
            folder_path = Path(destination_path)

            # Check if destination folder already has PDF files
            if folder_path.exists():
                existing_pdfs = list(folder_path.glob("*.pdf"))
                if existing_pdfs:
                    self.session_manager.warning(f"Destination folder already contains {len(existing_pdfs)} PDF files. New files will be added alongside existing ones.")

            # Ensure the folder exists
            folder_path.mkdir(parents=True, exist_ok=True)

            # Pass the exact path without any modification
            success, created_files, error_msg = PDFExtractor.extract_pages_to_folder(
                page_ranges, destination_path, naming_base, self.session_manager.get('total_pages', 0)
            )

            if success and created_files:
                # Update extraction history
                extraction_history = self.session_manager.get('extraction_history', [])
                extraction_record = {
                    'destination': folder_path.name,
                    'destination_path': destination_path,
                    'pages_extracted': len(created_files),
                    'page_ranges': page_ranges,
                    'files_created': created_files,
                    'naming_base': naming_base
                }
                extraction_history.append(extraction_record)
                self.session_manager.set('extraction_history', extraction_history)

                return True, created_files, ""

            elif success and not created_files:
                return True, [], "No pages were extracted. Please check your page ranges."
            else:
                return False, [], error_msg

        except Exception as e:
            return False, [], f"Extraction error: {str(e)}"

    def validate_pdf(self, pdf_path: str) -> Tuple[bool, str]:
        """Validate PDF file"""
        try:
            path = Path(pdf_path)

            if not path.exists():
                return False, "PDF file not found"

            if not path.is_file():
                return False, "Path is not a file"

            if path.suffix.lower() != '.pdf':
                return False, "File is not a PDF"

            # Try to read the PDF to validate it
            pdf_reader, total_pages = PDFExtractor.load_pdf_info(path)

            if pdf_reader and total_pages > 0:
                return True, f"Valid PDF with {total_pages} pages"
            else:
                return False, "PDF file is corrupted or invalid"

        except Exception as e:
            return False, f"Error validating PDF: {str(e)}"

    def get_pdf_info(self, pdf_path: str) -> Dict:
        """Get PDF information"""
        try:
            path = Path(pdf_path)

            if not path.exists():
                return {'exists': False, 'error': 'PDF file not found'}

            pdf_reader, total_pages = PDFExtractor.load_pdf_info(path)

            if pdf_reader and total_pages > 0:
                return {
                    'exists': True,
                    'path': str(path.absolute()),
                    'name': path.name,
                    'size': path.stat().st_size,
                    'pages': total_pages,
                    'valid': True
                }
            else:
                return {
                    'exists': True,
                    'path': str(path.absolute()),
                    'name': path.name,
                    'size': path.stat().st_size,
                    'pages': 0,
                    'valid': False,
                    'error': 'Invalid or corrupted PDF'
                }

        except Exception as e:
            return {
                'exists': False,
                'error': str(e)
            }

    def preview_extraction(self, page_ranges: List[str], total_pages: int) -> str:
        """Preview page extraction without actually doing it"""
        return PDFExtractor.preview_page_extraction(page_ranges, total_pages)

    def parse_page_ranges(self, page_ranges: List[str], total_pages: int) -> List[int]:
        """Parse page ranges into individual page numbers"""
        return PDFExtractor.parse_page_ranges(page_ranges, total_pages)