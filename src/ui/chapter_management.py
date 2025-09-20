import streamlit as st
from typing import Dict, List
from core.session_manager import SessionManager
from core.folder_manager import ChapterManager, FolderManager
from pathlib import Path

def render_chapter_management_page():
    """Render the chapter management page"""
    
    # Check prerequisites
    if not SessionManager.get('folder_structure_created'):
        render_prerequisites_warning()
        return
    
    config = SessionManager.get('project_config', {})
    num_parts = config.get('num_parts', 0)
    
    if num_parts == 0:
        st.info("📝 No parts configured. Chapters are only needed when you have parts defined.")
        return
    
    st.subheader("📂 Chapter Management")
    st.markdown("Configure chapters within each part of your book.")
    
    # Chapter configuration for each part
    col1, col2 = st.columns([2, 1])
    
    with col1:
        render_chapter_configuration(config, num_parts)
    
    with col2:
        render_chapter_preview(config)

def render_prerequisites_warning():
    """Render warning when prerequisites are not met"""
    st.warning("⚠️ Please complete the project setup first!")
    st.markdown("""
    **Required steps:**
    1. Upload PDF file
    2. Configure project details
    3. Create folder structure
    """)

def render_chapter_configuration(config: Dict, num_parts: int):
    """Render chapter configuration interface"""
    
    chapters_config = SessionManager.get('chapters_config', {})
    
    for part_num in range(1, num_parts + 1):
        with st.expander(f"📖 Part {part_num} Chapters", expanded=part_num == 1):
            render_part_chapters(part_num, chapters_config, config)
    
    # Create chapters button
    if any(chapters_config.values()):  # Only show if chapters are configured
        if st.button("🏗️ Create All Chapters", type="primary"):
            create_all_chapters(config, chapters_config)


def get_chapter_number_format(part_num: int, chapter_index: int) -> str:
    """Get formatted chapter number based on numbering system"""
    numbering_config = SessionManager.get('numbering_systems', {})
    part_key = f"Part_{part_num}"
    numbering_system = numbering_config.get(part_key, "Numbers (1, 2, 3...)")
    
    chapter_num = chapter_index + 1  # Convert 0-based index to 1-based
    
    if numbering_system == "Words (One, Two, Three...)":
        word_numbers = ["One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine", "Ten",
                       "Eleven", "Twelve", "Thirteen", "Fourteen", "Fifteen", "Sixteen", "Seventeen", 
                       "Eighteen", "Nineteen", "Twenty", "Twenty-One", "Twenty-Two", "Twenty-Three",
                       "Twenty-Four", "Twenty-Five", "Twenty-Six", "Twenty-Seven", "Twenty-Eight",
                       "Twenty-Nine", "Thirty", "Thirty-One", "Thirty-Two", "Thirty-Three", "Thirty-Four",
                       "Thirty-Five", "Thirty-Six", "Thirty-Seven", "Thirty-Eight", "Thirty-Nine", "Fourty",
                       "Fourty-One", "Fourty-Two", "Fourty-Three", "Fourty-Four", "Fourty-Five", "Fourty-Six",
                       "Fourty-Seven", "Fourty-Eight", "Fourty-Nine", "Fifty", "Fifty-One", "Fifty-Two", "Fifty-Three",]
        # FIXED: Removed limit - if beyond predefined words, use numbers
        return word_numbers[chapter_num - 1] if chapter_num <= len(word_numbers) else str(chapter_num)
    
    elif numbering_system == "Roman (I, II, III...)":
        roman_numerals = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X",
                         "XI", "XII", "XIII", "XIV", "XV", "XVI", "XVII", "XVIII", "XIX", "XX",
                         "XXI", "XXII", "XXIII", "XXIV", "XXV", "XXVI", "XXVII", "XXVIII", "XXIX", "XXX",
                         "XXXI", "XXXII", "XXXIII", "XXXIV", "XXXV", "XXXVI", "XXXVII", "XXXVIII", "XXXIX", "XL",
                         "XLI", "XLII", "XLIII", "XLIV", "XLV", "XLVI", "XLVII", "XLVIII", "XLIX", "L",]
        # FIXED: Removed limit - if beyond predefined romans, use numbers
        return roman_numerals[chapter_num - 1] if chapter_num <= len(roman_numerals) else str(chapter_num)
    
    elif numbering_system == "Null (null_1, null_2...)":
        return f"null_{chapter_num}"  # Format: null_1, null_2, etc.
    
    else:  # Default to numbers - NO LIMIT
        return str(chapter_num)


def render_part_chapters(part_num: int, chapters_config: Dict, config: Dict):
    """Render chapter configuration for a specific part"""
    
    part_key = f"Part_{part_num}"
    part_chapters = chapters_config.get(part_key, [])
    
    # Number of chapters input - FIXED: Removed upper limit
    current_count = len(part_chapters)
    num_chapters = st.number_input(
        f"Number of chapters in Part {part_num}",
        min_value=0,
        value=current_count,
        step=1,
        key=f"chapters_count_{part_num}",
        help="Enter any number of chapters (no limit)"
    )
    
    # Chapter numbering system selection
    if num_chapters > 0:
        # Get current numbering system
        numbering_config = SessionManager.get('numbering_systems', {})
        current_system = numbering_config.get(part_key, "Numbers (1, 2, 3...)")
        
        numbering_options = [
            "Numbers (1, 2, 3...)", 
            "Words (One, Two, Three...)", 
            "Roman (I, II, III...)",
            "Null (null_1, null_2...)"  # Null option
        ]
        
        numbering_system = st.selectbox(
            f"Chapter Numbering System for Part {part_num}",
            numbering_options,
            index=numbering_options.index(current_system) if current_system in numbering_options else 0,
            key=f"numbering_system_{part_num}",
            help="Choose how chapters should be numbered. 'Null' will create null_(1), null_(2) format."
        )
        
        # Check if numbering system changed
        if current_system != numbering_system:
            # Update numbering system and regenerate numbers
            numbering_config[part_key] = numbering_system
            SessionManager.set('numbering_systems', numbering_config)
            update_chapter_numbering_system(part_num)
            st.rerun()  # Refresh to show updated numbers
        
        # Store numbering system in config
        numbering_config[part_key] = numbering_system
        SessionManager.set('numbering_systems', numbering_config)
    
    # Update chapters list based on count
    if num_chapters != current_count:
        update_chapters_count(part_key, num_chapters, part_chapters, part_num)
        st.rerun()
    
    # Chapter details configuration
    if num_chapters > 0:
        render_chapter_details(part_num, part_chapters, config)
        
        # Individual create button for this part
        part_button_col1, part_button_col2 = st.columns(2)
        with part_button_col1:
            if st.button(f"🏗️ Create Part {part_num} Chapters", key=f"create_part_{part_num}"):
                create_chapters_for_part(config, part_num, part_chapters)
        
        with part_button_col2:
            if SessionManager.get('chapters_created') and any(part_chapters):
                if st.button(f"🔄 Update Part {part_num} Chapters", key=f"update_part_{part_num}"):
                    update_existing_chapters_for_part(config, part_num, part_chapters)


def get_chapter_number_format(part_num: int, chapter_index: int) -> str:
    """Get formatted chapter number based on numbering system"""
    numbering_config = SessionManager.get('numbering_systems', {})
    part_key = f"Part_{part_num}"
    numbering_system = numbering_config.get(part_key, "Numbers (1, 2, 3...)")
    
    chapter_num = chapter_index + 1  # Convert 0-based index to 1-based
    
    if numbering_system == "Words (One, Two, Three...)":
        word_numbers = ["One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine", "Ten",
                       "Eleven", "Twelve", "Thirteen", "Fourteen", "Fifteen", "Sixteen", "Seventeen", 
                       "Eighteen", "Nineteen", "Twenty"]
        return word_numbers[chapter_num - 1] if chapter_num <= len(word_numbers) else str(chapter_num)
    
    elif numbering_system == "Roman (I, II, III...)":
        roman_numerals = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X",
                         "XI", "XII", "XIII", "XIV", "XV", "XVI", "XVII", "XVIII", "XIX", "XX"]
        return roman_numerals[chapter_num - 1] if chapter_num <= len(roman_numerals) else str(chapter_num)
    
    elif numbering_system == "Null (null_1, null_2...)":
        return f"null_{chapter_num}"  # Format: null_1, null_2, etc.
    
    else:  # Default to numbers
        return str(chapter_num)

def update_chapters_count(part_key: str, num_chapters: int, current_chapters: List, part_num: int):
    """Update the number of chapters for a part with auto-numbering"""
    chapters_config = SessionManager.get('chapters_config', {})
    
    # Get current numbering system for this part
    numbering_config = SessionManager.get('numbering_systems', {})
    current_numbering_system = numbering_config.get(part_key, "Numbers (1, 2, 3...)")
    
    if num_chapters > len(current_chapters):
        # Add new chapters with auto-generated numbers
        for i in range(len(current_chapters), num_chapters):
            auto_number = get_chapter_number_format(part_num, i)
            current_chapters.append({'number': auto_number, 'name': ''})
    else:
        # Remove extra chapters
        current_chapters = current_chapters[:num_chapters]
    
    chapters_config[part_key] = current_chapters
    SessionManager.set('chapters_config', chapters_config)

def update_chapter_numbering_system(part_num: int):
    """Update all chapter numbers when numbering system changes"""
    part_key = f"Part_{part_num}"
    chapters_config = SessionManager.get('chapters_config', {})
    current_chapters = chapters_config.get(part_key, [])
    
    if current_chapters:
        # Update all chapter numbers based on new system
        for i, chapter in enumerate(current_chapters):
            new_number = get_chapter_number_format(part_num, i)
            current_chapters[i]['number'] = new_number
        
        chapters_config[part_key] = current_chapters
        SessionManager.set('chapters_config', chapters_config)

def render_chapter_details(part_num: int, chapters: List[Dict], config: Dict):
    """Render detailed configuration for each chapter with rename detection"""
    
    st.markdown(f"**Configure chapters for Part {part_num}:**")
    
    # Get old chapters config for comparison
    old_chapters_config = SessionManager.get('chapters_config', {})
    old_chapters = old_chapters_config.get(f"Part_{part_num}", [])
    
    updated_chapters = []
    safe_code = FolderManager.sanitize_name(config['code'])
    # Book name kept as is (no sanitization)
    book_name = config['book_name']
    base_name = f"{safe_code}_{book_name}"
    
    for i, chapter in enumerate(chapters):
        col1, col2 = st.columns(2)
        
        with col1:
            # Auto-populate with formatted number but allow editing
            auto_number = get_chapter_number_format(part_num, i)
            chapter_number = st.text_input(
                "Number",
                value=chapter.get('number', auto_number),
                placeholder=f"e.g., {auto_number}",
                key=f"chapter_num_{part_num}_{i}",
                help="Chapter number will auto-populate based on selected system"
            )
        
        with col2:
            chapter_name = st.text_input(
                "Name",
                value=chapter.get('name', ''),
                placeholder="e.g., Introduction, Basics (leave empty for 'Null Name')",
                key=f"chapter_name_{part_num}_{i}",
                help="Leave empty to use 'Null Name' in folder naming"
            )
        
        updated_chapters.append({
            'number': chapter_number,
            'name': chapter_name
        })
        
        # Show preview of folder name
        preview_name = ChapterManager.generate_chapter_folder_name(
            f"{base_name}_Part_{part_num}",
            chapter_number or None,
            chapter_name or None
        )
        st.caption(f"📁 Folder: `{preview_name}`")
        
        if i < len(chapters) - 1:  # Don't show separator after last chapter
            st.markdown("---")
    
    # Check for chapter name/number changes and handle file renaming
    if len(old_chapters) == len(updated_chapters) and SessionManager.get('chapters_created'):
        handle_chapter_renaming(part_num, old_chapters, updated_chapters, config)
    
    # Update session state
    chapters_config = SessionManager.get('chapters_config', {})
    chapters_config[f"Part_{part_num}"] = updated_chapters
    SessionManager.set('chapters_config', chapters_config)

def handle_chapter_renaming(part_num: int, old_chapters: List[Dict], new_chapters: List[Dict], config: Dict):
    """Handle renaming of chapter files when chapter details change"""
    folder_metadata = SessionManager.get('folder_metadata', {})
    safe_code = FolderManager.sanitize_name(config['code'])
    book_name = config['book_name']  # Book name kept as is
    base_name = f"{safe_code}_{book_name}"
    part_folder_name = f"{base_name}_Part_{part_num}"
    
    for i, (old_chapter, new_chapter) in enumerate(zip(old_chapters, new_chapters)):
        # Check if chapter name/number changed
        old_name = old_chapter.get('name', '').strip()
        old_number = old_chapter.get('number', '').strip()
        new_name = new_chapter.get('name', '').strip()
        new_number = new_chapter.get('number', '').strip()
        
        if old_name != new_name or old_number != new_number:
            # Find corresponding chapter folder and rename files
            for folder_id, metadata in folder_metadata.items():
                if (metadata['type'] == 'chapter' and 
                    metadata['parent_part'] == part_num and
                    metadata['chapter_number'] == old_number and
                    metadata['chapter_name'] == old_name):
                    
                    # Update metadata
                    metadata['chapter_number'] = new_number
                    metadata['chapter_name'] = new_name
                    
                    # Generate new naming base
                    new_naming_base = ChapterManager.generate_chapter_folder_name(
                        part_folder_name, new_number or None, new_name or None
                    )
                    
                    # Rename files and folder
                    if ChapterManager.rename_chapter_files(folder_id, new_naming_base):
                        st.success(f"📝 Renamed files in chapter {i+1}")
                    
                    # Update display name and naming base
                    display_chapter_name = new_naming_base.split(f'{part_folder_name}_')[-1]
                    metadata['display_name'] = f"Part {part_num} → {display_chapter_name}"
                    metadata['naming_base'] = new_naming_base
                    break
    
    SessionManager.set('folder_metadata', folder_metadata)

def render_chapter_preview(config: Dict):
    """Render chapter structure preview"""
    st.subheader("📋 Structure Preview")
    
    chapters_config = SessionManager.get('chapters_config', {})
    
    if not any(chapters_config.values()):
        st.info("Configure chapters to see preview")
        return
    
    safe_code = FolderManager.sanitize_name(config['code'])
    book_name = config['book_name']  # Book name kept as is
    base_name = f"{safe_code}_{book_name}"
    
    for part_key, chapters in chapters_config.items():
        if chapters:
            part_num = part_key.split('_')[1]
            st.markdown(f"**Part {part_num}:**")
            
            preview_chapters = ChapterManager.get_chapters_preview(
                base_name, int(part_num), chapters
            )
            
            for chapter_folder in preview_chapters:
                st.write(f"📂 {chapter_folder}")
            
            st.markdown("---")

def create_chapters_for_part(config: Dict, part_num: int, chapters: List[Dict]):
    """Create chapters for a specific part only"""
    if not chapters or not any(ch.get('number') or ch.get('name') for ch in chapters):
        st.warning(f"No chapters configured for Part {part_num}!")
        return
    
    try:
        with st.spinner(f"Creating chapters for Part {part_num}..."):
            safe_code = FolderManager.sanitize_name(config['code'])
            book_name = config['book_name']  # Book name kept as is
            base_name = f"{safe_code}_{book_name}"
            
            # FIXED: Check if project folder exists with current working directory
            import os
            current_dir = Path.cwd()
            
            # Try multiple possible project paths
            possible_paths = [
                Path(base_name),  # Current approach
                current_dir / base_name,  # Relative to current directory
                Path.cwd() / base_name  # Explicit current working directory
            ]
            
            project_path = None
            for path in possible_paths:
                if path.exists():
                    project_path = path
                    break
            
            # If no existing path found, create in current directory
            if not project_path:
                project_path = current_dir / base_name
                project_path.mkdir(parents=True, exist_ok=True)
                st.info(f"Created project directory: {project_path.absolute()}")
            
            # Validate chapters before creating
            is_valid, error_msg = ChapterManager.validate_chapter_data(chapters)
            if not is_valid:
                st.error(f"Error in Part {part_num}: {error_msg}")
                return
            
            created_chapters = ChapterManager.create_chapter_folders(
                project_path, base_name, part_num, chapters
            )
            
            if created_chapters:
                SessionManager.set('chapters_created', True)
                # Update created folders list
                current_folders = SessionManager.get('created_folders', [])
                current_folders.extend(created_chapters)
                SessionManager.set('created_folders', current_folders)
                
                st.success(f"✅ Created {len(created_chapters)} chapters for Part {part_num}!")
                
                # Show created chapters
                with st.expander(f"📂 View Created Chapters for Part {part_num}"):
                    for chapter in created_chapters:
                        st.write(f"📂 {chapter}")
    
    except Exception as e:
        st.error(f"Error creating chapters for Part {part_num}: {str(e)}")
        # Show debug information
        st.error(f"Debug info: Tried to find project at {base_name}")
        st.error(f"Current working directory: {Path.cwd()}")

def create_all_chapters(config: Dict, chapters_config: Dict):
    """Create all configured chapters with unique IDs and metadata tracking"""
    
    if not any(chapters_config.values()):
        st.warning("No chapters configured!")
        return
    
    try:
        with st.spinner("Creating chapter folders..."):
            safe_code = FolderManager.sanitize_name(config['code'])
            book_name = config['book_name']  # Book name kept as is
            base_name = f"{safe_code}_{book_name}"
            
            # FIXED: Same path resolution logic
            import os
            current_dir = Path.cwd()
            
            possible_paths = [
                Path(base_name),
                current_dir / base_name,
                Path.cwd() / base_name
            ]
            
            project_path = None
            for path in possible_paths:
                if path.exists():
                    project_path = path
                    break
            
            if not project_path:
                project_path = current_dir / base_name
                project_path.mkdir(parents=True, exist_ok=True)
                st.info(f"Created project directory: {project_path.absolute()}")
            
            all_created_chapters = []
            
            for part_key, chapters in chapters_config.items():
                if chapters and any(ch.get('number') or ch.get('name') for ch in chapters):
                    part_num = int(part_key.split('_')[1])
                    
                    # Validate chapters before creating
                    is_valid, error_msg = ChapterManager.validate_chapter_data(chapters)
                    if not is_valid:
                        st.error(f"Error in Part {part_num}: {error_msg}")
                        continue
                    
                    created_chapters = ChapterManager.create_chapter_folders(
                        project_path, base_name, part_num, chapters
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
        st.error(f"Debug info: Tried to find project at {base_name}")
        st.error(f"Current working directory: {Path.cwd()}")

def update_existing_chapters_for_part(config: Dict, part_num: int, chapters: List[Dict]):
    """Update existing chapters for a specific part"""
    try:
        with st.spinner(f"Updating chapters for Part {part_num}..."):
            # This will handle renaming through the existing logic
            st.success(f"✅ Updated chapters for Part {part_num}!")
            st.info("Chapter updates are handled automatically when you modify names/numbers.")
    except Exception as e:
        st.error(f"Error updating chapters for Part {part_num}: {str(e)}")