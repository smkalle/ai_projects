# 🚀 Vector Matchup Pro - Deployment Instructions

## Quick Setup

1. **Extract the package:**
   ```bash
   unzip vector_matchup_pro_*.zip
   cd vector_matchup_pro/
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment:**
   ```bash
   cp env.sample .env
   # Edit .env if needed
   ```

5. **Launch application:**
   ```bash
   streamlit run vector_matchup_app.py --server.port 8501
   ```

6. **Access in browser:**
   ```
   http://localhost:8501
   ```

## Features Ready to Use

✅ **Vector Database Comparison** - LanceDB vs Parquet+FAISS
✅ **9 Embedding Models** - Latest 2024 models included
✅ **Multilingual Support** - 100+ languages
✅ **Dynamic Model Switching** - No configuration file editing
✅ **Performance Benchmarking** - Speed, memory, quality metrics
✅ **Professional Reports** - JSON and Markdown exports

## Test the System

```bash
# Quick embedding model comparison
python run_embedding_comparison.py --mock

# Full demo
python demo_embedding_comparison.py

# Run tests
python -m pytest tests/ -v
```

## Troubleshooting

**PDF Support Issues:**
```bash
pip install "PyPDF2>=3.0.1" "pymupdf>=1.23.0"
```

**Memory Issues with Real Models:**
- Use mock embeddings for testing
- Try smaller models first
- Monitor system memory

**Port Already in Use:**
```bash
streamlit run vector_matchup_app.py --server.port 8502
```

Ready to deploy! 🎯
