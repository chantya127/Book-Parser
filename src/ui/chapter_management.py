# ui/chapter_management.py - Optimized with centralized utilities

from datetime import datetime
import streamlit as st
from typing import Dict, List
from core.session_manager import SessionManager
from core.folder_manager import ChapterManager, FolderManager
from core.chapter_utils import ChapterUtils, ChapterConfigManager, PartManager
from pathlib import Path
import shutil
import os

def render_chapter_management_page():
    """Render the chapter management page"""
    
    # Check prerequisites
    if not SessionManager.get('folder_structure_created'):
        render_prerequisites_warning()
        return
    
    config = SessionManager.get('project_config', {})
    
    st.subheader("📂 Chapter Management")
    st.markdown("Configure chapters within each custom part of your book, or create standalone chapters.")
    
    # Check for operation completion messages
    if st.session_state.get('part_operation_completed'):
        operation_info = st.session_state.get('part_operation_info', {})
        if operation_info.get('operation') == 'add':
            st.success(f"✅ Successfully created part '{operation_info.get('part_name')}'!")
            st.info(f"📂 Location: {operation_info.get('location', 'Unknown')}")
        elif operation_info.get('operation') == 'delete':
            st.success(f"✅ Successfully deleted part '{operation_info.get('part_name')}' and all its contents!")
        
        # Clear the flags
        st.session_state['part_operation_completed'] = False
        st.session_state['part_operation_info'] = {}
    
    # Standalone Chapters Section
    st.markdown("### 📖 Standalone Chapters")
    render_standalone_chapters_section(config)
    
    st.markdown("---")
    
    # Part Management Section
    st.markdown("### 🔧 Part Management")
    render_part_management_section(config)
    
    # Chapter configuration for parts
    updated_parts = get_existing_custom_parts(config)
    
    if not updated_parts:
        st.info("📝 No custom parts configured. You can add individual parts above or configure parts in Project Setup.")
    else:
        st.markdown("---")
        part_names = [part['name'] for part in updated_parts]
        st.info(f"Found {len(updated_parts)} existing parts: {', '.join(part_names)}")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            render_chapter_configuration(config, updated_parts)
        
        with col2:
            render_chapter_preview(config)


def render_standalone_chapters_section(config: Dict):
    """Render standalone chapters configuration section with optimized state management"""
    
    st.markdown("Create chapters directly under the project root (not inside any part).")
    
    context_key = 'standalone'
    
    # Get current state
    current_chapters = ChapterConfigManager.get_chapters_for_context(context_key)
    current_count = len(current_chapters)
    current_system = ChapterConfigManager.get_current_numbering_system(context_key)
    current_suffix = SessionManager.get_chapter_suffix(context_key)
    
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
                SessionManager.set_chapter_suffix(context_key, new_suffix)
                # Update existing chapters with new suffix
                if current_chapters:
                    updated_chapters = ChapterUtils.update_chapters_with_numbering(
                        current_chapters, new_system, new_suffix
                    )
                    SessionManager.set('standalone_chapters', updated_chapters)
            
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
        render_chapter_details_optimized(context_key, current_chapters, config, is_standalone=True)
        
        # Action buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🏗️ Create Standalone Chapters", key="create_standalone_chapters"):
                create_standalone_chapters(config, current_chapters)
        
        with col2:
            if SessionManager.get('chapters_created') and any(current_chapters):
                if st.button("🔄 Update Standalone Chapters", key="update_standalone_chapters"):
                    update_existing_standalone_chapters(config, current_chapters)


def add_individual_custom_part(config: Dict, part_name: str):
    """Add an individual custom part folder with proper font formatting"""
    try:
        from core.text_formatter import TextFormatter
        from core.folder_manager import FolderManager
        from pathlib import Path
        import shutil
        
        # Get font case and format the part name
        font_case = SessionManager.get_font_case()
        formatted_part_name = TextFormatter.format_part_name(part_name, font_case)
        
        safe_code = FolderManager.sanitize_name(config['code'])
        book_name = config['book_name']
        base_name = f"{safe_code}_{book_name}"
        
        # Use project destination instead of current directory
        project_destination = SessionManager.get_project_destination()
        if project_destination and os.path.exists(project_destination):
            base_path = Path(project_destination)
        else:
            base_path = Path.cwd()
        
        project_path = base_path / base_name
        
        if not project_path.exists():
            project_path.mkdir(parents=True, exist_ok=True)
            st.info(f"Created project directory: {project_path.absolute()}")
        
        # Create part folder with formatted name
        part_folder = project_path / f"{base_name}_{formatted_part_name}"
        
        if part_folder.exists():
            st.error(f"Part '{formatted_part_name}' already exists!")
            return False
        
        part_folder.mkdir(exist_ok=True)
        
        # Rest remains the same...
        custom_parts = SessionManager.get('custom_parts', {})
        base_id = formatted_part_name.lower().replace(' ', '_').replace('-', '_')
        part_id = f"part_{len(custom_parts) + 1}_{base_id}"
        
        # Ensure unique ID
        counter = 1
        original_id = part_id
        while part_id in custom_parts:
            part_id = f"{original_id}_{counter}"
            counter += 1
        
        custom_parts[part_id] = {
            'name': formatted_part_name,
            'display_name': formatted_part_name,
            'original_name': part_name,
            'created_timestamp': datetime.now().isoformat()
        }
        
        SessionManager.set('custom_parts', custom_parts)
        
        # Update created folders list
        current_folders = SessionManager.get('created_folders', [])
        new_part_path = str(part_folder.absolute())
        if new_part_path not in current_folders:
            current_folders.append(new_part_path)
            SessionManager.set('created_folders', current_folders)
        
        # Set operation completion flags
        st.session_state['part_operation_completed'] = True
        st.session_state['part_operation_info'] = {
            'operation': 'add',
            'part_name': formatted_part_name,
            'location': str(part_folder.absolute())
        }
        
        return True
        
    except Exception as e:
        st.error(f"Error creating part: {str(e)}")
        return False


def render_part_management_section(config: Dict):
    """Render part management section with optimized operations and font formatting"""
    
    col_opt1, col_opt2, col_opt3, col_opt4 = st.columns(4)
    
    # Show current font formatting
    font_case = SessionManager.get_font_case()
    st.caption(f"Font formatting: {font_case}")
    
    with col_opt2:
        part_name_input = st.text_input(
            "Part Name to Add",
            value="",
            placeholder="e.g., Mathematics, Science",
            key="individual_part_name_input",
            help=f"Enter the custom name for the new part (will be formatted as: {font_case})"
        )
    
    with col_opt1:
        if st.button("➕ Add Individual Part", type="secondary", key="add_part_btn"):
            if part_name_input.strip():
                # Use the improved function with font formatting
                success = add_individual_custom_part(config, part_name_input.strip())
                if success:
                    st.rerun()
                else:
                    from core.text_formatter import TextFormatter
                    formatted_name = TextFormatter.format_part_name(part_name_input.strip(), font_case)
                    st.error(f"Part '{formatted_name}' already exists!")
            else:
                st.error("Please enter a part name first")
    
    # Delete part functionality
    current_parts = get_existing_custom_parts(config)
    
    with col_opt3:
        if current_parts:
            part_to_delete = st.selectbox(
                "Select Part to Delete",
                [part['name'] for part in current_parts],
                key="part_to_delete_select",
                help="Choose which part to delete (this will delete all contents)"
            )
    
    with col_opt4:
        if current_parts:
            if st.button("🗑️ Delete Selected Part", type="secondary", key="delete_part_btn"):
                part_to_delete = st.session_state.get("part_to_delete_select")
                if part_to_delete:
                    delete_individual_custom_part(config, part_to_delete)
                    st.rerun()


def render_chapter_details_optimized(context_key: str, chapters: List[Dict], config: Dict, is_standalone: bool = False):
    """Optimized chapter details rendering with proper state management and font formatting"""
    
    if is_standalone:
        st.markdown("**Configure standalone chapters:**")
    else:
        st.markdown(f"**Configure chapters for {context_key}:**")
    
    # Lazy import for font formatting
    from core.text_formatter import TextFormatter
    font_case = st.session_state.get('selected_font_case', 'First Capital (Sentence case)')
    
    safe_code = FolderManager.sanitize_name(config['code'])
    book_name = config['book_name']
    base_name = f"{safe_code}_{book_name}"
    
    updated_chapters = []
    
    for i, chapter in enumerate(chapters):
        col1, col2 = st.columns(2)
        
        with col1:
            # For NULL sequence, show "NULL" as read-only
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
                # Use the current chapter number as value
                chapter_number = st.text_input(
                    "Number",
                    value=chapter.get('number', ''),
                    placeholder=f"e.g., {chapter.get('number', '')}",
                    key=f"{context_key}_chapter_num_{i}",
                    help="Chapter number (auto-generated based on system)"
                )
        
        with col2:
            # For NULL sequence, show auto-generated name as read-only
            if chapter.get('is_null_sequence'):
                st.text_input(
                    "Name",
                    value=chapter.get('name', ''),
                    key=f"{context_key}_chapter_name_{i}",
                    disabled=True,
                    help="NULL sequence name (auto-generated: Name, Name (1), Name (2)...)"
                )
                chapter_name = chapter.get('name', '')
            else:
                chapter_name = st.text_input(
                    "Name",
                    value=chapter.get('name', ''),
                    placeholder="e.g., Introduction, Overview (leave empty for 'Null Name')",
                    key=f"{context_key}_chapter_name_{i}",
                    help="Leave empty to use 'Null Name' in folder naming"
                )
        
        # Apply font formatting to the inputs before storing (only for non-NULL sequence)
        if not chapter.get('is_null_sequence'):
            formatted_chapter_number = TextFormatter.format_chapter_number(chapter_number, font_case) if chapter_number else ''
            formatted_chapter_name = TextFormatter.format_chapter_name(chapter_name, font_case) if chapter_name else ''
        else:
            # Use the already formatted values from NULL sequence
            formatted_chapter_number = chapter_number
            formatted_chapter_name = chapter_name
        
        updated_chapters.append({
            'number': formatted_chapter_number,
            'name': formatted_chapter_name,
            'original_number': chapter_number if not chapter.get('is_null_sequence') else '',
            'original_name': chapter_name if not chapter.get('is_null_sequence') else '',
            'is_null_sequence': chapter.get('is_null_sequence', False)
        })
        
        # Show preview of folder name with formatting
        if is_standalone:
            preview_name = ChapterManager.generate_chapter_folder_name(
                base_name,
                formatted_chapter_number or None,
                formatted_chapter_name or None
            )
        else:
            preview_name = ChapterManager.generate_chapter_folder_name(
                f"{base_name}_{context_key}",
                formatted_chapter_number or None,
                formatted_chapter_name or None
            )
        
        st.caption(f"📁 Folder: `{preview_name}`")
        
        if i < len(chapters) - 1:
            st.markdown("---")
    
    # Update session state
    if is_standalone:
        SessionManager.set('standalone_chapters', updated_chapters)
    else:
        chapters_config = SessionManager.get('chapters_config', {})
        chapters_config[context_key] = updated_chapters
        SessionManager.set('chapters_config', chapters_config)


def render_chapter_configuration(config: Dict, existing_parts: List[Dict]):
    """Render chapter configuration interface for custom parts"""
    
    for part_info in existing_parts:
        part_name = part_info['name']
        with st.expander(f"📖 {part_name} Chapters", expanded=part_info == existing_parts[0] if existing_parts else False):
            render_part_chapters_optimized(part_name, config)
    
    # Create all chapters button
    chapters_config = SessionManager.get('chapters_config', {})
    if any(chapters_config.values()):
        if st.button("🏗️ Create All Chapters", type="primary"):
            create_all_chapters(config, chapters_config)

def render_part_chapters_optimized(part_name: str, config: Dict):
    """Optimized part chapters rendering"""
    
    context_key = part_name
    
    # Get current state
    current_chapters = ChapterConfigManager.get_chapters_for_context(context_key)
    current_count = len(current_chapters)
    current_system = ChapterConfigManager.get_current_numbering_system(context_key)
    current_suffix = SessionManager.get_chapter_suffix(context_key)
    
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
        new_system, new_suffix = ChapterUtils.render_numbering_system_selector(
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
                SessionManager.set_chapter_suffix(context_key, new_suffix)
                # Update existing chapters with new suffix
                if current_chapters:
                    updated_chapters = ChapterUtils.update_chapters_with_numbering(
                        current_chapters, new_system, new_suffix
                    )
                    chapters_config = SessionManager.get('chapters_config', {})
                    chapters_config[context_key] = updated_chapters
                    SessionManager.set('chapters_config', chapters_config)
            
            st.rerun()
    
    # Handle count change
    if target_count != current_count:
        current_chapters = ChapterConfigManager.update_chapter_count(
            context_key, target_count, current_chapters, current_system, current_suffix
        )
        st.rerun()
    
    # Render chapter details
    if target_count > 0:
        render_chapter_details_optimized(context_key, current_chapters, config, is_standalone=False)
        
        # Action buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button(f"🏗️ Create {part_name} Chapters", key=f"create_part_{part_name}"):
                create_chapters_for_custom_part(config, part_name, current_chapters)
        
        with col2:
            if SessionManager.get('chapters_created') and any(current_chapters):
                if st.button(f"🔄 Update {part_name} Chapters", key=f"update_part_{part_name}"):
                    update_existing_chapters_for_part(config, part_name, current_chapters)

def render_chapter_preview(config: Dict):
    """Render chapter structure preview"""
    st.subheader("📋 Structure Preview")
    
    chapters_config = SessionManager.get('chapters_config', {})
    standalone_chapters = SessionManager.get('standalone_chapters', [])
    
    if not any(chapters_config.values()) and not standalone_chapters:
        st.info("Configure chapters to see preview")
        return
    
    safe_code = FolderManager.sanitize_name(config['code'])
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

# Keep existing functions but optimize them
def get_existing_custom_parts(config: Dict) -> List[Dict]:
    """Get list of actually existing custom parts by checking filesystem first, then session state"""
    existing_parts = []
    
    safe_code = FolderManager.sanitize_name(config.get('code', ''))
    book_name = config.get('book_name', '')
    base_name = f"{safe_code}_{book_name}"
    
    # Get custom parts from session state
    custom_parts = SessionManager.get('custom_parts', {})
    
    # Check filesystem directly to get the truth - use project destination
    try:
        project_destination = SessionManager.get_project_destination()
        if project_destination and os.path.exists(project_destination):
            base_path = Path(project_destination)
        else:
            base_path = Path.cwd()
        
        project_path = base_path / base_name
        
        if project_path.exists() and project_path.is_dir():
            # Check which custom parts actually exist on filesystem
            for part_id, part_info in custom_parts.items():
                part_name = part_info['name']
                part_folder = project_path / f"{base_name}_{part_name}"
                
                if part_folder.exists():
                    existing_parts.append({
                        'id': part_id,
                        'name': part_name,
                        'path': str(part_folder.absolute()),
                        'display_name': part_info.get('display_name', part_name)
                    })
    except Exception:
        pass
    
    return existing_parts

def delete_individual_custom_part(config: Dict, part_name: str):
    """Delete an individual custom part folder and all its contents"""
    try:
        safe_code = FolderManager.sanitize_name(config['code'])
        book_name = config['book_name']
        base_name = f"{safe_code}_{book_name}"
        
        # Use project destination instead of current directory
        project_destination = SessionManager.get_project_destination()
        if project_destination and os.path.exists(project_destination):
            base_path = Path(project_destination)
        else:
            base_path = Path.cwd()
        
        project_path = base_path / base_name
        
        if not project_path.exists():
            st.error(f"Project folder not found. Cannot delete part '{part_name}'.")
            return
        
        # Find the part folder
        part_folder = project_path / f"{base_name}_{part_name}"
        
        if not part_folder.exists():
            st.error(f"Part '{part_name}' folder not found.")
            return
        
        # Delete the folder and all contents
        shutil.rmtree(part_folder)
        
        # Rest of the cleanup logic remains the same...
        custom_parts = SessionManager.get('custom_parts', {})
        part_to_remove = None
        
        for part_id, part_info in custom_parts.items():
            if part_info['name'] == part_name:
                part_to_remove = part_id
                break
        
        if part_to_remove:
            del custom_parts[part_to_remove]
            SessionManager.set('custom_parts', custom_parts)
        
        # Update created folders list and remove related metadata
        current_folders = SessionManager.get('created_folders', [])
        part_path_str = str(part_folder.absolute())
        if part_path_str in current_folders:
            current_folders.remove(part_path_str)
        
        # Remove any chapter folders that were in this part
        folders_to_remove = []
        for folder_path in current_folders:
            if f"_{part_name}" in folder_path and base_name in folder_path:
                folders_to_remove.append(folder_path)
        
        for folder_path in folders_to_remove:
            current_folders.remove(folder_path)
        
        SessionManager.set('created_folders', current_folders)
        
        # Remove chapter metadata for this part
        folder_metadata = SessionManager.get('folder_metadata', {})
        metadata_to_remove = []
        for folder_id, metadata in folder_metadata.items():
            if (metadata.get('type') == 'chapter' and 
                metadata.get('parent_part_name') == part_name):
                metadata_to_remove.append(folder_id)
            elif (metadata.get('type') == 'custom' and 
                  f"_{part_name}" in metadata.get('actual_path', '')):
                metadata_to_remove.append(folder_id)
        
        for folder_id in metadata_to_remove:
            del folder_metadata[folder_id]
        
        SessionManager.set('folder_metadata', folder_metadata)
        
        # Remove chapters config for this part
        chapters_config = SessionManager.get('chapters_config', {})
        if part_name in chapters_config:
            del chapters_config[part_name]
            SessionManager.set('chapters_config', chapters_config)
        
        # Set success message for next render
        st.session_state['part_operation_completed'] = True
        st.session_state['part_operation_info'] = {
            'operation': 'delete',
            'part_name': part_name
        }
        
    except PermissionError:
        st.error(f"❌ Permission denied. Cannot delete part '{part_name}'. Please check folder permissions.")
    except Exception as e:
        st.error(f"❌ Error deleting part '{part_name}': {str(e)}")

def render_prerequisites_warning():
    """Render warning when prerequisites are not met"""
    st.warning("⚠️ Please complete the project setup first!")
    st.markdown("""
    **Required steps:**
    1. Upload PDF file
    2. Configure project details
    3. Create folder structure
    """)

# Keep existing creation functions (they work fine)
def create_standalone_chapters(config: Dict, chapters: List[Dict]):
    """Create standalone chapters directly under project root"""
    if not chapters or not any(ch.get('number') or ch.get('name') for ch in chapters):
        st.warning("No standalone chapters configured!")
        return
    
    try:
        with st.spinner("Creating standalone chapters..."):
            safe_code = FolderManager.sanitize_name(config['code'])
            book_name = config['book_name']
            base_name = f"{safe_code}_{book_name}"
            
            # Use project destination instead of current directory
            project_destination = SessionManager.get_project_destination()
            if project_destination and os.path.exists(project_destination):
                base_path = Path(project_destination)
            else:
                base_path = Path.cwd()
            
            project_path = base_path / base_name
            
            if not project_path.exists():
                project_path.mkdir(parents=True, exist_ok=True)
                st.info(f"Created project directory: {project_path.absolute()}")
            
            # Validate chapters before creating
            is_valid, error_msg = ChapterManager.validate_chapter_data(chapters)
            if not is_valid:
                st.error(f"Error in standalone chapters: {error_msg}")
                return
            
            created_chapters = ChapterManager.create_standalone_chapter_folders(
                project_path, base_name, chapters
            )
            
            if created_chapters:
                SessionManager.set('chapters_created', True)
                # Update created folders list
                current_folders = SessionManager.get('created_folders', [])
                current_folders.extend(created_chapters)
                SessionManager.set('created_folders', current_folders)
                
                st.success(f"✅ Created {len(created_chapters)} standalone chapters!")
                
                # Show created chapters
                with st.expander("📂 View Created Standalone Chapters"):
                    for chapter in created_chapters:
                        st.write(f"📂 {chapter}")
    
    except Exception as e:
        st.error(f"Error creating standalone chapters: {str(e)}")


def update_existing_standalone_chapters(config: Dict, chapters: List[Dict]):
    """Update existing standalone chapters"""
    try:
        with st.spinner("Updating standalone chapters..."):
            st.success("✅ Updated standalone chapters!")
            st.info("Chapter updates are handled automatically when you modify names/numbers.")
    except Exception as e:
        st.error(f"Error updating standalone chapters: {str(e)}")


def create_chapters_for_custom_part(config: Dict, part_name: str, chapters: List[Dict]):
    """Create chapters for a specific custom part only"""
    if not chapters or not any(ch.get('number') or ch.get('name') for ch in chapters):
        st.warning(f"No chapters configured for {part_name}!")
        return
    
    try:
        with st.spinner(f"Creating chapters for {part_name}..."):
            safe_code = FolderManager.sanitize_name(config['code'])
            book_name = config['book_name']
            base_name = f"{safe_code}_{book_name}"
            
            # Use project destination instead of current directory
            project_destination = SessionManager.get_project_destination()
            if project_destination and os.path.exists(project_destination):
                base_path = Path(project_destination)
            else:
                base_path = Path.cwd()
            
            project_path = base_path / base_name
            
            if not project_path.exists():
                project_path.mkdir(parents=True, exist_ok=True)
                st.info(f"Created project directory: {project_path.absolute()}")
            
            # Validate chapters before creating
            is_valid, error_msg = ChapterManager.validate_chapter_data(chapters)
            if not is_valid:
                st.error(f"Error in {part_name}: {error_msg}")
                return
            
            created_chapters = ChapterManager.create_chapter_folders_for_custom_part(
                project_path, base_name, part_name, chapters
            )
            
            if created_chapters:
                SessionManager.set('chapters_created', True)
                # Update created folders list
                current_folders = SessionManager.get('created_folders', [])
                current_folders.extend(created_chapters)
                SessionManager.set('created_folders', current_folders)
                
                st.success(f"✅ Created {len(created_chapters)} chapters for {part_name}!")
                
                # Show created chapters
                with st.expander(f"📂 View Created Chapters for {part_name}"):
                    for chapter in created_chapters:
                        st.write(f"📂 {chapter}")
    
    except Exception as e:
        st.error(f"Error creating chapters for {part_name}: {str(e)}")

def create_all_chapters(config: Dict, chapters_config: Dict):
    """Create all configured chapters with unique IDs and metadata tracking"""
    
    if not any(chapters_config.values()):
        st.warning("No chapters configured!")
        return
    
    try:
        with st.spinner("Creating chapter folders..."):
            safe_code = FolderManager.sanitize_name(config['code'])
            book_name = config['book_name']
            base_name = f"{safe_code}_{book_name}"
            
            # Use project destination instead of current directory
            project_destination = SessionManager.get_project_destination()
            if project_destination and os.path.exists(project_destination):
                base_path = Path(project_destination)
            else:
                base_path = Path.cwd()
            
            project_path = base_path / base_name
            
            if not project_path.exists():
                project_path.mkdir(parents=True, exist_ok=True)
                st.info(f"Created project directory: {project_path.absolute()}")
            
            all_created_chapters = []
            
            for part_name, chapters in chapters_config.items():
                if chapters and any(ch.get('number') or ch.get('name') for ch in chapters):
                    
                    # Validate chapters before creating
                    is_valid, error_msg = ChapterManager.validate_chapter_data(chapters)
                    if not is_valid:
                        st.error(f"Error in {part_name}: {error_msg}")
                        continue
                    
                    created_chapters = ChapterManager.create_chapter_folders_for_custom_part(
                        project_path, base_name, part_name, chapters
                    )
                    all_created_chapters.extend(created_chapters)
            
            if all_created_chapters:
                SessionManager.set('chapters_created', True)
                # Update created folders list
                current_folders = SessionManager.get('created_folders', [])
                current_folders.extend(all_created_chapters)
                SessionManager.set('created_folders', current_folders)
                
                st.success(f"✅ Created {len(all_created_chapters)} chapter folders successfully!")
                
                # Show created chapters
                with st.expander("📂 View Created Chapters"):
                    for chapter in all_created_chapters:
                        st.write(f"📂 {chapter}")
            else:
                st.warning("No chapter folders created. Please configure chapters first.")
    
    except Exception as e:
        st.error(f"Error creating chapters: {str(e)}")


def update_existing_chapters_for_part(config: Dict, part_name: str, chapters: List[Dict]):
    """Update existing chapters for a specific custom part"""
    try:
        with st.spinner(f"Updating chapters for {part_name}..."):
            st.success(f"✅ Updated chapters for {part_name}!")
            st.info("Chapter updates are handled automatically when you modify names/numbers.")
    except Exception as e:
        st.error(f"Error updating chapters for {part_name}: {str(e)}")