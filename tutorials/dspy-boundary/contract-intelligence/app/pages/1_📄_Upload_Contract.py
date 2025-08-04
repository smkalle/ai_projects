"""Contract upload and initial analysis page with Silicon Valley design."""

import streamlit as st
import sys
import io
from pathlib import Path
from datetime import datetime
import time

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from config.settings import settings
from services.document_parser import document_parser, DocumentParsingError
from services.storage_service import storage_service, StorageError
from app.components.design_system import apply_design_system, create_card, create_button, create_metric_card, create_progress_bar
from app.components.responsive_layout import create_responsive_header, create_responsive_card_grid, create_responsive_container, create_mobile_navigation
from app.components.animations import get_animation_css, create_loading_spinner, create_morphing_button, create_floating_action_button
from app.components.theme_system import get_theme_css, create_theme_toggle

st.set_page_config(
    page_title="Upload Contract - Contract Intelligence",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Apply Silicon Valley design system
apply_design_system()
st.markdown(get_theme_css(), unsafe_allow_html=True)
st.markdown(get_animation_css(), unsafe_allow_html=True)
st.markdown(create_theme_toggle(), unsafe_allow_html=True)

# Modern responsive header
header_content = create_responsive_header(
    title="📄 Upload & Analyze Contract",
    subtitle="Upload your contract documents for AI-powered analysis with real-time processing",
    actions=[
        create_button("📊 View Dashboard", variant="secondary", icon="📊"),
        create_button("⚖️ Check Compliance", variant="primary", icon="⚖️")
    ]
)
st.markdown(header_content, unsafe_allow_html=True)

# Initialize session state
if 'stored_documents' not in st.session_state:
    st.session_state.stored_documents = []
if 'processing_status' not in st.session_state:
    st.session_state.processing_status = {}
if 'upload_progress' not in st.session_state:
    st.session_state.upload_progress = 0
if 'current_processing' not in st.session_state:
    st.session_state.current_processing = None

# Modern upload section with drag & drop styling
upload_section = create_card(f"""
    <div class="animate-fade-in-up" style="text-align: center;">
        <h3 style="color: var(--primary); font-weight: 700; margin-bottom: var(--space-6); font-size: 1.5rem;">
            📁 Document Upload
        </h3>
        <div style="
            border: 2px dashed var(--border-primary);
            border-radius: var(--radius-xl);
            padding: var(--space-8);
            background: var(--surface-secondary);
            transition: all 0.3s ease;
            margin-bottom: var(--space-6);
        " class="hover-lift">
            <div style="font-size: 3rem; margin-bottom: var(--space-4); color: var(--primary);">📁</div>
            <h4 style="color: var(--text-primary); margin-bottom: var(--space-3); font-weight: 600;">
                Drag and drop files here
            </h4>
            <p style="color: var(--text-secondary); margin-bottom: var(--space-4);">
                or click below to browse files
            </p>
            <div style="
                background: var(--gray-100);
                padding: var(--space-3);
                border-radius: var(--radius-md);
                margin: var(--space-4) 0;
                font-size: 0.875rem;
                color: var(--text-secondary);
            ">
                <strong>Supported:</strong> PDF, DOCX, DOC, TXT • <strong>Max size:</strong> {settings.max_file_size_mb}MB
            </div>
        </div>
    </div>
""")
st.markdown(upload_section, unsafe_allow_html=True)

# File uploader with enhanced styling
uploaded_files = st.file_uploader(
    "Choose contract files",
    type=['pdf', 'docx', 'doc', 'txt'],
    accept_multiple_files=True,
    help=f"Maximum file size: {settings.max_file_size_mb}MB. Supported formats: PDF, DOCX, DOC, TXT",
    label_visibility="collapsed"
)

def process_uploaded_file(uploaded_file, progress_container=None):
    """Process a single uploaded file with modern UI feedback."""
    try:
        # Read file data
        file_data = uploaded_file.read()
        uploaded_file.seek(0)  # Reset for display purposes
        
        # Update progress
        if progress_container:
            progress_container.markdown(f"""
            <div class="animate-fade-in-up" style="
                background: var(--surface-elevated);
                padding: var(--space-4);
                border-radius: var(--radius-lg);
                border-left: 4px solid var(--primary);
                margin: var(--space-4) 0;
            ">
                <div style="display: flex; align-items: center; gap: var(--space-3);">
                    <div class="animate-spin" style="color: var(--primary); font-size: 1.5rem;">⚙️</div>
                    <div>
                        <strong>Processing {uploaded_file.name}</strong><br>
                        <span style="color: var(--text-secondary); font-size: 0.875rem;">Validating file...</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Validate file
        validation = document_parser.validate_file(file_data, uploaded_file.name)
        
        if not validation['valid']:
            error_msg = create_card(f"""
                <div style="background: var(--error); color: white; padding: var(--space-4); border-radius: var(--radius-md);">
                    <strong>❌ {uploaded_file.name}</strong><br>
                    {'; '.join(validation['errors'])}
                </div>
            """)
            st.markdown(error_msg, unsafe_allow_html=True)
            return None
        
        if validation['warnings']:
            for warning in validation['warnings']:
                warning_msg = create_card(f"""
                    <div style="background: var(--warning); color: white; padding: var(--space-4); border-radius: var(--radius-md);">
                        <strong>⚠️ {uploaded_file.name}</strong><br>
                        {warning}
                    </div>
                """)
                st.markdown(warning_msg, unsafe_allow_html=True)
        
        # Update progress - storing
        if progress_container:
            progress_container.markdown(f"""
            <div class="animate-fade-in-up" style="
                background: var(--surface-elevated);
                padding: var(--space-4);
                border-radius: var(--radius-lg);
                border-left: 4px solid var(--accent);
                margin: var(--space-4) 0;
            ">
                <div style="display: flex; align-items: center; gap: var(--space-3);">
                    <div class="animate-pulse" style="color: var(--accent); font-size: 1.5rem;">💾</div>
                    <div>
                        <strong>Storing {uploaded_file.name}</strong><br>
                        <span style="color: var(--text-secondary); font-size: 0.875rem;">Saving to secure storage...</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            time.sleep(0.5)  # Simulate processing time
        
        # Store document
        stored_doc = storage_service.store_document(file_data, uploaded_file.name)
        
        # Update progress - parsing
        if progress_container:
            progress_container.markdown(f"""
            <div class="animate-fade-in-up" style="
                background: var(--surface-elevated);
                padding: var(--space-4);
                border-radius: var(--radius-lg);
                border-left: 4px solid var(--success);
                margin: var(--space-4) 0;
            ">
                <div style="display: flex; align-items: center; gap: var(--space-3);">
                    <div class="animate-bounce" style="color: var(--success); font-size: 1.5rem;">🔍</div>
                    <div>
                        <strong>Analyzing {uploaded_file.name}</strong><br>
                        <span style="color: var(--text-secondary); font-size: 0.875rem;">AI-powered content extraction...</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            time.sleep(1.0)  # Simulate processing time
        
        # Parse document
        try:
            parsed_doc = document_parser.parse_document(file_data, uploaded_file.name)
            
            # Store processed data
            storage_service.store_processed_document(stored_doc.doc_id, parsed_doc)
            
            # Success message
            success_msg = create_card(f"""
                <div class="animate-fade-in-up" style="
                    background: linear-gradient(135deg, var(--success), var(--accent));
                    color: white;
                    padding: var(--space-6);
                    border-radius: var(--radius-lg);
                    text-align: center;
                ">
                    <div style="font-size: 2rem; margin-bottom: var(--space-3);">✅</div>
                    <strong style="font-size: 1.125rem;">Successfully processed {uploaded_file.name}</strong><br>
                    <span style="opacity: 0.9; font-size: 0.875rem;">Ready for analysis and compliance checking</span>
                </div>
            """)
            if progress_container:
                progress_container.markdown(success_msg, unsafe_allow_html=True)
            else:
                st.markdown(success_msg, unsafe_allow_html=True)
            
            return stored_doc, parsed_doc
            
        except DocumentParsingError as e:
            error_msg = create_card(f"""
                <div style="background: var(--error); color: white; padding: var(--space-4); border-radius: var(--radius-md);">
                    <strong>❌ Failed to parse {uploaded_file.name}</strong><br>
                    {str(e)}
                </div>
            """)
            st.markdown(error_msg, unsafe_allow_html=True)
            storage_service.update_document_status(stored_doc.doc_id, "error")
            return stored_doc, None
            
    except Exception as e:
        error_msg = create_card(f"""
            <div style="background: var(--error); color: white; padding: var(--space-4); border-radius: var(--radius-md);">
                <strong>❌ Error processing {uploaded_file.name}</strong><br>
                {str(e)}
            </div>
        """)
        st.markdown(error_msg, unsafe_allow_html=True)
        return None

if uploaded_files:
    # Success notification with modern styling
    success_notification = create_card(f"""
        <div class="animate-fade-in-up" style="
            background: linear-gradient(135deg, var(--success), var(--accent));
            color: white;
            padding: var(--space-6);
            border-radius: var(--radius-xl);
            text-align: center;
            margin: var(--space-6) 0;
        ">
            <div style="font-size: 2.5rem; margin-bottom: var(--space-3);">🎉</div>
            <h3 style="margin: 0; font-weight: 700; font-size: 1.25rem;">
                {len(uploaded_files)} file(s) uploaded successfully!
            </h3>
            <p style="margin: var(--space-2) 0 0 0; opacity: 0.9; font-size: 0.875rem;">
                Ready for AI-powered processing and analysis
            </p>
        </div>
    """)
    st.markdown(success_notification, unsafe_allow_html=True)
    
    # Modern process button with morphing animation
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        # Traditional button for actual functionality
        if st.button(f"🚀 Process All {len(uploaded_files)} Files", type="primary", use_container_width=True):
            # Create progress container
            progress_container = st.empty()
            
            # Modern progress header
            progress_container.markdown("""
            <div class="animate-fade-in-up" style="
                background: var(--surface-elevated);
                padding: var(--space-6);
                border-radius: var(--radius-xl);
                margin: var(--space-6) 0;
                text-align: center;
            ">
                <h3 style="color: var(--primary); margin-bottom: var(--space-4); font-weight: 700;">
                    🚀 Processing Documents
                </h3>
                <div style="
                    background: var(--gray-200);
                    height: 8px;
                    border-radius: var(--radius-full);
                    overflow: hidden;
                    margin: var(--space-4) 0;
                ">
                    <div id="progress-fill" style="
                        height: 100%;
                        background: linear-gradient(90deg, var(--primary), var(--secondary));
                        width: 0%;
                        transition: width 0.5s ease;
                        border-radius: var(--radius-full);
                    "></div>
                </div>
                <p style="color: var(--text-secondary); margin: 0; font-size: 0.875rem;">
                    Preparing documents for AI analysis...
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            processed_docs = []
            
            for i, uploaded_file in enumerate(uploaded_files):
                result = process_uploaded_file(uploaded_file, progress_container)
                if result:
                    processed_docs.append(result)
            
            # Final success message
            progress_container.markdown("""
            <div class="animate-fade-in-up" style="
                background: linear-gradient(135deg, var(--success), var(--accent));
                color: white;
                padding: var(--space-8);
                border-radius: var(--radius-xl);
                text-align: center;
                margin: var(--space-6) 0;
            ">
                <div style="font-size: 3rem; margin-bottom: var(--space-4);">✨</div>
                <h3 style="margin: 0 0 var(--space-3) 0; font-weight: 700; font-size: 1.5rem;">
                    Processing Complete!
                </h3>
                <p style="margin: 0; opacity: 0.9; font-size: 1rem;">
                    All documents have been successfully processed and analyzed
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            st.session_state.stored_documents.extend(processed_docs)
            time.sleep(2)  # Brief pause to show completion
            st.rerun()
    
    # Modern file display with cards
    st.markdown("<h3 style='color: var(--primary); margin: var(--space-8) 0 var(--space-6) 0; font-weight: 700; text-align: center;'>📋 Uploaded Files Preview</h3>", unsafe_allow_html=True)
    
    # Create file cards in responsive grid
    file_cards = []
    for i, file in enumerate(uploaded_files):
        # Quick validation for status
        file_data = file.read()
        file.seek(0)
        validation = document_parser.validate_file(file_data, file.name)
        
        # Determine file icon and status
        file_ext = file.name.split('.')[-1].lower()
        file_icons = {
            'pdf': '📄',
            'docx': '📃', 
            'doc': '📃',
            'txt': '📝'
        }
        file_icon = file_icons.get(file_ext, '📄')
        
        status_badge = "✅ Valid" if validation['valid'] else "❌ Invalid"
        status_color = "var(--success)" if validation['valid'] else "var(--error)"
        
        # Create preview content for text files
        preview_content = ""
        if file.type == "text/plain" and file.size < 10000:
            try:
                content = str(file.read(), "utf-8")
                preview_text = content[:200] + "..." if len(content) > 200 else content
                preview_content = f"""
                <div style="
                    background: var(--gray-50);
                    padding: var(--space-3);
                    border-radius: var(--radius-md);
                    margin-top: var(--space-4);
                    font-family: var(--font-mono);
                    font-size: 0.75rem;
                    line-height: 1.4;
                    color: var(--text-secondary);
                    border-left: 3px solid var(--primary);
                ">
                    <strong>Preview:</strong><br>
                    {preview_text}
                </div>
                """
                file.seek(0)
            except:
                preview_content = "<p style='color: var(--text-tertiary); font-size: 0.875rem; margin-top: var(--space-4);'>Cannot preview this file</p>"
        
        file_card = create_card(f"""
            <div class="animate-fade-in-up hover-lift" style="animation-delay: {i * 0.1}s; text-align: center;">
                <div style="font-size: 3rem; margin-bottom: var(--space-4); color: var(--primary);">{file_icon}</div>
                <h4 style="color: var(--text-primary); font-weight: 600; margin-bottom: var(--space-3); word-break: break-word;">
                    {file.name}
                </h4>
                
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: var(--space-4); margin: var(--space-4) 0;">
                    <div style="
                        background: var(--surface-secondary);
                        padding: var(--space-3);
                        border-radius: var(--radius-md);
                        text-align: center;
                    ">
                        <div style="font-size: 1.25rem; font-weight: 700; color: var(--primary);">
                            {file.size/1024:.1f} KB
                        </div>
                        <div style="color: var(--text-secondary); font-size: 0.75rem; margin-top: var(--space-1);">
                            File Size
                        </div>
                    </div>
                    <div style="
                        background: var(--surface-secondary);
                        padding: var(--space-3);
                        border-radius: var(--radius-md);
                        text-align: center;
                    ">
                        <div style="font-size: 1rem; font-weight: 600; color: {status_color};">
                            {status_badge}
                        </div>
                        <div style="color: var(--text-secondary); font-size: 0.75rem; margin-top: var(--space-1);">
                            Status
                        </div>
                    </div>
                </div>
                
                <div style="
                    background: var(--surface-secondary);
                    padding: var(--space-3);
                    border-radius: var(--radius-md);
                    margin: var(--space-4) 0;
                    text-align: left;
                ">
                    <strong style="color: var(--text-primary); font-size: 0.875rem;">File Type:</strong>
                    <span style="color: var(--text-secondary); font-size: 0.875rem;"> {file.type or 'Unknown'}</span>
                </div>
                
                {preview_content}
            </div>
        """)
        file_cards.append(file_card)
    
    # Display cards in responsive grid
    if file_cards:
        cards_grid = create_responsive_card_grid(file_cards, {'desktop': 3, 'tablet': 2, 'mobile': 1})
        st.markdown(cards_grid, unsafe_allow_html=True)

# Show stored documents with modern design
if st.session_state.stored_documents:
    st.markdown("<h3 style='color: var(--primary); margin: var(--space-8) 0 var(--space-6) 0; font-weight: 700; text-align: center;'>📚 Processed Documents</h3>", unsafe_allow_html=True)
    
    stored_cards = []
    for stored_doc, parsed_doc in st.session_state.stored_documents:
        # Status styling
        status_colors = {
            'completed': 'var(--success)',
            'processing': 'var(--warning)', 
            'error': 'var(--error)',
            'pending': 'var(--primary)'
        }
        status_color = status_colors.get(stored_doc.processing_status, 'var(--gray-500)')
        
        # Create metadata grid
        metadata_items = []
        if parsed_doc:
            metadata_items = [
                f"📄 {parsed_doc.metadata.page_count} pages",
                f"📋 {parsed_doc.metadata.file_type}",
                f"🎯 {parsed_doc.confidence_score:.1%} confidence",
                f"⚙️ {parsed_doc.parsing_method}"
            ]
        
        stored_card = create_card(f"""
            <div class="animate-fade-in-up hover-lift">
                <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: var(--space-4);">
                    <div>
                        <h4 style="color: var(--text-primary); font-weight: 600; margin: 0 0 var(--space-2) 0;">
                            📄 {stored_doc.original_filename}
                        </h4>
                        <div style="display: flex; align-items: center; gap: var(--space-2);">
                            <span style="
                                background: {status_color};
                                color: white;
                                padding: var(--space-1) var(--space-2);
                                border-radius: var(--radius-full);
                                font-size: 0.75rem;
                                font-weight: 500;
                            ">
                                {stored_doc.processing_status.title()}
                            </span>
                            <span style="color: var(--text-secondary); font-size: 0.875rem;">
                                {stored_doc.upload_timestamp.strftime('%Y-%m-%d %H:%M')}
                            </span>
                        </div>
                    </div>
                    <div style="text-align: right;">
                        <div style="color: var(--primary); font-weight: 600; font-size: 1.125rem;">
                            {stored_doc.file_size/1024:.1f} KB
                        </div>
                        <div style="color: var(--text-secondary); font-size: 0.75rem;">
                            File Size
                        </div>
                    </div>
                </div>
                
                {"<div style='display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: var(--space-2); margin: var(--space-4) 0; padding: var(--space-3); background: var(--surface-secondary); border-radius: var(--radius-md);'>" + "".join([f"<div style='color: var(--text-secondary); font-size: 0.875rem;'>{item}</div>" for item in metadata_items]) + "</div>" if metadata_items else ""}
                
                {f"<div style='background: var(--gray-50); padding: var(--space-4); border-radius: var(--radius-md); margin: var(--space-4) 0; font-family: var(--font-mono); font-size: 0.875rem; line-height: 1.5; border-left: 3px solid var(--accent);'><strong>Content Preview:</strong><br>{parsed_doc.content[:300] + '...' if len(parsed_doc.content) > 300 else parsed_doc.content}</div>" if parsed_doc and parsed_doc.content else ""}
                
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(120px, 1fr)); gap: var(--space-3); margin-top: var(--space-6);">
                    <button style="
                        background: var(--primary);
                        color: white;
                        border: none;
                        border-radius: var(--radius-lg);
                        padding: var(--space-2) var(--space-3);
                        font-weight: 500;
                        font-size: 0.875rem;
                        cursor: pointer;
                        transition: all 0.2s ease;
                    " class="btn btn-primary">
                        📊 Analyze
                    </button>
                    <button style="
                        background: var(--secondary);
                        color: white;
                        border: none;
                        border-radius: var(--radius-lg);
                        padding: var(--space-2) var(--space-3);
                        font-weight: 500;
                        font-size: 0.875rem;
                        cursor: pointer;
                        transition: all 0.2s ease;
                    " class="btn btn-secondary">
                        📥 Download
                    </button>
                    <button style="
                        background: var(--error);
                        color: white;
                        border: none;
                        border-radius: var(--radius-lg);
                        padding: var(--space-2) var(--space-3);
                        font-weight: 500;
                        font-size: 0.875rem;
                        cursor: pointer;
                        transition: all 0.2s ease;
                    " class="btn btn-error">
                        🗑️ Delete
                    </button>
                </div>
            </div>
        """)
        stored_cards.append(stored_card)
    
    if stored_cards:
        cards_grid = create_responsive_card_grid(stored_cards, {'desktop': 2, 'tablet': 1, 'mobile': 1})
        st.markdown(cards_grid, unsafe_allow_html=True)

# Getting started section for new users
if not uploaded_files and not st.session_state.stored_documents:
    getting_started_content = create_card("""
        <div class="animate-fade-in-up" style="text-align: center;">
            <div style="font-size: 4rem; margin-bottom: var(--space-6); color: var(--primary);">🚀</div>
            <h3 style="color: var(--primary); font-weight: 700; margin-bottom: var(--space-4);">
                Get Started with Contract Intelligence
            </h3>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: var(--space-6); margin: var(--space-6) 0; text-align: left;">
                <div>
                    <h4 style="color: var(--text-primary); font-weight: 600; margin-bottom: var(--space-3); display: flex; align-items: center; gap: var(--space-2);">
                        <span style="background: var(--primary); color: white; width: 24px; height: 24px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 0.875rem; font-weight: 700;">1</span>
                        Upload Documents
                    </h4>
                    <p style="color: var(--text-secondary); line-height: 1.6; margin: 0;">
                        Drag and drop or browse to upload your contract files. We support PDF, DOCX, DOC, and TXT formats up to {settings.max_file_size_mb}MB.
                    </p>
                </div>
                <div>
                    <h4 style="color: var(--text-primary); font-weight: 600; margin-bottom: var(--space-3); display: flex; align-items: center; gap: var(--space-2);">
                        <span style="background: var(--secondary); color: white; width: 24px; height: 24px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 0.875rem; font-weight: 700;">2</span>
                        AI Processing
                    </h4>
                    <p style="color: var(--text-secondary); line-height: 1.6; margin: 0;">
                        Our AI automatically extracts text, identifies key terms, parties, and obligations. OCR is applied to scanned documents automatically.
                    </p>
                </div>
                <div>
                    <h4 style="color: var(--text-primary); font-weight: 600; margin-bottom: var(--space-3); display: flex; align-items: center; gap: var(--space-2);">
                        <span style="background: var(--accent); color: white; width: 24px; height: 24px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 0.875rem; font-weight: 700;">3</span>
                        Analysis & Reports
                    </h4>
                    <p style="color: var(--text-secondary); line-height: 1.6; margin: 0;">
                        Review comprehensive analysis, run compliance checks, compare versions, and generate professional reports for stakeholders.
                    </p>
                </div>
            </div>
        </div>
    """)
    st.markdown(getting_started_content, unsafe_allow_html=True)
    
    # Sample contracts section
    sample_section = create_card("""
        <div class="animate-fade-in-up" style="animation-delay: 0.2s; text-align: center;">
            <h4 style="color: var(--primary); font-weight: 600; margin-bottom: var(--space-4);">
                📋 Try Sample Contracts
            </h4>
            <p style="color: var(--text-secondary); margin-bottom: var(--space-6);">
                Don't have a contract ready? Try our sample documents to explore the platform:
            </p>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: var(--space-4);">
                <button style="
                    background: var(--surface-secondary);
                    border: 1px solid var(--border-primary);
                    border-radius: var(--radius-lg);
                    padding: var(--space-4);
                    cursor: pointer;
                    transition: all 0.2s ease;
                    text-align: center;
                " class="hover-lift">
                    <div style="font-size: 2rem; margin-bottom: var(--space-2);">📄</div>
                    <strong style="color: var(--text-primary);">Service Agreement</strong>
                    <p style="color: var(--text-secondary); font-size: 0.875rem; margin: var(--space-2) 0 0 0;">Professional services contract template</p>
                </button>
                <button style="
                    background: var(--surface-secondary);
                    border: 1px solid var(--border-primary);
                    border-radius: var(--radius-lg);
                    padding: var(--space-4);
                    cursor: pointer;
                    transition: all 0.2s ease;
                    text-align: center;
                " class="hover-lift">
                    <div style="font-size: 2rem; margin-bottom: var(--space-2);">🤝</div>
                    <strong style="color: var(--text-primary);">NDA Template</strong>
                    <p style="color: var(--text-secondary); font-size: 0.875rem; margin: var(--space-2) 0 0 0;">Non-disclosure agreement template</p>
                </button>
                <button style="
                    background: var(--surface-secondary);
                    border: 1px solid var(--border-primary);
                    border-radius: var(--radius-lg);
                    padding: var(--space-4);
                    cursor: pointer;
                    transition: all 0.2s ease;
                    text-align: center;
                " class="hover-lift">
                    <div style="font-size: 2rem; margin-bottom: var(--space-2);">💼</div>
                    <strong style="color: var(--text-primary);">Employment Contract</strong>
                    <p style="color: var(--text-secondary); font-size: 0.875rem; margin: var(--space-2) 0 0 0;">Standard employment agreement</p>
                </button>
            </div>
        </div>
    """)
    st.markdown(sample_section, unsafe_allow_html=True)

# Next steps section
next_steps_content = create_card("""
    <div class="animate-fade-in-up" style="animation-delay: 0.4s;">
        <h4 style="color: var(--primary); font-weight: 600; margin-bottom: var(--space-4); text-align: center;">
            📈 Next Steps After Upload
        </h4>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: var(--space-4);">
            <div style="
                padding: var(--space-4);
                background: var(--surface-secondary);
                border-radius: var(--radius-lg);
                border-left: 4px solid var(--primary);
                transition: all 0.2s ease;
            " class="hover-lift">
                <div style="display: flex; align-items: center; gap: var(--space-3); margin-bottom: var(--space-3);">
                    <div style="font-size: 1.5rem;">📊</div>
                    <strong style="color: var(--text-primary);">Analysis Dashboard</strong>
                </div>
                <p style="color: var(--text-secondary); font-size: 0.875rem; line-height: 1.5; margin: 0;">
                    View comprehensive analysis results with key terms, parties, obligations, and risk assessments.
                </p>
            </div>
            <div style="
                padding: var(--space-4);
                background: var(--surface-secondary);
                border-radius: var(--radius-lg);
                border-left: 4px solid var(--secondary);
                transition: all 0.2s ease;
            " class="hover-lift">
                <div style="display: flex; align-items: center; gap: var(--space-3); margin-bottom: var(--space-3);">
                    <div style="font-size: 1.5rem;">⚖️</div>
                    <strong style="color: var(--text-primary);">Compliance Check</strong>
                </div>
                <p style="color: var(--text-secondary); font-size: 0.875rem; line-height: 1.5; margin: 0;">
                    Verify contracts against regulations, policies, and industry standards automatically.
                </p>
            </div>
            <div style="
                padding: var(--space-4);
                background: var(--surface-secondary);
                border-radius: var(--radius-lg);
                border-left: 4px solid var(--accent);
                transition: all 0.2s ease;
            " class="hover-lift">
                <div style="display: flex; align-items: center; gap: var(--space-3); margin-bottom: var(--space-3);">
                    <div style="font-size: 1.5rem;">🔄</div>
                    <strong style="color: var(--text-primary);">Compare Contracts</strong>
                </div>
                <p style="color: var(--text-secondary); font-size: 0.875rem; line-height: 1.5; margin: 0;">
                    Side-by-side comparison with other versions to identify critical changes and impacts.
                </p>
            </div>
            <div style="
                padding: var(--space-4);
                background: var(--surface-secondary);
                border-radius: var(--radius-lg);
                border-left: 4px solid var(--success);
                transition: all 0.2s ease;
            " class="hover-lift">
                <div style="display: flex; align-items: center; gap: var(--space-3); margin-bottom: var(--space-3);">
                    <div style="font-size: 1.5rem;">📝</div>
                    <strong style="color: var(--text-primary);">Generate Reports</strong>
                </div>
                <p style="color: var(--text-secondary); font-size: 0.875rem; line-height: 1.5; margin: 0;">
                    Create professional reports for stakeholders with executive summaries and detailed findings.
                </p>
            </div>
        </div>
    </div>
""")
st.markdown(next_steps_content, unsafe_allow_html=True)

# Add floating action button for quick navigation
fab = create_floating_action_button(
    icon="📊", 
    tooltip="Go to Dashboard", 
    position="bottom-right"
)
st.markdown(fab, unsafe_allow_html=True)

# Add mobile navigation
mobile_nav = create_mobile_navigation()
st.markdown(mobile_nav, unsafe_allow_html=True)

# Update session state for navigation
if 'uploaded_files' in st.session_state:
    st.session_state.uploaded_files = uploaded_files or []