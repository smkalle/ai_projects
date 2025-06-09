"""
Configuration settings for the Custom RAG System
"""
import os
from typing import Dict, Any, Optional, List
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Model Configuration with environment variable support
EMBEDDING_MODEL = os.getenv('EMBEDDING_MODEL', 'sentence-transformers/all-MiniLM-L6-v2')
EMBEDDING_DEVICE = os.getenv('EMBEDDING_DEVICE', 'cpu')  # cpu, cuda, mps
EMBEDDING_BATCH_SIZE = int(os.getenv('EMBEDDING_BATCH_SIZE', '32'))
EMBEDDING_MAX_LENGTH = int(os.getenv('EMBEDDING_MAX_LENGTH', '512'))
EMBEDDING_NORMALIZE = os.getenv('EMBEDDING_NORMALIZE', 'true').lower() == 'true'

# Model cache configuration
MODEL_CACHE_DIR = os.getenv('MODEL_CACHE_DIR', './models')

RERANK_MODEL = 'cross-encoder/ms-marco-MiniLM-L-6-v2'
LLM_MODEL = 'gpt-4o-mini'

# Processing Parameters
CHUNK_SIZE = 512  # characters
CHUNK_OVERLAP = 50  # characters
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB

# Retrieval Parameters
TOP_K_INITIAL = 20
TOP_K_RERANK = 10
TOP_K_FINAL = 5

# Performance Settings
BATCH_SIZE = 32
MAX_CONCURRENT_REQUESTS = 10

# Storage Configuration
DATA_DIR = "./data"
LANCEDB_DIR = os.path.join(DATA_DIR, "lancedb")
FAISS_INDEX_PATH = os.path.join(DATA_DIR, "faiss_index.bin")
PARQUET_PATH = os.path.join(DATA_DIR, "documents.parquet")

# Web Interface Settings
STREAMLIT_CONFIG = {
    "page_title": "Custom RAG System",
    "page_icon": "🤖",
    "layout": "wide",
    "initial_sidebar_state": "expanded"
}

# OpenAI Configuration
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
if not OPENAI_API_KEY:
    print("Warning: OPENAI_API_KEY environment variable not set. LLM synthesis will not work.")

# Logging Configuration
LOG_LEVEL = "INFO"
LOG_FORMAT = "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"

# Backend Configuration
BACKEND_CONFIGS: Dict[str, Dict[str, Any]] = {
    "lancedb": {
        "name": "LanceDB",
        "description": "Modern single-file vector database with atomic consistency",
        "pros": [
            "Atomic data consistency",
            "Simple scaling model",
            "Memory-mapped I/O",
            "Built-in version control"
        ],
        "cons": [
            "Single-node bottleneck",
            "Limited horizontal scaling"
        ],
        "best_for": [
            "Single-node deployments",
            "Strong consistency requirements",
            "Rapid prototyping"
        ]
    },
    "parquet_faiss": {
        "name": "Parquet + FAISS",
        "description": "Distributed multi-file approach with separate vector and metadata storage",
        "pros": [
            "Horizontal scaling",
            "Separate optimization",
            "Fine-grained control",
            "Industry standards"
        ],
        "cons": [
            "Data consistency challenges",
            "Complex architecture",
            "Network latency issues"
        ],
        "best_for": [
            "Large-scale deployments",
            "High-throughput systems",
            "Complex metadata filtering"
        ]
    }
}

# File Type Support
SUPPORTED_FILE_TYPES = {
    'txt': 'Text files',
    'pdf': 'PDF documents (future)',
    'docx': 'Word documents (future)',
    'md': 'Markdown files'
}

# Error Messages
ERROR_MESSAGES = {
    "file_too_large": f"File size exceeds maximum limit of {MAX_FILE_SIZE // (1024*1024)}MB",
    "unsupported_file": f"Unsupported file type. Supported types: {', '.join(SUPPORTED_FILE_TYPES.keys())}",
    "no_content": "File appears to be empty or unreadable",
    "index_not_built": "Index not built. Please upload and process a document first.",
    "api_key_missing": "OpenAI API key not configured. Please set OPENAI_API_KEY environment variable.",
    "model_load_error": "Error loading models. Please check your internet connection and try again."
}

# Success Messages
SUCCESS_MESSAGES = {
    "file_uploaded": "File uploaded successfully",
    "index_built": "Index built successfully",
    "query_processed": "Query processed successfully"
}

# Embedding model information database
EMBEDDING_MODEL_INFO = {
    # English-focused models
    'sentence-transformers/all-MiniLM-L6-v2': {
        'name': 'All-MiniLM-L6-v2',
        'dimensions': 384,
        'size_mb': 80,
        'languages': ['English'],
        'speed': 'Very Fast',
        'quality': 'Good',
        'use_case': 'Development/Testing'
    },
    'sentence-transformers/all-mpnet-base-v2': {
        'name': 'All-MPNet-Base-v2',
        'dimensions': 768,
        'size_mb': 420,
        'languages': ['English'],
        'speed': 'Fast',
        'quality': 'High',
        'use_case': 'English Production'
    },
    
    # Multilingual models
    'intfloat/multilingual-e5-small': {
        'name': 'Multilingual-E5-Small',
        'dimensions': 384,
        'size_mb': 470,
        'languages': ['100+ languages'],
        'speed': 'Medium',
        'quality': 'Very Good',
        'use_case': 'Resource Constrained'
    },
    'intfloat/multilingual-e5-base': {
        'name': 'Multilingual-E5-Base',
        'dimensions': 768,
        'size_mb': 1100,
        'languages': ['100+ languages'],
        'speed': 'Medium',
        'quality': 'Better',
        'use_case': 'Balanced Production'
    },
    'intfloat/multilingual-e5-large': {
        'name': 'Multilingual-E5-Large',
        'dimensions': 1024,
        'size_mb': 2200,
        'languages': ['100+ languages'],
        'speed': 'Medium',
        'quality': 'Best',
        'use_case': 'Multilingual Production'
    },
    'intfloat/multilingual-e5-large-instruct': {
        'name': 'Multilingual-E5-Large-Instruct',
        'dimensions': 1024,
        'size_mb': 2200,
        'languages': ['100+ languages'],
        'speed': 'Medium',
        'quality': 'Best',
        'use_case': 'Instruction-tuned'
    },
    
    # BGE models
    'BAAI/bge-m3': {
        'name': 'BGE-M3',
        'dimensions': 1024,
        'size_mb': 2200,
        'languages': ['100+ languages'],
        'speed': 'Medium',
        'quality': 'Best',
        'use_case': 'Dense+Sparse Retrieval'
    },
    
    # Static models (ultra-fast)
    'sentence-transformers/static-retrieval-mrl-en-v1': {
        'name': 'Static-Retrieval-MRL-EN',
        'dimensions': 1024,
        'size_mb': 50,
        'languages': ['English'],
        'speed': 'Ultra Fast',
        'quality': 'Good',
        'use_case': 'Edge/Mobile Deployment'
    },
    'sentence-transformers/static-similarity-mrl-multilingual-v1': {
        'name': 'Static-Similarity-MRL-Multilingual',
        'dimensions': 1024,
        'size_mb': 120,
        'languages': ['50+ languages'],
        'speed': 'Ultra Fast',
        'quality': 'Good',
        'use_case': 'Edge/Mobile Deployment'
    }
}

def get_embedding_model_info(model_name: str) -> Dict[str, Any]:
    """Get information about the embedding model"""
    return EMBEDDING_MODEL_INFO.get(model_name, {
        'name': model_name.split('/')[-1],
        'dimensions': 'Unknown',
        'size_mb': 'Unknown',
        'languages': ['Unknown'],
        'speed': 'Unknown',
        'quality': 'Unknown',
        'use_case': 'Custom Model'
    })

def get_available_embedding_models() -> List[str]:
    """Get list of available pre-configured embedding models"""
    return list(EMBEDDING_MODEL_INFO.keys())

def validate_embedding_config() -> Dict[str, Any]:
    """Validate embedding configuration and return status"""
    issues = []
    warnings = []
    
    # Check if model is known
    model_info = get_embedding_model_info(EMBEDDING_MODEL)
    if model_info['use_case'] == 'Custom Model':
        warnings.append(f"Unknown model: {EMBEDDING_MODEL}")
    
    # Check device compatibility
    if EMBEDDING_DEVICE not in ['cpu', 'cuda', 'mps']:
        issues.append(f"Invalid device: {EMBEDDING_DEVICE}")
    
    # Check batch size
    if EMBEDDING_BATCH_SIZE <= 0:
        issues.append(f"Invalid batch size: {EMBEDDING_BATCH_SIZE}")
    
    # Check max length
    if EMBEDDING_MAX_LENGTH <= 0:
        issues.append(f"Invalid max length: {EMBEDDING_MAX_LENGTH}")
    
    return {
        'valid': len(issues) == 0,
        'issues': issues,
        'warnings': warnings,
        'model_info': model_info
    }

def ensure_data_dir():
    """Ensure data directory exists"""
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(LANCEDB_DIR, exist_ok=True)
    os.makedirs(MODEL_CACHE_DIR, exist_ok=True) 