# LangExtract Medical Research Assistant

A powerful Streamlit application that enables medical research students to extract structured information from medical literature using Google's LangExtract library.

![LangExtract Medical](https://via.placeholder.com/800x400/0066CC/FFFFFF?text=LangExtract+Medical+Research+Assistant)

## 🚀 Features

- **User-Friendly Interface**: Intuitive Streamlit web application designed for medical researchers
- **Pre-configured Medical Templates**: 
  - Clinical Trial Data extraction
  - Case Reports analysis
  - Drug Information parsing
  - Research Findings summarization
  - Patient Records processing
  - Literature Review extraction
- **Multiple File Formats**: Support for PDF, TXT, DOCX, and HTML documents
- **Batch Processing**: Process multiple documents simultaneously
- **Interactive Visualizations**: Charts, word clouds, and entity networks
- **Export Options**: CSV, JSON, Excel, LaTeX, and BibTeX formats
- **Source Citation Tracking**: Maintain references to original text
- **Error Handling**: Comprehensive error management and logging

## 📋 Prerequisites

- Python 3.8 or higher
- Gemini API key (for cloud processing)
- 4GB RAM minimum (8GB recommended)
- Internet connection (for API access)

## 🛠️ Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/lang-extract-app.git
cd lang-extract-app
```

2. **Create a virtual environment**
```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your Gemini API key
# LANGEXTRACT_API_KEY=your-api-key-here
```

## 🚀 Quick Start

1. **Run the application**
```bash
streamlit run app.py
```

2. **Open your browser**
Navigate to `http://localhost:8501`

3. **Configure API Key**
- Click on "API Configuration" in the sidebar
- Enter your Gemini API key
- The key will be saved for the session

4. **Upload and Process**
- Upload medical documents (PDF, TXT, DOCX, or HTML)
- Select a pre-configured template or create custom
- Click "Start Extraction"
- View and export results

## 📚 Usage Guide

### Selecting Templates

The application includes 6 pre-configured medical templates:

1. **Clinical Trial Data**: Extracts patient demographics, interventions, outcomes
2. **Case Report**: Analyzes patient history, symptoms, diagnosis, treatment
3. **Drug Information**: Parses drug names, dosages, side effects, interactions
4. **Research Findings**: Summarizes hypotheses, methods, results, conclusions
5. **Patient Records**: Processes chief complaints, diagnoses, medications
6. **Literature Review**: Extracts key findings, methodologies, citations

### Processing Documents

1. **Single Document**:
   - Upload one file
   - Select appropriate template
   - Configure advanced settings if needed
   - Start extraction

2. **Batch Processing**:
   - Upload multiple files (up to 10)
   - All files will use the same template
   - Progress tracked for each file
   - Results aggregated automatically

3. **URL Processing**:
   - Enter document URL directly
   - Supports direct links to PDFs or text files
   - Same template options available

### Viewing Results

Results are displayed in four tabs:

1. **Data Table**: Structured view of all extractions
2. **Visualizations**: Charts and graphs of extraction data
3. **Export**: Download options in various formats
4. **Details**: Detailed JSON view of each extraction

### Exporting Data

Supported export formats:

- **CSV**: Flat table format, Excel-compatible
- **JSON**: Nested structure with full details
- **Excel**: Multi-sheet workbook with formatting
- **LaTeX**: Publication-ready tables
- **BibTeX**: Bibliography entries (for literature reviews)

## 🔧 Advanced Configuration

### Processing Parameters

- **Parallel Workers** (1-30): Number of concurrent processing threads
- **Extraction Passes** (1-5): Multiple passes for better recall
- **Character Buffer** (100-5000): Size of text chunks for processing

### Custom Templates

Create custom extraction templates:

1. Click "Custom Template" in template selection
2. Define extraction fields
3. Provide example input/output pairs
4. Save template for reuse

## 🏥 Medical Research Use Cases

### Clinical Trial Analysis
- Extract patient demographics across multiple trials
- Compare intervention methods and outcomes
- Aggregate adverse event data
- Generate summary statistics

### Literature Review Automation
- Process hundreds of research papers
- Extract key findings and methodologies
- Build citation databases
- Identify research trends

### Drug Information Compilation
- Create drug interaction databases
- Summarize side effect profiles
- Track dosage recommendations
- Monitor contraindications

### Case Report Mining
- Analyze patient presentation patterns
- Track treatment outcomes
- Identify rare conditions
- Build case databases

## 🔒 Security & Privacy

- **Local Processing Option**: Keep sensitive data on-premise
- **Session-Based Storage**: No permanent data retention
- **Auto-Deletion**: Files removed after 24 hours
- **Encrypted API Keys**: Secure credential management
- **HIPAA Considerations**: De-identification tools available

## 🐛 Troubleshooting

### Common Issues

1. **API Key Error**
   - Verify key is correct
   - Check Gemini account status
   - Ensure Tier 2 quota for large documents

2. **File Upload Failed**
   - Check file size (<10MB)
   - Verify file format
   - Ensure file isn't corrupted

3. **Extraction Timeout**
   - Reduce parallel workers
   - Process smaller documents
   - Check internet connection

4. **Export Error**
   - Verify export directory permissions
   - Check available disk space
   - Try different export format

### Debug Mode

Enable debug mode for detailed error information:
```python
# In .env file
DEBUG=True
```

## 📊 Performance Tips

1. **Optimize for Speed**:
   - Increase parallel workers
   - Use larger character buffers
   - Process similar documents together

2. **Optimize for Accuracy**:
   - Increase extraction passes
   - Use smaller character buffers
   - Provide more template examples

3. **Reduce API Costs**:
   - Batch similar documents
   - Cache common extractions
   - Use local mode when possible

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
pytest tests/

# Format code
black src/ tests/

# Run linter
flake8 src/ tests/
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Google LangExtract team for the core library
- Streamlit for the amazing web framework
- Medical research community for feedback and use cases

## 📞 Support

- **Documentation**: [Full Docs](https://github.com/yourusername/lang-extract-app/wiki)
- **Issues**: [GitHub Issues](https://github.com/yourusername/lang-extract-app/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/lang-extract-app/discussions)
- **Email**: support@langextract-medical.com

## 🗺️ Roadmap

### Version 1.1 (Q2 2025)
- Multi-language support
- Real-time collaboration
- Enhanced visualizations
- Mobile responsive design

### Version 2.0 (Q4 2025)
- EMR system integration
- Voice input support
- AI-powered template suggestions
- Advanced analytics dashboard

---

Made with ❤️ for medical researchers by the LangExtract Medical team