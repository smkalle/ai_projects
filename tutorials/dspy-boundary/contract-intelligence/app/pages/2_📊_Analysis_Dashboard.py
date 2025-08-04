"""Analysis dashboard and results page."""

import streamlit as st
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from config.settings import settings

st.set_page_config(
    page_title="Analysis Dashboard - Contract Intelligence",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Analysis Dashboard")
st.markdown("Comprehensive view of your contract analysis results")

# Check if files have been uploaded
if not st.session_state.get('uploaded_files'):
    st.warning("⚠️ No contracts uploaded yet. Please upload contracts first.")
    if st.button("📄 Upload Contracts"):
        st.switch_page("pages/1_📄_Upload_Contract.py")
    st.stop()

# Dashboard tabs
tab1, tab2, tab3, tab4 = st.tabs(["📋 Overview", "📈 Risk Analysis", "👥 Parties & Terms", "📅 Obligations"])

with tab1:
    st.markdown("### 📋 Contract Overview")
    
    # Metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Contracts",
            len(st.session_state.uploaded_files),
            delta=None
        )
    
    with col2:
        st.metric(
            "Analysis Complete",
            "0",
            delta="0"
        )
    
    with col3:
        st.metric(
            "High Risk Issues",
            "0",
            delta="0"
        )
    
    with col4:
        st.metric(
            "Compliance Score",
            "N/A",
            delta=None
        )
    
    # Contract list
    st.markdown("### 📄 Uploaded Contracts")
    
    for i, file in enumerate(st.session_state.uploaded_files):
        with st.expander(f"📄 {file.name}", expanded=i == 0):
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                st.write(f"**File Size:** {file.size:,} bytes")
                st.write(f"**Type:** {file.type or 'Unknown'}")
                st.write("**Status:** ⏳ Pending Analysis")
            
            with col2:
                if st.button(f"🔍 Analyze", key=f"dashboard_analyze_{i}"):
                    st.info("🚀 Analysis starting soon! (Stage 3)")
            
            with col3:
                if st.button(f"📝 Report", key=f"dashboard_report_{i}"):
                    st.info("📄 Report generation coming soon!")

with tab2:
    st.markdown("### 📈 Risk Analysis")
    
    # Risk overview
    st.info("🔧 Risk analysis dashboard will be available after Stage 4 implementation!")
    
    # Placeholder content
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**🎯 Risk Categories**")
        st.markdown("""
        - **Financial Risk**: Payment terms, penalties
        - **Legal Risk**: Liability, indemnification  
        - **Operational Risk**: Performance obligations
        - **Compliance Risk**: Regulatory adherence
        """)
    
    with col2:
        st.markdown("**📊 Risk Metrics**")
        st.markdown("""
        - **Overall Risk Score**: 0-100 scale
        - **Critical Issues**: High priority items
        - **Recommendations**: Mitigation strategies
        - **Trend Analysis**: Risk over time
        """)

with tab3:
    st.markdown("### 👥 Parties & Key Terms")
    
    st.info("📋 Party and terms extraction will be available after Stage 3 implementation!")
    
    # Placeholder structure
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**👥 Contract Parties**")
        st.markdown("""
        - **Primary Party**: Company name, role, jurisdiction
        - **Counterparty**: Company name, role, jurisdiction
        - **Third Parties**: Guarantors, beneficiaries
        - **Contact Information**: Key personnel, addresses
        """)
    
    with col2:
        st.markdown("**💰 Key Financial Terms**")
        st.markdown("""
        - **Contract Value**: Total amount, currency
        - **Payment Terms**: Schedule, conditions
        - **Penalties**: Late fees, breach damages
        - **Pricing**: Rates, adjustments, escalations
        """)

with tab4:
    st.markdown("### 📅 Obligations & Deadlines")
    
    st.info("📅 Obligation tracking will be available after Stage 4 implementation!")
    
    # Calendar placeholder
    st.markdown("**📅 Upcoming Deadlines**")
    st.markdown("""
    This section will show:
    - Critical contract deadlines
    - Renewal dates
    - Performance milestones
    - Compliance checkpoints
    """)
    
    # Obligations table placeholder
    st.markdown("**📋 All Obligations**")
    st.markdown("""
    | Party | Obligation | Deadline | Status |
    |-------|------------|----------|--------|
    | - | No obligations extracted yet | - | Pending |
    """)

# Action buttons
st.markdown("---")
st.markdown("### 🚀 Quick Actions")

col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("⚖️ Run Compliance Check"):
        st.switch_page("pages/3_⚖️_Compliance_Check.py")

with col2:
    if st.button("🔄 Compare Contracts"):
        st.switch_page("pages/4_🔄_Compare_Contracts.py")

with col3:
    if st.button("📝 Generate Report"):
        st.switch_page("pages/5_📝_Reports.py")

with col4:
    if st.button("📄 Upload More"):
        st.switch_page("pages/1_📄_Upload_Contract.py")

# Footer
st.markdown("---")
st.caption("💡 **Tip**: Analysis results will update automatically as contracts are processed.")