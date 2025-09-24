# ui/font_selector.py - Font case selection interface

import streamlit as st

def render_font_case_selector():
    """Render font case selection interface"""
    # Lazy import to avoid circular dependency
    from core.text_formatter import TextFormatter
    
    st.subheader("🎨 Text Formatting Setup")
    st.markdown("Choose how all text elements (codes, names, chapters, etc.) should be formatted throughout the application.")
    
    # Center the content
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("### Select Font Case Style")
        
        # Get font case options
        font_options = TextFormatter.get_font_case_options()
        current_selection = st.session_state.get('selected_font_case', font_options[2])  # Default to First Capital
        
        # Find current index
        try:
            current_index = font_options.index(current_selection)
        except ValueError:
            current_index = 2  # Default to First Capital
        
        selected_font_case = st.radio(
            "Choose formatting style:",
            font_options,
            index=current_index,
            key="font_case_radio",
            help="This formatting will be applied to all text elements including book codes, names, chapters, and folder names"
        )
        
        # Show preview examples
        st.markdown("---")
        st.markdown("### Preview Examples")
        
        # Example texts
        example_code = "CS101"
        example_book = "Data Structures and Algorithms"
        example_part = "Advanced Topics"
        example_chapter = "Binary Search Trees"
        
        # Format examples
        formatted_code = TextFormatter.format_project_code(example_code, selected_font_case)
        formatted_book = TextFormatter.format_book_name(example_book, selected_font_case)
        formatted_part = TextFormatter.format_part_name(example_part, selected_font_case)
        formatted_chapter = TextFormatter.format_chapter_name(example_chapter, selected_font_case)
        
        # Display examples in a nice format
        st.markdown(f"**Project Code:** `{formatted_code}`")
        st.markdown(f"**Book Name:** `{formatted_book}`")
        st.markdown(f"**Part Name:** `{formatted_part}`")
        st.markdown(f"**Chapter Name:** `{formatted_chapter}`")
        
        st.markdown("---")
        
        # Confirmation button
        col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
        
        with col_btn2:
            if st.button("✅ Confirm Selection", type="primary", key="confirm_font_case"):
                st.session_state['selected_font_case'] = selected_font_case
                st.session_state['font_case_selected'] = True
                st.success(f"✅ Font case set to: {selected_font_case}")
                st.rerun()
        
        # Option to change later
        st.markdown("---")
        st.info("💡 You can change the font formatting later from the sidebar settings.")

def render_font_case_changer():
    """Render font case changer for sidebar with radio buttons"""
    from core.text_formatter import TextFormatter
    from core.session_manager import SessionManager
    
    if st.session_state.get('font_case_selected'):
        st.markdown("---")
        st.subheader("🎨 Text Format")
        
        current_font_case = st.session_state.get('selected_font_case', 'First Capital (Title Case)')
        font_options = TextFormatter.get_font_case_options()
        
        try:
            current_index = font_options.index(current_font_case)
        except ValueError:
            current_index = 2
        
        # Simple radio button selection
        selected_font_case = st.radio(
            "Select font format:",
            font_options,
            index=current_index,
            key="font_case_radio_selection",
            help="Choose how all text elements are formatted"
        )
        
        # Update session state whenever selection changes
        if selected_font_case != current_font_case:
            st.session_state['selected_font_case'] = selected_font_case
            SessionManager.set_font_case(selected_font_case)
            
            st.markdown("**Preview:**")
            sample_texts = ["CS101", "Data Structures", "Advanced Topics"]
            
            for sample in sample_texts:
                formatted = TextFormatter.format_text(sample, selected_font_case)
                st.write(f"`{formatted}`")
            
            st.success(f"Font format updated to: {selected_font_case}")
            
            # Only rerun if folder structure is not created
            if not SessionManager.get('folder_structure_created'):
                st.rerun()