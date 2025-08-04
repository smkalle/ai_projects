"""Contract comparison page."""

import streamlit as st
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from config.settings import settings

st.set_page_config(
    page_title="Compare Contracts - Contract Intelligence",
    page_icon="🔄",
    layout="wide"
)

st.title("🔄 Contract Comparison")
st.markdown("Side-by-side comparison of contract versions and changes")

# Check if files have been uploaded
if not st.session_state.get('uploaded_files') or len(st.session_state.uploaded_files) < 2:
    st.warning("⚠️ Need at least 2 contracts to compare. Please upload more contracts.")
    if st.button("📄 Upload Contracts"):
        st.switch_page("pages/1_📄_Upload_Contract.py")
    st.stop()

# Comparison setup
st.markdown("### 📋 Select Contracts to Compare")

col1, col2 = st.columns(2)

with col1:
    st.markdown("**📄 Contract A (Original)**")
    contract_a = st.selectbox(
        "Choose first contract:",
        options=range(len(st.session_state.uploaded_files)),
        format_func=lambda x: st.session_state.uploaded_files[x].name,
        key="contract_a"
    )

with col2:
    st.markdown("**📄 Contract B (Revised)**")
    contract_b = st.selectbox(
        "Choose second contract:",
        options=range(len(st.session_state.uploaded_files)),
        format_func=lambda x: st.session_state.uploaded_files[x].name,
        key="contract_b"
    )

# Comparison options
st.markdown("### ⚙️ Comparison Options")

col1, col2, col3 = st.columns(3)

with col1:
    comparison_type = st.radio(
        "Comparison Type:",
        ["📝 Text-based", "📊 Structural", "🎯 Semantic"],
        help="Choose how to compare the contracts"
    )

with col2:
    highlight_changes = st.checkbox("🎨 Highlight Changes", value=True)
    show_line_numbers = st.checkbox("🔢 Show Line Numbers", value=True)

with col3:
    focus_areas = st.multiselect(
        "Focus Areas:",
        ["💰 Financial Terms", "⚖️ Legal Clauses", "📅 Dates & Deadlines", "👥 Parties", "🔒 Confidentiality"],
        default=["💰 Financial Terms", "⚖️ Legal Clauses"]
    )

# Run comparison
if st.button("🔄 Compare Contracts", type="primary"):
    st.info("🔧 Contract comparison will be implemented in Stage 6!")
    
    # Progress placeholder
    with st.spinner("Analyzing contracts..."):
        import time
        time.sleep(2)
    
    st.success("✅ Comparison complete! (Demo)")

# Comparison results tabs
tab1, tab2, tab3, tab4 = st.tabs(["📊 Summary", "🔄 Side-by-Side", "📈 Change Analysis", "📝 Report"])

with tab1:
    st.markdown("### 📊 Comparison Summary")
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Changes", "0", help="Number of differences found")
    
    with col2:
        st.metric("Critical Changes", "0", help="High-impact modifications")
    
    with col3:
        st.metric("Similarity Score", "N/A", help="0-100% similarity rating")
    
    with col4:
        st.metric("Risk Impact", "N/A", help="Overall risk change assessment")
    
    # Change categories
    st.markdown("### 📋 Change Categories")
    
    change_categories = [
        {"category": "💰 Financial Terms", "changes": 0, "impact": "Low"},
        {"category": "⚖️ Legal Clauses", "changes": 0, "impact": "Medium"},
        {"category": "📅 Dates & Deadlines", "changes": 0, "impact": "Low"},
        {"category": "👥 Party Information", "changes": 0, "impact": "Low"},
        {"category": "🔒 Confidentiality", "changes": 0, "impact": "High"},
    ]
    
    for cat in change_categories:
        with st.expander(f"{cat['category']} - {cat['changes']} changes"):
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Changes Found:** {cat['changes']}")
            with col2:
                st.write(f"**Impact Level:** {cat['impact']}")

with tab2:
    st.markdown("### 🔄 Side-by-Side Comparison")
    
    st.info("📄 Side-by-side viewer will be available after Stage 6 implementation!")
    
    # Placeholder for side-by-side view
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**📄 Contract A**")
        st.markdown(f"*{st.session_state.uploaded_files[contract_a].name}*")
        st.text_area(
            "Content A",
            "Original contract content will appear here...",
            height=400,
            disabled=True
        )
    
    with col2:
        st.markdown("**📄 Contract B**")
        st.markdown(f"*{st.session_state.uploaded_files[contract_b].name}*")
        st.text_area(
            "Content B",
            "Revised contract content will appear here...",
            height=400,
            disabled=True
        )

with tab3:
    st.markdown("### 📈 Change Analysis")
    
    st.info("📊 Change analysis will be available after Stage 6 implementation!")
    
    # Placeholder analysis sections
    st.markdown("**🎯 Key Changes Identified:**")
    st.markdown("""
    - Added clauses
    - Removed sections  
    - Modified terms
    - Structural changes
    """)
    
    st.markdown("**⚖️ Risk Impact Assessment:**")
    st.markdown("""
    - Financial impact analysis
    - Legal risk changes
    - Compliance implications
    - Operational effects
    """)
    
    st.markdown("**💡 Recommendations:**")
    st.markdown("""
    - Priority review areas
    - Negotiation points
    - Approval requirements
    - Next steps
    """)

with tab4:
    st.markdown("### 📝 Comparison Report")
    
    # Report generation options
    st.markdown("**📋 Report Options:**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        report_type = st.radio(
            "Report Type:",
            ["📄 Executive Summary", "📊 Detailed Analysis", "📋 Change Log"]
        )
        
        include_images = st.checkbox("🖼️ Include Screenshots")
        include_recommendations = st.checkbox("💡 Include Recommendations", value=True)
    
    with col2:
        export_format = st.selectbox(
            "Export Format:",
            ["📄 PDF", "📊 Word Document", "📋 Excel Spreadsheet"]
        )
        
        if st.button("📥 Generate Report"):
            st.info("📄 Report generation coming in Stage 8!")

# Quick actions
st.markdown("---")
st.markdown("### 🚀 Quick Actions")

col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("📊 View Analysis"):
        st.switch_page("pages/2_📊_Analysis_Dashboard.py")

with col2:
    if st.button("⚖️ Check Compliance"):
        st.switch_page("pages/3_⚖️_Compliance_Check.py")

with col3:
    if st.button("📝 Generate Report"):
        st.switch_page("pages/5_📝_Reports.py")

with col4:
    if st.button("📄 Upload More"):
        st.switch_page("pages/1_📄_Upload_Contract.py")

# Footer
st.markdown("---")
st.caption("🔄 **Tip**: Use semantic comparison for better detection of meaning changes, even with different wording.")