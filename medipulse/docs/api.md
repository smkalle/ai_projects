# MediPulse API Documentation

## Classes

### MediPulseConfig

Configuration class for MediPulse settings.

```python
from medipulse import MediPulseConfig

config = MediPulseConfig()
```

**Attributes:**
- `openai_api_key`: OpenAI API key from environment variables
- `model`: OpenAI model to use (default: "gpt-4o")

**Methods:**
- `get_llm()`: Returns configured ChatOpenAI instance

### MediPulse

Main class for medical document extraction.

```python
from medipulse import MediPulse

medipulse = MediPulse()
# or with custom config
medipulse = MediPulse(config)
```

**Methods:**

#### `process_document(image_base64: str) -> dict`

Process a medical document from base64 encoded image.

**Parameters:**
- `image_base64` (str): Base64 encoded image of the medical document

**Returns:**
- `dict`: Processing result with the following structure:
  ```python
  {
      "success": bool,
      "doc_classification": {
          "doc_type": str,
          "confidence": float,
          "reasoning": str
      },
      "extracted_data": {
          "patient_name": str,
          "patient_id": str,
          "date_of_service": str,
          "lab_results": dict,
          # ... other medical fields
      },
      "validation": {
          "is_valid": bool,
          "errors": list,
          "warnings": list,
          "completeness_score": float
      },
      "processing_steps": list,
      "error_message": str  # if success is False
  }
  ```

**Example:**
```python
import base64

with open('lab_report.jpg', 'rb') as f:
    image_data = f.read()
    image_base64 = base64.b64encode(image_data).decode('utf-8')

result = medipulse.process_document(image_base64)
print(result['extracted_data'])
```

#### `process_document_from_file(file_path: str) -> dict`

Process a medical document from a file path.

**Parameters:**
- `file_path` (str): Path to the image file

**Returns:**
- `dict`: Same structure as `process_document()`

**Example:**
```python
result = medipulse.process_document_from_file('path/to/medical_document.jpg')
```

## Data Models

### DocumentType

Document classification result.

**Fields:**
- `doc_type`: One of "lab_report", "patient_intake", "prescription", "discharge_summary", "other"
- `confidence`: Float between 0.0 and 1.0
- `reasoning`: Brief explanation for the classification

### ExtractedData

Structured medical data extraction result.

**Fields:**
- `patient_name`: Patient's full name
- `patient_id`: Patient identifier
- `date_of_service`: Date of medical service
- `date_of_birth`: Patient's date of birth
- `physician_name`: Attending physician
- `lab_results`: Dictionary of lab test results
- `medications`: List of medications
- `diagnosis`: Medical diagnosis
- `vital_signs`: Dictionary of vital signs
- `allergies`: List of allergies
- `notes`: Additional notes
- `confidence_score`: Overall extraction confidence

### ValidationResult

Validation result for extracted data.

**Fields:**
- `is_valid`: Whether the data passes validation
- `errors`: List of validation errors
- `warnings`: List of validation warnings
- `completeness_score`: Data completeness score (0.0 to 1.0)

## Workflow Nodes

The agentic workflow consists of the following nodes:

1. **classify**: Document type classification
2. **extract**: Structure extraction based on document type
3. **reason**: Adaptive reasoning for ambiguities
4. **validate**: Schema validation
5. **handle_other**: Handle unsupported document types

## Error Handling

The API includes comprehensive error handling:

- Invalid API keys result in `ValueError` during initialization
- Processing errors are captured and returned in the result dictionary
- Individual workflow node failures are logged in `processing_steps`

## Performance Considerations

- Processing time varies based on image complexity (typically 5-15 seconds)
- Large images should be resized to improve processing speed
- Rate limits apply based on your OpenAI API plan

## Security Notes

⚠️ **Important**: This is a prototype. For production use:

- Implement proper HIPAA compliance
- Add encryption for data in transit and at rest
- Implement audit logging
- Use secure API endpoints
- Add authentication and authorization

## Supported Formats

**Input Formats:**
- JPEG images
- PNG images
- Base64 encoded images

**Document Types:**
- Laboratory reports
- Patient intake forms
- Prescription forms
- Discharge summaries

For PDF documents, convert to images using `pdf2image` before processing.
