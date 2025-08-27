"""
Streamlit UI for Energy Document AI
Professional interface for energy sector document analysis
"""

import streamlit as st
import os
import sys
import tempfile
from typing import Dict, List
import logging
import pandas as pd
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.pdf_processor import EnergyPDFProcessor
from models.rag_system import EnergyRAGSystem
from models.agent_workflow import EnergyDocumentAgent
from utils.config import settings, ENERGY_DOCUMENT_TYPES
from utils.helpers import (
    setup_logging, validate_pdf_file, estimate_processing_cost,
    format_search_results, create_document_summary
)

# Configure page
st.set_page_config(
    page_title="Energy Document AI",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Modern CSS theme - Claudable-inspired design
st.markdown("""
<style>
    /* Import system fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global styling */
    .main .block-container {
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
        max-width: 1200px !important;
    }
    
    /* Typography */
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }
    
    /* Hide default Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Modern sidebar styling */
    .css-1d391kg {
        background-color: #f8fafc;
        border-right: 1px solid #e2e8f0;
    }
    
    /* Card-based components */
    .stCard {
        background: white;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
        padding: 1.5rem;
        margin: 1rem 0;
    }
    
    /* Modern buttons */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        font-weight: 500;
        font-size: 0.875rem;
        transition: all 0.2s ease;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
    }
    
    /* Modern input styling */
    .stTextInput > div > div > input {
        border-radius: 8px;
        border: 1px solid #d1d5db;
        padding: 0.75rem;
        font-size: 0.875rem;
        transition: border-color 0.2s ease;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    /* Modern metrics */
    div[data-testid="metric-container"] {
        background: white;
        border: 1px solid #e2e8f0;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
    }
    
    /* Professional titles */
    .main h1 {
        color: #1f2937;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    
    .main h2, .main h3 {
        color: #374151;
        font-weight: 500;
    }
    
    /* Status indicators */
    .status-success {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-size: 0.875rem;
        font-weight: 500;
        display: inline-block;
        margin: 0.25rem;
    }
    
    .status-error {
        background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-size: 0.875rem;
        font-weight: 500;
        display: inline-block;
        margin: 0.25rem;
    }
    
    .status-info {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-size: 0.875rem;
        font-weight: 500;
        display: inline-block;
        margin: 0.25rem;
    }
    
    /* Modern expander */
    .streamlit-expanderHeader {
        background-color: #f8fafc;
        border-radius: 8px;
        border: 1px solid #e2e8f0;
    }
    
    /* Modern file uploader */
    .stFileUploader > div {
        border: 2px dashed #d1d5db;
        border-radius: 8px;
        padding: 2rem;
        transition: border-color 0.2s ease;
    }
    
    .stFileUploader > div:hover {
        border-color: #667eea;
    }
    
    /* Professional info boxes */
    .stAlert {
        border-radius: 8px;
        border: none;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
    }
    
    /* Custom progress bars */
    .stProgress > div > div {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 4px;
    }
    
    /* Sidebar card components */
    .sidebar-header {
        margin-bottom: 1.5rem;
    }
    
    .status-card, .upload-card, .stats-card, .system-card {
        background: white;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
        padding: 1.25rem;
        margin: 1rem 0;
    }
    
    .system-info .info-item {
        padding: 0.5rem 0;
        border-bottom: 1px solid #f1f5f9;
        font-size: 0.875rem;
    }
    
    .system-info .info-item:last-child {
        border-bottom: none;
    }
    
    /* Sidebar selectbox and input styling */
    .css-1d391kg .stSelectbox > div > div {
        background: white;
        border-radius: 6px;
        border: 1px solid #d1d5db;
    }
    
    /* Sidebar metrics styling */
    .css-1d391kg div[data-testid="metric-container"] {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
    }
    
    /* Main interface styling */
    .main-header {
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .subtitle {
        color: #6b7280;
        font-size: 1.125rem;
        font-weight: 400;
        margin-top: 0.5rem;
    }
    
    .welcome-card {
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        padding: 2rem;
        margin: 2rem 0;
        text-align: center;
    }
    
    .welcome-card h3 {
        color: #1f2937;
        margin-bottom: 1.5rem;
    }
    
    .welcome-steps {
        display: flex;
        justify-content: center;
        gap: 2rem;
        margin: 2rem 0;
        flex-wrap: wrap;
    }
    
    .step-item {
        display: flex;
        align-items: center;
        gap: 1rem;
        flex-direction: column;
        max-width: 200px;
    }
    
    .step-number {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        width: 40px;
        height: 40px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 600;
        font-size: 1.125rem;
    }
    
    .step-content {
        color: #374151;
        font-size: 0.875rem;
        text-align: center;
    }
    
    .welcome-footer {
        color: #6b7280;
        font-size: 0.875rem;
        margin-top: 1.5rem;
    }
    
    .query-card, .samples-section {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1.5rem 0;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
    }
    
    .samples-section .stButton > button {
        background: white;
        color: #374151;
        border: 1px solid #e2e8f0;
        margin-bottom: 0.5rem;
        text-align: left;
        font-weight: 400;
    }
    
    .samples-section .stButton > button:hover {
        background: #f8fafc;
        border-color: #667eea;
        color: #667eea;
    }
    
    /* Processing card styling */
    .processing-card {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 1.25rem;
        margin: 1rem 0;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
    }
    
    /* Chat history styling */
    .chat-history-section {
        margin-top: 2rem;
    }
    
    .chat-card {
        background: white;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    
    .query-section {
        background: #f8fafc;
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 1rem;
        border-left: 4px solid #667eea;
    }
    
    .query-text {
        color: #1f2937;
        font-size: 0.95rem;
        margin-bottom: 0.5rem;
    }
    
    .timestamp {
        color: #6b7280;
        font-size: 0.875rem;
    }
    
    .answer-section {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    .metrics-section {
        margin: 1rem 0;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 1rem;
        text-align: center;
        margin: 0.25rem;
    }
    
    .metric-label {
        color: #6b7280;
        font-size: 0.75rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.5rem;
    }
    
    .metric-value {
        color: #1f2937;
        font-size: 1.5rem;
        font-weight: 600;
    }
    
    .sources-section {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 1rem;
        margin-top: 1rem;
    }
    
    /* Modern dataframe styling */
    .stDataFrame {
        border-radius: 8px;
        overflow: hidden;
    }
    
    /* Warning card styling */
    .warning-card {
        background: linear-gradient(135deg, #fef3cd 0%, #fde68a 100%);
        border: 1px solid #f59e0b;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1.5rem 0;
        border-left: 4px solid #f59e0b;
    }
    
    .warning-card h4 {
        color: #92400e;
        margin-bottom: 1rem;
        font-weight: 600;
    }
    
    .warning-card p, .warning-card li {
        color: #78350f;
        font-size: 0.875rem;
    }
    
    .warning-card ul {
        margin: 0.5rem 0;
        padding-left: 1.5rem;
    }
    
    .warning-card strong {
        color: #92400e;
    }
</style>
""", unsafe_allow_html=True)

# Setup logging
setup_logging(settings.debug)
logger = logging.getLogger(__name__)

class EnergyDocumentAI:
    """Main application class"""

    def __init__(self):
        self.initialize_session_state()
        self.setup_components()

    def initialize_session_state(self):
        """Initialize Streamlit session state"""
        if 'documents' not in st.session_state:
            st.session_state.documents = []
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []
        if 'rag_system' not in st.session_state:
            st.session_state.rag_system = None
        if 'agent' not in st.session_state:
            st.session_state.agent = None
        if 'processing_status' not in st.session_state:
            st.session_state.processing_status = {}

    def setup_components(self):
        """Setup core components"""
        if settings.openai_api_key:
            try:
                # Initialize RAG system
                if st.session_state.rag_system is None:
                    st.session_state.rag_system = EnergyRAGSystem(
                        qdrant_url=settings.qdrant_host,
                        qdrant_port=settings.qdrant_port,
                        openai_api_key=settings.openai_api_key,
                        collection_name=settings.collection_name
                    )

                # Initialize agent
                if st.session_state.agent is None:
                    st.session_state.agent = EnergyDocumentAgent(
                        rag_system=st.session_state.rag_system,
                        openai_api_key=settings.openai_api_key,
                        model=settings.llm_model,
                        max_iterations=settings.max_iterations
                    )
            except Exception as e:
                st.error(f"Error initializing components: {e}")

    def render_sidebar(self):
        """Render sidebar with document management"""
        st.sidebar.markdown('<div class="sidebar-header">', unsafe_allow_html=True)
        st.sidebar.title("⚡ Energy Document AI")
        st.sidebar.markdown('</div>', unsafe_allow_html=True)
        
        # API Key validation with modern status
        st.sidebar.markdown('<div class="status-card">', unsafe_allow_html=True)
        if not settings.openai_api_key:
            st.sidebar.markdown('<div class="status-error">⚠️ API key not configured</div>', unsafe_allow_html=True)
            st.sidebar.markdown("Please set your `OPENAI_API_KEY` environment variable.")
            st.sidebar.markdown('</div>', unsafe_allow_html=True)
            return
        else:
            st.sidebar.markdown('<div class="status-success">✅ API key configured</div>', unsafe_allow_html=True)
        st.sidebar.markdown('</div>', unsafe_allow_html=True)

        # Document upload section with modern card
        st.sidebar.markdown('<div class="upload-card">', unsafe_allow_html=True)
        st.sidebar.markdown("### 📄 Document Upload")

        uploaded_file = st.sidebar.file_uploader(
            "Upload Energy Document (PDF)",
            type=["pdf"],
            help="Upload technical documents, research papers, regulatory files, etc."
        )

        if uploaded_file:
            self.handle_file_upload(uploaded_file)

        # Document type selector
        doc_type = st.sidebar.selectbox(
            "Document Category",
            options=list(ENERGY_DOCUMENT_TYPES.keys()),
            format_func=lambda x: ENERGY_DOCUMENT_TYPES[x]
        )
        st.sidebar.markdown('</div>', unsafe_allow_html=True)

        # Document statistics with modern card
        st.sidebar.markdown('<div class="stats-card">', unsafe_allow_html=True)
        st.sidebar.markdown("### 📊 Document Stats")
        if st.session_state.rag_system:
            try:
                # Check system status first
                system_status = st.session_state.rag_system.get_status()
                
                if not system_status['qdrant_available']:
                    st.sidebar.markdown('<div class="status-error">⚠️ Vector database unavailable</div>', unsafe_allow_html=True)
                    st.sidebar.markdown('<div class="status-info">Documents can be processed but not stored or searched</div>', unsafe_allow_html=True)
                elif not system_status['embeddings_available']:
                    st.sidebar.markdown('<div class="status-error">⚠️ OpenAI embeddings unavailable</div>', unsafe_allow_html=True)
                    st.sidebar.markdown('<div class="status-info">Please configure your OpenAI API key</div>', unsafe_allow_html=True)
                else:
                    stats = st.session_state.rag_system.get_document_stats()
                    if stats and stats.get('total_documents', 0) > 0:
                        col1, col2 = st.sidebar.columns(2)
                        with col1:
                            st.metric("Documents", stats.get('total_documents', 0))
                        with col2:
                            st.metric("Chunks", stats.get('total_points', 0))

                        # Document types breakdown
                        if stats.get('document_types'):
                            fig = px.pie(
                                values=list(stats['document_types'].values()),
                                names=list(stats['document_types'].keys()),
                                title="Document Types"
                            )
                            fig.update_layout(
                                height=250,
                                font=dict(family="Inter, sans-serif"),
                                plot_bgcolor='rgba(0,0,0,0)',
                                paper_bgcolor='rgba(0,0,0,0)'
                            )
                            st.sidebar.plotly_chart(fig, use_container_width=True)
                    else:
                        st.sidebar.markdown('<div class="status-info">✅ System ready - No documents uploaded yet</div>', unsafe_allow_html=True)
            except Exception as e:
                st.sidebar.markdown(f'<div class="status-error">Error loading stats: {str(e)}</div>', unsafe_allow_html=True)
        else:
            st.sidebar.markdown('<div class="status-error">RAG system not initialized</div>', unsafe_allow_html=True)
        st.sidebar.markdown('</div>', unsafe_allow_html=True)

        # System info with modern card
        st.sidebar.markdown('<div class="system-card">', unsafe_allow_html=True)
        st.sidebar.markdown("### 🔧 System Info")
        
        # Get system status for display
        if st.session_state.rag_system:
            system_status = st.session_state.rag_system.get_status()
            db_status = "✅ Connected" if system_status['qdrant_available'] else "❌ Disconnected"
            embeddings_status = "✅ Ready" if system_status['embeddings_available'] else "❌ Not configured"
        else:
            db_status = "❌ Not initialized"
            embeddings_status = "❌ Not initialized"
        
        st.sidebar.markdown(f"""
        <div class="system-info">
            <div class="info-item"><strong>Model:</strong> {settings.llm_model}</div>
            <div class="info-item"><strong>Max Iterations:</strong> {settings.max_iterations}</div>
            <div class="info-item"><strong>Database:</strong> {db_status}</div>
            <div class="info-item"><strong>Embeddings:</strong> {embeddings_status}</div>
            <div class="info-item"><strong>Collection:</strong> {settings.collection_name}</div>
            <div class="info-item"><strong>Version:</strong> {settings.app_version}</div>
        </div>
        """, unsafe_allow_html=True)
        st.sidebar.markdown('</div>', unsafe_allow_html=True)

    def handle_file_upload(self, uploaded_file):
        """Handle PDF file upload and processing"""
        try:
            # Save uploaded file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                tmp_file.write(uploaded_file.read())
                tmp_file_path = tmp_file.name

            # Validate file
            is_valid, message = validate_pdf_file(tmp_file_path, settings.max_file_size_mb)
            if not is_valid:
                st.sidebar.error(f"Invalid file: {message}")
                os.unlink(tmp_file_path)
                return

            # Estimate cost
            # For estimation, assume 10 pages (would need to get actual page count)
            estimated_cost = estimate_processing_cost(10, settings.pdf_dpi)

            if st.sidebar.button(f"Process Document (Est. ${estimated_cost:.2f})"):
                self.process_document(tmp_file_path, uploaded_file.name)

            # Clean up temp file if not processing
            if tmp_file_path not in st.session_state.processing_status:
                os.unlink(tmp_file_path)

        except Exception as e:
            st.sidebar.error(f"Error handling upload: {e}")

    def process_document(self, file_path: str, file_name: str):
        """Process uploaded document"""
        try:
            # Modern progress indicators
            st.sidebar.markdown('<div class="processing-card">', unsafe_allow_html=True)
            st.sidebar.markdown("### 📄 Processing Document")
            
            progress_bar = st.sidebar.progress(0)
            status_text = st.sidebar.empty()

            # Initialize processor
            processor = EnergyPDFProcessor(
                openai_api_key=settings.openai_api_key,
                dpi=settings.pdf_dpi
            )

            # Extract text with modern status
            status_text.markdown('<div class="status-info">📖 Extracting text from PDF...</div>', unsafe_allow_html=True)
            progress_bar.progress(25)

            extracted_text = processor.extract_and_combine_text(file_path, "energy")

            # Store in RAG system
            status_text.markdown('<div class="status-info">💾 Storing in knowledge base...</div>', unsafe_allow_html=True)
            progress_bar.progress(75)

            chunks_stored = st.session_state.rag_system.process_and_store_document(
                text=extracted_text,
                document_name=file_name,
                document_type="energy",
                metadata={
                    "upload_timestamp": datetime.now().isoformat(),
                    "file_size": os.path.getsize(file_path)
                }
            )

            # Complete
            progress_bar.progress(100)
            status_text.markdown('<div class="status-success">✅ Processing complete!</div>', unsafe_allow_html=True)

            # Add to session state
            st.session_state.documents.append({
                "name": file_name,
                "chunks": chunks_stored,
                "timestamp": datetime.now(),
                "type": "energy"
            })

            # Modern success indicator
            st.sidebar.markdown(f'<div class="status-success">✅ Processed {chunks_stored} chunks from {file_name}</div>', unsafe_allow_html=True)
            st.sidebar.markdown('</div>', unsafe_allow_html=True)

            # Clean up
            os.unlink(file_path)

        except Exception as e:
            st.sidebar.markdown(f'<div class="status-error">❌ Processing failed: {e}</div>', unsafe_allow_html=True)
            logger.error(f"Document processing error: {e}")

    def render_main_interface(self):
        """Render main chat interface"""
        # Modern header
        st.markdown('<div class="main-header">', unsafe_allow_html=True)
        st.title("⚡ Energy Document AI Assistant")
        st.markdown('<p class="subtitle">Ask questions about your energy sector documents using advanced AI analysis.</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # Quick start guide with modern card
        if not st.session_state.documents:
            st.markdown("""
            <div class="welcome-card">
                <h3>🚀 Getting Started</h3>
                <div class="welcome-steps">
                    <div class="step-item">
                        <div class="step-number">1</div>
                        <div class="step-content">Upload a PDF document using the sidebar</div>
                    </div>
                    <div class="step-item">
                        <div class="step-number">2</div>
                        <div class="step-content">Wait for processing to complete</div>
                    </div>
                    <div class="step-item">
                        <div class="step-number">3</div>
                        <div class="step-content">Ask questions about your documents</div>
                    </div>
                </div>
                <div class="welcome-footer">
                    <strong>Perfect for:</strong> Technical specifications, regulatory documents, research papers, compliance reports, and more!
                </div>
            </div>
            """, unsafe_allow_html=True)

        # System status warning
        if st.session_state.rag_system:
            system_status = st.session_state.rag_system.get_status()
            if not system_status['fully_operational']:
                st.markdown("""
                <div class="warning-card">
                    <h4>⚠️ Limited Functionality</h4>
                    <p>The system is running with limited capabilities:</p>
                    <ul>
                """, unsafe_allow_html=True)
                
                if not system_status['qdrant_available']:
                    st.markdown('<li>Vector database unavailable - documents cannot be stored or searched</li>', unsafe_allow_html=True)
                if not system_status['embeddings_available']:
                    st.markdown('<li>OpenAI API not configured - embeddings unavailable</li>', unsafe_allow_html=True)
                
                st.markdown("""
                    </ul>
                    <p><strong>To enable full functionality:</strong></p>
                    <ul>
                        <li>Start Qdrant database (./start.sh option 5)</li>
                        <li>Configure OpenAI API key in .env file</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)

        # Query input with modern card
        st.markdown('<div class="query-card">', unsafe_allow_html=True)
        query = st.text_input(
            "Ask your question:",
            placeholder="e.g., What are the NERC compliance requirements for grid protection?",
            help="Ask technical questions about energy systems, regulations, safety protocols, etc."
        )

        col1, col2, col3 = st.columns([2, 2, 6])

        with col1:
            # Check if system is ready for queries
            system_ready = (st.session_state.rag_system and 
                          st.session_state.rag_system.is_available() and 
                          st.session_state.agent)
            
            if st.button("🔍 Analyze", type="primary", use_container_width=True, 
                        disabled=not system_ready):
                if query:
                    if system_ready:
                        self.process_query(query)
                    else:
                        st.error("System not ready - check database and API key configuration")
                else:
                    st.warning("Please enter a question")

        with col2:
            if st.button("🗑️ Clear Chat", use_container_width=True):
                st.session_state.chat_history = []
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

        # Sample queries with modern cards
        st.markdown('<div class="samples-section">', unsafe_allow_html=True)
        st.subheader("💡 Sample Queries")
        sample_queries = [
            "What are the safety requirements for electrical installations?",
            "Explain the grid interconnection standards and procedures.", 
            "What are the environmental compliance requirements for renewable energy projects?",
            "Describe the equipment specifications for transformer installations.",
            "What are the NERC CIP cybersecurity requirements?"
        ]

        # Display sample queries as cards
        cols = st.columns(2)
        for i, sample_query in enumerate(sample_queries):
            with cols[i % 2]:
                if st.button(f"📝 {sample_query[:50]}{'...' if len(sample_query) > 50 else ''}", 
                           key=f"sample_{i}", use_container_width=True):
                    if st.session_state.agent:
                        self.process_query(sample_query)
                    else:
                        st.error("System not initialized")
        st.markdown('</div>', unsafe_allow_html=True)

        # Chat history
        self.render_chat_history()

    def process_query(self, query: str):
        """Process user query through agent"""
        try:
            with st.spinner("🤖 Analyzing your question..."):
                result = st.session_state.agent.process_query(query)

            # Add to chat history
            st.session_state.chat_history.append({
                "timestamp": datetime.now(),
                "query": query,
                "response": result,
                "type": "user_query"
            })

            st.rerun()

        except Exception as e:
            st.error(f"Error processing query: {e}")
            logger.error(f"Query processing error: {e}")

    def render_chat_history(self):
        """Render chat history"""
        if st.session_state.chat_history:
            st.markdown('<div class="chat-history-section">', unsafe_allow_html=True)
            st.subheader("💬 Analysis History")

            for i, chat in enumerate(reversed(st.session_state.chat_history)):
                with st.expander(f"🔍 {chat['query'][:80]}...", expanded=(i == 0)):
                    st.markdown('<div class="chat-card">', unsafe_allow_html=True)
                    
                    # Query info with modern styling
                    st.markdown(f"""
                    <div class="query-section">
                        <div class="query-text"><strong>Query:</strong> {chat['query']}</div>
                        <div class="timestamp">📅 {chat['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}</div>
                    </div>
                    """, unsafe_allow_html=True)

                    result = chat['response']

                    # Answer with modern card
                    st.markdown('<div class="answer-section">', unsafe_allow_html=True)
                    st.markdown("**Answer:**")
                    st.markdown(result['answer'])
                    st.markdown('</div>', unsafe_allow_html=True)

                    # Analysis details with modern metrics
                    st.markdown('<div class="metrics-section">', unsafe_allow_html=True)
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.markdown(f"""
                        <div class="metric-card">
                            <div class="metric-label">Relevance Score</div>
                            <div class="metric-value">{result['relevance_score']:.2f}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    with col2:
                        st.markdown(f"""
                        <div class="metric-card">
                            <div class="metric-label">Iterations</div>
                            <div class="metric-value">{result['iterations']}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    with col3:
                        st.markdown(f"""
                        <div class="metric-card">
                            <div class="metric-label">Document Type</div>
                            <div class="metric-value">{result['document_type']}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)

                    # Source documents with modern styling
                    if result['retrieved_docs']:
                        st.markdown('<div class="sources-section">', unsafe_allow_html=True)
                        st.markdown("**📚 Source Documents:**")
                        docs_df = format_search_results(result['retrieved_docs'])
                        st.dataframe(docs_df, use_container_width=True)
                        st.markdown('</div>', unsafe_allow_html=True)
                    
                    st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)

    def run(self):
        """Run the Streamlit application"""
        self.render_sidebar()
        self.render_main_interface()

# Run the application
if __name__ == "__main__":
    app = EnergyDocumentAI()
    app.run()
