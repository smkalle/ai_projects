# 📱 Termux Quickstart

Ultra-quick setup guide for running Energy Document AI on Android.

## 🚀 30-Second Setup

```bash
# 1. Install packages
pkg update && pkg install python git curl

# 2. Clone & setup
git clone <repo> pypdfium && cd pypdfium
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# 3. Configure
cp .env.example .env
nano .env  # Add OpenAI API key

# 4. Start everything
./start_termux_services.sh
```

**Done!** Access at: http://localhost:8501

## 🛠️ Individual Components

### Start Qdrant Only
```bash
./start_qdrant_termux.sh
```

### Start UI Only (after Qdrant is running)
```bash
source venv/bin/activate
python app/main.py --mode ui
```

### Use Interactive Menu
```bash
./start.sh
# Choose option 5 (Start Qdrant), then option 1 (UI)
```

## 📱 Termux Tips

### Multiple Sessions
- **New**: Swipe left → "New session"
- **Switch**: Swipe left → tap session

### tmux (Better Terminal Management)
```bash
pkg install tmux
tmux
# Ctrl+b then " = horizontal split
# Ctrl+b then % = vertical split
# Ctrl+b then arrow = switch pane
```

### Background Services
```bash
# Start all in background
./start_termux_services.sh

# Monitor
tail -f logs/qdrant.log
tail -f logs/streamlit.log

# Stop all
./stop.sh
```

### Troubleshooting
```bash
# Kill all processes
pkill -f 'qdrant|streamlit|uvicorn'

# Check processes
ps aux | grep -E 'qdrant|streamlit'

# Check ports
netstat -tlnp | grep -E '6333|8501'

# Memory check
free -h
```

## ⚡ Quick Commands

| Task | Command |
|------|---------|
| Start everything | `./start_termux_services.sh` |
| Interactive menu | `./start.sh` |
| Stop everything | `./stop.sh` |
| Just Qdrant | `./start_qdrant_termux.sh` |
| Check logs | `tail -f logs/*.log` |
| Kill processes | `pkill -f qdrant` |

## 🎯 URLs

- **UI**: http://localhost:8501
- **Qdrant**: http://localhost:6333
- **Qdrant Dashboard**: http://localhost:6333/dashboard

That's it! Your AI document system is running on Android! 🚀📱