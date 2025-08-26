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
        st.sidebar.title("⚡ Energy Document AI")
        st.sidebar.markdown("---")

        # API Key validation
        if not settings.openai_api_key:
            st.sidebar.error("⚠️ OpenAI API key not configured")
            st.sidebar.markdown("Please set your `OPENAI_API_KEY` environment variable.")
            return
        else:
            st.sidebar.success("✅ API key configured")

        # Document upload section
        st.sidebar.subheader("📄 Document Upload")

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

        # Document statistics
        st.sidebar.subheader("📊 Document Stats")
        if st.session_state.rag_system:
            try:
                stats = st.session_state.rag_system.get_document_stats()
                if stats:
                    st.sidebar.metric("Total Documents", stats.get('total_documents', 0))
                    st.sidebar.metric("Total Chunks", stats.get('total_points', 0))

                    # Document types breakdown
                    if stats.get('document_types'):
                        fig = px.pie(
                            values=list(stats['document_types'].values()),
                            names=list(stats['document_types'].keys()),
                            title="Document Types"
                        )
                        fig.update_layout(height=300)
                        st.sidebar.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.sidebar.error(f"Error loading stats: {e}")

        # System info
        st.sidebar.subheader("🔧 System Info")
        st.sidebar.info(f"""
        **Model**: {settings.llm_model}  
        **Max Iterations**: {settings.max_iterations}  
        **Collection**: {settings.collection_name}  
        **Version**: {settings.app_version}
        """)

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
            progress_bar = st.sidebar.progress(0)
            status_text = st.sidebar.empty()

            # Initialize processor
            processor = EnergyPDFProcessor(
                openai_api_key=settings.openai_api_key,
                dpi=settings.pdf_dpi
            )

            # Extract text
            status_text.text("Extracting text from PDF...")
            progress_bar.progress(25)

            extracted_text = processor.extract_and_combine_text(file_path, "energy")

            # Store in RAG system
            status_text.text("Storing in knowledge base...")
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
            status_text.text("Processing complete!")

            # Add to session state
            st.session_state.documents.append({
                "name": file_name,
                "chunks": chunks_stored,
                "timestamp": datetime.now(),
                "type": "energy"
            })

            st.sidebar.success(f"✅ Processed {chunks_stored} chunks from {file_name}")

            # Clean up
            os.unlink(file_path)

        except Exception as e:
            st.sidebar.error(f"Processing failed: {e}")
            logger.error(f"Document processing error: {e}")

    def render_main_interface(self):
        """Render main chat interface"""
        st.title("⚡ Energy Document AI Assistant")
        st.markdown("Ask questions about your energy sector documents using advanced AI analysis.")

        # Quick start guide
        if not st.session_state.documents:
            st.info("""
            🚀 **Getting Started**
            1. Upload a PDF document using the sidebar
            2. Wait for processing to complete
            3. Ask questions about your documents

            **Perfect for**: Technical specifications, regulatory documents, research papers, compliance reports, and more!
            """)

        # Query input
        query = st.text_input(
            "Ask your question:",
            placeholder="e.g., What are the NERC compliance requirements for grid protection?",
            help="Ask technical questions about energy systems, regulations, safety protocols, etc."
        )

        col1, col2, col3 = st.columns([1, 1, 4])

        with col1:
            if st.button("🔍 Analyze", type="primary"):
                if query and st.session_state.agent:
                    self.process_query(query)
                elif not query:
                    st.warning("Please enter a question")
                else:
                    st.error("System not initialized")

        with col2:
            if st.button("🗑️ Clear Chat"):
                st.session_state.chat_history = []
                st.rerun()

        # Sample queries
        st.subheader("💡 Sample Queries")
        sample_queries = [
            "What are the safety requirements for electrical installations?",
            "Explain the grid interconnection standards and procedures.",
            "What are the environmental compliance requirements for renewable energy projects?",
            "Describe the equipment specifications for transformer installations.",
            "What are the NERC CIP cybersecurity requirements?"
        ]

        cols = st.columns(len(sample_queries))
        for i, sample_query in enumerate(sample_queries):
            with cols[i]:
                if st.button(f"📝 {sample_query[:30]}...", key=f"sample_{i}"):
                    if st.session_state.agent:
                        self.process_query(sample_query)
                    else:
                        st.error("System not initialized")

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
            st.subheader("💬 Analysis History")

            for i, chat in enumerate(reversed(st.session_state.chat_history)):
                with st.expander(f"🔍 {chat['query'][:80]}...", expanded=(i == 0)):

                    # Query info
                    st.markdown(f"**Query:** {chat['query']}")
                    st.markdown(f"**Time:** {chat['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")

                    result = chat['response']

                    # Answer
                    st.markdown("**Answer:**")
                    st.markdown(result['answer'])

                    # Analysis details
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Relevance Score", f"{result['relevance_score']:.2f}")
                    with col2:
                        st.metric("Iterations", result['iterations'])
                    with col3:
                        st.metric("Document Type", result['document_type'])

                    # Source documents
                    if result['retrieved_docs']:
                        st.markdown("**Source Documents:**")
                        docs_df = format_search_results(result['retrieved_docs'])
                        st.dataframe(docs_df, use_container_width=True)

    def run(self):
        """Run the Streamlit application"""
        self.render_sidebar()
        self.render_main_interface()

# Run the application
if __name__ == "__main__":
    app = EnergyDocumentAI()
    app.run()
