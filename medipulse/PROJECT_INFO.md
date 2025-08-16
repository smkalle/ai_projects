# MediPulse Project Structure

Generated on: Sat Aug 16 04:41:22 UTC 2025

## Project Overview

MediPulse is an agentic workflow for medical document extraction, built with:
- **LangGraph**: For agentic workflow orchestration
- **OpenAI GPT-4o**: For vision and language processing
- **Pydantic**: For data validation and schema management
- **Python-dotenv**: For environment configuration

## Directory Structure

```
medipulse/
├── .env.example
├── .github
│   └── workflows
│       └── ci.yml
├── .gitignore
├── CONTRIBUTING.md
├── LICENSE
├── Makefile
├── README.md
├── docs
│   └── api.md
├── examples
│   ├── __init__.py
│   ├── demo.py
│   └── pdf_converter.py
├── requirements.txt
├── setup.py
├── src
│   ├── __init__.py
│   └── medipulse.py
└── tests
    ├── __init__.py
    └── test_medipulse.py

```

## Key Files

### Core Application
- `src/medipulse.py` - Main application with agentic workflow
- `src/__init__.py` - Package initialization and exports

### Configuration
- `requirements.txt` - Python dependencies
- `.env.example` - Environment variable template
- `setup.py` - Package setup configuration

### Documentation
- `README.md` - Comprehensive project documentation
- `docs/api.md` - Detailed API documentation
- `CONTRIBUTING.md` - Contribution guidelines

### Examples & Testing
- `examples/demo.py` - Interactive demo application
- `examples/pdf_converter.py` - PDF to image conversion utility
- `tests/test_medipulse.py` - Unit tests

### Development Tools
- `Makefile` - Common development tasks
- `.gitignore` - Git ignore patterns
- `.github/workflows/ci.yml` - GitHub Actions CI pipeline

## Quick Start

1. **Setup Environment**
   ```bash
   pip install -r requirements.txt
   cp .env.example .env
   # Edit .env with your OPENAI_API_KEY
   ```

2. **Run Demo**
   ```bash
   python examples/demo.py
   ```

3. **Run Tests**
   ```bash
   make test
   ```

## Next Steps

1. Add your OpenAI API key to `.env`
2. Test with sample medical documents
3. Explore the examples and documentation
4. Contribute improvements to the project

## License

MIT License - see LICENSE file for details.
