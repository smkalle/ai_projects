# GitHub Deployment Guide 🚀

## Overview
The `commit_github.sh` script safely deploys your Medical AI Assistant MVP to GitHub while automatically excluding sensitive files and directories.

## 🔒 **What Gets Excluded (Automatically)**

### **Sensitive Files & Directories:**
- `.venv/` - Virtual environment
- `.env` - Environment variables with API keys
- `mvp_medical.db` - Database with patient data
- `__pycache__/` - Python cache files
- `static/photos/*.jpg` - Uploaded medical photos
- `*.log` - Log files
- `.DS_Store` - macOS system files

### **What Gets Included:**
- All source code (`src/`)
- Templates (`templates/`)
- Requirements (`requirements.txt`)
- Configuration files (`src/config.py`)
- Documentation (`*.md`)
- Static assets (except photos)

## 🚀 **How to Use**

### **Step 1: Run the Script**
```bash
./commit_github.sh
```

### **Step 2: Follow the Prompts**
The script will:
1. ✅ Create/update `.gitignore` automatically
2. ✅ Show you what files will be committed
3. ✅ Ask for a commit message (or use default)
4. ✅ Ask for your GitHub repository URL (if needed)
5. ✅ Confirm before pushing to GitHub

### **Step 3: Example Run**
```bash
🚀 Medical AI Assistant MVP - GitHub Deployment
================================================
[INFO] Creating/updating .gitignore file...
[SUCCESS] .gitignore file created/updated
[INFO] Ensuring photos directory structure...
[INFO] Checking for sensitive files...
[WARNING] Found sensitive files that will be excluded:
  - .env
  - .venv/
  - mvp_medical.db
[INFO] Files to be committed:
  A  src/main.py
  A  src/agents.py
  A  templates/assess.html
  ...
Enter commit message (or press Enter for default): 
[INFO] Committing changes...
[SUCCESS] Changes committed successfully
Enter your GitHub repository URL: https://github.com/yourusername/medical-ai-assistant.git
[SUCCESS] Remote origin added
Push to GitHub? (y/N): y
[INFO] Pushing to GitHub...
[SUCCESS] Successfully pushed to GitHub!
```

## 📁 **Files Created Automatically**

### **1. `.gitignore`**
Comprehensive exclusion rules for:
- Python artifacts
- Virtual environments  
- Environment variables
- Database files
- User uploads
- IDE files
- OS files

### **2. `README.md`**
Professional documentation including:
- Feature overview
- Installation instructions
- API documentation
- Technology stack
- Deployment guide

### **3. `.env.example`**
Template for environment variables:
```bash
OPENAI_API_KEY=your_openai_api_key_here
ENVIRONMENT=development
DEBUG=true
# ... other settings
```

### **4. `static/photos/.gitkeep`**
Ensures photos directory exists in repo without committing actual photos.

## 🛡️ **Security Features**

### **Automatic Protection:**
- ❌ **API Keys**: Never committed (`.env` excluded)
- ❌ **Database**: Patient data stays local
- ❌ **Photos**: Medical images excluded
- ❌ **Virtual Environment**: Dependencies via `requirements.txt` only
- ❌ **Logs**: No sensitive log data

### **Safe Deployment:**
- ✅ **Source Code**: All application code included
- ✅ **Templates**: Web interface files
- ✅ **Configuration**: Non-sensitive settings
- ✅ **Documentation**: README and guides
- ✅ **Dependencies**: `requirements.txt` for reproducibility

## 🔧 **Manual Override (If Needed)**

### **Check What's Staged:**
```bash
git status
```

### **Remove Sensitive File (If Accidentally Added):**
```bash
git reset HEAD .env
git rm --cached .env
```

### **Force Exclude a File:**
Add to `.gitignore`:
```bash
echo "sensitive_file.txt" >> .gitignore
```

## 🎯 **Post-Deployment Setup**

### **1. Clone on New Machine:**
```bash
git clone https://github.com/yourusername/medical-ai-assistant.git
cd medical-ai-assistant
```

### **2. Set Up Environment:**
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your API keys
```

### **3. Run Application:**
```bash
python -m uvicorn src.main:app --reload
```

## 🚨 **Important Notes**

### **Before First Run:**
- ✅ Ensure you have a GitHub account
- ✅ Create a new repository on GitHub
- ✅ Have your repository URL ready

### **Environment Variables:**
- ⚠️ **Never commit `.env`** - Contains API keys
- ✅ **Use `.env.example`** - Template for others
- ✅ **Set up secrets** in production deployment

### **Database:**
- ⚠️ **Local database excluded** - Contains patient data
- ✅ **Schema included** - In source code
- ✅ **Migrations supported** - Database recreated on new deployments

## 🎉 **Success Indicators**

After running the script, you should see:
- ✅ Repository created/updated on GitHub
- ✅ All source code visible in GitHub
- ✅ No sensitive files in repository
- ✅ README.md displays properly
- ✅ Others can clone and run your project

## 🆘 **Troubleshooting**

### **"Permission denied" Error:**
```bash
chmod +x commit_github.sh
```

### **"Not a git repository" Error:**
Script will automatically initialize git repository.

### **"Remote already exists" Error:**
```bash
git remote remove origin
./commit_github.sh
```

### **Authentication Issues:**
- Set up GitHub personal access token
- Configure git credentials:
```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

---

## 🎯 **Ready to Deploy!**

Your Medical AI Assistant MVP is now ready for safe GitHub deployment. The script ensures:
- 🔒 **Security**: No sensitive data exposed
- 📚 **Documentation**: Professional README included  
- 🚀 **Reproducibility**: Others can clone and run
- 🛡️ **Best Practices**: Proper `.gitignore` and structure

**Run `./commit_github.sh` when ready to deploy!** 