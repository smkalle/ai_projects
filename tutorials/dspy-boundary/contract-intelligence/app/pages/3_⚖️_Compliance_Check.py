"""Compliance checking page."""

import streamlit as st
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from config.settings import settings

st.set_page_config(
    page_title="Compliance Check - Contract Intelligence",
    page_icon="⚖️",
    layout="wide"
)

st.title("⚖️ Compliance Check")
st.markdown("Verify your contracts against regulations and company policies")

# Check if files have been uploaded
if not st.session_state.get('uploaded_files'):
    st.warning("⚠️ No contracts uploaded yet. Please upload contracts first.")
    if st.button("📄 Upload Contracts"):
        st.switch_page("pages/1_📄_Upload_Contract.py")
    st.stop()

# Compliance check interface
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("### 📋 Select Contract for Compliance Review")
    
    # Contract selector
    if st.session_state.uploaded_files:
        selected_contract = st.selectbox(
            "Choose contract to review:",
            options=range(len(st.session_state.uploaded_files)),
            format_func=lambda x: st.session_state.uploaded_files[x].name
        )
        
        if selected_contract is not None:
            file = st.session_state.uploaded_files[selected_contract]
            st.info(f"Selected: **{file.name}** ({file.size:,} bytes)")

with col2:
    st.markdown("### ⚙️ Compliance Settings")
    
    # Regulation checkboxes
    st.markdown("**📜 Regulations to Check:**")
    check_gdpr = st.checkbox("🇪🇺 GDPR (EU Data Protection)", value=True)
    check_ccpa = st.checkbox("🇺🇸 CCPA (California Privacy)", value=True)
    check_sox = st.checkbox("📊 SOX (Sarbanes-Oxley)", value=False)
    check_hipaa = st.checkbox("🏥 HIPAA (Healthcare)", value=False)
    
    st.markdown("**🏢 Company Policies:**")
    check_security = st.checkbox("🔒 Security Policy", value=True)
    check_procurement = st.checkbox("💼 Procurement Policy", value=True)
    check_legal = st.checkbox("⚖️ Legal Standards", value=True)

# Compliance check tabs
tab1, tab2, tab3 = st.tabs(["🚀 Run Check", "📊 Results", "📋 Policy Library"])

with tab1:
    st.markdown("### 🚀 Start Compliance Review")
    
    if st.button("▶️ Run Compliance Check", type="primary"):
        st.info("🔧 Compliance checking will be implemented in Stage 5!")
        
        # Progress placeholder
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        import time
        for i in range(101):
            progress_bar.progress(i)
            if i < 30:
                status_text.text(f"📄 Processing document... {i}%")
            elif i < 60:
                status_text.text(f"🔍 Checking GDPR compliance... {i}%")
            elif i < 90:
                status_text.text(f"⚖️ Reviewing legal standards... {i}%")
            else:
                status_text.text(f"✅ Finalizing report... {i}%")
            time.sleep(0.02)
        
        st.success("✅ Compliance check complete! (Demo)")
    
    # Quick compliance overview
    st.markdown("### 📋 Compliance Overview")
    st.markdown("""
    **What we check:**
    - **Data Protection**: GDPR, CCPA compliance clauses
    - **Security Requirements**: Data security, access controls
    - **Legal Standards**: Jurisdiction, governing law, dispute resolution
    - **Company Policies**: Procurement rules, approval workflows
    - **Industry Regulations**: Sector-specific requirements
    """)

with tab2:
    st.markdown("### 📊 Compliance Results")
    
    # Placeholder results
    st.info("📊 Results will appear here after running compliance check")
    
    # Mock results structure
    st.markdown("**🎯 Overall Compliance Score: Coming Soon**")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**✅ Passed**")
        st.markdown("- Standard clauses present")
        st.markdown("- Proper jurisdiction specified")
        st.markdown("- Basic liability terms")
    
    with col2:
        st.markdown("**⚠️ Warnings**")
        st.markdown("- Missing data protection clause")
        st.markdown("- Unclear termination terms")
        st.markdown("- No force majeure provision")
    
    with col3:
        st.markdown("**❌ Critical Issues**")
        st.markdown("- GDPR compliance gaps")
        st.markdown("- Unlimited liability exposure")
        st.markdown("- No dispute resolution")

with tab3:
    st.markdown("### 📋 Policy Library")
    
    # Policy management interface
    st.markdown("**📁 Available Policies:**")
    
    policies = [
        {"name": "GDPR Compliance Policy", "type": "Regulation", "status": "Active"},
        {"name": "Data Security Standards", "type": "Company", "status": "Active"},
        {"name": "Procurement Guidelines", "type": "Company", "status": "Active"},
        {"name": "Legal Review Checklist", "type": "Company", "status": "Draft"},
    ]
    
    for policy in policies:
        with st.expander(f"📄 {policy['name']} ({policy['type']})"):
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                st.write(f"**Type:** {policy['type']}")
                st.write(f"**Status:** {policy['status']}")
            
            with col2:
                if st.button("✏️ Edit", key=f"edit_{policy['name']}"):
                    st.info("Policy editor coming soon!")
            
            with col3:
                if st.button("👁️ View", key=f"view_{policy['name']}"):
                    st.info("Policy viewer coming soon!")
    
    # Add new policy
    st.markdown("**➕ Add New Policy:**")
    if st.button("📄 Upload Policy Document"):
        st.info("Policy upload feature coming in Stage 5!")

# Action buttons
st.markdown("---")
st.markdown("### 🚀 Next Steps")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("📊 View Full Analysis"):
        st.switch_page("pages/2_📊_Analysis_Dashboard.py")

with col2:
    if st.button("🔄 Compare with Standards"):
        st.switch_page("pages/4_🔄_Compare_Contracts.py")

with col3:
    if st.button("📝 Generate Compliance Report"):
        st.switch_page("pages/5_📝_Reports.py")

# Footer
st.markdown("---")
st.caption("⚖️ **Note**: Compliance checks are advisory only. Always consult legal counsel for final review.")