# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is a medical document processing application using the Dolphin framework (Document Image Parsing via Heterogeneous Anchor Prompting) for parsing healthcare PDFs. The project consists of:

1. **Tutorial Documentation** (`medical_pdfparse_dolphin.md`) - Comprehensive guide for implementing AI-powered medical document parsing
2. **Streamlit Web Application** (`medical_pdfparser_dolphin.py`) - Interactive web interface for processing medical PDFs

## Project Structure

- `medical_pdfparse_dolphin.md` - Tutorial documentation explaining Dolphin framework implementation for medical documents
- `medical_pdfparser_dolphin.py` - Streamlit application with medical PDF parsing functionality

## Development Commands

### Running the Application
```bash
# Run the Streamlit web application
streamlit run medical_pdfparser_dolphin.py

# Install required dependencies (based on tutorial documentation)
pip install streamlit pandas plotly seaborn scikit-learn
pip install huggingface_hub  # For model downloads
```

### Model Setup
```bash
# Download Dolphin model from Hugging Face
huggingface-cli download ByteDance/Dolphin --local-dir ./hf_model

# Optional: Install acceleration libraries
pip install tensorrt-llm  # For NVIDIA GPU acceleration
pip install vllm  # For efficient inference
```

## Architecture

### DolphinMedicalParser Class
The main parser class in `medical_pdfparser_dolphin.py` handles medical document processing:

- **Initialization**: Sets up model path and supported formats
- **Document Parsing**: `parse_medical_document()` - main entry point
- **Data Extraction Methods**:
  - `_extract_patient_info()` - demographics
  - `_extract_clinical_data()` - vital signs and measurements
  - `_extract_medications()` - prescription information
  - `_extract_lab_results()` - laboratory test data
  - `_extract_diagnostic_info()` - diagnoses and procedures

### Streamlit Application Flow
1. **Configuration Sidebar**: Document type selection, processing options, model settings
2. **File Upload**: Accepts PDF, JPG, JPEG, PNG files
3. **Processing**: Creates temporary files, parses with DolphinMedicalParser
4. **Results Display**: 
   - Summary tab with key metrics
   - Detailed analysis with structured data
   - Raw text extraction
   - Export options (JSON/CSV)
   - HIPAA compliance information

### Key Medical Document Types Supported
- Clinical Reports
- Lab Results
- Prescriptions
- Discharge Summaries
- Radiology Reports
- Pathology Reports
- Insurance Claims

## Important Implementation Notes

1. **Mock Implementation**: Current `DolphinMedicalParser` returns mock data for demonstration. Integration with actual Dolphin framework API needed for production use.

2. **HIPAA Compliance**: Application includes privacy notices and compliance guidelines for handling Protected Health Information (PHI).

3. **Temporary File Handling**: Uploaded files are processed via temporary files that are automatically deleted after processing.

4. **Data Export**: Supports JSON and CSV export formats for parsed medical data.

5. **Model Path**: Default model path is `./hf_model` - ensure Dolphin models are downloaded to this location.

## Complete Processing Workflow

### Stage 1: Document Analysis
1. **File Upload/Batch Load**: Multi-format support with validation
2. **Image Conversion**: PDF to images with configurable DPI
3. **Layout Analysis**: Dolphin identifies document structure and regions
4. **Anchor Generation**: Creates typed anchor points (text, table, list, etc.)
5. **Confidence Assessment**: Scores each identified region
6. **Progress Logging**: Real-time progress tracking and metrics

### Stage 2: Content Extraction
1. **Anchor Processing**: Type-specific parsing for each identified region
2. **Medical NLP**: Enhanced processing for medical terminology
3. **Structured Output**: Converts visual content to structured medical data
4. **Quality Validation**: Confidence-based filtering and medical logic checking
5. **Data Aggregation**: Combines multi-page results into cohesive records
6. **Database Storage**: Persistent storage with full medical data schema

### Stage 3: Results and Analytics
1. **Real-time Visualization**: Interactive charts and medical data displays
2. **Export Generation**: Multiple formats (JSON, CSV, medical standards)
3. **Search and Browse**: Patient lookup and historical analysis
4. **Performance Analytics**: Processing metrics and system health monitoring
5. **Session Management**: Complete session lifecycle with cleanup
6. **Audit and Compliance**: Full audit trails and compliance reporting