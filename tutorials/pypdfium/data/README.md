# Data Directory Structure

This directory contains sample documents and processed data for the Energy Document AI system.

## Directory Structure

```
data/
├── README.md                    # This file
├── sample_pdfs/                 # Sample PDF documents for testing
│   ├── solar_panel_technical_specifications.pdf
│   ├── wind_farm_regulatory_compliance.pdf
│   ├── transmission_environmental_impact_report.pdf
│   └── substation_equipment_maintenance_manual.pdf
├── sample_documents/           # Original markdown samples
│   └── solar_installation_guide.md
└── processed/                  # Processed document chunks (auto-generated)
    └── (generated during processing)
```

## Sample PDFs

The system includes realistic sample PDF documents representing different energy sector document types:

### 1. Solar Panel Technical Specifications
- **File**: `solar_panel_technical_specifications.pdf`
- **Type**: Technical/Equipment
- **Content**: Detailed technical specs, electrical characteristics, mechanical specifications
- **Features**: Tables with numerical data, certification requirements
- **Use Case**: Testing OCR accuracy on technical tables and specifications

### 2. Wind Farm Regulatory Compliance
- **File**: `wind_farm_regulatory_compliance.pdf`
- **Type**: Regulatory/Compliance
- **Content**: FERC/NERC compliance report, environmental assessments
- **Features**: Regulatory tables, compliance status, environmental data
- **Use Case**: Testing regulatory document classification and query handling

### 3. Transmission Environmental Impact Report
- **File**: `transmission_environmental_impact_report.pdf`
- **Type**: Environmental/Impact Assessment
- **Content**: Environmental impact analysis, mitigation measures, monitoring programs
- **Features**: Impact assessment tables, monitoring procedures
- **Use Case**: Testing environmental document processing and impact analysis queries

### 4. Substation Equipment Maintenance Manual
- **File**: `substation_equipment_maintenance_manual.pdf`
- **Type**: Equipment/Maintenance
- **Content**: Safety procedures, maintenance schedules, troubleshooting guides
- **Features**: Maintenance tables, safety requirements, procedural information
- **Use Case**: Testing equipment manual processing and maintenance query handling

## Testing the System

### Quick Test with Sample PDFs

1. **Start the application**:
   ```bash
   ./start.sh
   ```

2. **Upload a sample PDF**:
   - Open http://localhost:8501
   - Use the file uploader in the sidebar
   - Select one of the sample PDFs
   - Choose appropriate document type

3. **Test queries**:
   ```
   Solar Technical Spec:
   - "What is the maximum power output?"
   - "What are the electrical characteristics?"
   - "What certifications does this module have?"
   
   Wind Regulatory:
   - "What NERC standards apply to this project?"
   - "What are the environmental compliance requirements?"
   - "How many turbines are in the project?"
   
   Environmental Report:
   - "What are the main environmental impacts?"
   - "What mitigation measures are required?"
   - "How long is the transmission line?"
   
   Equipment Manual:
   - "What safety equipment is required?"
   - "How often should circuit breakers be maintained?"
   - "What are the emergency procedures?"
   ```

## Generating New Sample PDFs

To generate fresh sample PDFs or create additional types:

```bash
# Generate all samples
python scripts/generate_sample_pdfs.py --all

# Generate specific type
python scripts/generate_sample_pdfs.py --type technical
python scripts/generate_sample_pdfs.py --type regulatory
python scripts/generate_sample_pdfs.py --type environmental
python scripts/generate_sample_pdfs.py --type equipment

# Custom output directory
python scripts/generate_sample_pdfs.py --all --output custom/path
```

## Data Processing Notes

- **Processed files** are stored in `processed/` after document upload
- **Vector embeddings** are stored in Qdrant database (not in filesystem)
- **Document metadata** includes processing timestamps and document types
- **Original PDFs** remain unchanged after processing

## File Size Considerations

- Sample PDFs are designed to be compact (~50-200KB each) for quick testing
- Real-world energy documents can be much larger (1-50MB)
- System supports PDFs up to 50MB (configurable via `MAX_FILE_SIZE_MB`)

## Adding Your Own Documents

1. Place PDF files in `sample_pdfs/` directory
2. Ensure files are under the size limit
3. Use descriptive filenames
4. Test upload through the web interface
5. Verify OCR quality and processing results

## Data Privacy

- Sample PDFs contain only synthetic/public information
- No sensitive or proprietary data is included
- All generated content is for testing purposes only
- Real documents should be handled according to your organization's data policies