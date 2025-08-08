"""
Production-Ready Dolphin Medical Document Parser
Streamlit application with full Dolphin integration, logging, and database storage
"""

import streamlit as st
import os
import tempfile
import json
import base64
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any, Optional
import io
import zipfile
import logging
import time
from pathlib import Path
from PIL import Image
import plotly.express as px
import plotly.graph_objects as go

# Import our Dolphin modules
from dolphin_config import DolphinConfig, DolphinPrompts
from dolphin_model import DolphinModel, DolphinAnchor
from extraction_logger import ExtractionLogger, ProgressTracker, ExtractionStage
from file_manager import FileManager, FileInfo
from database import DolphinDatabase

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DolphinMedicalParser:
    """
    Production-ready Medical PDF Parser using real Dolphin framework
    Implements analyze-then-parse with logging, progress tracking, and database storage
    """

    def __init__(self, config: DolphinConfig):
        """Initialize the Dolphin Medical Parser"""
        self.config = config
        self.supported_formats = ['.pdf', '.jpg', '.jpeg', '.png', '.tiff', '.tif']
        
        # Initialize components
        self.dolphin_model = DolphinModel(config)
        self.database = DolphinDatabase()
        self.logger = ExtractionLogger()
        self.file_manager = FileManager()
        
        # Load model
        self.model_loaded = self.dolphin_model.load_model()
        
        if not self.model_loaded:
            logger.warning("Dolphin model not fully loaded - using mock mode")

    def parse_medical_document(self, 
                             file_path: str, 
                             document_type: str = "clinical_report",
                             session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Parse medical document using Dolphin's analyze-then-parse pipeline
        
        Args:
            file_path: Path to the medical document
            document_type: Type of medical document
            session_id: Session identifier for tracking
            
        Returns:
            Complete extraction results with metadata
        """
        start_time = time.time()
        
        try:
            # Create session if not provided
            if not session_id:
                session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
                self.database.create_session(session_id, self.config.to_dict())
            
            # Initialize logging for this file
            file_name = Path(file_path).name
            self.logger.start_extraction(file_path)
            
            # Add file to manager and database
            file_info = self.file_manager.add_file(file_path)
            if not file_info:
                raise ValueError("Failed to process file")
            
            file_id = self._generate_file_id(file_path)
            
            # Add to database
            db_file_info = {
                "file_id": file_id,
                "session_id": session_id,
                "file_name": file_info.file_name,
                "file_path": file_info.file_path,
                "file_type": file_info.file_type,
                "file_size": file_info.file_size,
                "file_hash": file_info.file_hash,
                "page_count": file_info.page_count
            }
            self.database.add_file(db_file_info)
            
            # Convert to images for processing
            self.logger.log_event(
                ExtractionStage.LOADING,
                "info",
                "Converting document to images"
            )
            
            images = self.file_manager.convert_to_images(file_path)
            if not images:
                raise ValueError("Could not convert document to processable format")
            
            # Update page count
            self.logger.total_pages = len(images)
            
            # Use Dolphin model's built-in processing
            complete_results = self.dolphin_model.process_document(images, document_type)
            
            # Add metadata
            complete_results["file_info"] = {
                "file_id": file_id,
                "session_id": session_id,
                "filename": file_name,
                "file_type": document_type,
                "parsed_at": datetime.now().isoformat(),
                "total_processing_time": time.time() - start_time
            }
            
            # Save results to database
            self.database.save_extraction(file_id, complete_results)
            
            # Update file status
            processing_time = time.time() - start_time
            self.database.update_file_status(
                file_id, 
                "completed", 
                processing_time=processing_time
            )
            
            # Save file processing results
            result_path = self.file_manager.save_results(file_id, complete_results)
            self.file_manager.mark_completed(file_id, result_path, processing_time)
            
            # Log completion
            self.logger.log_extraction_result(
                file_path,
                True,
                complete_results,
                processing_time
            )
            
            return complete_results
            
        except Exception as e:
            error_msg = f"Error parsing document: {str(e)}"
            logger.error(error_msg)
            
            # Update database with error
            if 'file_id' in locals():
                self.database.update_file_status(
                    file_id, 
                    "failed", 
                    error_message=error_msg
                )
                self.file_manager.mark_failed(file_id, error_msg)
            
            # Log failure
            self.logger.log_extraction_result(
                file_path,
                False,
                {},
                time.time() - start_time
            )
            
            return {"error": error_msg}

    def _generate_file_id(self, file_path: str) -> str:
        """Generate unique file ID"""
        import hashlib
        path_hash = hashlib.md5(str(file_path).encode()).hexdigest()[:8]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{timestamp}_{Path(file_path).stem}_{path_hash}"

    def get_session_stats(self, session_id: str) -> Dict[str, Any]:
        """Get processing statistics for a session"""
        return self.database.get_session_stats(session_id)

    def search_extractions(self, search_term: str) -> List[Dict[str, Any]]:
        """Search for patient records"""
        return self.database.search_patients(search_term)

    def get_recent_activity(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent extraction activities"""
        return self.database.get_recent_extractions(limit)

    def cleanup_session(self):
        """Clean up temporary files and save logs"""
        self.file_manager.cleanup_temp_files()
        self.logger.save_session_report()

    def export_session_data(self, session_id: str) -> str:
        """Export complete session data"""
        output_path = f"./exports/session_{session_id}_export.json"
        return self.database.export_session_data(session_id, output_path)

# Streamlit UI Functions
def create_download_link(data: Dict[str, Any], filename: str, file_format: str = "json") -> str:
    """Create a download link for parsed data"""
    if file_format == "json":
        json_str = json.dumps(data, indent=2, default=str)
        b64 = base64.b64encode(json_str.encode()).decode()
        href = f'<a href="data:application/json;base64,{b64}" download="{filename}.json">Download JSON Report</a>'
    elif file_format == "csv":
        # Convert to DataFrame for CSV export
        df = pd.json_normalize(data)
        csv_str = df.to_csv(index=False)
        b64 = base64.b64encode(csv_str.encode()).decode()
        href = f'<a href="data:text/csv;base64,{b64}" download="{filename}.csv">Download CSV Report</a>'
    else:
        href = "Unsupported format"

    return href

def display_extraction_progress(progress_data: Dict[str, Any]):
    """Display real-time extraction progress"""
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Files Processed", progress_data.get("processed", 0))
    with col2:
        st.metric("Current Stage", progress_data.get("current_stage", "Waiting"))
    with col3:
        st.metric("Progress", f"{progress_data.get('progress', 0):.1f}%")
    
    # Progress bar
    if progress_data.get("total", 0) > 0:
        progress = progress_data.get("processed", 0) / progress_data.get("total", 1)
        st.progress(progress)

def display_anchor_analysis(anchors: List[DolphinAnchor]):
    """Display analysis results with anchor visualization"""
    st.subheader("📍 Dolphin Analysis Results")
    
    if not anchors:
        st.info("No anchors detected in document")
        return
    
    # Anchor summary
    anchor_types = {}
    for anchor in anchors:
        anchor_types[anchor.anchor_type] = anchor_types.get(anchor.anchor_type, 0) + 1
    
    # Display as metrics
    cols = st.columns(len(anchor_types))
    for i, (anchor_type, count) in enumerate(anchor_types.items()):
        with cols[i]:
            st.metric(f"{anchor_type.replace('_', ' ').title()}", count)
    
    # Detailed anchor information
    with st.expander("Detailed Anchor Information"):
        anchor_df = pd.DataFrame([
            {
                "Type": anchor.anchor_type,
                "Confidence": f"{anchor.confidence:.2%}",
                "Page": anchor.page_num + 1,
                "Bbox": f"({anchor.bbox[0]}, {anchor.bbox[1]}, {anchor.bbox[2]}, {anchor.bbox[3]})",
                "Section": anchor.metadata.get("section", "Unknown")
            }
            for anchor in anchors
        ])
        st.dataframe(anchor_df, use_container_width=True)

def display_patient_info(patient_data: Dict[str, str]):
    """Display patient information in a structured format"""
    st.subheader("👤 Patient Information")

    if not patient_data:
        st.info("No patient information extracted")
        return

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Name", patient_data.get("patient_name", "N/A"))
        st.metric("Age", patient_data.get("age", "N/A"))

    with col2:
        st.metric("Gender", patient_data.get("gender", "N/A"))
        st.metric("Patient ID", patient_data.get("patient_id", "N/A"))

    with col3:
        st.metric("Date of Birth", patient_data.get("dob", "N/A"))
        st.metric("Phone", patient_data.get("phone", "N/A"))

def display_medications(medications: List[Dict[str, str]]):
    """Display medication information in a table"""
    st.subheader("💊 Medications")

    if not medications:
        st.info("No medications found in the document")
        return

    # Create enhanced dataframe
    med_data = []
    for i, med in enumerate(medications):
        med_data.append({
            "#": i + 1,
            "Drug Name": med.get("name", ""),
            "Strength": med.get("strength", ""),
            "Form": med.get("form", ""),
            "Directions": med.get("sig", ""),
            "Quantity": med.get("quantity", ""),
            "Refills": med.get("refills", "")
        })
    
    df = pd.DataFrame(med_data)
    st.dataframe(df, use_container_width=True)

def display_lab_results(lab_results: List[Dict[str, Any]]):
    """Display laboratory test results with enhanced visualization"""
    st.subheader("🧪 Laboratory Results")

    if not lab_results:
        st.info("No laboratory results found")
        return

    for i, lab_group in enumerate(lab_results):
        with st.expander(f"Lab Group {i+1}", expanded=True):
            if "headers" in lab_group and "rows" in lab_group:
                # Create DataFrame from table data
                df = pd.DataFrame(lab_group["rows"], columns=lab_group["headers"])
                st.dataframe(df, use_container_width=True)
                
                # Create visualization if numeric data present
                if len(df.columns) >= 3:
                    try:
                        # Try to create a chart for numeric values
                        numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns
                        if len(numeric_cols) > 0:
                            fig = px.bar(df, x=df.columns[0], y=numeric_cols[0], 
                                       title="Lab Values Visualization")
                            st.plotly_chart(fig, use_container_width=True)
                    except:
                        pass  # Skip visualization if data isn't suitable

def display_processing_metrics(metrics: Dict[str, Any]):
    """Display processing performance metrics"""
    st.subheader("⚡ Processing Metrics")
    
    if not metrics:
        st.info("No metrics available")
        return
    
    # Overall metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Time", f"{metrics.get('processing_time', 0):.2f}s")
    with col2:
        st.metric("Pages", metrics.get('page_count', 0))
    with col3:
        st.metric("Avg Confidence", f"{metrics.get('avg_confidence', 0):.1%}")
    with col4:
        st.metric("Data Points", metrics.get('extraction_count', 0))
    
    # Stage-wise metrics
    if "pages" in metrics:
        stage_data = []
        for page in metrics["pages"]:
            analysis = page.get("analysis", {})
            stage_data.append({
                "Page": page["page_number"],
                "Anchors": analysis.get("anchor_count", 0),
                "Confidence": analysis.get("confidence", 0),
                "Time": analysis.get("time", 0)
            })
        
        if stage_data:
            df = pd.DataFrame(stage_data)
            
            # Create charts
            col1, col2 = st.columns(2)
            
            with col1:
                fig = px.bar(df, x="Page", y="Anchors", title="Anchors per Page")
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                fig = px.line(df, x="Page", y="Confidence", title="Confidence by Page")
                st.plotly_chart(fig, use_container_width=True)

def main():
    """Main Streamlit application"""
    st.set_page_config(
        page_title="Dolphin Medical Parser - Production MVP",
        page_icon="🐬",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Custom CSS
    st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(90deg, #2E86AB 0%, #A23B72 100%);
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .main-header h1 {
        color: white;
        text-align: center;
        margin: 0;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #2E86AB;
    }
    .stage-indicator {
        padding: 0.5rem;
        border-radius: 5px;
        text-align: center;
        font-weight: bold;
    }
    .stage-analyzing { background-color: #FFF3CD; color: #856404; }
    .stage-parsing { background-color: #D1ECF1; color: #0C5460; }
    .stage-completed { background-color: #D4EDDA; color: #155724; }
    .stage-failed { background-color: #F8D7DA; color: #721C24; }
    </style>
    """, unsafe_allow_html=True)

    # Main header
    st.markdown("""
    <div class="main-header">
        <h1>🐬 Dolphin Medical Document Parser</h1>
        <p style="color: white; text-align: center; margin: 0;">
            Production-Ready MVP with Analyze-Then-Parse Pipeline
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Initialize session state
    if 'parser' not in st.session_state:
        config = DolphinConfig()
        st.session_state.parser = DolphinMedicalParser(config)
        st.session_state.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Sidebar Configuration
    with st.sidebar:
        st.header("⚙️ Dolphin Configuration")

        # Document type selection
        document_types = [
            "clinical_report",
            "lab_results", 
            "prescription",
            "discharge_summary",
            "radiology_report",
            "pathology_report"
        ]
        selected_doc_type = st.selectbox("Document Type:", document_types)

        # Processing options
        st.subheader("Processing Options")
        batch_size = st.slider("Batch Size", 1, 16, 8)
        confidence_threshold = st.slider("Confidence Threshold", 0.1, 1.0, 0.8)
        
        # Advanced settings
        with st.expander("Advanced Settings"):
            use_gpu = st.checkbox("Use GPU Acceleration", value=True)
            enable_logging = st.checkbox("Enable Detailed Logging", value=True)
            save_to_db = st.checkbox("Save to Database", value=True)
        
        # Session info
        st.subheader("Session Information")
        st.info(f"""
        **Session ID:** {st.session_state.session_id}
        
        **Model Status:** {'✅ Loaded' if st.session_state.parser.model_loaded else '⚠️ Mock Mode'}
        
        **Database:** {'✅ Connected' if save_to_db else '❌ Disabled'}
        """)

    # Main content area
    tab1, tab2, tab3, tab4 = st.tabs([
        "📄 Document Processing", 
        "📊 Analytics Dashboard", 
        "🔍 Search & Browse",
        "⚙️ System Status"
    ])

    with tab1:
        st.header("📄 Document Processing")

        # File upload section
        uploaded_files = st.file_uploader(
            "Upload Medical Documents",
            type=['pdf', 'jpg', 'jpeg', 'png', 'tiff'],
            accept_multiple_files=True,
            help="Supported formats: PDF, JPG, JPEG, PNG, TIFF"
        )

        if uploaded_files:
            # Process files
            for uploaded_file in uploaded_files:
                with st.container():
                    st.markdown(f"### 📋 Processing: {uploaded_file.name}")
                    
                    # Create temporary file
                    with tempfile.NamedTemporaryFile(delete=False, 
                                                   suffix=os.path.splitext(uploaded_file.name)[1]) as tmp_file:
                        tmp_file.write(uploaded_file.getvalue())
                        tmp_path = tmp_file.name

                    try:
                        # Processing with progress tracking
                        progress_container = st.container()
                        
                        with progress_container:
                            st.info("🐬 Initializing Dolphin processing pipeline...")
                            progress_bar = st.progress(0)
                            status_text = st.empty()
                            
                            # Start processing
                            progress_bar.progress(10)
                            status_text.text("Stage 1: Document Analysis...")
                            
                            # Parse document
                            parsed_data = st.session_state.parser.parse_medical_document(
                                tmp_path, 
                                selected_doc_type,
                                st.session_state.session_id
                            )
                            
                            progress_bar.progress(100)
                            status_text.text("✅ Processing Complete!")

                        if "error" not in parsed_data:
                            st.success("✅ Document processed successfully!")

                            # Create detailed results tabs
                            result_tabs = st.tabs([
                                "📊 Summary", 
                                "👤 Patient Data",
                                "💊 Medications",
                                "🧪 Lab Results", 
                                "📈 Metrics",
                                "🔄 Processing Log",
                                "💾 Export"
                            ])

                            with result_tabs[0]:  # Summary
                                st.markdown("### 📊 Extraction Summary")
                                
                                file_info = parsed_data.get("file_info", {})
                                aggregated = parsed_data.get("aggregated_data", {})
                                
                                col1, col2, col3, col4 = st.columns(4)
                                with col1:
                                    st.metric("Processing Time", 
                                            f"{file_info.get('total_processing_time', 0):.2f}s")
                                with col2:
                                    st.metric("Pages", parsed_data.get("page_count", 0))
                                with col3:
                                    st.metric("Medications", len(aggregated.get("medications", [])))
                                with col4:
                                    st.metric("Lab Results", len(aggregated.get("lab_results", [])))

                            with result_tabs[1]:  # Patient Data
                                patient_info = aggregated.get("patient_info", {})
                                display_patient_info(patient_info)

                            with result_tabs[2]:  # Medications
                                medications = aggregated.get("medications", [])
                                display_medications(medications)

                            with result_tabs[3]:  # Lab Results
                                lab_results = aggregated.get("lab_results", [])
                                display_lab_results(lab_results)

                            with result_tabs[4]:  # Metrics
                                display_processing_metrics(parsed_data)

                            with result_tabs[5]:  # Processing Log
                                st.subheader("🔄 Processing Log")
                                
                                # Show processing stages
                                for page_data in parsed_data.get("pages", []):
                                    with st.expander(f"Page {page_data['page_number']}"):
                                        analysis = page_data.get("analysis", {})
                                        st.json({
                                            "layout_type": analysis.get("layout_type"),
                                            "anchor_count": analysis.get("anchor_count"),
                                            "confidence": analysis.get("confidence"),
                                            "processing_time": analysis.get("time")
                                        })

                            with result_tabs[6]:  # Export
                                st.subheader("💾 Export Options")
                                
                                col1, col2 = st.columns(2)
                                
                                with col1:
                                    filename = os.path.splitext(uploaded_file.name)[0]
                                    json_link = create_download_link(parsed_data, filename, "json")
                                    st.markdown(json_link, unsafe_allow_html=True)

                                with col2:
                                    csv_link = create_download_link(parsed_data, filename, "csv")
                                    st.markdown(csv_link, unsafe_allow_html=True)

                        else:
                            st.error(f"❌ Processing failed: {parsed_data['error']}")

                    finally:
                        # Clean up temporary file
                        if os.path.exists(tmp_path):
                            os.unlink(tmp_path)

        else:
            # Show instructions
            st.info("""
            👆 **Upload medical documents to begin processing**
            
            The Dolphin framework will:
            1. 🔍 **Analyze** document structure and identify anchor points
            2. 📝 **Parse** content from each identified region  
            3. 🗂️ **Aggregate** data into structured medical records
            4. 💾 **Store** results in database for future access
            """)

    with tab2:
        st.header("📊 Analytics Dashboard")
        
        # Session statistics
        session_stats = st.session_state.parser.get_session_stats(st.session_state.session_id)
        
        if session_stats:
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Files", session_stats.get("total_files", 0))
            with col2:
                st.metric("Success Rate", f"{session_stats.get('success_rate', 0):.1%}")
            with col3:
                st.metric("Avg Time/File", f"{session_stats.get('avg_processing_time', 0):.2f}s")
            with col4:
                st.metric("Total Pages", session_stats.get("total_pages", 0))
            
            # Recent activity
            st.subheader("Recent Processing Activity")
            recent_files = st.session_state.parser.get_recent_activity(10)
            
            if recent_files:
                activity_df = pd.DataFrame(recent_files)
                st.dataframe(activity_df, use_container_width=True)
        else:
            st.info("No processing statistics available yet. Upload and process documents to see analytics.")

    with tab3:
        st.header("🔍 Search & Browse Extractions")
        
        # Search functionality
        search_term = st.text_input("Search patients by name or ID:")
        
        if search_term:
            search_results = st.session_state.parser.search_extractions(search_term)
            
            if search_results:
                st.subheader(f"Found {len(search_results)} result(s)")
                
                for result in search_results:
                    with st.expander(f"Patient: {result.get('patient_name', 'Unknown')}"):
                        st.json(result)
            else:
                st.info("No results found")

    with tab4:
        st.header("⚙️ System Status")
        
        # System information
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Model Status")
            st.info(f"""
            **Dolphin Model:** {'✅ Loaded' if st.session_state.parser.model_loaded else '⚠️ Mock Mode'}
            
            **Database:** ✅ Connected
            
            **File Manager:** ✅ Active
            
            **Logger:** ✅ Active
            """)
        
        with col2:
            st.subheader("Session Management")
            
            if st.button("Export Session Data"):
                export_path = st.session_state.parser.export_session_data(st.session_state.session_id)
                st.success(f"Session exported to: {export_path}")
            
            if st.button("Cleanup Session"):
                st.session_state.parser.cleanup_session()
                st.success("Session cleanup completed")

    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666;">
        <p>🐬 Dolphin Medical Parser MVP v2.0 | Production-Ready with Full Pipeline Integration</p>
        <p><small>⚠️ Ensure HIPAA compliance for production medical data processing</small></p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()