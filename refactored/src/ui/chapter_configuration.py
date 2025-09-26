# src/ui/chapter_configuration.py - Chapter configuration UI components
import streamlit as st
from typing import Dict, List
from ..services.service_factory import service_factory
from ..core.chapter_utils import ChapterConfigManager
from ..core.folder_manager import ChapterManager

class ChapterConfigurationUI:
    """UI components for chapter configuration"""

    def __init__(self):
        self.chapter_service = service_factory.get_chapter_service()

    def render_chapter_configuration(self, config: Dict, existing_parts: List[Dict]):
        """Render chapter configuration interface for custom parts"""

        for part_info in existing_parts:
            part_name = part_info['name']
            with st.expander(f"📖 {part_name} Chapters", expanded=part_info == existing_parts[0] if existing_parts else False):
                self._render_part_chapters_optimized(part_name, config)

        # Create all chapters button
        chapters_config = self._get_chapters_config()
        if any(chapters_config.values()):
            if st.button("🏗️ Create All Chapters", type="primary"):
                self._create_all_chapters(config, chapters_config)

    def _render_part_chapters_optimized(self, part_name: str, config: Dict):
        """Optimized part chapters rendering"""

        context_key = part_name

        # Get current state
        current_chapters = ChapterConfigManager.get_chapters_for_context(context_key)
        current_count = len(current_chapters)
        current_system = ChapterConfigManager.get_current_numbering_system(context_key)
        current_suffix = self._get_chapter_suffix(context_key)

        # Number of chapters input
        target_count = st.number_input(
            f"Number of chapters in {part_name}",
            min_value=0,
            value=current_count,
            step=1,
            key=f"chapters_count_{part_name}",
            help="Enter any number of chapters (no limit)"
        )

        # Numbering system selector with suffix
        if target_count > 0:
            new_system, new_suffix = self._render_numbering_system_selector(
                f"part_{context_key}",
                current_system,
                f"Choose how chapters should be numbered for {part_name}",
                current_suffix
            )

            # Handle system or suffix change
            system_changed = new_system != current_system
            suffix_changed = new_suffix != current_suffix

            if system_changed or suffix_changed:
                if system_changed:
                    ChapterConfigManager.update_numbering_system(context_key, new_system)
                if suffix_changed:
                    self._set_chapter_suffix(context_key, new_suffix)
                    # Update existing chapters with new suffix
                    if current_chapters:
                        updated_chapters = self._update_chapters_with_numbering(
                            current_chapters, new_system, new_suffix
                        )
                        chapters_config = self._get_chapters_config()
                        chapters_config[context_key] = updated_chapters
                        self._set_chapters_config(chapters_config)

                st.rerun()

        # Handle count change
        if target_count != current_count:
            current_chapters = ChapterConfigManager.update_chapter_count(
                context_key, target_count, current_chapters, current_system, current_suffix
            )
            st.rerun()

        # Render chapter details
        if target_count > 0:
            self._render_chapter_details(context_key, current_chapters, config, is_standalone=False)

            # Action buttons
            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"🏗️ Create {part_name} Chapters", key=f"create_part_{part_name}"):
                    self._create_chapters_for_custom_part(config, part_name, current_chapters)

            with col2:
                if self._has_chapters_created() and any(current_chapters):
                    if st.button(f"🔄 Update {part_name} Chapters", key=f"update_part_{part_name}"):
                        self._update_existing_chapters_for_part(config, part_name, current_chapters)

    def _render_numbering_system_selector(self, context_key: str, current_system: str,
                                         help_text: str, current_suffix: str):
        """Render numbering system selector"""
        from ..core.chapter_utils import ChapterUtils
        return ChapterUtils.render_numbering_system_selector(
            context_key, current_system, help_text, current_suffix
        )

    def _render_chapter_details(self, context_key: str, chapters: List[Dict], config: Dict, is_standalone: bool = False):
        """Render chapter details using the operations UI"""
        from .chapter_operations import ChapterOperationsUI
        chapter_ops_ui = ChapterOperationsUI()
        chapter_ops_ui.render_chapter_details_optimized(context_key, chapters, config, is_standalone)

    def _get_chapter_suffix(self, context_key: str) -> str:
        """Get chapter suffix from session"""
        from ..core.session_manager import SessionManager
        return SessionManager.get_chapter_suffix(context_key)

    def _set_chapter_suffix(self, context_key: str, suffix: str):
        """Set chapter suffix in session"""
        from ..core.session_manager import SessionManager
        SessionManager.set_chapter_suffix(context_key, suffix)

    def _update_chapters_with_numbering(self, chapters: List[Dict], system: str, suffix: str) -> List[Dict]:
        """Update chapters with numbering"""
        from ..core.chapter_utils import ChapterUtils
        return ChapterUtils.update_chapters_with_numbering(chapters, system, suffix)

    def _get_chapters_config(self) -> Dict:
        """Get chapters config from session"""
        from ..core.session_manager import SessionManager
        return SessionManager.get('chapters_config', {})

    def _set_chapters_config(self, config: Dict):
        """Set chapters config in session"""
        from ..core.session_manager import SessionManager
        SessionManager.set('chapters_config', config)

    def _has_chapters_created(self) -> bool:
        """Check if chapters have been created"""
        from ..core.session_manager import SessionManager
        return SessionManager.get('chapters_created', False)

    def _create_chapters_for_custom_part(self, config: Dict, part_name: str, chapters: List[Dict]):
        """Create chapters for a specific custom part only"""
        if not chapters or not any(ch.get('number') or ch.get('name') for ch in chapters):
            st.warning(f"No chapters configured for {part_name}!")
            return

        try:
            with st.spinner(f"Creating chapters for {part_name}..."):
                # Use service layer
                created_count = 0
                for chapter in chapters:
                    if chapter.get('number') or chapter.get('name'):
                        if self.chapter_service.create_chapter(config, part_name, chapter, is_standalone=False):
                            created_count += 1

                if created_count > 0:
                    self._mark_chapters_created()
                    st.success(f"✅ Created {created_count} chapters for {part_name}!")
                    self._show_created_chapters(part_name, chapters)
                else:
                    st.warning("No chapters were created. Please check your configuration.")

        except Exception as e:
            st.error(f"Error creating chapters for {part_name}: {str(e)}")

    def _update_existing_chapters_for_part(self, config: Dict, part_name: str, chapters: List[Dict]):
        """Update existing chapters for a specific custom part"""
        try:
            with st.spinner(f"Updating chapters for {part_name}..."):
                # This would need to be implemented in the service layer
                # For now, just show a message
                st.info("Update functionality will be implemented in the service layer")

        except Exception as e:
            st.error(f"Error updating chapters for {part_name}: {str(e)}")

    def _mark_chapters_created(self):
        """Mark chapters as created in session"""
        from ..core.session_manager import SessionManager
        SessionManager.set('chapters_created', True)

    def _show_created_chapters(self, part_name: str, chapters: List[Dict]):
        """Show created chapters in an expander"""
        with st.expander(f"📂 View Created Chapters for {part_name}"):
            for chapter in chapters:
                if chapter.get('number') or chapter.get('name'):
                    st.write(f"📂 Chapter {chapter.get('number', '')} - {chapter.get('name', '')}")

    def render_chapter_preview(self, config: Dict):
        """Render chapter structure preview"""
        st.subheader("📋 Structure Preview")

        chapters_config = self._get_chapters_config()
        standalone_chapters = self._get_standalone_chapters()

        if not any(chapters_config.values()) and not standalone_chapters:
            st.info("Configure chapters to see preview")
            return

        safe_code = config['code']
        book_name = config['book_name']
        base_name = f"{safe_code}_{book_name}"

        # Show standalone chapters first
        if standalone_chapters:
            st.markdown("**Standalone Chapters:**")
            preview_chapters = ChapterManager.get_chapters_preview(
                base_name, "standalone", standalone_chapters, is_standalone=True
            )

            for chapter_folder in preview_chapters:
                st.write(f"📖 {chapter_folder}")

            st.markdown("---")

        # Show part chapters
        for part_name, chapters in chapters_config.items():
            if chapters:
                st.markdown(f"**{part_name}:**")

                preview_chapters = ChapterManager.get_chapters_preview(
                    base_name, part_name, chapters, is_custom_part=True
                )

                for chapter_folder in preview_chapters:
                    st.write(f"📂 {chapter_folder}")

                st.markdown("---")

    def _get_standalone_chapters(self) -> List[Dict]:
        """Get standalone chapters from session"""
        from ..core.session_manager import SessionManager
        return SessionManager.get('standalone_chapters', [])

    def _create_all_chapters(self, config: Dict, chapters_config: Dict):
        """Create all configured chapters with unique IDs and metadata tracking"""

        if not any(chapters_config.values()):
            st.warning("No chapters configured!")
            return

        try:
            with st.spinner("Creating chapter folders..."):
                all_created_chapters = []

                for part_name, chapters in chapters_config.items():
                    if chapters and any(ch.get('number') or ch.get('name') for ch in chapters):
                        # Use service layer
                        for chapter in chapters:
                            if chapter.get('number') or chapter.get('name'):
                                if self.chapter_service.create_chapter(config, part_name, chapter, is_standalone=False):
                                    all_created_chapters.append(chapter)

                if all_created_chapters:
                    self._mark_chapters_created()
                    st.success(f"✅ Created {len(all_created_chapters)} chapter folders successfully!")

                    # Show created chapters
                    with st.expander("📂 View Created Chapters"):
                        for chapter in all_created_chapters:
                            st.write(f"📂 Chapter {chapter.get('number', '')} - {chapter.get('name', '')}")
                else:
                    st.warning("No chapter folders created. Please configure chapters first.")

        except Exception as e:
            st.error(f"Error creating chapters: {str(e)}")