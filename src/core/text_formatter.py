# core/text_formatter.py - Text formatting utilities

from enum import Enum
from typing import Any, Dict, Optional

class FontCase(Enum):
    """Font case formatting options"""
    ALL_CAPS = "All Caps (UPPERCASE)"
    ALL_SMALL = "All Small (lowercase)" 
    FIRST_CAPITAL = "First Capital (Sentence case)"

class TextFormatter:
    """Centralized text formatting based on selected font case"""
    
    @staticmethod
    def format_text(text: str, font_case: str) -> str:
        """
        Format text according to the selected font case
        
        Args:
            text: Original text to format
            font_case: Font case option from FontCase enum
            
        Returns:
            Formatted text
        """
        if not text or not isinstance(text, str):
            return text
        
        text = str(text).strip()
        
        # Debug: Check what font_case value we're getting
        if font_case == FontCase.ALL_CAPS.value or font_case == "All Caps (UPPERCASE)":
            return text.upper()
        elif font_case == FontCase.ALL_SMALL.value or font_case == "All Small (lowercase)":
            return text.lower()
        elif font_case == FontCase.FIRST_CAPITAL.value or font_case == "First Capital (Sentence case)":
            return text.capitalize()
        else:
            # Default to original text if unknown format
            return text
    
    @staticmethod
    def get_font_case_options() -> list:
        """Get all available font case options"""
        return [case.value for case in FontCase]
    
    @staticmethod
    def format_project_code(code: str, font_case: str) -> str:
        """Format project code"""
        return TextFormatter.format_text(code, font_case)
    
    @staticmethod
    def format_book_name(book_name: str, font_case: str) -> str:
        """Format book name"""
        return TextFormatter.format_text(book_name, font_case)
    
    @staticmethod
    def format_part_name(part_name: str, font_case: str) -> str:
        """Format part name"""
        return TextFormatter.format_text(part_name, font_case)
    
    @staticmethod
    def format_chapter_name(chapter_name: str, font_case: str) -> str:
        """Format chapter name"""
        return TextFormatter.format_text(chapter_name, font_case)
    
    @staticmethod
    def format_chapter_number(chapter_number: str, font_case: str) -> str:
        """Format chapter number"""
        return TextFormatter.format_text(chapter_number, font_case)
    
    @staticmethod
    def format_folder_name(folder_name: str, font_case: str) -> str:
        """Format folder name"""
        return TextFormatter.format_text(folder_name, font_case)
    
    @staticmethod
    def format_custom_folder_name(custom_name: str, font_case: str) -> str:
        """Format custom folder name"""
        return TextFormatter.format_text(custom_name, font_case)
    
    @staticmethod
    def get_current_font_case():
        """Get current font case from session - using lazy import"""
        import streamlit as st
        return st.session_state.get('selected_font_case', 'First Capital (Sentence case)')