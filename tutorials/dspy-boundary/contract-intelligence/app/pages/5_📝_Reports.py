"""Reports generation page."""

import streamlit as st
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from config.settings import settings

st.set_page_config(
    page_title="Reports - Contract Intelligence",
    page_icon="📝",
    layout="wide"
)

st.title("📝 Reports & Documentation")
st.markdown("Generate professional reports and documentation from your contract analysis")

# Check if files have been uploaded
if not st.session_state.get('uploaded_files'):
    st.warning("⚠️ No contracts uploaded yet. Please upload contracts first.")
    if st.button("📄 Upload Contracts"):
        st.switch_page("pages/1_📄_Upload_Contract.py")
    st.stop()

# Report configuration
st.markdown("### ⚙️ Report Configuration")

col1, col2 = st.columns([2, 1])

with col1:
    # Contract selection
    st.markdown("**📄 Select Contracts for Report:**")
    
    selected_contracts = []
    for i, file in enumerate(st.session_state.uploaded_files):
        if st.checkbox(f"📄 {file.name}", key=f"report_contract_{i}"):
            selected_contracts.append(i)
    
    if not selected_contracts:
        st.info("Please select at least one contract to generate a report.")

with col2:
    st.markdown("**📊 Report Settings:**")
    
    report_type = st.selectbox(
        "Report Type:",
        [
            "📄 Executive Summary",
            "📊 Detailed Analysis", 
            "⚖️ Compliance Report",
            "🔄 Comparison Report",
            "📋 Risk Assessment",
            "📅 Obligation Tracker"
        ]
    )
    
    export_format = st.selectbox(
        "Export Format:",
        ["📄 PDF", "📊 Word Document", "📋 Excel Workbook", "📧 Email Summary"]
    )
    
    include_charts = st.checkbox("📈 Include Charts", value=True)
    include_raw_data = st.checkbox("📊 Include Raw Data", value=False)

# Report templates
st.markdown("### 📋 Report Templates")

templates_tab1, templates_tab2, templates_tab3 = st.tabs(["📄 Standard", "🏢 Custom", "📚 Library"])

with templates_tab1:
    st.markdown("**📄 Standard Report Templates:**")
    
    templates = [
        {
            "name": "Executive Summary",
            "description": "High-level overview for executives and stakeholders",
            "sections": ["Key findings", "Risk summary", "Recommendations", "Action items"],
            "length": "2-3 pages"
        },
        {
            "name": "Legal Review Report", 
            "description": "Comprehensive legal analysis for legal teams",
            "sections": ["Contract structure", "Risk analysis", "Compliance check", "Legal recommendations"],
            "length": "5-10 pages"
        },
        {
            "name": "Risk Assessment",
            "description": "Detailed risk analysis and mitigation strategies",
            "sections": ["Risk matrix", "Impact analysis", "Mitigation plans", "Monitoring requirements"],
            "length": "3-5 pages"
        }
    ]
    
    for template in templates:
        with st.expander(f"📄 {template['name']} ({template['length']})"):
            st.write(f"**Description:** {template['description']}")
            st.write(f"**Sections:** {', '.join(template['sections'])}")
            if st.button(f"📋 Use Template", key=f"template_{template['name']}"):
                st.success(f"✅ Selected template: {template['name']}")

with templates_tab2:
    st.markdown("**🏢 Custom Templates:**")
    st.info("📝 Custom template builder coming in Stage 8!")
    
    if st.button("➕ Create Custom Template"):
        st.info("🔧 Template builder will be available soon!")

with templates_tab3:
    st.markdown("**📚 Template Library:**")
    st.info("📚 Template library coming in Stage 8!")

# Report generation
st.markdown("### 🚀 Generate Report")

if selected_contracts:
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("📄 Preview Report", type="secondary"):
            st.info("👁️ Report preview coming in Stage 8!")
    
    with col2:
        if st.button("📥 Generate Report", type="primary"):
            st.info("🔧 Report generation will be implemented in Stage 8!")
            
            # Progress simulation
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            import time
            for i in range(101):
                progress_bar.progress(i)
                if i < 30:
                    status_text.text(f"📊 Analyzing contracts... {i}%")
                elif i < 60:
                    status_text.text(f"📝 Generating content... {i}%")
                elif i < 90:
                    status_text.text(f"🎨 Formatting report... {i}%")
                else:
                    status_text.text(f"📄 Finalizing document... {i}%")
                time.sleep(0.02)
            
            st.success("✅ Report generated successfully! (Demo)")
    
    with col3:
        if st.button("📧 Email Report"):
            st.info("📧 Email integration coming in Stage 11!")

# Report history
st.markdown("### 📚 Report History")

# Mock report history
report_history = [
    {
        "name": "Executive Summary - Service Agreement",
        "date": "2024-01-15",
        "type": "Executive Summary",
        "format": "PDF",
        "size": "2.3 MB"
    },
    {
        "name": "Risk Assessment - Multiple Contracts",
        "date": "2024-01-10", 
        "type": "Risk Assessment",
        "format": "Word",
        "size": "1.8 MB"
    }
]

if not report_history:
    st.info("📄 No reports generated yet. Create your first report above!")
else:
    for i, report in enumerate(report_history):
        with st.expander(f"📄 {report['name']} - {report['date']}"):
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.write(f"**Type:** {report['type']}")
                st.write(f"**Format:** {report['format']}")
            
            with col2:
                st.write(f"**Date:** {report['date']}")
                st.write(f"**Size:** {report['size']}")
            
            with col3:
                if st.button("📥 Download", key=f"download_{i}"):
                    st.info("💾 Download feature coming soon!")
            
            with col4:
                if st.button("🗑️ Delete", key=f"delete_{i}"):
                    st.warning("🗑️ Delete confirmation coming soon!")

# Quick actions
st.markdown("---")
st.markdown("### 🚀 Quick Actions")

col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("📊 View Dashboard"):
        st.switch_page("pages/2_📊_Analysis_Dashboard.py")

with col2:
    if st.button("⚖️ Run Compliance"):
        st.switch_page("pages/3_⚖️_Compliance_Check.py")

with col3:
    if st.button("🔄 Compare Contracts"):
        st.switch_page("pages/4_🔄_Compare_Contracts.py")

with col4:
    if st.button("📄 Upload More"):
        st.switch_page("pages/1_📄_Upload_Contract.py")

# Footer
st.markdown("---")
st.caption("📝 **Note**: All reports are automatically saved and can be accessed from the Report History section.")