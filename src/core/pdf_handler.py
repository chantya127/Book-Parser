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
        Load PDF and extract basic information with optimized memory handling
        
        Args:
            uploaded_file: Streamlit uploaded file object
            
        Returns:
            Tuple of (PDF reader object, total pages)
        """
        try:
            # Always read and store the full content for reliability
            # Reset file pointer to beginning
            uploaded_file.seek(0)
            file_content = uploaded_file.read()
            
            # Validate we actually got content
            if not file_content or len(file_content) == 0:
                st.error("PDF file appears to be empty or corrupted")
                return None, 0
            
            pdf_reader = PyPDF2.PdfReader(BytesIO(file_content))
            total_pages = len(pdf_reader.pages)
            
            # Store file content in session state for ALL files
            # For memory management, we'll handle this differently
            file_size_mb = len(file_content) / (1024 * 1024)
            
            if file_size_mb > 100:
                st.info(f"Large PDF detected ({file_size_mb:.1f}MB). Processing may take longer.")
                # Still store content but warn about memory usage
                st.session_state.pdf_content = file_content
                st.session_state.pdf_large_file = True
            else:
                st.session_state.pdf_content = file_content
                st.session_state.pdf_large_file = False
            
            # Also store file name for reference
            st.session_state.pdf_file_name = uploaded_file.name
            
            return pdf_reader, total_pages
            
        except Exception as e:
            st.error(f"Error reading PDF: {str(e)}")
            return None, 0
    
    @staticmethod
    def get_pdf_reader() -> Optional[PyPDF2.PdfReader]:
        """Get PDF reader from stored content"""
        try:
            # Always try to get from stored content first
            pdf_content = st.session_state.get('pdf_content')
            if pdf_content:
                return PyPDF2.PdfReader(BytesIO(pdf_content))
            
            # Fallback: try to get from uploaded file (may not work for large files)
            pdf_file = st.session_state.get('pdf_file')
            if pdf_file:
                try:
                    pdf_file.seek(0)
                    file_content = pdf_file.read()
                    if file_content:
                        return PyPDF2.PdfReader(BytesIO(file_content))
                except:
                    pass
            
            # If all else fails, show helpful error
            st.error("PDF content not available. Please re-upload your PDF file.")
            return None
            
        except Exception as e:
            st.error(f"Error accessing PDF: {str(e)}")
            return None
    
    @staticmethod
    def validate_pdf(uploaded_file) -> bool:
        """Validate if uploaded file is a proper PDF"""
        try:
            uploaded_file.seek(0)  # Reset file pointer
            content = uploaded_file.read()
            uploaded_file.seek(0)  # Reset for future reads
            
            if not content or len(content) == 0:
                return False
                
            pdf_reader = PyPDF2.PdfReader(BytesIO(content))
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
        """
        try:
            # Parse page ranges into individual page numbers
            pages_to_extract = PDFExtractor.parse_page_ranges(page_ranges, total_pages)
            
            if not pages_to_extract:
                return False, [], "No valid pages specified"
            
            # Get PDF reader
            pdf_reader = PDFHandler.get_pdf_reader()
            if not pdf_reader:
                pdf_content = st.session_state.get('pdf_content')
                if pdf_content:
                    try:
                        from io import BytesIO
                        import PyPDF2
                        pdf_reader = PyPDF2.PdfReader(BytesIO(pdf_content))
                    except Exception as e:
                        return False, [], f"Could not access PDF file: {str(e)}"
                
                if not pdf_reader:
                    return False, [], "Could not access PDF file. Please re-upload your PDF."
            
            # Use the destination_folder exactly as provided
            dest_path = Path(destination_folder)
            
            # Create destination folder if it doesn't exist
            dest_path.mkdir(parents=True, exist_ok=True)
            
            created_files = []
            failed_pages = []
            
            # Extract each page
            for idx, (sequential_num, actual_page_num) in enumerate(enumerate(pages_to_extract, 1)):
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
        Extract a single page from PDF with proper naming convention and correct spacing
        """
        try:
            # Validate page number
            if actual_page_num < 1 or actual_page_num > len(pdf_reader.pages):
                return False, f"Page {actual_page_num} out of range"
            
            # Create new PDF with single page
            pdf_writer = PyPDF2.PdfWriter()
            pdf_writer.add_page(pdf_reader.pages[actual_page_num - 1])
            
            # Use sequential numbering if provided, otherwise use actual page number
            page_num_for_filename = sequential_page_num if sequential_page_num is not None else actual_page_num
            
            # Apply font formatting to the page number text
            import streamlit as st
            from core.text_formatter import TextFormatter
            font_case = st.session_state.get('selected_font_case', 'First Capital (Title Case)')
            formatted_page_num = TextFormatter.format_text(str(page_num_for_filename), font_case)
            
            # Generate file name with proper spacing - KEEP THE SPACE
            # Don't sanitize the naming_base if it already has proper formatting
            file_name = f"{naming_base}_Page {formatted_page_num}.pdf"
            
            # Use the exact dest_path provided
            file_path = dest_path / file_name
            
            # Write PDF file
            with open(file_path, 'wb') as output_file:
                pdf_writer.write(output_file)
            
            return True, str(file_path.absolute())
            
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