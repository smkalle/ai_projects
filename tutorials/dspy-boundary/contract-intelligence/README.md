# Contract Intelligence Platform

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/streamlit-1.28+-red.svg)](https://streamlit.io/)
[![DSPy](https://img.shields.io/badge/DSPy-2.4+-green.svg)](https://github.com/stanfordnlp/dspy)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🎯 Overview

Professional AI-powered contract intelligence platform built with Streamlit and DSPy. Features comprehensive legal document analysis, risk assessment, compliance checking, and executive dashboards with Silicon Valley-grade UI/UX.

![Platform Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen)

## ✨ Features

### 🤖 AI-Powered Analysis
- **Contract Parsing** - Multi-format document processing (PDF, DOCX, TXT)
- **Clause Extraction** - AI + pattern-based identification with risk scoring
- **Risk Assessment** - Comprehensive analysis with mitigation recommendations
- **Obligation Tracking** - Party commitments with deadline management
- **Key Terms Extraction** - Automated extraction of parties, financials, dates

### ⚖️ Compliance & Legal
- **Multi-Regulation Support** - GDPR, SOX, HIPAA, PCI DSS, CCPA
- **Automated Compliance Checking** - Real-time regulatory validation
- **Legal Review Insights** - Professional analysis and recommendations
- **Contract Comparison** - Side-by-side analysis and diff visualization

### 📊 Executive Dashboard
- **Professional UI** - Silicon Valley design standards
- **Interactive Analytics** - Plotly-powered data visualizations
- **Real-time Metrics** - KPI tracking and trend analysis
- **Comprehensive Reports** - Executive summaries and detailed exports

## 📋 Requirements

- Python 3.11+
- OpenAI API key (for AI features)
- 2GB+ RAM recommended

## 🛠️ Installation

1. Clone the repository:
```bash
git clone https://github.com/your-org/contract-intelligence.git
cd contract-intelligence
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

## 🏃 Running the Application

### Production Application
```bash
# Start the professional application
streamlit run professional_app.py
```

### Development Demo
```bash
# Start the development demo
streamlit run demo_app.py
```

The application will be available at http://localhost:8501

### Environment Configuration

Create `.env` file with:
```bash
# Required for AI features
OPENAI_API_KEY=your_openai_api_key_here

# Optional configurations
APP_NAME="Contract Intelligence Platform"
DEBUG=false
LOG_LEVEL=INFO
MAX_FILE_SIZE_MB=50
```

## 📁 Project Structure

```
contract-intelligence/
├── app/                  # Streamlit application
│   ├── main.py          # Main entry point
│   ├── pages/           # Application pages
│   └── components/      # Reusable UI components
├── core/                # Core business logic
│   ├── modules/         # DSPy modules
│   └── signatures/      # DSPy signatures
├── services/            # Service layer
├── models/              # Data models
├── config/              # Configuration
└── tests/               # Test suite
```

## 🔧 Development

For development setup:
```bash
pip install -r requirements-dev.txt
pre-commit install
```

Run tests:
```bash
pytest
```

## 📄 License

MIT License - see LICENSE file for details.

## 🤝 Contributing

Please read CONTRIBUTING.md for details on our code of conduct and the process for submitting pull requests.

## 📧 Support

For support, email support@contractintelligence.com or open an issue in the GitHub repository.