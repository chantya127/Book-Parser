import streamlit as st
from typing import Dict, List
from core.session_manager import SessionManager
from core.folder_manager import ChapterManager, FolderManager
from pathlib import Path
import shutil

def render_chapter_management_page():
    """Render the chapter management page"""
    
    # Check prerequisites
    if not SessionManager.get('folder_structure_created'):
        render_prerequisites_warning()
        return
    
    config = SessionManager.get('project_config', {})
    
    st.subheader("📂 Chapter Management")
    st.markdown("Configure chapters within each part of your book.")
    
    # Check for operation completion messages
    if st.session_state.get('part_operation_completed'):
        operation_info = st.session_state.get('part_operation_info', {})
        if operation_info.get('operation') == 'add':
            st.success(f"✅ Successfully created Part {operation_info.get('part_number')}!")
            st.info(f"📂 Location: {operation_info.get('location', 'Unknown')}")
        elif operation_info.get('operation') == 'delete':
            st.success(f"✅ Successfully deleted Part {operation_info.get('part_number')} and all its contents!")
        
        # Clear the flags
        st.session_state['part_operation_completed'] = False
        st.session_state['part_operation_info'] = {}
    
    # Add option to create individual parts
    st.markdown("### 🔧 Additional Options")
    col_opt1, col_opt2, col_opt3, col_opt4 = st.columns(4)
    
    # Get actual parts that exist (including individually created ones)
    actual_parts = get_existing_parts(config)
    max_part_num = max(actual_parts) if actual_parts else 0
    
    with col_opt1:
        if st.button("➕ Add Individual Part", type="secondary"):
            individual_part_num = st.session_state.get('individual_part_input', max_part_num + 1)
            add_individual_part(config, individual_part_num)
            st.rerun()  # Force refresh after adding part
    
    with col_opt2:
        individual_part_num = st.number_input(
            "Part Number to Add",
            min_value=1,
            value=max_part_num + 1,
            step=1,
            key="individual_part_input",
            help="Specify which part number to create individually"
        )
    
    with col_opt3:
        # Delete part option - refresh the list each time
        current_parts = get_existing_parts(config)  # Get fresh list
        if current_parts:
            part_to_delete = st.selectbox(
                "Select Part to Delete",
                current_parts,
                key="part_to_delete_select",
                help="Choose which part to delete (this will delete all contents)"
            )
            
    with col_opt4:
        if current_parts:
            if st.button("🗑️ Delete Selected Part", type="secondary", key="delete_part_btn"):
                part_to_delete = st.session_state.get("part_to_delete_select")
                if part_to_delete:
                    delete_individual_part(config, part_to_delete)
                    st.rerun()
    
    # Refresh parts list after any operations for display
    updated_parts = get_existing_parts(config)
    
    if not updated_parts:
        st.info("📝 No parts configured. You can add individual parts above or configure parts in Project Setup.")
        return
    
    st.markdown("---")
    st.info(f"Found {len(updated_parts)} existing parts: {', '.join(map(str, sorted(updated_parts)))}")
    
    # Chapter configuration for each part - use updated parts list
    col1, col2 = st.columns([2, 1])
    
    with col1:
        render_chapter_configuration(config, updated_parts)
    
    with col2:
        render_chapter_preview(config)

def delete_individual_part(config: Dict, part_number: int):
    """Delete an individual part folder and all its contents"""
    try:
        safe_code = FolderManager.sanitize_name(config['code'])
        book_name = config['book_name']
        base_name = f"{safe_code}_{book_name}"
        
        # Use consistent path resolution
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
            st.error(f"Project folder not found. Cannot delete Part {part_number}.")
            return
        
        # Find the part folder
        part_folder = project_path / f"{base_name}_Part_{part_number}"
        
        if not part_folder.exists():
            st.error(f"Part {part_number} folder not found.")
            return
        
        # Delete the folder and all contents
        shutil.rmtree(part_folder)
        
        # Update session state - remove from created folders
        current_folders = SessionManager.get('created_folders', [])
        part_path_str = str(part_folder.absolute())
        if part_path_str in current_folders:
            current_folders.remove(part_path_str)
        
        # Remove any chapter folders that were in this part
        folders_to_remove = []
        for folder_path in current_folders:
            if f"Part_{part_number}" in folder_path and part_folder.name in folder_path:
                folders_to_remove.append(folder_path)
        
        for folder_path in folders_to_remove:
            current_folders.remove(folder_path)
        
        SessionManager.set('created_folders', current_folders)
        
        # Remove chapter metadata for this part
        folder_metadata = SessionManager.get('folder_metadata', {})
        metadata_to_remove = []
        for folder_id, metadata in folder_metadata.items():
            if metadata.get('type') == 'chapter' and metadata.get('parent_part') == part_number:
                metadata_to_remove.append(folder_id)
            elif metadata.get('type') == 'custom' and f"Part_{part_number}" in metadata.get('actual_path', ''):
                metadata_to_remove.append(folder_id)
        
        for folder_id in metadata_to_remove:
            del folder_metadata[folder_id]
        
        SessionManager.set('folder_metadata', folder_metadata)
        
        # Remove chapters config for this part
        chapters_config = SessionManager.get('chapters_config', {})
        part_key = f"Part_{part_number}"
        if part_key in chapters_config:
            del chapters_config[part_key]
            SessionManager.set('chapters_config', chapters_config)
        
        # Update num_parts if this was the highest numbered part
        current_num_parts = config.get('num_parts', 0)
        if part_number == current_num_parts:
            # Find the new highest part number
            existing_parts = get_existing_parts(config)
            new_max_parts = max(existing_parts) if existing_parts else 0
            SessionManager.update_config({'num_parts': new_max_parts})
        
        # Set success message for next render
        st.session_state['part_operation_completed'] = True
        st.session_state['part_operation_info'] = {
            'operation': 'delete',
            'part_number': part_number
        }
        
    except PermissionError:
        st.error(f"❌ Permission denied. Cannot delete Part {part_number}. Please check folder permissions.")
    except Exception as e:
        st.error(f"❌ Error deleting Part {part_number}: {str(e)}")

def get_existing_parts(config: Dict) -> List[int]:
    """Get list of actually existing part numbers by checking filesystem first, then session state"""
    existing_parts = set()
    
    safe_code = FolderManager.sanitize_name(config.get('code', ''))
    book_name = config.get('book_name', '')
    base_name = f"{safe_code}_{book_name}"
    
    # First, check filesystem directly to get the truth
    try:
        current_dir = Path.cwd()
        possible_paths = [
            Path(base_name),
            current_dir / base_name,
            Path.cwd() / base_name
        ]
        
        for project_path in possible_paths:
            if project_path.exists() and project_path.is_dir():
                for item in project_path.iterdir():
                    if item.is_dir() and f"{base_name}_Part_" in item.name:
                        try:
                            part_num_str = item.name.split(f"{base_name}_Part_")[-1]
                            part_num = int(part_num_str)
                            existing_parts.add(part_num)
                        except (ValueError, IndexError):
                            continue
                break
    except Exception:
        pass
    
    # If no parts found in filesystem, fall back to session state and config
    if not existing_parts:
        # Check created folders for individual parts
        created_folders = SessionManager.get('created_folders', [])
        
        for folder_path in created_folders:
            # Skip if folder doesn't exist on filesystem
            if not Path(folder_path).exists():
                continue
                
            folder_name = Path(folder_path).name
            # Look for pattern: base_name_Part_X
            if f"{base_name}_Part_" in folder_name:
                try:
                    part_num_str = folder_name.split(f"{base_name}_Part_")[-1]
                    part_num = int(part_num_str)
                    existing_parts.add(part_num)
                except (ValueError, IndexError):
                    continue
        
        # Only add from config if parts actually exist on filesystem
        config_parts = config.get('num_parts', 0)
        if config_parts > 0:
            for i in range(1, config_parts + 1):
                part_folder = None
                try:
                    current_dir = Path.cwd()
                    possible_paths = [
                        Path(base_name),
                        current_dir / base_name,
                        Path.cwd() / base_name
                    ]
                    
                    for project_path in possible_paths:
                        if project_path.exists():
                            part_folder = project_path / f"{base_name}_Part_{i}"
                            break
                    
                    if part_folder and part_folder.exists():
                        existing_parts.add(i)
                except:
                    continue
    
    return sorted(list(existing_parts))

def add_individual_part(config: Dict, part_number: int):
    """Add an individual part folder"""
    try:
        safe_code = FolderManager.sanitize_name(config['code'])
        book_name = config['book_name']
        base_name = f"{safe_code}_{book_name}"
        
        # Use consistent path resolution
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
        
        # Create individual part folder
        part_folder = project_path / f"{base_name}_Part_{part_number}"
        
        # Check if part already exists
        if part_folder.exists():
            st.error(f"❌ Part {part_number} already exists!")
            return
        
        part_folder.mkdir(exist_ok=True)
        
        # Update session state
        current_folders = SessionManager.get('created_folders', [])
        new_part_path = str(part_folder.absolute())
        if new_part_path not in current_folders:
            current_folders.append(new_part_path)
            SessionManager.set('created_folders', current_folders)
        
        # Update num_parts if this part number is higher
        current_num_parts = config.get('num_parts', 0)
        if part_number > current_num_parts:
            SessionManager.update_config({'num_parts': part_number})
        
        # Set success message for next render
        st.session_state['part_operation_completed'] = True
        st.session_state['part_operation_info'] = {
            'operation': 'add',
            'part_number': part_number,
            'location': str(part_folder.absolute())
        }
        
    except Exception as e:
        st.error(f"❌ Error creating individual part: {str(e)}")

def render_prerequisites_warning():
    """Render warning when prerequisites are not met"""
    st.warning("⚠️ Please complete the project setup first!")
    st.markdown("""
    **Required steps:**
    1. Upload PDF file
    2. Configure project details
    3. Create folder structure
    """)

def render_chapter_configuration(config: Dict, existing_parts: List[int]):
    """Render chapter configuration interface"""
    
    chapters_config = SessionManager.get('chapters_config', {})
    
    for part_num in existing_parts:
        with st.expander(f"📖 Part {part_num} Chapters", expanded=part_num == existing_parts[0] if existing_parts else False):
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
                       "Thirty-Five", "Thirty-Six", "Thirty-Seven", "Thirty-Eight", "Thirty-Nine", "Forty",
                       "Forty-One", "Forty-Two", "Forty-Three", "Forty-Four", "Forty-Five", "Forty-Six",
                       "Forty-Seven", "Forty-Eight", "Forty-Nine", "Fifty"]
        return word_numbers[chapter_num - 1] if chapter_num <= len(word_numbers) else str(chapter_num)
    
    elif numbering_system == "Roman (I, II, III...)":
        roman_numerals = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X",
                         "XI", "XII", "XIII", "XIV", "XV", "XVI", "XVII", "XVIII", "XIX", "XX",
                         "XXI", "XXII", "XXIII", "XXIV", "XXV", "XXVI", "XXVII", "XXVIII", "XXIX", "XXX",
                         "XXXI", "XXXII", "XXXIII", "XXXIV", "XXXV", "XXXVI", "XXXVII", "XXXVIII", "XXXIX", "XL",
                         "XLI", "XLII", "XLIII", "XLIV", "XLV", "XLVI", "XLVII", "XLVIII", "XLIX", "L"]
        return roman_numerals[chapter_num - 1] if chapter_num <= len(roman_numerals) else str(chapter_num)
    
    elif numbering_system == "Null (null_1, null_2...)":
        return f"null_{chapter_num}"
    
    else:  # Default to numbers
        return str(chapter_num)

def render_part_chapters(part_num: int, chapters_config: Dict, config: Dict):
    """Render chapter configuration for a specific part"""
    
    part_key = f"Part_{part_num}"
    part_chapters = chapters_config.get(part_key, [])
    
    # Number of chapters input
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
        numbering_config = SessionManager.get('numbering_systems', {})
        current_system = numbering_config.get(part_key, "Numbers (1, 2, 3...)")
        
        numbering_options = [
            "Numbers (1, 2, 3...)", 
            "Words (One, Two, Three...)", 
            "Roman (I, II, III...)",
            "Null (null_1, null_2...)"
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
            numbering_config[part_key] = numbering_system
            SessionManager.set('numbering_systems', numbering_config)
            update_chapter_numbering_system(part_num)
            st.rerun()
        
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

def update_chapters_count(part_key: str, num_chapters: int, current_chapters: List, part_num: int):
    """Update the number of chapters for a part with auto-numbering"""
    chapters_config = SessionManager.get('chapters_config', {})
    
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
    book_name = config['book_name']
    base_name = f"{safe_code}_{book_name}"
    
    for i, chapter in enumerate(chapters):
        col1, col2 = st.columns(2)
        
        with col1:
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
        
        if i < len(chapters) - 1:
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
    book_name = config['book_name']
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
    book_name = config['book_name']
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
            book_name = config['book_name']
            base_name = f"{safe_code}_{book_name}"
            
            # Use consistent path resolution
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
            book_name = config['book_name']
            base_name = f"{safe_code}_{book_name}"
            
            # Use consistent path resolution
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
            st.success(f"✅ Updated chapters for Part {part_num}!")
            st.info("Chapter updates are handled automatically when you modify names/numbers.")
    except Exception as e:
        st.error(f"Error updating chapters for Part {part_num}: {str(e)}")