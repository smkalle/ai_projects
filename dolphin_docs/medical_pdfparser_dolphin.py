
import streamlit as st
import os
import tempfile
import json
import base64
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any
import io
import zipfile
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DolphinMedicalParser:
    """
    Medical PDF Parser using Dolphin framework for healthcare documents
    This class provides methods to parse medical PDFs and extract structured data
    """

    def __init__(self, model_path: str = "./hf_model"):
        """Initialize the Dolphin Medical Parser"""
        self.model_path = model_path
        self.supported_formats = ['.pdf', '.jpg', '.jpeg', '.png']

    def parse_medical_document(self, file_path: str, document_type: str = "medical") -> Dict[str, Any]:
        """
        Parse medical document using Dolphin framework
        Returns structured medical data
        """
        try:
            # Simulate Dolphin parsing - in real implementation, this would call actual Dolphin API
            # For demo purposes, we're creating a mock response
            parsed_data = {
                "document_info": {
                    "filename": os.path.basename(file_path),
                    "type": document_type,
                    "parsed_at": datetime.now().isoformat(),
                    "pages": 1
                },
                "patient_info": self._extract_patient_info(),
                "clinical_data": self._extract_clinical_data(),
                "medications": self._extract_medications(),
                "lab_results": self._extract_lab_results(),
                "diagnostic_info": self._extract_diagnostic_info(),
                "raw_text": self._extract_raw_text(),
                "structured_sections": self._extract_sections()
            }
            return parsed_data
        except Exception as e:
            logger.error(f"Error parsing document: {str(e)}")
            return {"error": str(e)}

    def _extract_patient_info(self) -> Dict[str, str]:
        """Extract patient demographic information"""
        return {
            "name": "John Doe",
            "age": "45",
            "gender": "Male",
            "patient_id": "P123456",
            "dob": "1979-01-15",
            "phone": "+1-555-0123",
            "address": "123 Main St, City, State 12345"
        }

    def _extract_clinical_data(self) -> Dict[str, Any]:
        """Extract clinical measurements and vital signs"""
        return {
            "vital_signs": {
                "blood_pressure": "120/80 mmHg",
                "heart_rate": "72 bpm",
                "temperature": "98.6Â°F",
                "respiratory_rate": "16/min",
                "oxygen_saturation": "98%"
            },
            "measurements": {
                "height": "5'10"",
                "weight": "175 lbs",
                "bmi": "25.1"
            }
        }

    def _extract_medications(self) -> List[Dict[str, str]]:
        """Extract medication information"""
        return [
            {
                "name": "Metformin",
                "dosage": "500mg",
                "frequency": "Twice daily",
                "route": "Oral",
                "prescriber": "Dr. Smith"
            },
            {
                "name": "Lisinopril",
                "dosage": "10mg",
                "frequency": "Once daily",
                "route": "Oral",
                "prescriber": "Dr. Smith"
            }
        ]

    def _extract_lab_results(self) -> List[Dict[str, Any]]:
        """Extract laboratory test results"""
        return [
            {
                "test_name": "Complete Blood Count",
                "date": "2025-08-05",
                "results": {
                    "WBC": "7.2 K/uL",
                    "RBC": "4.5 M/uL",
                    "Hemoglobin": "14.2 g/dL",
                    "Hematocrit": "42.1%"
                },
                "reference_ranges": {
                    "WBC": "4.0-11.0 K/uL",
                    "RBC": "4.2-5.4 M/uL",
                    "Hemoglobin": "13.5-17.5 g/dL",
                    "Hematocrit": "41-50%"
                },
                "status": "Normal"
            }
        ]

    def _extract_diagnostic_info(self) -> Dict[str, Any]:
        """Extract diagnostic information"""
        return {
            "primary_diagnosis": "Type 2 Diabetes Mellitus",
            "icd_10_code": "E11.9",
            "secondary_diagnoses": ["Hypertension", "Hyperlipidemia"],
            "procedures": ["Blood glucose monitoring", "Blood pressure check"],
            "assessment": "Patient shows good control of diabetes with current medication regimen"
        }

    def _extract_raw_text(self) -> str:
        """Extract raw text content"""
        return """
        PATIENT: John Doe
        DOB: 01/15/1979
        MRN: P123456

        CHIEF COMPLAINT: Routine diabetes follow-up

        HISTORY OF PRESENT ILLNESS:
        45-year-old male with Type 2 diabetes mellitus presents for routine follow-up.
        Patient reports good adherence to medication regimen. No recent episodes of
        hypoglycemia or hyperglycemia. Blood sugar logs show values ranging 120-160 mg/dL.

        PHYSICAL EXAMINATION:
        Vital Signs: BP 120/80, HR 72, Temp 98.6Â°F, RR 16, O2 Sat 98%
        General: Well-appearing, no acute distress
        HEENT: Pupils equal, reactive to light
        Cardiovascular: Regular rate and rhythm, no murmurs
        Pulmonary: Clear to auscultation bilaterally

        ASSESSMENT AND PLAN:
        1. Type 2 Diabetes Mellitus - well controlled
           - Continue current Metformin 500mg BID
           - Repeat HbA1c in 3 months
        2. Hypertension - well controlled
           - Continue Lisinopril 10mg daily

        Follow-up in 3 months or sooner if concerns.
        """

    def _extract_sections(self) -> List[Dict[str, str]]:
        """Extract structured document sections"""
        return [
            {"section": "Patient Demographics", "content": "John Doe, 45 years old, Male"},
            {"section": "Chief Complaint", "content": "Routine diabetes follow-up"},
            {"section": "History of Present Illness", "content": "45-year-old male with Type 2 diabetes..."},
            {"section": "Physical Examination", "content": "Vital Signs: BP 120/80, HR 72..."},
            {"section": "Assessment and Plan", "content": "Type 2 Diabetes Mellitus - well controlled..."}
        ]

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

def display_patient_info(patient_data: Dict[str, str]):
    """Display patient information in a structured format"""
    st.subheader("ðŸ‘¤ Patient Information")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Name", patient_data.get("name", "N/A"))
        st.metric("Age", patient_data.get("age", "N/A"))

    with col2:
        st.metric("Gender", patient_data.get("gender", "N/A"))
        st.metric("Patient ID", patient_data.get("patient_id", "N/A"))

    with col3:
        st.metric("Date of Birth", patient_data.get("dob", "N/A"))
        st.metric("Phone", patient_data.get("phone", "N/A"))

def display_clinical_data(clinical_data: Dict[str, Any]):
    """Display clinical measurements and vital signs"""
    st.subheader("ðŸ©º Clinical Data")

    # Vital Signs
    st.write("**Vital Signs:**")
    vital_signs = clinical_data.get("vital_signs", {})

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric("Blood Pressure", vital_signs.get("blood_pressure", "N/A"))
    with col2:
        st.metric("Heart Rate", vital_signs.get("heart_rate", "N/A"))
    with col3:
        st.metric("Temperature", vital_signs.get("temperature", "N/A"))
    with col4:
        st.metric("Respiratory Rate", vital_signs.get("respiratory_rate", "N/A"))
    with col5:
        st.metric("O2 Saturation", vital_signs.get("oxygen_saturation", "N/A"))

    # Physical Measurements
    st.write("**Physical Measurements:**")
    measurements = clinical_data.get("measurements", {})

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Height", measurements.get("height", "N/A"))
    with col2:
        st.metric("Weight", measurements.get("weight", "N/A"))
    with col3:
        st.metric("BMI", measurements.get("bmi", "N/A"))

def display_medications(medications: List[Dict[str, str]]):
    """Display medication information in a table"""
    st.subheader("ðŸ’Š Medications")

    if medications:
        df = pd.DataFrame(medications)
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No medications found in the document")

def display_lab_results(lab_results: List[Dict[str, Any]]):
    """Display laboratory test results"""
    st.subheader("ðŸ§ª Laboratory Results")

    for lab in lab_results:
        with st.expander(f"{lab['test_name']} - {lab['date']}"):
            st.write(f"**Status:** {lab['status']}")

            col1, col2 = st.columns(2)

            with col1:
                st.write("**Results:**")
                for test, value in lab['results'].items():
                    st.write(f"â€¢ {test}: {value}")

            with col2:
                st.write("**Reference Ranges:**")
                for test, range_val in lab['reference_ranges'].items():
                    st.write(f"â€¢ {test}: {range_val}")

def display_diagnostic_info(diagnostic_data: Dict[str, Any]):
    """Display diagnostic information"""
    st.subheader("ðŸ”¬ Diagnostic Information")

    col1, col2 = st.columns(2)

    with col1:
        st.write("**Primary Diagnosis:**")
        st.write(f"â€¢ {diagnostic_data.get('primary_diagnosis', 'N/A')}")
        st.write(f"â€¢ ICD-10: {diagnostic_data.get('icd_10_code', 'N/A')}")

        st.write("**Secondary Diagnoses:**")
        for diagnosis in diagnostic_data.get('secondary_diagnoses', []):
            st.write(f"â€¢ {diagnosis}")

    with col2:
        st.write("**Procedures:**")
        for procedure in diagnostic_data.get('procedures', []):
            st.write(f"â€¢ {procedure}")

        st.write("**Assessment:**")
        st.write(diagnostic_data.get('assessment', 'N/A'))

def main():
    """Main Streamlit application"""
    st.set_page_config(
        page_title="Medical PDF Parser - Dolphin Framework",
        page_icon="ðŸ¥",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Custom CSS
    st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
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
        border-left: 4px solid #667eea;
    }
    .section-header {
        color: #667eea;
        border-bottom: 2px solid #667eea;
        padding-bottom: 0.5rem;
        margin-bottom: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)

    # Main header
    st.markdown("""
    <div class="main-header">
        <h1>ðŸ¥ Medical PDF Document Parser</h1>
        <p style="color: white; text-align: center; margin: 0;">
            Powered by Dolphin Framework - Advanced AI for Healthcare Document Analysis
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Sidebar
    with st.sidebar:
        st.header("âš™ï¸ Configuration")

        # Document type selection
        document_types = [
            "Clinical Report",
            "Lab Results", 
            "Prescription",
            "Discharge Summary",
            "Radiology Report",
            "Pathology Report",
            "Insurance Claim",
            "General Medical Document"
        ]
        selected_doc_type = st.selectbox("Select Document Type:", document_types)

        # Processing options
        st.subheader("Processing Options")
        extract_tables = st.checkbox("Extract Tables", value=True)
        extract_images = st.checkbox("Extract Images", value=False)
        ocr_enhancement = st.checkbox("Enhanced OCR", value=True)

        # Model settings
        st.subheader("Model Settings")
        batch_size = st.slider("Batch Size", 1, 16, 8)
        confidence_threshold = st.slider("Confidence Threshold", 0.1, 1.0, 0.8)

        # Information box
        st.info("""
        **About Dolphin Framework:**

        â€¢ Novel analyze-then-parse approach
        â€¢ Trained on 30M+ samples
        â€¢ Supports complex medical layouts
        â€¢ TensorRT-LLM acceleration
        â€¢ State-of-the-art accuracy
        """)

    # File upload section
    st.header("ðŸ“„ Upload Medical Document")

    uploaded_files = st.file_uploader(
        "Choose medical PDF or image files",
        type=['pdf', 'jpg', 'jpeg', 'png'],
        accept_multiple_files=True,
        help="Supported formats: PDF, JPG, JPEG, PNG"
    )

    if uploaded_files:
        # Initialize parser
        parser = DolphinMedicalParser()

        # Process files
        for uploaded_file in uploaded_files:
            st.subheader(f"ðŸ“‹ Processing: {uploaded_file.name}")

            # Create temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                tmp_path = tmp_file.name

            try:
                # Show processing status
                with st.spinner(f"Parsing {uploaded_file.name} using Dolphin framework..."):
                    parsed_data = parser.parse_medical_document(tmp_path, selected_doc_type.lower())

                if "error" not in parsed_data:
                    # Display results
                    st.success("âœ… Document parsed successfully!")

                    # Create tabs for different views
                    tab1, tab2, tab3, tab4, tab5 = st.tabs([
                        "ðŸ“Š Summary", 
                        "ðŸ” Detailed Analysis", 
                        "ðŸ“„ Raw Text", 
                        "ðŸ“¥ Export", 
                        "âš ï¸ Compliance"
                    ])

                    with tab1:
                        # Summary view
                        st.markdown("### ðŸ“ˆ Document Summary")

                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("Document Type", selected_doc_type)
                        with col2:
                            st.metric("Pages", parsed_data["document_info"]["pages"])
                        with col3:
                            st.metric("Parsed Sections", len(parsed_data["structured_sections"]))
                        with col4:
                            st.metric("Medications Found", len(parsed_data["medications"]))

                        # Key findings
                        st.markdown("### ðŸŽ¯ Key Findings")
                        primary_dx = parsed_data["diagnostic_info"]["primary_diagnosis"]
                        st.info(f"**Primary Diagnosis:** {primary_dx}")

                        # Quick patient overview
                        patient_name = parsed_data["patient_info"]["name"]
                        patient_age = parsed_data["patient_info"]["age"]
                        st.write(f"**Patient:** {patient_name}, Age {patient_age}")

                    with tab2:
                        # Detailed analysis
                        display_patient_info(parsed_data["patient_info"])
                        display_clinical_data(parsed_data["clinical_data"])
                        display_medications(parsed_data["medications"])
                        display_lab_results(parsed_data["lab_results"])
                        display_diagnostic_info(parsed_data["diagnostic_info"])

                    with tab3:
                        # Raw text view
                        st.subheader("ðŸ“„ Extracted Text Content")
                        st.text_area(
                            "Raw Text",
                            parsed_data["raw_text"],
                            height=400,
                            help="This is the raw text extracted from the document"
                        )

                        # Structured sections
                        st.subheader("ðŸ“‘ Document Sections")
                        for section in parsed_data["structured_sections"]:
                            with st.expander(section["section"]):
                                st.write(section["content"])

                    with tab4:
                        # Export options
                        st.subheader("ðŸ“¥ Export Options")

                        col1, col2 = st.columns(2)

                        with col1:
                            # JSON export
                            filename = os.path.splitext(uploaded_file.name)[0]
                            json_link = create_download_link(parsed_data, filename, "json")
                            st.markdown(json_link, unsafe_allow_html=True)

                        with col2:
                            # CSV export for structured data
                            csv_link = create_download_link(parsed_data, filename, "csv")
                            st.markdown(csv_link, unsafe_allow_html=True)

                        # Generate report
                        if st.button("ðŸ“Š Generate Medical Report"):
                            report_data = {
                                "patient_name": parsed_data["patient_info"]["name"],
                                "document_type": selected_doc_type,
                                "primary_diagnosis": parsed_data["diagnostic_info"]["primary_diagnosis"],
                                "medications_count": len(parsed_data["medications"]),
                                "processed_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            }

                            st.json(report_data)

                    with tab5:
                        # HIPAA Compliance information
                        st.subheader("âš ï¸ HIPAA Compliance & Privacy")

                        st.warning("""
                        **Important Privacy Notice:**

                        This application processes medical documents containing Protected Health Information (PHI). 
                        Please ensure compliance with HIPAA and other applicable privacy regulations.
                        """)

                        compliance_checklist = [
                            "âœ… Data processed locally (no external transmission)",
                            "âœ… Temporary files automatically deleted",
                            "âœ… No data stored permanently on server",
                            "âš ï¸ User responsible for access control",
                            "âš ï¸ Audit logs should be maintained separately"
                        ]

                        for item in compliance_checklist:
                            st.write(item)

                        st.info("""
                        **Recommendations:**
                        1. Use this tool only in secure, authorized environments
                        2. Ensure proper user authentication and access controls
                        3. Maintain audit trails of document processing
                        4. Regularly review and update security measures
                        5. Train staff on HIPAA compliance requirements
                        """)

                else:
                    st.error(f"âŒ Error processing document: {parsed_data['error']}")

            finally:
                # Clean up temporary file
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)

    else:
        # Show demo information
        st.info("""
        ðŸ‘† **Upload medical documents to get started!**

        This application uses the state-of-the-art Dolphin framework to parse complex medical PDFs 
        and extract structured healthcare data including:

        â€¢ **Patient Demographics** - Name, age, contact information
        â€¢ **Clinical Data** - Vital signs, measurements, physical exam findings  
        â€¢ **Medications** - Prescriptions, dosages, administration routes
        â€¢ **Laboratory Results** - Test values, reference ranges, interpretations
        â€¢ **Diagnostic Information** - Diagnoses, ICD codes, treatment plans
        â€¢ **Document Structure** - Organized sections and metadata
        """)

        # Sample document types
        st.subheader("ðŸ“‹ Supported Document Types")

        doc_examples = [
            ("ðŸ¥ Clinical Reports", "Comprehensive patient visit summaries with diagnoses and treatment plans"),
            ("ðŸ§ª Lab Results", "Laboratory test results with values and reference ranges"),
            ("ðŸ’Š Prescriptions", "Medication prescriptions with dosage and administration instructions"),
            ("ðŸ“‹ Discharge Summaries", "Hospital discharge documentation and follow-up care instructions"),
            ("ðŸ“· Radiology Reports", "Imaging study results and radiologist interpretations"),
            ("ðŸ”¬ Pathology Reports", "Tissue and specimen analysis results"),
            ("ðŸ“„ Insurance Claims", "Medical billing and insurance claim documentation")
        ]

        for doc_type, description in doc_examples:
            st.write(f"**{doc_type}**: {description}")

    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666;">
        <p>Medical PDF Parser v1.0 | Powered by Dolphin Framework | 
        Built with â¤ï¸ for Healthcare Professionals</p>
        <p><small>âš ï¸ This tool is for demonstration purposes. Always verify extracted data for clinical use.</small></p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
