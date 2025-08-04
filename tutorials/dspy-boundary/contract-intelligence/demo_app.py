"""Simplified demo app to showcase Silicon Valley UI transformation."""

import streamlit as st
import time
from datetime import datetime
from pathlib import Path

# Mock settings class for demo
class MockSettings:
    app_name = "Contract Intelligence Platform"
    app_version = "1.0.0"
    debug = True
    max_file_size_mb = 50
    max_pages_per_document = 100
    analysis_timeout_seconds = 30

settings = MockSettings()

# Import our design components
sys_path = Path(__file__).parent
import sys
sys.path.insert(0, str(sys_path))

try:
    from app.components.design_system import apply_design_system, create_card, create_button, create_metric_card
    from app.components.responsive_layout import create_responsive_header, create_responsive_card_grid
    from app.components.animations import get_animation_css, create_floating_action_button
    from app.components.theme_system import get_theme_css, create_theme_toggle
except ImportError:
    # Fallback if components not available
    def apply_design_system(): pass
    def create_card(content): return f"<div style='padding: 20px; background: white; border-radius: 10px; margin: 10px 0; box-shadow: 0 2px 10px rgba(0,0,0,0.1);'>{content}</div>"
    def create_button(text, variant="primary", icon=""): return f"<button style='background: #6366f1; color: white; border: none; padding: 10px 20px; border-radius: 6px; cursor: pointer;'>{icon} {text}</button>"
    def create_metric_card(title, value, icon=""): return create_card(f"<div style='text-align: center;'><div style='font-size: 2rem;'>{icon}</div><h3>{title}</h3><p style='font-size: 1.5rem; font-weight: bold; color: #6366f1;'>{value}</p></div>")
    def create_responsive_header(title, subtitle="", actions=[]): return f"<div style='text-align: center; padding: 40px; background: linear-gradient(135deg, #6366f1, #8b5cf6); color: white; border-radius: 20px; margin-bottom: 30px;'><h1>{title}</h1><p>{subtitle}</p></div>"
    def create_responsive_card_grid(cards, columns={}): return "<div style='display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px;'>" + "".join(cards) + "</div>"
    def get_animation_css(): return "<style>.hover-lift:hover { transform: translateY(-4px); transition: transform 0.2s ease; } .animate-fade-in-up { animation: fadeInUp 0.6s ease-out; } @keyframes fadeInUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }</style>"
    def create_floating_action_button(icon, tooltip, position): return f"<div style='position: fixed; bottom: 20px; right: 20px; background: #6366f1; color: white; width: 56px; height: 56px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 1.5rem; box-shadow: 0 4px 12px rgba(99, 102, 241, 0.4); cursor: pointer;'>{icon}</div>"
    def get_theme_css(): return "<style>:root { --primary: #6366f1; --secondary: #8b5cf6; --accent: #06b6d4; --success: #10b981; --warning: #f59e0b; --error: #ef4444; --gray-50: #f9fafb; --text-primary: #1f2937; --text-secondary: #6b7280; --surface-secondary: #f8fafc; --space-4: 1rem; --space-6: 1.5rem; --radius-lg: 0.5rem; --radius-xl: 0.75rem; }</style>"
    def create_theme_toggle(): return "<div style='position: fixed; top: 20px; right: 20px; background: white; border: 1px solid #ccc; border-radius: 50%; width: 48px; height: 48px; display: flex; align-items: center; justify-content: center; cursor: pointer; box-shadow: 0 2px 10px rgba(0,0,0,0.1);'>🌙</div>"

st.set_page_config(
    page_title="Contract Intelligence - Silicon Valley Demo",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Apply Silicon Valley design system
apply_design_system()
st.markdown(get_theme_css(), unsafe_allow_html=True)
st.markdown(get_animation_css(), unsafe_allow_html=True)
st.markdown(create_theme_toggle(), unsafe_allow_html=True)

# Initialize session state
if 'page' not in st.session_state:
    st.session_state.page = 'home'
if 'uploaded_files' not in st.session_state:
    st.session_state.uploaded_files = []
if 'processed_docs' not in st.session_state:
    st.session_state.processed_docs = []

# Sidebar navigation
with st.sidebar:
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #6366f1, #8b5cf6);
        color: white;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
        text-align: center;
    ">
        <h3 style="margin: 0; font-weight: 700;">🏠 Navigation</h3>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("🏠 Home", use_container_width=True):
        st.session_state.page = 'home'
        st.rerun()
    
    if st.button("📄 Upload Contract", use_container_width=True):
        st.session_state.page = 'upload'
        st.rerun()
    
    if st.button("📊 Analysis Dashboard", use_container_width=True):
        st.session_state.page = 'dashboard'
        st.rerun()
    
    if st.button("⚖️ Compliance Check", use_container_width=True):
        st.session_state.page = 'compliance'
        st.rerun()
    
    # Stats
    st.markdown("<h4 style='color: #6366f1; margin: 30px 0 15px 0;'>📊 Quick Stats</h4>", unsafe_allow_html=True)
    
    stats_card = create_metric_card("Uploaded", str(len(st.session_state.uploaded_files)), "📄")
    st.markdown(stats_card, unsafe_allow_html=True)
    
    stats_card2 = create_metric_card("Processed", str(len(st.session_state.processed_docs)), "✅")
    st.markdown(stats_card2, unsafe_allow_html=True)

# Main content based on selected page
if st.session_state.page == 'home':
    # Home page with Silicon Valley design
    header_content = create_responsive_header(
        title="⚖️ Contract Intelligence Platform",
        subtitle="AI-powered contract analysis with Silicon Valley design aesthetics - Stage 4 Demo"
    )
    st.markdown(header_content, unsafe_allow_html=True)
    
    # Welcome section
    welcome_content = create_card("""
        <div class="animate-fade-in-up" style="text-align: center;">
            <h2 style="color: var(--primary); font-weight: 700; margin-bottom: 20px;">
                🎨 Silicon Valley Transformation Complete
            </h2>
            <p style="font-size: 1.125rem; line-height: 1.6; color: var(--text-secondary);">
                Experience the complete UI transformation with modern design system, responsive layouts, 
                smooth animations, and premium aesthetics that match Silicon Valley SaaS standards.
            </p>
        </div>
    """)
    st.markdown(welcome_content, unsafe_allow_html=True)
    
    # Feature showcase
    st.markdown("<h3 style='color: var(--primary); margin: 40px 0 20px 0; font-weight: 700; text-align: center;'>🚀 Platform Features</h3>", unsafe_allow_html=True)
    
    feature_cards = [
        create_card("""
            <div class="animate-fade-in-up hover-lift" style="text-align: center;">
                <div style="font-size: 3rem; margin-bottom: 20px; color: var(--primary);">📄</div>
                <h4 style="color: var(--text-primary); font-weight: 600; margin-bottom: 15px;">Smart Upload</h4>
                <p style="color: var(--text-secondary); line-height: 1.6;">
                    Drag & drop interface with real-time processing, validation, and beautiful progress indicators.
                </p>
            </div>
        """),
        create_card("""
            <div class="animate-fade-in-up hover-lift" style="text-align: center; animation-delay: 0.1s;">
                <div style="font-size: 3rem; margin-bottom: 20px; color: var(--secondary);">📊</div>
                <h4 style="color: var(--text-primary); font-weight: 600; margin-bottom: 15px;">Dynamic Dashboard</h4>
                <p style="color: var(--text-secondary); line-height: 1.6;">
                    Interactive data visualizations with responsive charts and modern metric displays.
                </p>
            </div>
        """),
        create_card("""
            <div class="animate-fade-in-up hover-lift" style="text-align: center; animation-delay: 0.2s;">
                <div style="font-size: 3rem; margin-bottom: 20px; color: var(--accent);">🌓</div>
                <h4 style="color: var(--text-primary); font-weight: 600; margin-bottom: 15px;">Theme System</h4>
                <p style="color: var(--text-secondary); line-height: 1.6;">
                    Dark/light theme toggle with smooth transitions and system preference detection.
                </p>
            </div>
        """)
    ]
    
    cards_grid = create_responsive_card_grid(feature_cards)
    st.markdown(cards_grid, unsafe_allow_html=True)

elif st.session_state.page == 'upload':
    # Upload page demo
    header_content = create_responsive_header(
        title="📄 Upload & Analyze Contract",
        subtitle="Experience the modern file upload with Silicon Valley UX design"
    )
    st.markdown(header_content, unsafe_allow_html=True)
    
    # Upload section
    upload_section = create_card("""
        <div class="animate-fade-in-up" style="text-align: center;">
            <h3 style="color: var(--primary); font-weight: 700; margin-bottom: 30px; font-size: 1.5rem;">
                📁 Document Upload
            </h3>
            <div style="
                border: 2px dashed var(--primary);
                border-radius: 20px;
                padding: 60px;
                background: var(--surface-secondary);
                transition: all 0.3s ease;
                margin-bottom: 30px;
            " class="hover-lift">
                <div style="font-size: 4rem; margin-bottom: 20px; color: var(--primary);">📁</div>
                <h4 style="color: var(--text-primary); margin-bottom: 15px; font-weight: 600;">
                    Drag and drop files here
                </h4>
                <p style="color: var(--text-secondary); margin-bottom: 20px;">
                    or click below to browse files
                </p>
                <div style="
                    background: var(--gray-50);
                    padding: 15px;
                    border-radius: 10px;
                    margin: 20px 0;
                    font-size: 0.875rem;
                    color: var(--text-secondary);
                ">
                    <strong>Supported:</strong> PDF, DOCX, DOC, TXT • <strong>Max size:</strong> 50MB
                </div>
            </div>
        </div>
    """)
    st.markdown(upload_section, unsafe_allow_html=True)
    
    # File uploader
    uploaded_files = st.file_uploader(
        "Choose contract files",
        type=['pdf', 'docx', 'doc', 'txt'],
        accept_multiple_files=True,
        label_visibility="collapsed"
    )
    
    if uploaded_files:
        st.session_state.uploaded_files = uploaded_files
        
        # Success notification
        success_notification = create_card(f"""
            <div class="animate-fade-in-up" style="
                background: linear-gradient(135deg, var(--success), var(--accent));
                color: white;
                padding: 30px;
                border-radius: 20px;
                text-align: center;
                margin: 30px 0;
            ">
                <div style="font-size: 2.5rem; margin-bottom: 15px;">🎉</div>
                <h3 style="margin: 0; font-weight: 700; font-size: 1.25rem;">
                    {len(uploaded_files)} file(s) uploaded successfully!
                </h3>
                <p style="margin: 10px 0 0 0; opacity: 0.9; font-size: 0.875rem;">
                    Ready for AI-powered processing and analysis
                </p>
            </div>
        """)
        st.markdown(success_notification, unsafe_allow_html=True)
        
        # Process button
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button(f"🚀 Process All {len(uploaded_files)} Files", type="primary", use_container_width=True):
                # Processing simulation
                progress_container = st.empty()
                
                for i, file in enumerate(uploaded_files):
                    progress_container.markdown(f"""
                    <div class="animate-fade-in-up" style="
                        background: white;
                        padding: 20px;
                        border-radius: 15px;
                        border-left: 4px solid var(--primary);
                        margin: 20px 0;
                        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                    ">
                        <div style="display: flex; align-items: center; gap: 15px;">
                            <div style="color: var(--primary); font-size: 1.5rem;">⚙️</div>
                            <div>
                                <strong>Processing {file.name}</strong><br>
                                <span style="color: var(--text-secondary); font-size: 0.875rem;">AI-powered analysis in progress...</span>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    time.sleep(1)
                
                # Success message
                progress_container.markdown("""
                <div class="animate-fade-in-up" style="
                    background: linear-gradient(135deg, var(--success), var(--accent));
                    color: white;
                    padding: 40px;
                    border-radius: 20px;
                    text-align: center;
                    margin: 30px 0;
                ">
                    <div style="font-size: 3rem; margin-bottom: 20px;">✨</div>
                    <h3 style="margin: 0 0 15px 0; font-weight: 700; font-size: 1.5rem;">
                        Processing Complete!
                    </h3>
                    <p style="margin: 0; opacity: 0.9; font-size: 1rem;">
                        All documents have been successfully processed and analyzed
                    </p>
                </div>
                """, unsafe_allow_html=True)
                
                st.session_state.processed_docs = uploaded_files
                time.sleep(2)
                st.rerun()

elif st.session_state.page == 'dashboard':
    # Dashboard demo
    header_content = create_responsive_header(
        title="📊 Analysis Dashboard",
        subtitle="Modern data visualization with Silicon Valley aesthetics"
    )
    st.markdown(header_content, unsafe_allow_html=True)
    
    # Metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        metric_card = create_metric_card("Total Contracts", "156", "📄")
        st.markdown(metric_card, unsafe_allow_html=True)
    
    with col2:
        metric_card = create_metric_card("Processed Today", "12", "⚡")
        st.markdown(metric_card, unsafe_allow_html=True)
    
    with col3:
        metric_card = create_metric_card("Compliance Rate", "94.2%", "⚖️")
        st.markdown(metric_card, unsafe_allow_html=True)
    
    with col4:
        metric_card = create_metric_card("Risk Score", "Low", "🛡️")
        st.markdown(metric_card, unsafe_allow_html=True)
    
    # Chart placeholder
    chart_content = create_card("""
        <div class="animate-fade-in-up" style="text-align: center; padding: 60px;">
            <div style="font-size: 4rem; margin-bottom: 20px; color: var(--primary);">📈</div>
            <h3 style="color: var(--primary); margin-bottom: 15px;">Interactive Data Visualizations</h3>
            <p style="color: var(--text-secondary);">
                Real-time charts and analytics would be displayed here with responsive design
                and smooth animations. Features include contract trend analysis, risk assessment charts,
                and compliance monitoring dashboards.
            </p>
        </div>
    """)
    st.markdown(chart_content, unsafe_allow_html=True)

elif st.session_state.page == 'compliance':
    # Compliance demo
    header_content = create_responsive_header(
        title="⚖️ Compliance Check",
        subtitle="Automated compliance verification with modern UI"
    )
    st.markdown(header_content, unsafe_allow_html=True)
    
    compliance_content = create_card("""
        <div class="animate-fade-in-up" style="text-align: center; padding: 60px;">
            <div style="font-size: 4rem; margin-bottom: 20px; color: var(--secondary);">⚖️</div>
            <h3 style="color: var(--primary); margin-bottom: 15px;">Compliance Dashboard</h3>
            <p style="color: var(--text-secondary); margin-bottom: 30px;">
                Advanced compliance checking with industry standards, regulatory requirements,
                and custom policy validation - all with Silicon Valley design aesthetics.
            </p>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-top: 30px;">
                <div style="background: var(--surface-secondary); padding: 20px; border-radius: 10px; border-left: 4px solid var(--success);">
                    <h4 style="color: var(--success); margin: 0 0 10px 0;">✅ GDPR Compliant</h4>
                    <p style="color: var(--text-secondary); margin: 0; font-size: 0.875rem;">All data protection requirements met</p>
                </div>
                <div style="background: var(--surface-secondary); padding: 20px; border-radius: 10px; border-left: 4px solid var(--warning);">
                    <h4 style="color: var(--warning); margin: 0 0 10px 0;">⚠️ SOX Review Needed</h4>
                    <p style="color: var(--text-secondary); margin: 0; font-size: 0.875rem;">Financial controls require review</p>
                </div>
                <div style="background: var(--surface-secondary); padding: 20px; border-radius: 10px; border-left: 4px solid var(--success);">
                    <h4 style="color: var(--success); margin: 0 0 10px 0;">✅ Legal Approved</h4>
                    <p style="color: var(--text-secondary); margin: 0; font-size: 0.875rem;">Standard terms and conditions validated</p>
                </div>
            </div>
        </div>
    """)
    st.markdown(compliance_content, unsafe_allow_html=True)

# Add floating action button
fab = create_floating_action_button("📄", "Quick Upload", "bottom-right")
st.markdown(fab, unsafe_allow_html=True)

# Footer
st.markdown("""---""")
footer_content = create_card(f"""
    <div style="text-align: center;">
        <h4 style="color: var(--primary); margin-bottom: 15px;">🎉 Stage 4 Complete - Dynamic Silicon Valley UI</h4>
        <p style="color: var(--text-secondary); margin: 0;">
            Modern Streamlit application with responsive design, theme switching, animations, and premium aesthetics.
            Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        </p>
    </div>
""")
st.markdown(footer_content, unsafe_allow_html=True)