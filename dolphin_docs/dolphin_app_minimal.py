"""
Minimal Dolphin Medical Document Parser for Testing
Streamlit application with mock processing to verify the pipeline works
"""

import streamlit as st
import os
import tempfile
import json
import base64
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any, Optional
import time
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MockDolphinParser:
    """
    Mock Dolphin parser for testing the pipeline without heavy dependencies
    """
    
    def __init__(self):
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        logger.info("Initialized MockDolphinParser")
    
    def parse_medical_document(self, file_path: str, document_type: str = "clinical_report") -> Dict[str, Any]:
        """Mock document processing with realistic timing"""
        start_time = time.time()
        
        try:
            file_name = Path(file_path).name
            logger.info(f"Processing {file_name} as {document_type}")
            
            # Simulate processing stages
            time.sleep(0.5)  # Analysis stage
            time.sleep(1.0)  # Parsing stage
            time.sleep(0.3)  # Aggregation stage
            
            # Mock extraction results
            mock_results = {
                "file_info": {
                    "filename": file_name,
                    "file_type": document_type,
                    "parsed_at": datetime.now().isoformat(),
                    "total_processing_time": time.time() - start_time
                },
                "page_count": 2,
                "document_type": document_type,
                "pages": [
                    {
                        "page_number": 1,
                        "analysis": {
                            "layout_type": document_type,
                            "anchor_count": 4,
                            "confidence": 0.94,
                            "time": 0.5
                        },
                        "extracted_data": {
                            "patient_header": {
                                "patient_name": "Jane Smith",
                                "patient_id": "MRN-2025-001",
                                "dob": "1985-03-22",
                                "gender": "Female"
                            },
                            "clinical_notes": {
                                "chief_complaint": "Routine follow-up",
                                "assessment": "Patient doing well on current medications"
                            }
                        }
                    },
                    {
                        "page_number": 2,
                        "analysis": {
                            "layout_type": document_type,
                            "anchor_count": 3,
                            "confidence": 0.91,
                            "time": 0.4
                        },
                        "extracted_data": {
                            "medications": {
                                "medications": [
                                    {
                                        "name": "Metformin",
                                        "strength": "500mg",
                                        "form": "tablet",
                                        "sig": "Take 1 tablet twice daily",
                                        "quantity": "60",
                                        "refills": "5"
                                    }
                                ]
                            }
                        }
                    }
                ],
                "aggregated_data": {
                    "patient_info": {
                        "patient_name": "Jane Smith",
                        "patient_id": "MRN-2025-001",
                        "dob": "1985-03-22",
                        "gender": "Female",
                        "phone": "555-0123"
                    },
                    "medications": [
                        {
                            "name": "Metformin",
                            "strength": "500mg",
                            "form": "tablet",
                            "sig": "Take 1 tablet twice daily",
                            "quantity": "60",
                            "refills": "5"
                        },
                        {
                            "name": "Lisinopril", 
                            "strength": "10mg",
                            "form": "tablet",
                            "sig": "Take 1 tablet once daily",
                            "quantity": "30",
                            "refills": "11"
                        }
                    ],
                    "lab_results": [
                        {
                            "table_type": "lab_results",
                            "headers": ["Test Name", "Result", "Units", "Reference Range", "Flag"],
                            "rows": [
                                ["Glucose", "95", "mg/dL", "70-110", ""],
                                ["Creatinine", "0.9", "mg/dL", "0.6-1.2", ""],
                                ["Hemoglobin", "13.2", "g/dL", "12.0-16.0", ""]
                            ]
                        }
                    ],
                    "diagnoses": [
                        {
                            "description": "Type 2 diabetes mellitus",
                            "icd10": "E11.9",
                            "status": "active"
                        }
                    ],
                    "clinical_notes": [
                        "Patient presents for routine diabetes follow-up. Current medications well tolerated."
                    ]
                }
            }
            
            processing_time = time.time() - start_time
            mock_results["file_info"]["total_processing_time"] = processing_time
            
            logger.info(f"Completed processing {file_name} in {processing_time:.2f}s")
            return mock_results
            
        except Exception as e:
            logger.error(f"Error processing {file_path}: {e}")
            return {"error": str(e)}

def create_download_link(data: Dict[str, Any], filename: str, file_format: str = "json") -> str:
    """Create a download link for parsed data"""
    if file_format == "json":
        json_str = json.dumps(data, indent=2, default=str)
        b64 = base64.b64encode(json_str.encode()).decode()
        href = f'<a href="data:application/json;base64,{b64}" download="{filename}.json">Download JSON Report</a>'
    elif file_format == "csv":
        # Simple CSV conversion for demo
        csv_data = "Type,Count\n"
        aggregated = data.get("aggregated_data", {})
        csv_data += f"Medications,{len(aggregated.get('medications', []))}\n"
        csv_data += f"Lab Results,{len(aggregated.get('lab_results', []))}\n"
        csv_data += f"Diagnoses,{len(aggregated.get('diagnoses', []))}\n"
        
        b64 = base64.b64encode(csv_data.encode()).decode()
        href = f'<a href="data:text/csv;base64,{b64}" download="{filename}.csv">Download CSV Report</a>'
    else:
        href = "Unsupported format"
    return href

def display_patient_info(patient_data: Dict[str, str]):
    """Display patient information"""
    st.subheader("👤 Patient Information")
    
    if not patient_data:
        st.info("No patient information extracted")
        return
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Name", patient_data.get("patient_name", "N/A"))
        st.metric("Gender", patient_data.get("gender", "N/A"))
    
    with col2:
        st.metric("Patient ID", patient_data.get("patient_id", "N/A"))
        st.metric("DOB", patient_data.get("dob", "N/A"))
    
    with col3:
        st.metric("Phone", patient_data.get("phone", "N/A"))

def display_medications(medications: List[Dict[str, str]]):
    """Display medication information"""
    st.subheader("💊 Medications")
    
    if not medications:
        st.info("No medications found")
        return
    
    # Create table
    med_data = []
    for i, med in enumerate(medications):
        med_data.append({
            "#": i + 1,
            "Drug": med.get("name", ""),
            "Strength": med.get("strength", ""),
            "Form": med.get("form", ""),
            "Directions": med.get("sig", ""),
            "Quantity": med.get("quantity", ""),
            "Refills": med.get("refills", "")
        })
    
    df = pd.DataFrame(med_data)
    st.dataframe(df, use_container_width=True)

def display_lab_results(lab_results: List[Dict[str, Any]]):
    """Display lab results"""
    st.subheader("🧪 Laboratory Results")
    
    if not lab_results:
        st.info("No lab results found")
        return
    
    for i, lab in enumerate(lab_results):
        with st.expander(f"Lab Group {i+1}", expanded=True):
            if "headers" in lab and "rows" in lab:
                df = pd.DataFrame(lab["rows"], columns=lab["headers"])
                st.dataframe(df, use_container_width=True)

def display_processing_metrics(data: Dict[str, Any]):
    """Display processing metrics"""
    st.subheader("⚡ Processing Metrics")
    
    file_info = data.get("file_info", {})
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Processing Time", f"{file_info.get('total_processing_time', 0):.2f}s")
    with col2:
        st.metric("Pages", data.get("page_count", 0))
    with col3:
        # Calculate average confidence
        pages = data.get("pages", [])
        if pages:
            avg_conf = sum(p.get("analysis", {}).get("confidence", 0) for p in pages) / len(pages)
            st.metric("Avg Confidence", f"{avg_conf:.1%}")
        else:
            st.metric("Avg Confidence", "N/A")
    with col4:
        aggregated = data.get("aggregated_data", {})
        total_items = (len(aggregated.get("medications", [])) + 
                      len(aggregated.get("lab_results", [])) +
                      len(aggregated.get("diagnoses", [])))
        st.metric("Data Points", total_items)

def main():
    """Main Streamlit application"""
    st.set_page_config(
        page_title="Dolphin Medical Parser - Test Version",
        page_icon="🐬",
        layout="wide"
    )
    
    # Header
    st.markdown("""
    <div style="background: linear-gradient(90deg, #2E86AB 0%, #A23B72 100%); padding: 1.5rem; border-radius: 10px; margin-bottom: 2rem;">
        <h1 style="color: white; text-align: center; margin: 0;">🐬 Dolphin Medical Parser - Test Version</h1>
        <p style="color: white; text-align: center; margin: 0;">Verifying MVP Pipeline Functionality</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize parser
    if 'parser' not in st.session_state:
        st.session_state.parser = MockDolphinParser()
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Test Configuration")
        
        document_types = [
            "clinical_report",
            "lab_results", 
            "prescription",
            "discharge_summary",
            "radiology_report"
        ]
        selected_doc_type = st.selectbox("Document Type:", document_types)
        
        st.subheader("System Status")
        st.success("✅ Mock Parser: Active")
        st.success("✅ Pipeline: Functional")
        st.info(f"Session: {st.session_state.parser.session_id}")
    
    # Main content
    st.header("📄 Document Processing Test")
    
    # File upload
    uploaded_files = st.file_uploader(
        "Upload Test Documents (any format for demo)",
        type=['pdf', 'jpg', 'jpeg', 'png', 'txt'],
        accept_multiple_files=True,
        help="Upload any file type for testing - processing is simulated"
    )
    
    if uploaded_files:
        for uploaded_file in uploaded_files:
            st.markdown(f"### 📋 Processing: {uploaded_file.name}")
            
            # Create temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                tmp_path = tmp_file.name
            
            try:
                # Show processing progress
                progress_container = st.container()
                
                with progress_container:
                    with st.spinner("🐬 Processing with Dolphin pipeline..."):
                        progress_bar = st.progress(0)
                        status_text = st.empty()
                        
                        # Simulate processing stages
                        status_text.text("Stage 1: Document Analysis...")
                        progress_bar.progress(20)
                        time.sleep(0.2)
                        
                        status_text.text("Stage 2: Anchor Detection...")
                        progress_bar.progress(50)
                        time.sleep(0.2)
                        
                        status_text.text("Stage 3: Content Parsing...")
                        progress_bar.progress(80)
                        time.sleep(0.2)
                        
                        # Process document
                        result = st.session_state.parser.parse_medical_document(
                            tmp_path, 
                            selected_doc_type
                        )
                        
                        progress_bar.progress(100)
                        status_text.text("✅ Processing Complete!")
                
                if "error" not in result:
                    st.success("✅ Document processed successfully!")
                    
                    # Results tabs
                    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
                        "📊 Summary",
                        "👤 Patient", 
                        "💊 Medications",
                        "🧪 Lab Results",
                        "📈 Metrics",
                        "💾 Export"
                    ])
                    
                    with tab1:  # Summary
                        st.markdown("### 📊 Processing Summary")
                        
                        file_info = result.get("file_info", {})
                        aggregated = result.get("aggregated_data", {})
                        
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("Processing Time", f"{file_info.get('total_processing_time', 0):.2f}s")
                        with col2:
                            st.metric("Pages", result.get("page_count", 0))
                        with col3:
                            st.metric("Medications", len(aggregated.get("medications", [])))
                        with col4:
                            st.metric("Lab Results", len(aggregated.get("lab_results", [])))
                        
                        # Show pipeline stages
                        st.markdown("### 🔄 Pipeline Stages")
                        for page in result.get("pages", []):
                            page_num = page.get("page_number", 1)
                            analysis = page.get("analysis", {})
                            
                            with st.expander(f"Page {page_num} Processing"):
                                col1, col2, col3 = st.columns(3)
                                with col1:
                                    st.metric("Anchors Found", analysis.get("anchor_count", 0))
                                with col2:
                                    st.metric("Confidence", f"{analysis.get('confidence', 0):.1%}")
                                with col3:
                                    st.metric("Stage Time", f"{analysis.get('time', 0):.2f}s")
                    
                    with tab2:  # Patient Info
                        patient_info = aggregated.get("patient_info", {})
                        display_patient_info(patient_info)
                    
                    with tab3:  # Medications
                        medications = aggregated.get("medications", [])
                        display_medications(medications)
                    
                    with tab4:  # Lab Results
                        lab_results = aggregated.get("lab_results", [])
                        display_lab_results(lab_results)
                    
                    with tab5:  # Metrics
                        display_processing_metrics(result)
                    
                    with tab6:  # Export
                        st.subheader("💾 Export Options")
                        
                        filename = os.path.splitext(uploaded_file.name)[0]
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            json_link = create_download_link(result, filename, "json")
                            st.markdown(json_link, unsafe_allow_html=True)
                        with col2:
                            csv_link = create_download_link(result, filename, "csv")
                            st.markdown(csv_link, unsafe_allow_html=True)
                
                else:
                    st.error(f"❌ Processing failed: {result['error']}")
                
            finally:
                # Clean up temp file
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)
    
    else:
        # Instructions
        st.info("""
        👆 **Upload test documents to verify the pipeline**
        
        This test version demonstrates:
        - ✅ Two-stage processing pipeline (Analyze → Parse)
        - ✅ Progress tracking with visual feedback
        - ✅ Structured medical data extraction
        - ✅ Multi-tab results display
        - ✅ Export functionality (JSON/CSV)
        - ✅ Error handling and cleanup
        
        The processing is simulated but follows the real Dolphin architecture.
        """)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666;">
        <p>🐬 Dolphin Medical Parser MVP - Pipeline Verification Test</p>
        <p><small>✅ Core functionality verified - Ready for production Dolphin integration</small></p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()