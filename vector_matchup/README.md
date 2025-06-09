# 🚀 Vector Matchup Pro

**Enterprise-grade vector database benchmarking platform with advanced embedding model comparison capabilities**

Vector Matchup Pro is a comprehensive tool for comparing vector database performance across different storage backends and embedding models. Built with Streamlit, it provides real-time benchmarking, detailed analytics, and professional reporting capabilities.

## ✨ Key Features

### 🏗️ **Vector Database Comparison**
- **LanceDB**: Modern, high-performance vector database
- **Parquet + FAISS**: Traditional but powerful combination
- **Real-time Performance Metrics**: Throughput, latency, memory usage
- **Interactive Visualizations**: Professional charts and graphs

### 🧠 **Advanced Embedding Model Support**
- **9 Pre-configured Models**: Latest 2024 state-of-the-art models
- **Dynamic Model Switching**: Change models without configuration files
- **Multilingual Support**: 100+ languages across various models
- **Performance Benchmarking**: Speed, memory, and quality metrics

### 📊 **Comprehensive Analytics**
- **Executive Dashboard**: High-level performance overview
- **Deep Dive Analysis**: Detailed performance breakdowns
- **Predictive Insights**: Scaling and performance predictions
- **Professional Reports**: JSON and Markdown export options

### 🌍 **Multilingual & Enterprise Ready**
- **100+ Languages**: Support across English, Chinese, Japanese, Korean, Arabic, Hindi, and more
- **Enterprise Models**: BGE-M3, Multilingual-E5 series, static models
- **Quality Metrics**: Embedding diversity, similarity analysis
- **Scalability Testing**: Performance at different document volumes

## 🛠️ Installation

### Prerequisites
- Python 3.8+
- 4GB+ RAM (8GB recommended for real embeddings)
- pip package manager

### Quick Setup
```bash
# Clone the repository
git clone <repository-url>
cd vector_matchup_pro

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment configuration
cp env.sample .env

# Launch the application
streamlit run vector_matchup_app.py --server.port 8501
```

## 🚗 Quick Start Guide

### 1. **Basic Usage**
```bash
# Start the application
streamlit run vector_matchup_app.py

# Access in browser
http://localhost:8501
```

### 2. **Upload Documents**
- Navigate to "🚗 Kick the Tyres"
- Upload PDF, TXT, DOC, or DOCX files
- Or paste text directly
- Or use sample data

### 3. **Configure Embedding Models**
- Use sidebar "🧠 Embedding Model" section
- Select from 9 pre-configured models
- Switch between mock (fast) and real embeddings
- Override per benchmark if needed

### 4. **Run Benchmarks**
- Click "🚀 Run Benchmark"
- Monitor real-time progress
- View detailed results and comparisons
- Download comprehensive reports

## 🧠 Embedding Models

### English-Focused Models
| Model | Dimensions | Size | Speed | Quality | Use Case |
|-------|------------|------|-------|---------|----------|
| **All-MiniLM-L6-v2** | 384 | 80MB | ⚡⚡⚡ | ⭐⭐⭐ | General purpose, fast |
| **All-MPNet-Base-v2** | 768 | 420MB | ⚡⚡ | ⭐⭐⭐⭐ | High quality English |

### Multilingual Models
| Model | Dimensions | Size | Languages | Use Case |
|-------|------------|------|-----------|----------|
| **Multilingual-E5-Small** | 384 | 470MB | 100+ | Efficient multilingual |
| **Multilingual-E5-Base** | 768 | 1.1GB | 100+ | Balanced multilingual |
| **Multilingual-E5-Large** | 1024 | 2.2GB | 100+ | High-quality multilingual |
| **BGE-M3** | 1024 | 2.2GB | 100+ | State-of-the-art 2024 |

### Ultra-Fast Static Models
| Model | Dimensions | Size | Speed | Use Case |
|-------|------------|------|-------|----------|
| **Static-Retrieval-MRL** | 1024 | 50MB | ⚡⚡⚡⚡ | 100x faster CPU inference |
| **Static-Similarity-MRL** | 1024 | 120MB | ⚡⚡⚡⚡ | Ultra-fast multilingual |

## 🔧 Configuration

### Environment Variables (.env)
```bash
# Default embedding model
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# Computation device
EMBEDDING_DEVICE=cpu  # or 'cuda' for GPU

# Vector database settings
LANCEDB_PATH=./data/lancedb
FAISS_INDEX_PATH=./data/faiss

# Chunk settings
DEFAULT_CHUNK_SIZE=500
DEFAULT_CHUNK_OVERLAP=50
```

### Model Configuration
All embedding models are pre-configured in `config.py` with:
- Model specifications (dimensions, size, languages)
- Performance characteristics (speed, quality ratings)
- Use case recommendations
- Validation and compatibility checks

## 📈 Advanced Features

### Embedding Model Comparison
```bash
# Quick mock comparison (fast)
python run_embedding_comparison.py --mock

# Real model comparison (comprehensive)
python run_embedding_comparison.py --real

# Multilingual focus testing
python run_embedding_comparison.py --multilingual

# Quick real model test
python run_embedding_comparison.py --quick --real

# Run demo suite
python demo_embedding_comparison.py
```

### Batch Testing
```bash
# Run all tests
python -m pytest tests/ -v

# Test embedding configurations
python -m pytest tests/test_embedding_config.py -v

# Test model comparisons
python -m pytest tests/test_embedding_comparison.py -v
```

### Report Generation
- **JSON Reports**: Machine-readable performance data
- **Markdown Reports**: Human-readable analysis
- **Performance Rankings**: Speed and efficiency comparisons
- **Quality Metrics**: Embedding diversity and similarity analysis
- **Recommendations**: Best model suggestions for use cases

## 🎯 Use Cases

### 1. **Model Selection**
- Compare embedding models for your specific domain
- Test multilingual capabilities
- Evaluate speed vs quality trade-offs
- Find the best model for your hardware constraints

### 2. **Performance Optimization**
- Benchmark vector database performance
- Identify bottlenecks in your pipeline
- Scale testing for production workloads
- Memory and throughput optimization

### 3. **Enterprise Deployment**
- Validate models for production use
- Generate compliance reports
- Test across different languages and domains
- Capacity planning and resource estimation

### 4. **Research & Development**
- Compare latest embedding models
- Evaluate new vector database technologies
- Benchmark custom datasets
- Academic research and publication

## 📊 Output Examples

### Performance Report
```
🏆 Performance Rankings

⚡ Speed Ranking (docs/second)
1. Multilingual-E5-Small: 36,095.6 docs/sec
2. All-MiniLM-L6-v2: 21,811.3 docs/sec
3. BGE-M3: 8,924.1 docs/sec

💾 Memory Efficiency Ranking
1. All-MiniLM-L6-v2: 80MB
2. Static-Retrieval-MRL: 50MB
3. Multilingual-E5-Small: 470MB

💡 Recommendations
- Fastest Model: Multilingual-E5-Small
- Most Memory Efficient: Static-Retrieval-MRL
- Best Balance: All-MiniLM-L6-v2
```

### Quality Metrics
```
🎯 Quality Metrics (Real Models)
- Embedding Diversity: 0.998
- Average Similarity: 0.002
- Standard Deviation: 0.997
- Average Norm: 19.537
```

## 🚀 Deployment

### Local Development
```bash
streamlit run vector_matchup_app.py --server.port 8501
```

### Production Deployment
```bash
# Install production dependencies
pip install -r requirements.txt

# Set environment variables
export EMBEDDING_DEVICE=cpu
export EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# Run with production settings
streamlit run vector_matchup_app.py --server.port 8080 --server.headless true
```

### Docker Deployment
```dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8501

CMD ["streamlit", "run", "vector_matchup_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

## 🧪 Testing

### Test Coverage
- **Unit Tests**: Individual component testing
- **Integration Tests**: End-to-end workflow testing
- **Performance Tests**: Benchmarking and load testing
- **Mock Tests**: Fast development testing

### Run Tests
```bash
# All tests
python -m pytest tests/ -v

# Specific test categories
python -m pytest tests/test_embedding_comparison.py -v
python -m pytest tests/test_backend_comparison.py -v

# With coverage
python -m pytest tests/ --cov=. --cov-report=html
```

## 📚 API Reference

### Core Classes
- **`VectorMatchupPro`**: Main application class
- **`EmbeddingModelComparator`**: Model comparison engine
- **`BackendComparator`**: Vector database comparison
- **`LanceDBBackend`**: LanceDB implementation
- **`ParquetFAISSBackend`**: Parquet + FAISS implementation

### Configuration Functions
- **`get_available_embedding_models()`**: List available models
- **`get_embedding_model_info(model)`**: Get model specifications
- **`validate_embedding_config()`**: Validate configuration
- **`create_embedding_model(model_name)`**: Create model instance

## 🤝 Contributing

### Development Setup
```bash
# Fork and clone the repository
git clone <your-fork-url>
cd vector_matchup_pro

# Create development environment
python -m venv venv
source venv/bin/activate

# Install development dependencies
pip install -r requirements.txt
pip install pytest pytest-cov black

# Run tests
python -m pytest tests/ -v

# Format code
black .
```

### Adding New Models
1. Add model configuration to `config.py`
2. Update model info database
3. Add validation tests
4. Update documentation

### Submitting Changes
1. Create feature branch
2. Add tests for new functionality
3. Update documentation
4. Submit pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Streamlit**: Web application framework
- **LanceDB**: Modern vector database
- **FAISS**: Facebook AI Similarity Search
- **Sentence Transformers**: Embedding model library
- **Plotly**: Interactive visualizations
- **HuggingFace**: Model hosting and APIs

## 📞 Support

### Documentation
- **GitHub Wiki**: Detailed documentation
- **API Reference**: Function and class documentation
- **Examples**: Sample implementations and use cases

### Community
- **Issues**: Bug reports and feature requests
- **Discussions**: Questions and community support
- **Contributing**: Development guidelines and contribution process

*Vector Matchup Pro - Making vector database decisions data-driven* 
