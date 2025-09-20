
# src/ui/chapter_management.py
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

def render_part_chapters(part_num: int, chapters_config: Dict, config: Dict):
    """Render chapter configuration for a specific part"""
    
    part_key = f"part_{part_num}"
    part_chapters = chapters_config.get(part_key, [])
    
    # Number of chapters input
    num_chapters = st.number_input(
        f"Number of chapters in Part {part_num}",
        min_value=0,
        max_value=100,
        value=len(part_chapters),
        step=1,
        key=f"chapters_count_{part_num}"
    )
    
    # Update chapters list based on count
    if num_chapters != len(part_chapters):
        update_chapters_count(part_key, num_chapters, part_chapters)
        st.rerun()
    
    # Chapter details configuration
    if num_chapters > 0:
        render_chapter_details(part_num, part_chapters, config)

def update_chapters_count(part_key: str, num_chapters: int, current_chapters: List):
    """Update the number of chapters for a part"""
    chapters_config = SessionManager.get('chapters_config', {})
    
    if num_chapters > len(current_chapters):
        # Add new chapters
        for i in range(len(current_chapters), num_chapters):
            current_chapters.append({'number': str(i + 1), 'name': ''})
    else:
        # Remove extra chapters
        current_chapters = current_chapters[:num_chapters]
    
    chapters_config[part_key] = current_chapters
    SessionManager.set('chapters_config', chapters_config)

def render_chapter_details(part_num: int, chapters: List[Dict], config: Dict):
    """Render detailed configuration for each chapter"""
    
    st.markdown(f"**Configure chapters for Part {part_num}:**")
    
    updated_chapters = []
    safe_code = FolderManager.sanitize_name(config['code'])
    safe_book_name = FolderManager.sanitize_name(config['book_name'])
    base_name = f"{safe_code}_{safe_book_name}"
    
    for i, chapter in enumerate(chapters):
        col1, col2 = st.columns(2)
        
        with col1:
            chapter_number = st.text_input(
                "Number",
                value=chapter.get('number', ''),
                placeholder="e.g., 1, 1.1, A",
                key=f"chapter_num_{part_num}_{i}"
            )
        
        with col2:
            chapter_name = st.text_input(
                "Name",
                value=chapter.get('name', ''),
                placeholder="e.g., Introduction, Basics",
                key=f"chapter_name_{part_num}_{i}"
            )
        
        updated_chapters.append({
            'number': chapter_number,
            'name': chapter_name
        })
        
        # Show preview of folder name
        preview_name = ChapterManager.generate_chapter_folder_name(
            f"{base_name}_part_{part_num}",
            chapter_number or None,
            chapter_name or None
        )
        st.caption(f"📁 Folder: `{preview_name}`")
        
        if i < len(chapters) - 1:  # Don't show separator after last chapter
            st.markdown("---")
    
    # Update session state
    chapters_config = SessionManager.get('chapters_config', {})
    chapters_config[f"part_{part_num}"] = updated_chapters
    SessionManager.set('chapters_config', chapters_config)

def render_chapter_preview(config: Dict):
    """Render chapter structure preview"""
    st.subheader("📋 Structure Preview")
    
    chapters_config = SessionManager.get('chapters_config', {})
    
    if not any(chapters_config.values()):
        st.info("Configure chapters to see preview")
        return
    
    safe_code = FolderManager.sanitize_name(config['code'])
    safe_book_name = FolderManager.sanitize_name(config['book_name'])
    base_name = f"{safe_code}_{safe_book_name}"
    
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

def create_all_chapters(config: Dict, chapters_config: Dict):
    """Create all configured chapters"""
    
    if not any(chapters_config.values()):
        st.warning("No chapters configured!")
        return
    
    try:
        with st.spinner("Creating chapter folders..."):
            safe_code = FolderManager.sanitize_name(config['code'])
            safe_book_name = FolderManager.sanitize_name(config['book_name'])
            base_name = f"{safe_code}_{safe_book_name}"
            project_path = Path(base_name)
            
            if not project_path.exists():
                st.error("Project folder not found. Please create folder structure first.")
                return
            
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
