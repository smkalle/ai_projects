# Project Structure Overview

This NGO Medical AI Assistant project is organized as follows:

## 📁 Directory Structure

```
medai-hackathon-project/
├── 📄 README.md                    # Main project documentation
├── 📄 LICENSE                      # MIT license
├── 📄 CONTRIBUTING.md               # Contribution guidelines
├── 📄 requirements.txt              # Full Python dependencies
├── 📄 requirements-gradio.txt       # Minimal demo dependencies
├── 📄 Dockerfile                   # Docker container configuration
├── 📄 docker-compose.yml           # Multi-container orchestration
├── 📄 .gitignore                   # Git ignore patterns
│
├── 📁 src/                         # Source code
│   ├── 📄 main.py                  # FastAPI application entry point
│   ├── 📄 gradio_demo.py           # Gradio demo interface
│   ├── 📁 models/                  # AI models and medical knowledge
│   ├── 📁 utils/                   # Utility functions
│   └── 📁 api/                     # API-specific modules
│
├── 📁 config/                      # Configuration files
│   ├── 📄 .env.example             # Environment variables template
│   └── 📄 model_config.yaml        # AI model configuration
│
├── 📁 tests/                       # Test suite
│   ├── 📄 test_main.py             # Main application tests
│   └── 📄 __init__.py              # Test package initialization
│
├── 📁 docs/                        # Documentation
│   └── 📄 QUICK_START.md           # Quick start guide for hackathons
│
├── 📁 scripts/                     # Setup and utility scripts
│   └── 📄 setup.py                 # Project setup script
│
├── 📁 frontend/                    # Frontend assets (for web interface)
│   ├── 📁 static/                  # Static files (CSS, JS, images)
│   └── 📁 templates/               # HTML templates
│
├── 📁 data/                        # Data directory (created during setup)
│   ├── 📁 sample/                  # Sample medical data
│   └── 📁 medical_images/          # Medical imaging files
│
├── 📁 notebooks/                   # Jupyter notebooks for analysis
├── 📁 logs/                        # Application logs
└── 📁 .github/                     # GitHub configuration
    └── 📁 workflows/               # CI/CD workflows
        └── 📄 ci.yml               # Continuous integration
```

## 🚀 Getting Started

Choose your setup method:

1. **Quick Demo** (5 minutes): `python src/gradio_demo.py`
2. **Full Development** (15 minutes): `python src/main.py` 
3. **Docker Production** (10 minutes): `docker-compose up --build`

See [docs/QUICK_START.md](docs/QUICK_START.md) for detailed instructions.

## 🔧 Key Files Explained

- **`src/main.py`**: FastAPI web application with medical analysis API
- **`src/gradio_demo.py`**: Interactive demo interface for rapid prototyping
- **`config/.env.example`**: Template for API keys and configuration
- **`requirements.txt`**: All Python dependencies for full functionality
- **`requirements-gradio.txt`**: Minimal dependencies for demo mode
- **`Dockerfile`**: Production container configuration
- **`docker-compose.yml`**: Complete application stack (app + Redis + Nginx)

## 🏥 Medical AI Components

- **Multimodal Analysis**: Combines image analysis with symptom processing
- **Chain-of-Thought Reasoning**: Step-by-step diagnostic reasoning
- **Confidence Scoring**: Uncertainty quantification for all assessments
- **Emergency Triage**: Rapid patient prioritization algorithms
- **Medical Chat**: Context-aware Q&A for healthcare workers
- **Ethics & Safety**: Comprehensive medical disclaimers and limitations

## 🎯 Hackathon Ready

This project is designed for medical AI hackathons with:

- ✅ Complete working application in under 30 minutes setup
- ✅ Professional-grade architecture and documentation
- ✅ Real medical use cases and sample data
- ✅ Docker deployment for demos
- ✅ Comprehensive testing and CI/CD
- ✅ Medical ethics and compliance framework
- ✅ Scalable cloud deployment options

## 📊 Technical Stack

- **Backend**: FastAPI, Python 3.9+, OpenAI GPT-4o, LLaVA-Med
- **Frontend**: HTML5, Tailwind CSS, JavaScript, Gradio
- **Database**: SQLite/PostgreSQL, Redis for caching
- **Deployment**: Docker, Docker Compose, Cloud-ready
- **Testing**: pytest, coverage reporting
- **CI/CD**: GitHub Actions, automated testing

## 🌟 Next Steps

1. **Setup**: Run `python scripts/setup.py` to initialize
2. **Configure**: Add API keys to `config/.env`
3. **Test**: Try sample medical cases in Gradio demo
4. **Deploy**: Use Docker Compose for full stack
5. **Customize**: Adapt for your specific hackathon theme
6. **Scale**: Deploy to cloud platforms for production

Happy hacking! 🚀🏥
