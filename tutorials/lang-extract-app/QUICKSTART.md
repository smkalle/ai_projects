# Quick Start Guide - LangExtract Medical Research Assistant

Get up and running in 5 minutes! 🚀

## 1. Installation (2 minutes)

```bash
# Clone the repository
git clone https://github.com/yourusername/lang-extract-app.git
cd lang-extract-app

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## 2. Configuration (1 minute)

```bash
# Copy environment file
cp .env.example .env

# Add your Gemini API key to .env file
# LANGEXTRACT_API_KEY=your-gemini-api-key-here
```

Get your Gemini API key from: https://makersuite.google.com/app/apikey

## 3. Launch Application (30 seconds)

```bash
streamlit run app.py
```

Your browser will open automatically to `http://localhost:8501`

## 4. First Extraction (2 minutes)

### Step 1: Enter API Key
- Click "⚙️ API Configuration" in sidebar
- Paste your Gemini API key
- Click outside the text box to save

### Step 2: Upload Document
- Drag and drop a medical PDF or click "Browse files"
- Supported formats: PDF, TXT, DOCX, HTML

### Step 3: Select Template
Choose from the dropdown:
- **Clinical Trial Data** - For research studies
- **Case Report** - For patient cases
- **Drug Information** - For medication data
- **Research Findings** - For scientific papers

### Step 4: Extract
- Click "🚀 Start Extraction"
- Wait 10-30 seconds
- View results in the tabs below

## 5. Export Results (30 seconds)

1. Go to "💾 Export" tab
2. Select format (CSV, JSON, Excel)
3. Click "📥 Generate Export"
4. Download file

## 🎉 Success!

You've completed your first extraction! 

### Next Steps:
- Try batch processing multiple files
- Create a custom template
- Explore visualization options
- Read the [full documentation](README.md)

### Need Help?
- Check [Troubleshooting](README.md#troubleshooting)
- Visit [GitHub Issues](https://github.com/yourusername/lang-extract-app/issues)
- Join our [Discord Community](https://discord.gg/langextract)

---

**Pro Tip**: Save your frequently used templates by bookmarking the URL with parameters!