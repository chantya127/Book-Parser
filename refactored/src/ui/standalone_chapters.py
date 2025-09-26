# src/ui/standalone_chapters.py - Standalone chapters UI components
import streamlit as st
from typing import Dict, List
from ..services.service_factory import service_factory
from ..core.chapter_utils import ChapterUtils, ChapterConfigManager

class StandaloneChaptersUI:
    """UI components for standalone chapters management"""

    def __init__(self):
        self.chapter_service = service_factory.get_chapter_service()

    def render_standalone_chapters_section(self, config: Dict):
        """Render standalone chapters configuration section with optimized state management"""

        st.markdown("Create chapters directly under the project root (not inside any part).")

        context_key = 'standalone'

        # Get current state
        current_chapters = ChapterConfigManager.get_chapters_for_context(context_key)
        current_count = len(current_chapters)
        current_system = ChapterConfigManager.get_current_numbering_system(context_key)
        current_suffix = self._get_chapter_suffix(context_key)

        # Number of standalone chapters input
        target_count = st.number_input(
            "Number of standalone chapters",
            min_value=0,
            value=current_count,
            step=1,
            key="standalone_chapters_count",
            help="Enter number of chapters to create directly under project root"
        )

        # Numbering system selector with suffix
        if target_count > 0:
            new_system, new_suffix = ChapterUtils.render_numbering_system_selector(
                context_key,
                current_system,
                "Choose how standalone chapters should be numbered",
                current_suffix
            )

            # Handle system or suffix change with immediate update
            system_changed = new_system != current_system
            suffix_changed = new_suffix != current_suffix

            if system_changed or suffix_changed:
                if system_changed:
                    ChapterConfigManager.update_numbering_system(context_key, new_system)
                if suffix_changed:
                    self._set_chapter_suffix(context_key, new_suffix)
                    # Update existing chapters with new suffix
                    if current_chapters:
                        updated_chapters = ChapterUtils.update_chapters_with_numbering(
                            current_chapters, new_system, new_suffix
                        )
                        self._set_standalone_chapters(updated_chapters)

                current_system = new_system
                current_suffix = new_suffix
                # Force rerun to update UI
                st.rerun()

        # Handle count change
        if target_count != current_count:
            current_chapters = ChapterConfigManager.update_chapter_count(
                context_key, target_count, current_chapters, current_system, current_suffix
            )
            st.rerun()

        # Render chapter details
        if target_count > 0:
            self._render_chapter_details(context_key, current_chapters, config, is_standalone=True)

            # Action buttons
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🏗️ Create Standalone Chapters", key="create_standalone_chapters"):
                    self._create_standalone_chapters(config, current_chapters)

            with col2:
                if self._has_chapters_created() and any(current_chapters):
                    if st.button("🔄 Update Standalone Chapters", key="update_standalone_chapters"):
                        self._update_existing_standalone_chapters(config, current_chapters)

    def _render_chapter_details(self, context_key: str, chapters: List[Dict], config: Dict, is_standalone: bool = False):
        """Render chapter details using the operations UI"""
        from .chapter_operations import ChapterOperationsUI
        chapter_ops_ui = ChapterOperationsUI()
        chapter_ops_ui.render_chapter_details_optimized(context_key, chapters, config, is_standalone)

    def _get_chapter_suffix(self, context_key: str) -> str:
        """Get chapter suffix from session"""
        from core.session_manager import SessionManager
        return SessionManager.get_chapter_suffix(context_key)

    def _set_chapter_suffix(self, context_key: str, suffix: str):
        """Set chapter suffix in session"""
        from ..core.session_manager import SessionManager
        SessionManager.set_chapter_suffix(context_key, suffix)

    def _set_standalone_chapters(self, chapters: List[Dict]):
        """Set standalone chapters in session"""
        from ..core.session_manager import SessionManager
        SessionManager.set('standalone_chapters', chapters)

    def _has_chapters_created(self) -> bool:
        """Check if chapters have been created"""
        from ..core.session_manager import SessionManager
        return SessionManager.get('chapters_created', False)

    def _create_standalone_chapters(self, config: Dict, chapters: List[Dict]):
        """Create standalone chapters directly under project root"""
        if not chapters or not any(ch.get('number') or ch.get('name') for ch in chapters):
            st.warning("No standalone chapters configured!")
            return

        try:
            with st.spinner("Creating standalone chapters..."):
                # Use service layer
                created_count = 0
                for chapter in chapters:
                    if chapter.get('number') or chapter.get('name'):
                        if self.chapter_service.create_chapter(config, 'standalone', chapter, is_standalone=True):
                            created_count += 1

                if created_count > 0:
                    self._mark_chapters_created()
                    st.success(f"✅ Created {created_count} standalone chapters!")
                    self._show_created_chapters(chapters)
                else:
                    st.warning("No chapters were created. Please check your configuration.")

        except Exception as e:
            st.error(f"Error creating standalone chapters: {str(e)}")

    def _update_existing_standalone_chapters(self, config: Dict, chapters: List[Dict]):
        """Update existing standalone chapters in backend"""
        try:
            with st.spinner("Updating standalone chapters..."):
                # This would need to be implemented in the service layer
                # For now, just show a message
                st.info("Update functionality will be implemented in the service layer")

        except Exception as e:
            st.error(f"Error updating standalone chapters: {str(e)}")

    def _mark_chapters_created(self):
        """Mark chapters as created in session"""
        from ..core.session_manager import SessionManager
        SessionManager.set('chapters_created', True)

    def _show_created_chapters(self, chapters: List[Dict]):
        """Show created chapters in an expander"""
        with st.expander("📂 View Created Standalone Chapters"):
            for chapter in chapters:
                if chapter.get('number') or chapter.get('name'):
                    st.write(f"📂 Chapter {chapter.get('number', '')} - {chapter.get('name', '')}")