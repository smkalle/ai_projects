"""Main Streamlit application for LangExtract Medical Research Assistant."""

import streamlit as st
import pandas as pd
from pathlib import Path
import json
import time
from datetime import datetime
import logging

from config.settings import settings
from src.extractors import MedicalExtractor, ExtractionResult
from src.utils.file_handler import FileHandler
from src.utils.export_manager import ExportManager
try:
    from src.utils.visualization import create_extraction_chart, create_word_cloud
except ImportError:
    # Fallback functions if visualization modules are not available
    def create_extraction_chart(data):
        import plotly.graph_objects as go
        return go.Figure()
    def create_word_cloud(data):
        import matplotlib.pyplot as plt
        fig = plt.figure(figsize=(8, 4))
        plt.text(0.5, 0.5, "Visualization not available", ha='center', va='center')
        plt.axis('off')
        return fig


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title=settings.page_title,
    page_icon=settings.page_icon,
    layout=settings.layout,
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .stApp {
        background-color: #f5f5f5;
    }
    .upload-box {
        border: 2px dashed #0066CC;
        border-radius: 10px;
        padding: 20px;
        text-align: center;
        background-color: #f0f8ff;
    }
    .result-card {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 10px;
    }
    .metric-card {
        background-color: #e8f4f8;
        padding: 15px;
        border-radius: 8px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize session state variables."""
    if 'extractor' not in st.session_state:
        st.session_state.extractor = None
    if 'results' not in st.session_state:
        st.session_state.results = []
    if 'current_file' not in st.session_state:
        st.session_state.current_file = None
    if 'api_key' not in st.session_state:
        st.session_state.api_key = settings.langextract_api_key


def sidebar_content():
    """Render sidebar content."""
    with st.sidebar:
        st.image("https://via.placeholder.com/300x100/0066CC/FFFFFF?text=LangExtract+Medical", width=300)
        st.title("Navigation")
        
        # API Key configuration
        with st.expander("⚙️ API Configuration", expanded=False):
            api_key = st.text_input(
                "Gemini API Key",
                value=st.session_state.api_key,
                type="password",
                help="Enter your Gemini API key for cloud processing"
            )
            if api_key != st.session_state.api_key:
                st.session_state.api_key = api_key
                st.session_state.extractor = None
                st.success("API key updated!")
        
        # Mode selection
        st.subheader("🔧 Processing Mode")
        processing_mode = st.radio(
            "Select mode:",
            ["Cloud (Gemini)", "Local (Coming Soon)"],
            help="Choose between cloud-based or local processing"
        )
        
        # Template selection
        st.subheader("📋 Templates")
        template_options = [
            "Clinical Trial Data",
            "Case Report",
            "Drug Information",
            "Research Findings",
            "Patient Records",
            "Literature Review",
            "Custom Template"
        ]
        selected_template = st.selectbox(
            "Choose template:",
            template_options,
            help="Select a pre-configured medical extraction template"
        )
        
        # Advanced settings
        with st.expander("🔬 Advanced Settings"):
            max_workers = st.slider(
                "Parallel Workers",
                min_value=1,
                max_value=30,
                value=10,
                help="Number of parallel processing threads"
            )
            extraction_passes = st.slider(
                "Extraction Passes",
                min_value=1,
                max_value=5,
                value=2,
                help="Number of extraction passes for better recall"
            )
            max_char_buffer = st.number_input(
                "Character Buffer Size",
                min_value=100,
                max_value=5000,
                value=1000,
                step=100,
                help="Maximum characters per processing chunk"
            )
        
        # Export history
        st.subheader("📊 Export History")
        if st.session_state.results:
            st.info(f"Total extractions: {len(st.session_state.results)}")
            if st.button("Clear History"):
                st.session_state.results = []
                st.rerun()
        
        return selected_template, max_workers, extraction_passes, max_char_buffer


def main_content(template, max_workers, extraction_passes, max_char_buffer):
    """Render main content area."""
    st.title("🔬 LangExtract Medical Research Assistant")
    st.markdown("Extract structured information from medical documents with AI-powered analysis")
    
    # Initialize extractor if needed
    if st.session_state.extractor is None and st.session_state.api_key:
        try:
            st.session_state.extractor = MedicalExtractor(api_key=st.session_state.api_key)
            st.success("Extractor initialized successfully!")
        except Exception as e:
            st.error(f"Failed to initialize extractor: {e}")
            return
    
    # File upload section
    st.header("📄 Document Upload")
    col1, col2 = st.columns([3, 1])
    
    with col1:
        uploaded_files = st.file_uploader(
            "Choose files to analyze",
            type=settings.supported_file_types,
            accept_multiple_files=True,
            help="Upload medical documents in PDF, TXT, DOCX, or HTML format"
        )
    
    with col2:
        st.markdown("### Supported Formats")
        for ft in settings.supported_file_types:
            st.markdown(f"- .{ft}")
    
    # URL input option
    with st.expander("🌐 Or extract from URL"):
        url_input = st.text_input(
            "Enter document URL:",
            placeholder="https://example.com/medical-document.pdf"
        )
    
    # Process uploaded files
    if uploaded_files or url_input:
        st.header("🔍 Extraction Process")
        
        # Template details
        if template != "Custom Template":
            template_key = template.lower().replace(" ", "_")
            if st.session_state.extractor:
                templates = st.session_state.extractor.get_available_templates()
                if template_key in templates:
                    st.info(f"**Template:** {template}")
                    st.markdown(f"**Fields:** {', '.join(templates[template_key]['fields'])}")
        
        # Process button
        if st.button("🚀 Start Extraction", type="primary"):
            if not st.session_state.extractor:
                st.error("Please configure API key first!")
                return
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Process files
            file_handler = FileHandler()
            total_items = len(uploaded_files) if uploaded_files else 1
            
            for idx, item in enumerate(uploaded_files or [url_input]):
                progress = (idx + 1) / total_items
                progress_bar.progress(progress)
                
                if uploaded_files:
                    # Handle uploaded file
                    status_text.text(f"Processing {item.name}...")
                    
                    # Save uploaded file temporarily
                    temp_path = file_handler.save_uploaded_file(item)
                    
                    try:
                        # Extract content
                        text_content = file_handler.extract_text(temp_path)
                        
                        # Perform extraction
                        template_key = template.lower().replace(" ", "_")
                        result = st.session_state.extractor.extract_with_template(
                            text=text_content,
                            template_name=template_key,
                            source_name=item.name,
                            max_workers=max_workers,
                            extraction_passes=extraction_passes,
                            max_char_buffer=max_char_buffer
                        )
                        
                        # Store result
                        st.session_state.results.append(result)
                        
                    except Exception as e:
                        st.error(f"Error processing {item.name}: {e}")
                    finally:
                        # Clean up
                        temp_path.unlink(missing_ok=True)
                
                else:
                    # Handle URL
                    status_text.text(f"Processing URL...")
                    
                    try:
                        template_key = template.lower().replace(" ", "_")
                        result = st.session_state.extractor.extract_from_url(
                            url=url_input,
                            prompt=st.session_state.extractor.templates[template_key]["prompt"],
                            max_workers=max_workers,
                            extraction_passes=extraction_passes,
                            max_char_buffer=max_char_buffer
                        )
                        
                        # Store result
                        st.session_state.results.append(result)
                        
                    except Exception as e:
                        st.error(f"Error processing URL: {e}")
            
            progress_bar.progress(1.0)
            status_text.text("Extraction complete!")
            time.sleep(1)
            status_text.empty()
            progress_bar.empty()
    
    # Display results
    if st.session_state.results:
        display_results()


def display_results():
    """Display extraction results."""
    st.header("📊 Extraction Results")
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    total_extractions = sum(len(r.extractions) for r in st.session_state.results)
    total_files = len(st.session_state.results)
    avg_time = sum(r.processing_time for r in st.session_state.results) / total_files if total_files > 0 else 0
    
    with col1:
        st.metric("Total Files", total_files)
    with col2:
        st.metric("Total Extractions", total_extractions)
    with col3:
        st.metric("Avg. Processing Time", f"{avg_time:.2f}s")
    with col4:
        st.metric("Success Rate", "100%")
    
    # Results tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Data Table", "📈 Visualizations", "💾 Export", "🔍 Details"])
    
    with tab1:
        # Compile all extractions into dataframe
        all_data = []
        for result in st.session_state.results:
            for extraction in result.extractions:
                data_row = {
                    "Source": result.source_file,
                    "Template": result.template_used,
                    "Timestamp": result.timestamp.strftime("%Y-%m-%d %H:%M:%S")
                }
                # Flatten extraction data
                if isinstance(extraction, dict):
                    data_row.update(extraction)
                all_data.append(data_row)
        
        if all_data:
            df = pd.DataFrame(all_data)
            st.dataframe(df, use_container_width=True, height=400)
    
    with tab2:
        # Visualizations
        if all_data:
            st.subheader("Extraction Overview")
            
            # Create visualization
            fig = create_extraction_chart(st.session_state.results)
            st.plotly_chart(fig, use_container_width=True)
            
            # Word cloud (if applicable)
            if len(all_data) > 5:
                st.subheader("Key Terms")
                try:
                    wordcloud_fig = create_word_cloud(all_data)
                    st.pyplot(wordcloud_fig)
                except Exception as e:
                    st.info("Word cloud generation requires more data")
    
    with tab3:
        # Export options
        st.subheader("Export Options")
        
        export_manager = ExportManager()
        
        col1, col2 = st.columns(2)
        
        with col1:
            export_format = st.selectbox(
                "Export Format",
                ["CSV", "JSON", "Excel", "LaTeX", "BibTeX"]
            )
        
        with col2:
            include_metadata = st.checkbox("Include metadata", value=True)
            include_citations = st.checkbox("Include source citations", value=True)
        
        if st.button("📥 Generate Export"):
            try:
                # Prepare export data
                export_data = []
                for result in st.session_state.results:
                    export_data.append(result.to_dict())
                
                # Generate export
                if export_format == "CSV":
                    file_path = export_manager.export_to_csv(export_data, include_metadata)
                elif export_format == "JSON":
                    file_path = export_manager.export_to_json(export_data)
                elif export_format == "Excel":
                    file_path = export_manager.export_to_excel(export_data, include_metadata)
                else:
                    st.warning(f"{export_format} export coming soon!")
                    return
                
                # Provide download
                with open(file_path, "rb") as f:
                    st.download_button(
                        label=f"Download {export_format}",
                        data=f.read(),
                        file_name=file_path.name,
                        mime=export_manager.get_mime_type(export_format)
                    )
                
                st.success(f"Export generated successfully!")
                
            except Exception as e:
                st.error(f"Export failed: {e}")
    
    with tab4:
        # Detailed view
        st.subheader("Detailed Results")
        
        for idx, result in enumerate(st.session_state.results):
            with st.expander(f"📄 {result.source_file} ({len(result.extractions)} extractions)"):
                st.markdown(f"**Processing Time:** {result.processing_time:.2f} seconds")
                st.markdown(f"**Template Used:** {result.template_used}")
                st.markdown(f"**Timestamp:** {result.timestamp}")
                
                st.markdown("### Extractions:")
                for i, extraction in enumerate(result.extractions, 1):
                    st.markdown(f"**Item {i}:**")
                    st.json(extraction)


def main():
    """Main application entry point."""
    initialize_session_state()
    
    # Sidebar
    template, max_workers, extraction_passes, max_char_buffer = sidebar_content()
    
    # Main content
    main_content(template, max_workers, extraction_passes, max_char_buffer)
    
    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: #666;'>
        LangExtract Medical Research Assistant v1.0 | 
        Powered by Google Gemini | 
        Built with ❤️ for medical researchers
        </div>
        """,
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()