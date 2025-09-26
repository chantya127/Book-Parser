# src/ui/chapter_operations.py - Chapter operations UI components
import streamlit as st
from typing import Dict, List
from ..services.service_factory import service_factory

class ChapterOperationsUI:
    """UI components for chapter operations"""

    def __init__(self):
        self.chapter_service = service_factory.get_chapter_service()

    def render_chapter_details_optimized(self, context_key: str, chapters: List[Dict],
                                       config: Dict, is_standalone: bool = False):
        """Optimized chapter details rendering with proper state management and font formatting"""

        if is_standalone:
            st.markdown("**Configure standalone chapters:**")
        else:
            st.markdown(f"**Configure chapters for {context_key}:**")

        # Lazy import for font formatting
        from ..core.text_formatter import TextFormatter
        font_case = st.session_state.get('selected_font_case', 'First Capital (Sentence case)')

        safe_code = config['code']
        book_name = config['book_name']
        base_name = f"{safe_code}_{book_name}"

        # Check which chapters already have folders created
        created_chapter_indices = self.chapter_service.get_created_chapter_indices(
            config, context_key, chapters, is_standalone
        )

        updated_chapters = []

        for i, chapter in enumerate(chapters):
            # Chapter number and name inputs with action buttons
            col1, col2, col3, col4 = st.columns([2, 2, 1, 1])

            with col1:
                if chapter.get('is_null_sequence'):
                    st.text_input(
                        "Number",
                        value=chapter.get('number', ''),
                        key=f"{context_key}_chapter_num_{i}",
                        disabled=True,
                        help="NULL sequence number (auto-generated)"
                    )
                    chapter_number = chapter.get('number', '')
                else:
                    chapter_number = st.text_input(
                        "Number",
                        value=chapter.get('number', ''),
                        placeholder=f"e.g., {chapter.get('number', '')}",
                        key=f"{context_key}_chapter_num_{i}",
                        help="Chapter number"
                    )

            with col2:
                if chapter.get('is_null_sequence'):
                    st.text_input(
                        "Name",
                        value=chapter.get('name', ''),
                        key=f"{context_key}_chapter_name_{i}",
                        disabled=True,
                        help="NULL sequence name (auto-generated)"
                    )
                    chapter_name = chapter.get('name', '')
                else:
                    chapter_name = st.text_input(
                        "Name",
                        value=chapter.get('name', ''),
                        placeholder="e.g., Introduction, Overview",
                        key=f"{context_key}_chapter_name_{i}",
                        help="Chapter name"
                    )

            # Apply font formatting to current input values
            if not chapter.get('is_null_sequence'):
                formatted_chapter_number = TextFormatter.format_chapter_number(chapter_number, font_case) if chapter_number else ''
                formatted_chapter_name = TextFormatter.format_chapter_name(chapter_name, font_case) if chapter_name else ''
            else:
                formatted_chapter_number = chapter_number
                formatted_chapter_name = chapter_name

            with col3:
                st.write("")
                st.write("")
                # Create button - only show if folder doesn't exist
                if i not in created_chapter_indices:
                    if st.button("💾", key=f"create_chapter_{context_key}_{i}", help="Create this chapter folder"):
                        chapter_to_create = {
                            'number': formatted_chapter_number,
                            'name': formatted_chapter_name,
                            'is_null_sequence': chapter.get('is_null_sequence', False)
                        }
                        if self.chapter_service.create_chapter(config, context_key, chapter_to_create, is_standalone, create_only=True, chapter_index=i):
                            st.success(f"Chapter folder created!")
                            st.rerun()
                else:
                    st.write("✅")  # Just show checkmark, no individual update

            with col4:
                st.write("")
                st.write("")
                # Delete button - only show if folder exists
                if i in created_chapter_indices:
                    if st.button("🗑️", key=f"delete_chapter_{context_key}_{i}", help="Delete this chapter folder"):
                        if self.chapter_service.delete_chapter(config, context_key, i, is_standalone):
                            st.success("Chapter deleted!")
                            st.rerun()

            # Store updated chapter data
            updated_chapters.append({
                'number': formatted_chapter_number,
                'name': formatted_chapter_name,
                'original_number': chapter_number if not chapter.get('is_null_sequence') else '',
                'original_name': chapter_name if not chapter.get('is_null_sequence') else '',
                'is_null_sequence': chapter.get('is_null_sequence', False)
            })

            # Show preview and status
            if is_standalone:
                preview_name = self._generate_chapter_folder_name(
                    base_name,
                    formatted_chapter_number or None,
                    formatted_chapter_name or None
                )
            else:
                preview_name = self._generate_chapter_folder_name(
                    f"{base_name}_{context_key}",
                    formatted_chapter_number or None,
                    formatted_chapter_name or None
                )

            status_text = "✅ Created" if i in created_chapter_indices else "⏳ Not created"
            st.caption(f"📁 Folder: `{preview_name}` | {status_text}")

            if i < len(chapters) - 1:
                st.markdown("---")

        # Update session state with new values
        if is_standalone:
            self._update_standalone_chapters(updated_chapters)
        else:
            self._update_part_chapters(context_key, updated_chapters)

    def _generate_chapter_folder_name(self, parent_folder_name: str, chapter_number: str = None, chapter_name: str = None) -> str:
        """Generate chapter folder name"""
        from ..core.folder_manager import ChapterManager
        return ChapterManager.generate_chapter_folder_name(parent_folder_name, chapter_number, chapter_name)

    def _update_standalone_chapters(self, chapters: List[Dict]):
        """Update standalone chapters in session"""
        from ..core.session_manager import SessionManager
        SessionManager.set('standalone_chapters', chapters)

    def _update_part_chapters(self, context_key: str, chapters: List[Dict]):
        """Update part chapters in session"""
        from ..core.session_manager import SessionManager
        chapters_config = SessionManager.get('chapters_config', {})
        chapters_config[context_key] = chapters
        SessionManager.set('chapters_config', chapters_config)