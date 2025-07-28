import streamlit as st
from src.utils.page_utils import (
    create_standard_page_layout,
    render_standard_disclaimer,
    REMEDY_CATEGORIES
)

def render_remedies_content(birth_data):
    """Render remedies specific content"""
    # Remedy categories
    tab1, tab2, tab3, tab4 = st.tabs([
        REMEDY_CATEGORIES["mantras"]["title"],
        REMEDY_CATEGORIES["gemstones"]["title"], 
        REMEDY_CATEGORIES["rituals"]["title"],
        REMEDY_CATEGORIES["donations"]["title"]
    ])
    
    with tab1:
        st.subheader(REMEDY_CATEGORIES["mantras"]["title"])
        st.info("🚧 Personalized mantra suggestions coming soon!")
        st.write("**General Mantras for All:**")
        for mantra in REMEDY_CATEGORIES["mantras"]["general"]:
            st.write(f"- {mantra}")
    
    with tab2:
        st.subheader(REMEDY_CATEGORIES["gemstones"]["title"])
        st.info("🚧 Personalized gemstone analysis coming soon!")
        st.write("**Important Notes:**")
        for note in REMEDY_CATEGORIES["gemstones"]["notes"]:
            st.write(f"- {note}")
    
    with tab3:
        st.subheader(REMEDY_CATEGORIES["rituals"]["title"])
        st.info("🚧 Personalized ritual recommendations coming soon!")
        st.write("**General Beneficial Practices:**")
        for ritual in REMEDY_CATEGORIES["rituals"]["general"]:
            st.write(f"- {ritual}")
    
    with tab4:
        st.subheader(REMEDY_CATEGORIES["donations"]["title"])
        st.info("🚧 Personalized donation guidance coming soon!")
        st.write("**General Charitable Acts:**")
        for donation in REMEDY_CATEGORIES["donations"]["general"]:
            st.write(f"- {donation}")
    
    render_standard_disclaimer()

def main():
    page_config = {
        'title': '💎 Vedic Remedies',
        'icon': '💎',
        'subtitle': 'Personalized Remedial Measures for Better Life',
        'content_callback': render_remedies_content,
        'page_id': 'remedies'
    }
    
    create_standard_page_layout(page_config)

if __name__ == "__main__":
    main()
