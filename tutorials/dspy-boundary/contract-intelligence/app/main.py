"""Main Streamlit application for Contract Intelligence Platform."""

import streamlit as st
import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config.settings import settings

# Page configuration
st.set_page_config(
    page_title=settings.app_name,
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://docs.contractintelligence.com',
        'Report a bug': 'https://github.com/your-org/contract-intelligence/issues',
        'About': f"{settings.app_name} v{settings.app_version} - AI-powered contract analysis"
    }
)

# Custom CSS for professional legal theme
st.markdown("""
<style>
    /* Main theme colors */
    :root {
        --primary-color: #1e3a8a;
        --secondary-color: #3b82f6;
        --accent-color: #f59e0b;
        --success-color: #10b981;
        --warning-color: #f59e0b;
        --error-color: #ef4444;
        --text-primary: #1f2937;
        --text-secondary: #6b7280;
        --background: #f8fafc;
        --card-background: #ffffff;
    }
    
    /* Main container styling */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }
    
    /* Header styling */
    .app-header {
        background: linear-gradient(90deg, var(--primary-color), var(--secondary-color));
        color: white;
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        text-align: center;
    }
    
    .app-header h1 {
        margin: 0;
        font-size: 2.5rem;
        font-weight: 700;
    }
    
    .app-header p {
        margin: 0.5rem 0 0 0;
        font-size: 1.2rem;
        opacity: 0.9;
    }
    
    /* Feature cards */
    .feature-card {
        background: var(--card-background);
        border: 1px solid #e5e7eb;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        transition: transform 0.2s, box-shadow 0.2s;
    }
    
    .feature-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
    }
    
    .feature-icon {
        font-size: 2.5rem;
        margin-bottom: 1rem;
    }
    
    .feature-title {
        font-size: 1.3rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
        color: var(--primary-color);
    }
    
    .feature-description {
        color: var(--text-secondary);
        line-height: 1.5;
    }
    
    /* Sidebar styling */
    .sidebar .sidebar-content {
        background: var(--background);
    }
    
    /* Button styling */
    .stButton > button {
        background: var(--primary-color);
        color: white;
        border: none;
        border-radius: 5px;
        padding: 0.5rem 1rem;
        font-weight: 600;
        transition: background 0.2s;
    }
    
    .stButton > button:hover {
        background: var(--secondary-color);
    }
    
    /* Info boxes */
    .info-box {
        background: #dbeafe;
        border-left: 4px solid var(--secondary-color);
        padding: 1rem;
        border-radius: 0 5px 5px 0;
        margin: 1rem 0;
    }
    
    .success-box {
        background: #d1fae5;
        border-left: 4px solid var(--success-color);
        padding: 1rem;
        border-radius: 0 5px 5px 0;
        margin: 1rem 0;
    }
    
    .warning-box {
        background: #fef3c7;
        border-left: 4px solid var(--warning-color);
        padding: 1rem;
        border-radius: 0 5px 5px 0;
        margin: 1rem 0;
    }
    
    /* Metrics styling */
    .metric-card {
        background: var(--card-background);
        border: 1px solid #e5e7eb;
        border-radius: 8px;
        padding: 1rem;
        text-align: center;
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: var(--primary-color);
    }
    
    .metric-label {
        color: var(--text-secondary);
        font-size: 0.9rem;
        margin-top: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'uploaded_files' not in st.session_state:
    st.session_state.uploaded_files = []
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = {}

# Modern responsive sidebar
with st.sidebar:
    # Navigation header
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, var(--primary), var(--secondary));
        color: white;
        padding: var(--space-4);
        border-radius: var(--radius-lg);
        margin-bottom: var(--space-6);
        text-align: center;
    ">
        <h3 style="margin: 0; font-weight: 700;">🏠 Navigation</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Application status with modern styling
    if settings.debug:
        st.markdown("""
        <div style="
            background: var(--warning);
            color: white;
            padding: var(--space-3);
            border-radius: var(--radius-md);
            margin-bottom: var(--space-4);
            text-align: center;
            font-weight: 500;
        ">
            🔧 Development Mode
        </div>
        """, unsafe_allow_html=True)
    
    # Quick stats with metric cards
    st.markdown("<h4 style='color: var(--primary); margin: var(--space-6) 0 var(--space-4) 0;'>📊 Quick Stats</h4>", unsafe_allow_html=True)
    
    stats_cards = [
        create_metric_card("Documents", str(len(st.session_state.uploaded_files)), icon="📄"),
        create_metric_card("Analyses", str(len(st.session_state.analysis_results)), icon="📊")
    ]
    
    for card in stats_cards:
        st.markdown(card, unsafe_allow_html=True)
    
    # Feature toggles with modern badges
    st.markdown("<h4 style='color: var(--primary); margin: var(--space-6) 0 var(--space-4) 0;'>⚙️ Features</h4>", unsafe_allow_html=True)
    
    features = [
        ("OCR", settings.enable_ocr),
        ("Comparison", settings.enable_comparison),
        ("Redlining", settings.enable_redlining),
        ("Collaboration", settings.enable_collaboration)
    ]
    
    for feature_name, enabled in features:
        status_text = "✅ Enabled" if enabled else "❌ Disabled"
        status_color = "var(--success)" if enabled else "var(--gray-500)"
        st.markdown(f"""
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: var(--space-2);">
            <span style="color: var(--text-primary); font-weight: 500;">{feature_name}:</span>
            <span style="color: {status_color}; font-weight: 500; font-size: 0.875rem;">{status_text}</span>
        </div>
        """, unsafe_allow_html=True)
    
    # Help section with modern links
    st.markdown("<h4 style='color: var(--primary); margin: var(--space-6) 0 var(--space-4) 0;'>🔗 Quick Links</h4>", unsafe_allow_html=True)
    
    links = [
        ("📖 User Guide", "https://docs.contractintelligence.com"),
        ("🎥 Video Tutorials", "https://tutorials.contractintelligence.com"),
        ("💬 Support", "mailto:support@contractintelligence.com")
    ]
    
    for link_text, link_url in links:
        st.markdown(f"""
        <a href="{link_url}" target="_blank" style="
            display: block;
            padding: var(--space-3);
            margin-bottom: var(--space-2);
            background: var(--surface-secondary);
            color: var(--text-primary);
            text-decoration: none;
            border-radius: var(--radius-md);
            border: 1px solid var(--border-primary);
            transition: all 0.2s ease;
            font-weight: 500;
        " class="hover-lift">
            {link_text}
        </a>
        """, unsafe_allow_html=True)

# Main content area
def main():
    """Main application content."""
    
    # Header
    st.markdown("""
    <div class="app-header">
        <h1>⚖️ Contract Intelligence Platform</h1>
        <p>AI-powered contract analysis, risk assessment, and compliance checking</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Welcome message
    st.markdown("## Welcome to Contract Intelligence Platform")
    st.markdown("""
    Transform your contract review process with AI-powered analysis. Upload contracts, 
    get instant insights, assess risks, and ensure compliance with just a few clicks.
    """)
    
    # Feature cards
    st.markdown("### 🚀 Platform Features")
    
    # Row 1: Core features
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">📄</div>
            <div class="feature-title">Document Analysis</div>
            <div class="feature-description">
                Upload and analyze contracts instantly. Extract key terms, parties, 
                dates, and obligations with AI precision.
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("📄 Analyze Document", key="analyze_btn"):
            st.switch_page("pages/1_📄_Upload_Contract.py")
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">⚖️</div>
            <div class="feature-title">Risk Assessment</div>
            <div class="feature-description">
                Identify potential risks, liability issues, and compliance gaps 
                before you sign.
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("⚖️ Assess Risks", key="risk_btn"):
            st.switch_page("pages/3_⚖️_Compliance_Check.py")
    
    with col3:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">🔄</div>
            <div class="feature-title">Contract Comparison</div>
            <div class="feature-description">
                Compare contract versions side-by-side and identify critical 
                changes and their impact.
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🔄 Compare Contracts", key="compare_btn"):
            st.switch_page("pages/4_🔄_Compare_Contracts.py")
    
    # Row 2: Advanced features  
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">✏️</div>
            <div class="feature-title">Automated Redlining</div>
            <div class="feature-description">
                Get AI-powered suggestions for contract improvements and 
                risk mitigation strategies.
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("✏️ Review & Redline", key="redline_btn"):
            st.info("Redlining feature coming in Stage 7!")
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">📊</div>
            <div class="feature-title">Analytics Dashboard</div>
            <div class="feature-description">
                View comprehensive analytics and reports on your contract 
                portfolio and compliance status.
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("📊 View Dashboard", key="dashboard_btn"):
            st.switch_page("pages/2_📊_Analysis_Dashboard.py")
    
    with col3:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">📝</div>
            <div class="feature-title">Generate Reports</div>
            <div class="feature-description">
                Create professional reports for stakeholders with executive 
                summaries and detailed findings.
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("📝 Generate Report", key="report_btn"):
            st.switch_page("pages/5_📝_Reports.py")
    
    # Getting started section
    st.markdown("### 🚀 Getting Started")
    
    with st.expander("📖 Quick Start Guide", expanded=False):
        st.markdown("""
        1. **Upload a Contract**: Click on "📄 Analyze Document" and upload your contract (PDF, DOCX, or TXT)
        2. **Review Analysis**: Get instant insights on parties, terms, obligations, and risks
        3. **Check Compliance**: Run automated compliance checks against industry standards
        4. **Compare Versions**: Upload multiple versions to see changes and their impact
        5. **Generate Reports**: Create professional reports for stakeholders
        
        **Tip**: Start with a simple contract to familiarize yourself with the platform!
        """)
    
    with st.expander("📋 Sample Documents", expanded=False):
        st.markdown("""
        Try these sample contract types:
        - **Service Agreement**: Professional services contract template
        - **NDA**: Non-disclosure agreement template  
        - **Software License**: SaaS agreement template
        - **Employment Contract**: Standard employment agreement
        
        [📥 Download Sample Contracts](https://samples.contractintelligence.com)
        """)
    
    # System status with modern design
    if settings.debug:
        st.markdown("<h3 style='color: var(--primary); margin: var(--space-8) 0 var(--space-4) 0;'>🔧 System Information</h3>", unsafe_allow_html=True)
        
        debug_content = create_card(f"""
            <h4 style="color: var(--primary); margin-bottom: var(--space-4);">Debug Information</h4>
            <div style="background: var(--gray-50); padding: var(--space-4); border-radius: var(--radius-md); font-family: var(--font-mono); font-size: 0.875rem;">
                <strong>App Version:</strong> {settings.app_version}<br>
                <strong>Environment:</strong> {settings.environment}<br><br>
                <strong>Features:</strong><br>
                • OCR: {'✅' if settings.enable_ocr else '❌'}<br>
                • Comparison: {'✅' if settings.enable_comparison else '❌'}<br>
                • Redlining: {'✅' if settings.enable_redlining else '❌'}<br>
                • Collaboration: {'✅' if settings.enable_collaboration else '❌'}<br><br>
                <strong>Limits:</strong><br>
                • Max File Size: {settings.max_file_size_mb} MB<br>
                • Max Pages: {settings.max_pages_per_document}<br>
                • Analysis Timeout: {settings.analysis_timeout_seconds}s
            </div>
        """)
        
        with st.expander("🔧 Debug Information", expanded=False):
            st.markdown(debug_content, unsafe_allow_html=True)
    
    # Add floating action button for quick upload
    fab = create_floating_action_button(
        icon="📄", 
        tooltip="Quick Upload", 
        position="bottom-right"
    )
    st.markdown(fab, unsafe_allow_html=True)
    
    # Add mobile navigation
    mobile_nav = """
    <div class="mobile-nav">
        <div class="mobile-nav-items">
            <a href="#" class="mobile-nav-item active">
                <div class="mobile-nav-icon">🏠</div>
                <span>Home</span>
            </a>
            <a href="#" class="mobile-nav-item" onclick="window.parent.postMessage({type: 'streamlit:setPage', page: 'pages/1_📄_Upload_Contract.py'}, '*')">
                <div class="mobile-nav-icon">📄</div>
                <span>Upload</span>
            </a>
            <a href="#" class="mobile-nav-item" onclick="window.parent.postMessage({type: 'streamlit:setPage', page: 'pages/2_📊_Analysis_Dashboard.py'}, '*')">
                <div class="mobile-nav-icon">📊</div>
                <span>Dashboard</span>
            </a>
            <a href="#" class="mobile-nav-item" onclick="window.parent.postMessage({type: 'streamlit:setPage', page: 'pages/3_⚖️_Compliance_Check.py'}, '*')">
                <div class="mobile-nav-icon">⚖️</div>
                <span>Compliance</span>
            </a>
            <a href="#" class="mobile-nav-item" onclick="window.parent.postMessage({type: 'streamlit:setPage', page: 'pages/5_📝_Reports.py'}, '*')">
                <div class="mobile-nav-icon">📝</div>
                <span>Reports</span>
            </a>
        </div>
    </div>
    """
    st.markdown(mobile_nav, unsafe_allow_html=True)

if __name__ == "__main__":
    main()