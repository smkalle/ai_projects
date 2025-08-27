# Termux Setup Guide 📱

Complete guide for running Energy Document AI on Android using Termux.

## 🚀 Quick Termux Setup

### 1. Install Termux and Required Packages

```bash
# Update package lists
pkg update && pkg upgrade

# Install essential packages
pkg install python python-pip git curl wget build-essential libffi openssl

# Install additional dependencies
pkg install rust nodejs-lts binutils

# Optional: Install text editors
pkg install nano vim
```

### 2. Setup Storage Access (Optional)

```bash
# Allow Termux to access Android storage
termux-setup-storage
```

### 3. Clone and Setup Project

```bash
# Clone the repository
git clone <your-repo-url> pypdfium
cd pypdfium

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt
```

### 4. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env file (add your OpenAI API key)
nano .env
```

### 5. Start Qdrant (Termux Method)

```bash
# Use the Termux-specific Qdrant script
./start_qdrant_termux.sh
```

### 6. Run the Application

```bash
# In another Termux session or after Qdrant is running
./start.sh
# Choose option 1 (Streamlit UI)
```

## 🔧 Termux-Specific Commands

### Multiple Termux Sessions
- **New session**: Swipe from left edge, tap "New session"
- **Switch sessions**: Swipe from left edge, tap session
- **Split screen**: Use `tmux` for multiple terminals

### Install tmux for Multiple Terminals
```bash
pkg install tmux

# Start tmux
tmux

# Split horizontally: Ctrl+b, then "
# Split vertically: Ctrl+b, then %
# Switch panes: Ctrl+b, then arrow keys
```

### Background Processes
```bash
# Run Qdrant in background
nohup ./start_qdrant_termux.sh > qdrant.log 2>&1 &

# Run Streamlit in background  
nohup python app/main.py --mode ui > streamlit.log 2>&1 &

# Check background processes
jobs
ps aux | grep python
```

## 📱 Android-Specific Tips

### 1. Memory Management
```bash
# Check available memory
free -h

# Monitor resource usage
top
htop  # if installed: pkg install htop
```

### 2. Network Access
- Make sure Qdrant runs on `0.0.0.0:6333` (configured in script)
- Access from Android browser: `http://localhost:8501`
- If accessing from other devices: `http://[termux-ip]:8501`

### 3. Battery Optimization
- Disable battery optimization for Termux in Android settings
- Use "Acquire wakelock" in Termux notification

### 4. File Management
```bash
# Access Android storage
ls ~/storage/shared/

# Copy files to/from Android
cp ~/storage/shared/Documents/file.pdf ./data/
cp ./output/result.pdf ~/storage/shared/Downloads/
```

## 🐛 Common Termux Issues

### Issue: "Permission denied" for Qdrant binary
```bash
chmod +x ~/qdrant/qdrant
```

### Issue: Python packages fail to install
```bash
# Update pip
pip install --upgrade pip

# Install with no cache
pip install --no-cache-dir -r requirements.txt

# Install individually if needed
pip install streamlit fastapi openai
```

### Issue: Port already in use
```bash
# Kill processes using ports
pkill -f qdrant
pkill -f streamlit
pkill -f uvicorn

# Check what's using port 6333
netstat -tlnp | grep 6333
```

### Issue: Not enough storage space
```bash
# Check disk usage
df -h

# Clean package cache
pkg clean

# Remove unused packages
pkg autoremove
```

### Issue: Qdrant binary not found/wrong architecture
```bash
# Check your architecture
uname -m

# For ARM64 (most modern Android devices):
# The script will download: qdrant-aarch64-unknown-linux-gnu

# For older ARM devices:
# The script will download: qdrant-armv7-unknown-linux-gnueabihf
```

## 🚀 Optimized Termux Workflow

### Method 1: Three Sessions
1. **Session 1**: Run Qdrant
   ```bash
   ./start_qdrant_termux.sh
   ```

2. **Session 2**: Run Streamlit UI
   ```bash
   source venv/bin/activate
   python app/main.py --mode ui
   ```

3. **Session 3**: Development/monitoring
   ```bash
   # Monitor logs, edit files, etc.
   tail -f qdrant.log
   ```

### Method 2: tmux (Recommended)
```bash
# Start tmux
tmux

# Split into 3 panes
Ctrl+b, then "    # Split horizontally
Ctrl+b, then %    # Split vertically

# In pane 1: Start Qdrant
./start_qdrant_termux.sh

# In pane 2: Start Streamlit
source venv/bin/activate
python app/main.py --mode ui

# In pane 3: Monitor/develop
tail -f qdrant.log
```

### Method 3: Background Services
```bash
# Start all services in background
./start_termux_services.sh
```

## 📊 Performance Tips

### 1. Memory Optimization
```bash
# Set Python memory limits
export PYTHONHASHSEED=0
export PYTHONUNBUFFERED=1

# Limit Qdrant memory usage (already configured in script)
```

### 2. CPU Optimization
```bash
# Use fewer CPU cores for intensive operations
export OMP_NUM_THREADS=2
export OPENBLAS_NUM_THREADS=2
```

### 3. Storage Optimization
```bash
# Use symbolic links for large data
ln -s ~/storage/shared/Documents/pdfs ./data/pdfs

# Compress old data
tar -czf old_data.tar.gz old_data/
rm -rf old_data/
```

## 📱 Access URLs

When running on Termux:
- **Streamlit UI**: `http://localhost:8501`
- **Qdrant API**: `http://localhost:6333`
- **Qdrant Dashboard**: `http://localhost:6333/dashboard`
- **FastAPI Docs**: `http://localhost:8000/docs`

## 🔄 Starting/Stopping Services

### Start Everything
```bash
# Option 1: Use the enhanced start script
./start.sh
# Choose option 5 to start Qdrant, then choose option 1 for UI

# Option 2: Manual start
./start_qdrant_termux.sh &  # In background
source venv/bin/activate
python app/main.py --mode ui
```

### Stop Everything
```bash
# Use the stop script
./stop.sh

# Or manually
pkill -f qdrant
pkill -f streamlit
pkill -f uvicorn
```

This setup allows you to run the full Energy Document AI system natively on Android! 🎉