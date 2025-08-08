#!/bin/bash

# Dolphin Medical Document Parser Setup Script
# Production-ready MVP setup with full pipeline integration

echo "🐬 Setting up Dolphin Medical Document Parser MVP..."

# Create necessary directories
echo "📁 Creating directory structure..."
mkdir -p models/dolphin
mkdir -p data
mkdir -p logs
mkdir -p input
mkdir -p output
mkdir -p temp
mkdir -p archive
mkdir -p exports

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Download Dolphin models (placeholder - actual implementation would download real models)
echo "🤖 Setting up Dolphin models..."
if [ ! -d "models/dolphin/config.json" ]; then
    echo "⚠️  Dolphin models not found. Creating placeholder configuration..."
    
    # Create mock model configuration
    cat > models/dolphin/config.json << EOL
{
    "model_type": "dolphin-vision-language",
    "version": "1.0.0",
    "architecture": "analyze-then-parse",
    "supported_documents": [
        "clinical_report",
        "lab_results",
        "prescription",
        "discharge_summary",
        "radiology_report",
        "pathology_report"
    ],
    "anchor_types": [
        "text",
        "table", 
        "list",
        "key_value",
        "medication",
        "diagnosis"
    ]
}
EOL

    echo "✅ Model configuration created"
    echo "⚠️  Note: This is a placeholder. In production, download actual Dolphin models:"
    echo "   huggingface-cli download ByteDance/Dolphin --local-dir ./models/dolphin"
fi

# Initialize SQLite database
echo "🗄️  Initializing database..."
python3 -c "
from database import DolphinDatabase
db = DolphinDatabase()
print('✅ Database initialized successfully')
"

# Set up logging configuration
echo "📝 Setting up logging..."
cat > logging_config.json << EOL
{
    "version": 1,
    "formatters": {
        "default": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default"
        },
        "file": {
            "class": "logging.FileHandler",
            "formatter": "default",
            "filename": "logs/dolphin.log"
        }
    },
    "loggers": {
        "": {
            "handlers": ["console", "file"],
            "level": "INFO"
        }
    }
}
EOL

# Create sample configuration
echo "⚙️  Creating sample configuration..."
python3 -c "
from dolphin_config import DolphinConfig
config = DolphinConfig()
config.save_json('dolphin_config.json')
print('✅ Configuration file created: dolphin_config.json')
"

# Test the setup
echo "🧪 Testing setup..."
python3 -c "
print('Testing imports...')
try:
    from dolphin_config import DolphinConfig
    from dolphin_model import DolphinModel
    from extraction_logger import ExtractionLogger
    from file_manager import FileManager
    from database import DolphinDatabase
    print('✅ All modules imported successfully')
except Exception as e:
    print(f'❌ Import error: {e}')
    exit(1)

print('Testing database connection...')
try:
    db = DolphinDatabase()
    print('✅ Database connection successful')
except Exception as e:
    print(f'❌ Database error: {e}')
    exit(1)
"

echo ""
echo "🎉 Setup complete!"
echo ""
echo "🚀 To run the application:"
echo "   streamlit run dolphin_app.py"
echo ""
echo "📚 Available components:"
echo "   • Dolphin Model (dolphin_model.py) - Analyze-then-parse pipeline"
echo "   • Configuration (dolphin_config.py) - Model and prompt configuration"  
echo "   • Extraction Logger (extraction_logger.py) - Detailed progress tracking"
echo "   • File Manager (file_manager.py) - Batch processing and file tracking"
echo "   • Database (database.py) - SQLite storage for results"
echo "   • Main App (dolphin_app.py) - Streamlit web interface"
echo ""
echo "📁 Directory structure:"
echo "   • models/dolphin/ - Model files"
echo "   • data/ - Database files"
echo "   • logs/ - Processing logs"
echo "   • input/ - Input documents"
echo "   • output/ - Extraction results"
echo "   • temp/ - Temporary processing files"
echo "   • archive/ - Processed document archive"
echo "   • exports/ - Data exports"
echo ""
echo "⚠️  Production notes:"
echo "   • Download actual Dolphin models for production use"
echo "   • Configure appropriate GPU settings for performance"
echo "   • Ensure HIPAA compliance for medical data"
echo "   • Set up proper access controls and audit logging"
echo ""