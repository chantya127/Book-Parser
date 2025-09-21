import PyPDF2
from io import BytesIO
import streamlit as st
from typing import Tuple, Optional, List
from pathlib import Path
import os

class PDFHandler:
    """Handles PDF file operations"""
    
    @staticmethod
    def load_pdf_info(uploaded_file) -> Tuple[Optional[PyPDF2.PdfReader], int]:
        """
        Load PDF and extract basic information with memory optimization
        
        Args:
            uploaded_file: Streamlit uploaded file object
            
        Returns:
            Tuple of (PDF reader object, total pages)
        """
        try:
            # For large files, avoid storing full content in session
            # Instead, store file info and reload when needed
            file_content = uploaded_file.read()
            pdf_reader = PyPDF2.PdfReader(BytesIO(file_content))
            total_pages = len(pdf_reader.pages)
            
            # Store file info instead of full content for large files
            file_size_mb = len(file_content) / (1024 * 1024)
            if file_size_mb > 100:  # Only store content for files smaller than 100MB
                st.session_state.pdf_file_name = uploaded_file.name
                st.session_state.pdf_large_file = True
                st.info(f"Large PDF detected ({file_size_mb:.1f}MB). Using optimized memory handling.")
            else:
                st.session_state.pdf_content = file_content
                st.session_state.pdf_large_file = False
            
            return pdf_reader, total_pages
        except Exception as e:
            st.error(f"Error reading PDF: {str(e)}")
            return None, 0
    
    @staticmethod
    def get_pdf_reader() -> Optional[PyPDF2.PdfReader]:
        """Get PDF reader from stored content or reload from file"""
        try:
            # Check if we have content stored (for smaller files)
            pdf_content = st.session_state.get('pdf_content')
            if pdf_content:
                return PyPDF2.PdfReader(BytesIO(pdf_content))
            
            # For large files, get from the uploaded file directly
            pdf_file = st.session_state.get('pdf_file')
            if pdf_file:
                return PyPDF2.PdfReader(BytesIO(pdf_file.read()))
            
            return None
        except Exception as e:
            st.error(f"Error accessing PDF: {str(e)}")
            return None
    
    @staticmethod
    def validate_pdf(uploaded_file) -> bool:
        """Validate if uploaded file is a proper PDF"""
        try:
            uploaded_file.seek(0)  # Reset file pointer
            pdf_reader = PyPDF2.PdfReader(BytesIO(uploaded_file.read()))
            uploaded_file.seek(0)  # Reset for future reads
            return len(pdf_reader.pages) > 0
        except:
            return False


class PDFExtractor:
    """Handles PDF page extraction and file creation"""
    
    @staticmethod
    def extract_pages_to_folder(page_ranges: List[str], destination_folder: str, 
                              naming_base: str, total_pages: int) -> Tuple[bool, List[str], str]:
        """
        Extract specified pages from PDF and save to destination folder with sequential numbering
        
        Args:
            page_ranges: List of page range strings (e.g., ["1-5", "10", "15-20"])
            destination_folder: Target folder path
            naming_base: Base name for file naming (should include full hierarchy)
            total_pages: Total pages in PDF for validation
            
        Returns:
            Tuple of (success, list of created files, error message)
        """
        try:
            # Parse page ranges into individual page numbers
            pages_to_extract = PDFExtractor.parse_page_ranges(page_ranges, total_pages)
            
            if not pages_to_extract:
                return False, [], "No valid pages specified"
            
            # Get PDF reader
            pdf_reader = PDFHandler.get_pdf_reader()
            if not pdf_reader:
                return False, [], "Could not access PDF file"
            
            # Create destination folder if it doesn't exist
            dest_path = Path(destination_folder)
            dest_path.mkdir(parents=True, exist_ok=True)
            
            created_files = []
            failed_pages = []
            
            # Extract each page with sequential numbering (starting from 1)
            for sequential_num, actual_page_num in enumerate(pages_to_extract, 1):
                success, file_path = PDFExtractor.extract_single_page(
                    pdf_reader, actual_page_num, dest_path, naming_base, sequential_num
                )
                
                if success:
                    created_files.append(file_path)
                else:
                    failed_pages.append(actual_page_num)
            
            # Report results
            if failed_pages:
                warning_msg = f"Failed to extract pages: {', '.join(map(str, failed_pages))}"
                st.warning(warning_msg)
            
            success_status = len(created_files) > 0
            return success_status, created_files, ""
            
        except Exception as e:
            return False, [], f"Error extracting pages: {str(e)}"
    
    @staticmethod
    def extract_single_page(pdf_reader: PyPDF2.PdfReader, actual_page_num: int, 
                          dest_path: Path, naming_base: str, sequential_page_num: int = None) -> Tuple[bool, str]:
        """
        Extract a single page from PDF with proper naming convention and sequential numbering
        
        Args:
            pdf_reader: PDF reader object
            actual_page_num: Actual page number in PDF to extract (1-indexed)
            dest_path: Destination folder path
            naming_base: Complete naming base including parent folder hierarchy
            sequential_page_num: Sequential page number for file naming (starts from 1)
            
        Returns:
            Tuple of (success, file_path)
        """
        try:
            # Validate page number
            if actual_page_num < 1 or actual_page_num > len(pdf_reader.pages):
                return False, f"Page {actual_page_num} out of range"
            
            # Create new PDF with single page
            pdf_writer = PyPDF2.PdfWriter()
            pdf_writer.add_page(pdf_reader.pages[actual_page_num - 1])  # Convert to 0-indexed
            
            # Use sequential numbering if provided, otherwise use actual page number
            page_num_for_filename = sequential_page_num if sequential_page_num is not None else actual_page_num
            
            # Generate file name using the complete naming base with sequential numbering
            safe_naming_base = PDFExtractor.sanitize_filename(naming_base)
            file_name = f"{safe_naming_base}_Page_{page_num_for_filename}.pdf"
            file_path = dest_path / file_name
            
            # Write PDF file
            with open(file_path, 'wb') as output_file:
                pdf_writer.write(output_file)
            
            return True, str(file_path)
            
        except Exception as e:
            st.error(f"Error extracting page {actual_page_num}: {str(e)}")
            return False, ""
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitize filename for cross-platform compatibility"""
        # Remove/replace problematic characters
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        
        # Remove extra spaces and limit length
        filename = '_'.join(filename.split())
        return filename[:200]  # Limit filename length
    
    @staticmethod
    def parse_page_ranges(page_ranges: List[str], total_pages: int) -> List[int]:
        """
        Parse page range strings into list of individual page numbers
        
        Args:
            page_ranges: List of range strings (e.g., ["1-5", "10", "15-20"])
            total_pages: Total pages for validation
            
        Returns:
            List of individual page numbers
        """
        pages = set()
        
        for range_str in page_ranges:
            range_str = range_str.strip()
            if not range_str:
                continue
            
            if '-' in range_str:
                # Handle range (e.g., "1-5")
                try:
                    parts = range_str.split('-')
                    if len(parts) != 2:
                        st.warning(f"Invalid range format: {range_str}")
                        continue
                        
                    start, end = parts
                    start_page = int(start.strip())
                    end_page = int(end.strip())
                    
                    # Validate range
                    if start_page > 0 and end_page <= total_pages and start_page <= end_page:
                        pages.update(range(start_page, end_page + 1))
                    else:
                        st.warning(f"Invalid range: {range_str} (PDF has {total_pages} pages)")
                        
                except ValueError:
                    st.warning(f"Invalid range format: {range_str}")
            else:
                # Handle single page
                try:
                    page_num = int(range_str)
                    if 1 <= page_num <= total_pages:
                        pages.add(page_num)
                    else:
                        st.warning(f"Page {page_num} out of range (1-{total_pages})")
                        
                except ValueError:
                    st.warning(f"Invalid page number: {range_str}")
        
        return sorted(list(pages))
    
    @staticmethod
    def preview_page_extraction(page_ranges: List[str], total_pages: int) -> str:
        """
        Generate preview of what pages will be extracted
        
        Args:
            page_ranges: List of page range strings
            total_pages: Total pages for validation
            
        Returns:
            Preview string describing the extraction
        """
        pages = PDFExtractor.parse_page_ranges(page_ranges, total_pages)
        
        if not pages:
            return "No valid pages to extract"
        
        # Group consecutive pages for better display
        if len(pages) == 0:
            return "No pages selected"
        
        groups = []
        current_group = [pages[0]]
        
        for i in range(1, len(pages)):
            if pages[i] == pages[i-1] + 1:
                current_group.append(pages[i])
            else:
                groups.append(current_group)
                current_group = [pages[i]]
        
        groups.append(current_group)
        
        # Format groups
        formatted_groups = []
        for group in groups:
            if len(group) == 1:
                formatted_groups.append(str(group[0]))
            else:
                formatted_groups.append(f"{group[0]}-{group[-1]}")
        
        return f"Pages to extract: {', '.join(formatted_groups)} (Total: {len(pages)} pages)"