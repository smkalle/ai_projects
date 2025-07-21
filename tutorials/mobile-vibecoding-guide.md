# Mobile Vibecoding with Alpine & tmux: The Ultimate AI Engineer's Guide

> Transform your Android device into a powerful AI development environment using Alpine Linux in Termux with Claude Code, Gemini CLI, and tmux for seamless mobile coding sessions.

## Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Initial Termux Setup](#initial-termux-setup)
- [Alpine Linux Setup](#alpine-linux-setup)
- [Storage Configuration](#storage-configuration)
- [tmux Configuration](#tmux-configuration)
- [Node.js & Package Manager Setup](#nodejs--package-manager-setup)
- [Claude CLI Installation & Setup](#claude-cli-installation--setup)
- [Gemini CLI Installation & Setup](#gemini-cli-installation--setup)
- [Essential Scripts](#essential-scripts)
- [Vibecoding Workflow](#vibecoding-workflow)
- [Mobile-Optimized Configurations](#mobile-optimized-configurations)
- [Troubleshooting](#troubleshooting)
- [Pro Tips](#pro-tips)

## Overview

**Vibecoding** is the art of coding with AI assistance in a flow state. This guide sets up the ultimate mobile development environment using:

- **Termux**: Android terminal emulator and Linux environment
- **Alpine Linux**: Lightweight Linux distribution via proot-distro
- **tmux**: Terminal multiplexer for session management
- **Claude Code**: Anthropic's AI coding assistant
- **Gemini CLI**: Google's AI assistant
- **Mobile-optimized workflows** for coding on the go

## Prerequisites

### Hardware Requirements
- Android device (Android 7.0+)
- Minimum 4GB RAM (8GB+ recommended)
- 8GB+ free storage
- External keyboard (highly recommended)
- Power bank for extended sessions

### Software Requirements
- [Termux](https://f-droid.org/packages/com.termux/) (install from F-Droid, not Play Store)
- [Termux:API](https://f-droid.org/packages/com.termux.api/) (optional but recommended)
- [Termux:Styling](https://f-droid.org/packages/com.termux.styling/) (optional)

## Initial Termux Setup

### 1. Install Termux
```bash
# Download from F-Droid (recommended) or GitHub releases
# DO NOT install from Google Play Store (outdated version)
```

### 2. First Launch Setup
```bash
# Update package lists
pkg update && pkg upgrade -y

# Install essential packages
pkg install -y \
    git \
    curl \
    wget \
    vim \
    nano \
    openssh \
    rsync \
    htop \
    tree \
    which \
    man \
    termux-api \
    proot-distro
```

### 3. Configure Git (Essential for AI coding)
```bash
# Set up git credentials
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# Generate SSH key for GitHub
ssh-keygen -t ed25519 -C "your.email@example.com"

# Display public key to add to GitHub
cat ~/.ssh/id_ed25519.pub
```

## Alpine Linux Setup

### 1. Install Alpine Linux Distribution
```bash
# Install Alpine Linux using proot-distro
proot-distro install alpine

# List available distributions (verify installation)
proot-distro list

# Login to Alpine Linux
proot-distro login alpine
```

### 2. Alpine Linux Initial Setup
```bash
# Inside Alpine Linux environment
# Update package index
apk update

# Install essential packages
apk add \
    bash \
    curl \
    wget \
    git \
    vim \
    nano \
    openssh \
    tmux \
    htop \
    tree \
    nodejs \
    npm \
    python3 \
    py3-pip \
    build-base \
    linux-headers

# Set bash as default shell
chsh -s /bin/bash

# Create user directory structure
mkdir -p ~/dev/{projects,scripts,configs}
```

### 3. Configure Alpine for Development
```bash
# Add community repository for more packages
echo "http://dl-cdn.alpinelinux.org/alpine/edge/community" >> /etc/apk/repositories
apk update

# Install additional development tools
apk add \
    gcc \
    g++ \
    make \
    cmake \
    docker \
    docker-compose

# Setup Git in Alpine
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# Copy SSH keys from Termux to Alpine (if needed)
# Run this from Termux, not Alpine:
# cp ~/.ssh/id_ed25519* /data/data/com.termux/files/usr/var/lib/proot-distro/installed-rootfs/alpine/home/
```

### 4. Alpine Login Script
Create a convenient login script in Termux `~/alpine-login.sh`:

```bash
#!/bin/bash
# Alpine Linux login script for vibecoding

echo "🏔️ Entering Alpine Linux environment..."
echo "🎯 Ready for vibecoding with AI!"

# Login to Alpine with proper environment
proot-distro login alpine --bind /sdcard:/mnt/sdcard --bind /storage:/mnt/storage
```

Make it executable:
```bash
chmod +x ~/alpine-login.sh
echo 'alias alpine="~/alpine-login.sh"' >> ~/.bashrc
```

### 5. Shared Storage Setup Between Termux and Alpine
```bash
# From within Alpine Linux
# Create symlinks to access Android storage
ln -sf /mnt/sdcard ~/android-storage
ln -sf /mnt/storage ~/termux-storage

# Create shared development directory
mkdir -p /mnt/sdcard/alpine-dev
ln -sf /mnt/sdcard/alpine-dev ~/shared-dev
```

## Storage Configuration

### 1. Enable Shared Storage Access (Termux)
```bash
# Request storage permissions in Termux
termux-setup-storage

# This creates symlinks in ~/storage/
# ~/storage/shared -> Internal storage
# ~/storage/external-1 -> SD card (if available)
```

### 2. Create Development Directory Structure (Alpine)
```bash
# Inside Alpine Linux
# Create organized workspace in shared storage
mkdir -p /mnt/sdcard/alpine-dev/{projects,scripts,configs,ai-sessions}
mkdir -p ~/dev
ln -sf /mnt/sdcard/alpine-dev ~/dev

# Create quick access aliases for Alpine
echo 'alias dev="cd ~/dev"' >> ~/.bashrc
echo 'alias projects="cd ~/dev/projects"' >> ~/.bashrc
echo 'alias scripts="cd ~/dev/scripts"' >> ~/.bashrc

# Also create Termux aliases for accessing Alpine projects
# Run this in Termux:
echo 'alias alpine-dev="cd /storage/emulated/0/alpine-dev"' >> ~/.bashrc
```

### 3. Storage Management Script (Alpine)
Create `~/dev/scripts/storage-check.sh` in Alpine:

```bash
#!/bin/bash
# Storage monitoring script for mobile development

echo "=== Alpine Storage Status ==="
df -h $HOME
echo ""

echo "=== Shared Storage ==="
df -h /mnt/sdcard 2>/dev/null || echo "Shared storage not accessible"
echo ""

echo "=== Development Directory Sizes ==="
du -sh ~/dev/* 2>/dev/null
echo ""

echo "=== Package Cache Size ==="
du -sh /var/cache/apk/* 2>/dev/null
echo ""

echo "=== Cleanup Suggestions ==="
if [ $(du -s /var/cache/apk/* 2>/dev/null | cut -f1) -gt 100000 ]; then
    echo "📦 Run 'apk cache clean' to free up package cache space"
fi

if [ $(du -s ~/.npm/_cacache 2>/dev/null | cut -f1) -gt 50000 ]; then
    echo "📦 Run 'npm cache clean --force' to free up npm cache"
fi
```

Make it executable:
```bash
chmod +x ~/dev/scripts/storage-check.sh
echo 'alias storage="~/dev/scripts/storage-check.sh"' >> ~/.bashrc
```

## tmux Configuration

### 1. Install tmux (Already installed in Alpine setup)
```bash
# tmux is already installed in Alpine Linux from previous steps
# Verify installation
tmux -V
```

### 2. Mobile-Optimized tmux Configuration
Create `~/.tmux.conf`:

```bash
# Mobile-optimized tmux configuration for vibecoding

# Enable mouse support (essential for mobile)
set -g mouse on

# Start window numbering at 1
set -g base-index 1
setw -g pane-base-index 1

# Renumber windows when a window is closed
set -g renumber-windows on

# Increase scrollback buffer
set -g history-limit 10000

# Mobile-friendly prefix (easier on virtual keyboards)
unbind C-b
set -g prefix C-a
bind C-a send-prefix

# Quick pane switching (mobile-friendly)
bind h select-pane -L
bind j select-pane -D
bind k select-pane -U
bind l select-pane -R

# Split panes with more intuitive bindings
bind | split-window -h -c "#{pane_current_path}"
bind - split-window -v -c "#{pane_current_path}"

# Resize panes (mobile-friendly)
bind -r H resize-pane -L 5
bind -r J resize-pane -D 5
bind -r K resize-pane -U 5
bind -r L resize-pane -R 5

# Quick session management
bind C-c new-session
bind C-f choose-tree -Zs

# Copy mode improvements for mobile
setw -g mode-keys vi
bind v copy-mode
bind p paste-buffer

# Mobile status bar (compact but informative)
set -g status-position bottom
set -g status-bg '#2E3440'
set -g status-fg '#D8DEE9'
set -g status-left-length 20
set -g status-right-length 50

set -g status-left '#[bg=#5E81AC,fg=#2E3440,bold] #S #[bg=#2E3440] '
set -g status-right '#[fg=#81A1C1]%H:%M #[fg=#A3BE8C]%d-%b '

# Window status
setw -g window-status-format ' #I:#W '
setw -g window-status-current-format '#[bg=#81A1C1,fg=#2E3440,bold] #I:#W '

# Pane borders (subtle for small screens)
set -g pane-border-style 'fg=#3B4252'
set -g pane-active-border-style 'fg=#81A1C1'

# Enable true color support
set -g default-terminal "screen-256color"
set -ga terminal-overrides ",xterm-256color:Tc"

# Mobile-specific optimizations
set -g display-time 2000
set -g display-panes-time 2000
set -s escape-time 0

# Session persistence
set -g @plugin 'tmux-plugins/tmux-resurrect'
set -g @plugin 'tmux-plugins/tmux-continuum'
set -g @continuum-restore 'on'
set -g @continuum-save-interval '5'

# Initialize TMUX plugin manager (install manually on mobile)
run '~/.tmux/plugins/tpm/tpm'
```

### 3. Install tmux Plugin Manager
```bash
git clone https://github.com/tmux-plugins/tpm ~/.tmux/plugins/tpm
```

### 4. Essential tmux Scripts

Create `~/dev/scripts/tmux-ai-session.sh` in Alpine:
```bash
#!/bin/bash
# AI-focused tmux session setup for vibecoding

SESSION_NAME="ai-coding"

# Check if session exists
tmux has-session -t $SESSION_NAME 2>/dev/null

if [ $? != 0 ]; then
    # Create new session
    tmux new-session -d -s $SESSION_NAME -n "claude" -c "~/dev/projects"
    
    # Window 1: Claude Code
    tmux send-keys -t $SESSION_NAME:claude "clear && echo 'Claude Code Ready - Happy Vibecoding! 🚀'" C-m
    
    # Window 2: Gemini CLI
    tmux new-window -t $SESSION_NAME -n "gemini" -c "~/dev/projects"
    tmux send-keys -t $SESSION_NAME:gemini "clear && echo 'Gemini CLI Ready 🤖'" C-m
    
    # Window 3: Development
    tmux new-window -t $SESSION_NAME -n "dev" -c "~/dev/projects"
    tmux split-window -t $SESSION_NAME:dev -h -c "~/dev/projects"
    tmux send-keys -t $SESSION_NAME:dev.0 "clear && echo 'Main development pane'" C-m
    tmux send-keys -t $SESSION_NAME:dev.1 "clear && htop" C-m
    
    # Window 4: Files & Scripts
    tmux new-window -t $SESSION_NAME -n "files" -c "~/dev"
    tmux send-keys -t $SESSION_NAME:files "clear && tree -L 2" C-m
    
    # Select Claude window by default
    tmux select-window -t $SESSION_NAME:claude
fi

# Attach to session
tmux attach-session -t $SESSION_NAME
```

Make it executable:
```bash
chmod +x ~/dev/scripts/tmux-ai-session.sh
echo 'alias ai-session="~/dev/scripts/tmux-ai-session.sh"' >> ~/.bashrc
```

## Node.js & Package Manager Setup

### 1. Verify Node.js Installation (Already installed in Alpine)
```bash
# Node.js and npm are already installed in Alpine Linux
# Verify installation
node --version
npm --version
```

### 2. Configure npm for Global Packages
```bash
# Create directory for global packages
mkdir -p ~/.npm-global

# Configure npm
npm config set prefix '~/.npm-global'

# Add to PATH
echo 'export PATH=~/.npm-global/bin:$PATH' >> ~/.bashrc
source ~/.bashrc
```

### 3. Essential Development Packages
```bash
# Install essential global packages
npm install -g \
    typescript \
    ts-node \
    nodemon \
    pm2 \
    http-server \
    live-server \
    json-server \
    create-react-app \
    @vue/cli \
    @angular/cli
```

## Claude CLI Installation & Setup

### 1. Install Claude Code
```bash
# Install Claude Code CLI
npm install -g @anthropic-ai/claude-code

# Verify installation
claude --version
claude doctor
```

### 2. Authentication Setup
```bash
# Start authentication process
claude auth

# This will:
# 1. Open a browser or provide a URL
# 2. Ask you to log into your Anthropic account
# 3. Authorize the CLI application
# 4. Return an authentication token
```

### 3. API Key Method (Alternative)
If OAuth doesn't work on mobile:

```bash
# Set up API key manually
export ANTHROPIC_API_KEY="your-api-key-here"
echo 'export ANTHROPIC_API_KEY="your-api-key-here"' >> ~/.bashrc

# Test the connection
claude auth test
```

### 4. Claude Configuration
Create `~/.claude/config.json`:
```json
{
  "model": "claude-3-sonnet-20240229",
  "max_tokens": 4096,
  "temperature": 0.1,
  "mobile_optimized": true,
  "auto_save": true,
  "session_timeout": 3600
}
```

### 5. Simple Claude Example
Create `~/dev/projects/claude-test/` in Alpine:
```bash
mkdir -p ~/dev/projects/claude-test
cd ~/dev/projects/claude-test

# Create a simple project
echo "# Claude Test Project" > README.md
echo "console.log('Hello from Claude!');" > index.js

# Start Claude Code
claude

# In Claude, try:
# "Create a simple Express.js server with a hello world endpoint"
# "Add error handling and logging to this server"
# "Write tests for this API using Jest"
```

## Gemini CLI Installation & Setup

### 1. Install Gemini CLI
Since there's no official Gemini CLI, we'll create a wrapper using the API:

```bash
# Install required packages
npm install -g google-auth-library axios dotenv commander

# Create Gemini CLI directory in Alpine
mkdir -p ~/dev/scripts/gemini-cli
cd ~/dev/scripts/gemini-cli
```

### 2. Create Gemini CLI Script
Create `~/dev/scripts/gemini-cli/gemini.js` in Alpine:

```javascript
#!/usr/bin/env node

const { Command } = require('commander');
const axios = require('axios');
const fs = require('fs');
const path = require('path');
const readline = require('readline');

const program = new Command();

// Configuration
const CONFIG_FILE = path.join(process.env.HOME, '.gemini-cli-config.json');

class GeminiCLI {
    constructor() {
        this.config = this.loadConfig();
    }

    loadConfig() {
        try {
            if (fs.existsSync(CONFIG_FILE)) {
                return JSON.parse(fs.readFileSync(CONFIG_FILE, 'utf8'));
            }
        } catch (error) {
            console.error('Error loading config:', error.message);
        }
        return {};
    }

    saveConfig(config) {
        try {
            fs.writeFileSync(CONFIG_FILE, JSON.stringify(config, null, 2));
            console.log('✅ Configuration saved');
        } catch (error) {
            console.error('❌ Error saving config:', error.message);
        }
    }

    async setupAuth(apiKey) {
        this.config.apiKey = apiKey;
        this.config.baseUrl = 'https://generativelanguage.googleapis.com/v1beta';
        this.saveConfig(this.config);
    }

    async chat(prompt, model = 'gemini-pro') {
        if (!this.config.apiKey) {
            console.error('❌ API key not configured. Run: gemini auth setup');
            return;
        }

        try {
            console.log('🤖 Gemini is thinking...\n');
            
            const response = await axios.post(
                `${this.config.baseUrl}/models/${model}:generateContent?key=${this.config.apiKey}`,
                {
                    contents: [{
                        parts: [{ text: prompt }]
                    }]
                },
                {
                    headers: {
                        'Content-Type': 'application/json'
                    }
                }
            );

            const result = response.data?.candidates?.[0]?.content?.parts?.[0]?.text;
            if (result) {
                console.log('📝 Gemini Response:\n');
                console.log(result);
                
                // Save to history
                this.saveToHistory(prompt, result);
            } else {
                console.error('❌ No response from Gemini');
            }
        } catch (error) {
            console.error('❌ Error:', error.response?.data?.error?.message || error.message);
        }
    }

    saveToHistory(prompt, response) {
        const historyFile = path.join(process.env.HOME, '.gemini-cli-history.json');
        let history = [];
        
        try {
            if (fs.existsSync(historyFile)) {
                history = JSON.parse(fs.readFileSync(historyFile, 'utf8'));
            }
        } catch (error) {
            // Ignore errors, start fresh
        }

        history.push({
            timestamp: new Date().toISOString(),
            prompt,
            response
        });

        // Keep only last 50 entries
        if (history.length > 50) {
            history = history.slice(-50);
        }

        try {
            fs.writeFileSync(historyFile, JSON.stringify(history, null, 2));
        } catch (error) {
            // Ignore save errors
        }
    }

    async interactiveMode() {
        console.log('🚀 Gemini Interactive Mode (type "exit" to quit)\n');
        
        const rl = readline.createInterface({
            input: process.stdin,
            output: process.stdout
        });

        const askQuestion = () => {
            rl.question('You: ', async (input) => {
                if (input.toLowerCase() === 'exit') {
                    console.log('👋 Goodbye!');
                    rl.close();
                    return;
                }

                if (input.trim()) {
                    await this.chat(input);
                    console.log('\n' + '─'.repeat(50) + '\n');
                }
                askQuestion();
            });
        };

        askQuestion();
    }
}

const gemini = new GeminiCLI();

// CLI Commands
program
    .name('gemini')
    .description('Gemini CLI for mobile AI development')
    .version('1.0.0');

program
    .command('auth')
    .description('Configure Gemini API authentication')
    .action(async () => {
        const rl = readline.createInterface({
            input: process.stdin,
            output: process.stdout
        });

        rl.question('Enter your Gemini API key: ', (apiKey) => {
            gemini.setupAuth(apiKey.trim());
            rl.close();
        });
    });

program
    .command('chat [prompt]')
    .description('Chat with Gemini')
    .option('-m, --model <model>', 'Model to use', 'gemini-pro')
    .action(async (prompt, options) => {
        if (prompt) {
            await gemini.chat(prompt, options.model);
        } else {
            await gemini.interactiveMode();
        }
    });

program
    .command('code <prompt>')
    .description('Ask Gemini for coding help')
    .action(async (prompt) => {
        const codePrompt = `As an expert programmer, help me with this coding task. Provide clear, well-commented code with explanations:\n\n${prompt}`;
        await gemini.chat(codePrompt);
    });

program
    .command('debug <error>')
    .description('Debug an error with Gemini')
    .action(async (error) => {
        const debugPrompt = `Help me debug this error. Provide possible causes and solutions:\n\n${error}`;
        await gemini.chat(debugPrompt);
    });

program
    .command('explain <concept>')
    .description('Explain a concept')
    .action(async (concept) => {
        const explainPrompt = `Explain this concept clearly and concisely for a developer:\n\n${concept}`;
        await gemini.chat(explainPrompt);
    });

program
    .command('review')
    .description('Review code in current directory')
    .action(async () => {
        const files = fs.readdirSync('.').filter(f => 
            f.endsWith('.js') || f.endsWith('.ts') || f.endsWith('.py') || 
            f.endsWith('.java') || f.endsWith('.cpp') || f.endsWith('.c')
        );
        
        if (files.length === 0) {
            console.log('❌ No code files found in current directory');
            return;
        }

        console.log(`📁 Found ${files.length} code file(s): ${files.join(', ')}`);
        
        let codeContent = '';
        for (const file of files.slice(0, 3)) { // Limit to 3 files
            try {
                const content = fs.readFileSync(file, 'utf8');
                codeContent += `\n--- ${file} ---\n${content}\n`;
            } catch (error) {
                console.log(`⚠️  Could not read ${file}`);
            }
        }

        const reviewPrompt = `Please review this code for best practices, potential bugs, and improvements:\n${codeContent}`;
        await gemini.chat(reviewPrompt);
    });

program.parse();
```

### 3. Make Gemini CLI Executable
```bash
chmod +x ~/dev/scripts/gemini-cli/gemini.js

# Create symlink for global access
ln -sf ~/dev/scripts/gemini-cli/gemini.js ~/.npm-global/bin/gemini

# Test installation
gemini --version
```

### 4. Get Gemini API Key
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Create a new API key
4. Copy the key

### 5. Setup Gemini Authentication
```bash
# Configure API key
gemini auth
# Enter your API key when prompted
```

### 6. Simple Gemini Examples
```bash
# Basic chat
gemini chat "Explain async/await in JavaScript"

# Interactive mode
gemini chat

# Coding help
gemini code "Create a REST API with Express.js for user management"

# Debug assistance
gemini debug "TypeError: Cannot read property 'length' of undefined"

# Code review
cd ~/dev/projects/your-project
gemini review

# Explain concepts
gemini explain "What is event loop in Node.js"
```

## Essential Scripts

### 1. Development Environment Launcher
Create `~/dev/scripts/dev-env.sh` in Alpine:

```bash
#!/bin/bash
# Complete development environment setup

echo "🚀 Setting up mobile development environment..."

# Check and start required services
check_service() {
    if ! pgrep -f "$1" > /dev/null; then
        echo "⚠️  $1 not running"
        return 1
    else
        echo "✅ $1 is running"
        return 0
    fi
}

# Environment checks
echo "📋 Environment Status:"
echo "Node.js: $(node --version 2>/dev/null || echo 'Not installed')"
echo "npm: $(npm --version 2>/dev/null || echo 'Not installed')"
echo "Claude: $(claude --version 2>/dev/null || echo 'Not installed')"
echo "Gemini: $(gemini --version 2>/dev/null || echo 'Not installed')"
echo "tmux: $(tmux -V 2>/dev/null || echo 'Not installed')"
echo ""

# Check storage
echo "💾 Storage Status:"
~/dev/scripts/storage-check.sh
echo ""

# Start AI session
echo "🤖 Starting AI coding session..."
~/dev/scripts/tmux-ai-session.sh
```

### 2. Project Creator Script
Create `~/dev/scripts/new-project.sh` in Alpine:

```bash
#!/bin/bash
# Create new project with AI assistance

if [ -z "$1" ]; then
    echo "Usage: $0 <project-name> [project-type]"
    echo "Types: node, react, vue, python, static"
    exit 1
fi

PROJECT_NAME="$1"
PROJECT_TYPE="${2:-node}"
PROJECT_DIR="~/dev/projects/$PROJECT_NAME"

echo "🆕 Creating new $PROJECT_TYPE project: $PROJECT_NAME"

# Create project directory
mkdir -p "$PROJECT_DIR"
cd "$PROJECT_DIR"

# Initialize based on type
case $PROJECT_TYPE in
    "node")
        npm init -y
        echo "console.log('Hello from $PROJECT_NAME!');" > index.js
        echo "node_modules/\n*.log\n.env" > .gitignore
        ;;
    "react")
        npx create-react-app . --template typescript
        ;;
    "vue")
        vue create .
        ;;
    "python")
        echo "# $PROJECT_NAME" > README.md
        echo "print('Hello from $PROJECT_NAME!')" > main.py
        echo "__pycache__/\n*.pyc\n.env" > .gitignore
        python -m venv venv
        ;;
    "static")
        echo "<!DOCTYPE html><html><head><title>$PROJECT_NAME</title></head><body><h1>$PROJECT_NAME</h1></body></html>" > index.html
        mkdir -p css js
        echo "/* $PROJECT_NAME styles */" > css/style.css
        echo "// $PROJECT_NAME JavaScript" > js/script.js
        ;;
esac

# Initialize git
git init
git add .
git commit -m "Initial commit: $PROJECT_NAME"

echo "✅ Project created at $PROJECT_DIR"
echo "🤖 Starting Claude Code for project setup..."

# Start Claude in project directory
cd "$PROJECT_DIR"
claude
```

### 3. AI Assistant Switcher
Create `~/dev/scripts/ai-switch.sh` in Alpine:

```bash
#!/bin/bash
# Switch between AI assistants

show_menu() {
    echo "🤖 AI Assistant Selector"
    echo "1) Claude Code (Anthropic)"
    echo "2) Gemini CLI (Google)"
    echo "3) Both (Split tmux panes)"
    echo "4) Exit"
    echo -n "Choose an option: "
}

while true; do
    show_menu
    read choice
    case $choice in
        1)
            echo "🎯 Starting Claude Code..."
            claude
            break
            ;;
        2)
            echo "🎯 Starting Gemini CLI..."
            gemini chat
            break
            ;;
        3)
            echo "🎯 Starting both AIs in tmux..."
            tmux new-session -d -s "dual-ai" "claude"
            tmux split-window -h "gemini chat"
            tmux attach-session -s "dual-ai"
            break
            ;;
        4)
            echo "👋 Goodbye!"
            break
            ;;
        *)
            echo "❌ Invalid option. Please try again."
            ;;
    esac
done
```

### 4. Quick Backup Script
Create `~/dev/scripts/backup-dev.sh` in Alpine:

```bash
#!/bin/bash
# Backup development environment

BACKUP_DIR="/mnt/sdcard/alpine-dev-backup"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="dev_backup_$DATE"

echo "💾 Creating development backup..."

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Backup configurations
echo "📁 Backing up configurations..."
tar -czf "$BACKUP_DIR/${BACKUP_NAME}_configs.tar.gz" \
    ~/.bashrc \
    ~/.tmux.conf \
    ~/.claude/ \
    ~/.gemini-cli-config.json \
    ~/.ssh/config \
    ~/.gitconfig

# Backup projects (excluding node_modules)
echo "📁 Backing up projects..."
tar -czf "$BACKUP_DIR/${BACKUP_NAME}_projects.tar.gz" \
    --exclude="node_modules" \
    --exclude=".git" \
    --exclude="*.log" \
    ~/dev/projects/

# Backup scripts
echo "📁 Backing up scripts..."
tar -czf "$BACKUP_DIR/${BACKUP_NAME}_scripts.tar.gz" \
    ~/dev/scripts/

echo "✅ Backup completed: $BACKUP_DIR/$BACKUP_NAME"
echo "📊 Backup sizes:"
ls -lh "$BACKUP_DIR"/*"$DATE"*
```

Make all scripts executable:
```bash
chmod +x ~/dev/scripts/*.sh
```

Add aliases to `~/.bashrc`:
```bash
echo 'alias dev-env="~/dev/scripts/dev-env.sh"' >> ~/.bashrc
echo 'alias new-project="~/dev/scripts/new-project.sh"' >> ~/.bashrc
echo 'alias ai-switch="~/dev/scripts/ai-switch.sh"' >> ~/.bashrc
echo 'alias backup-dev="~/dev/scripts/backup-dev.sh"' >> ~/.bashrc
source ~/.bashrc
```

## Vibecoding Workflow

### 1. Morning Startup Routine
```bash
# Start your development environment
dev-env

# Or manually:
# 1. Launch tmux AI session
ai-session

# 2. Check project status
cd ~/dev/projects/current-project
git status

# 3. Start AI assistant
claude  # or gemini chat
```

### 2. Typical Vibecoding Session

**Step 1: Problem Definition**
```bash
# In Claude Code session
claude> "I want to build a REST API for a task management system. 
What's the best architecture for mobile-first development?"
```

**Step 2: Implementation**
```bash
# Let Claude create the project structure
claude> "Create the project structure with Express.js, 
add proper error handling, and include mobile-optimized responses"
```

**Step 3: Validation with Gemini**
```bash
# Switch to Gemini pane (Ctrl+a + arrow keys)
gemini code "Review this Express.js API structure for best practices"
```

**Step 4: Testing & Iteration**
```bash
# Back to development pane
npm test
npm run dev

# Ask AI for improvements
claude> "The API is working but response times are slow. 
How can we optimize for mobile connections?"
```

### 3. Project Workflows

**New Feature Development:**
```bash
# Create feature branch
git checkout -b feature/new-endpoint

# Describe to AI
claude> "Add a new endpoint for file uploads with progress tracking"

# Implement with AI assistance
# Test
npm test

# Review with Gemini
gemini review

# Commit
git add .
git commit -m "Add file upload endpoint with progress tracking"
```

**Debugging Session:**
```bash
# Encounter error
npm run dev
# Error appears

# Ask Claude to debug
claude> "I'm getting this error: [paste error]. 
Can you help me understand and fix it?"

# Or use Gemini for second opinion
gemini debug "TypeError: Cannot read property 'user' of undefined"
```

### 4. Mobile-Specific Optimizations

**Efficient tmux Usage:**
- Use `Ctrl+a + c` for new windows
- Use `Ctrl+a + n/p` for next/previous windows
- Use `Ctrl+a + [` for copy mode (scrolling)
- Use mouse for pane selection on mobile

**Battery-Saving Tips:**
- Use `tmux detach` to background sessions
- Set lower screen brightness
- Use airplane mode with WiFi for fewer distractions
- Enable power saving mode during long coding sessions

## Mobile-Optimized Configurations

### 1. Vim Configuration for Mobile
Create `~/.vimrc`:

```vim
" Mobile-optimized Vim configuration

" Basic settings
set number
set relativenumber
set expandtab
set tabstop=2
set shiftwidth=2
set autoindent
set smartindent

" Mobile-friendly features
set mouse=a
set clipboard=unnamedplus
set scrolloff=8
set sidescrolloff=8

" Visual improvements
syntax on
set cursorline
set showmatch
set hlsearch
set incsearch

" Color scheme for mobile screens
colorscheme desert

" Larger font simulation (terminal dependent)
set guifont=Monospace\ 14

" Key mappings for mobile
nnoremap <Space> :
nnoremap <C-s> :w<CR>
inoremap <C-s> <Esc>:w<CR>a

" Split navigation
nnoremap <C-h> <C-w>h
nnoremap <C-j> <C-w>j
nnoremap <C-k> <C-w>k
nnoremap <C-l> <C-w>l

" Quick exit
nnoremap <leader>q :q<CR>
nnoremap <leader>Q :q!<CR>
```

### 2. Enhanced .bashrc for Mobile Development
Add to `~/.bashrc`:

```bash
# Mobile Development Aliases
alias ll='ls -alF'
alias la='ls -A'
alias l='ls -CF'
alias grep='grep --color=auto'
alias ..='cd ..'
alias ...='cd ../..'

# Development shortcuts
alias npmr='npm run'
alias npmd='npm run dev'
alias npmt='npm test'
alias npmb='npm run build'

# Git shortcuts
alias gs='git status'
alias ga='git add'
alias gc='git commit'
alias gp='git push'
alias gl='git log --oneline'
alias gd='git diff'

# AI shortcuts
alias c='claude'
alias g='gemini chat'
alias ai='ai-switch'

# Project navigation
alias proj='cd ~/workspace/dev/projects'
alias scripts='cd ~/workspace/dev/scripts'

# System monitoring
alias top='htop'
alias disk='df -h'
alias mem='free -h'

# Quick edits
alias bashrc='vim ~/.bashrc && source ~/.bashrc'
alias tmuxconf='vim ~/.tmux.conf'
alias vimrc='vim ~/.vimrc'

# Mobile-specific functions
battery() {
    termux-battery-status | jq '.percentage'
}

wifi() {
    termux-wifi-connectioninfo | jq '.ssid'
}

notify() {
    termux-notification --title "Dev Environment" --content "$1"
}

# Auto-start tmux for SSH sessions
if [ -n "$SSH_CLIENT" ] || [ -n "$SSH_TTY" ]; then
    if ! tmux has-session 2>/dev/null; then
        tmux new-session -d -s "ssh-session"
    fi
    if [ -z "$TMUX" ]; then
        tmux attach-session -t "ssh-session"
    fi
fi

# Development environment status
dev_status() {
    echo "🔋 Battery: $(battery)%"
    echo "📶 WiFi: $(wifi)"
    echo "💾 Disk: $(df -h ~ | awk 'NR==2{print $4}')"
    echo "🧠 Memory: $(free -h | awk 'NR==2{print $7}')"
    echo "🎯 Active tmux sessions: $(tmux list-sessions 2>/dev/null | wc -l)"
}

alias status='dev_status'
```

### 3. Package.json Template for Mobile Development
Create `~/dev/templates/package.json` in Alpine:

```json
{
  "name": "mobile-dev-project",
  "version": "1.0.0",
  "description": "Mobile-optimized development project",
  "main": "index.js",
  "scripts": {
    "start": "node index.js",
    "dev": "nodemon index.js",
    "test": "jest",
    "test:watch": "jest --watch",
    "build": "babel src -d dist",
    "lint": "eslint .",
    "lint:fix": "eslint . --fix",
    "format": "prettier --write .",
    "mobile:start": "node --max-old-space-size=512 index.js",
    "mobile:test": "node --max-old-space-size=256 ./node_modules/.bin/jest"
  },
  "jest": {
    "testEnvironment": "node",
    "collectCoverageFrom": [
      "src/**/*.js",
      "!src/**/*.test.js"
    ]
  },
  "nodemonConfig": {
    "watch": ["src"],
    "ext": "js,json",
    "ignore": ["node_modules", "dist"],
    "delay": "2"
  },
  "keywords": ["mobile", "development", "ai", "vibecoding"],
  "author": "Your Name",
  "license": "MIT",
  "devDependencies": {
    "@babel/cli": "^7.22.0",
    "@babel/core": "^7.22.0",
    "@babel/preset-env": "^7.22.0",
    "eslint": "^8.44.0",
    "jest": "^29.6.0",
    "nodemon": "^3.0.0",
    "prettier": "^3.0.0"
  }
}
```

## Troubleshooting

### Common Issues and Solutions

**1. Claude CLI not found after installation**
```bash
# Check if npm global bin is in PATH
echo $PATH | grep npm-global

# If not, add it
echo 'export PATH=~/.npm-global/bin:$PATH' >> ~/.bashrc
source ~/.bashrc

# Reinstall Claude Code
npm install -g @anthropic-ai/claude-code
```

**2. Gemini API authentication issues**
```bash
# Check config file
cat ~/.gemini-cli-config.json

# Reconfigure
gemini auth

# Test connection
gemini chat "Hello"
```

**3. tmux sessions not persisting**
```bash
# Check if tmux-resurrect is working
ls ~/.tmux/resurrect/

# Manual save
tmux run-shell ~/.tmux/plugins/tmux-resurrect/scripts/save.sh

# Manual restore
tmux run-shell ~/.tmux/plugins/tmux-resurrect/scripts/restore.sh
```

**4. Storage permission issues**
```bash
# Re-setup storage
termux-setup-storage

# Check permissions
ls -la ~/storage/

# Fix symlinks if broken
rm ~/dev
ln -sf /mnt/sdcard/alpine-dev ~/dev
```

**5. Node.js memory issues**
```bash
# For low-memory devices, add to ~/.bashrc:
export NODE_OPTIONS="--max-old-space-size=512"

# Or run specific commands with limited memory
node --max-old-space-size=256 script.js
```

**6. Package installation failures**
```bash
# Clean npm cache
npm cache clean --force

# Update package lists
pkg update

# Install with verbose output for debugging
npm install -g package-name --verbose
```

### Performance Optimization

**1. Reduce Memory Usage:**
```bash
# Add to ~/.bashrc
export NODE_OPTIONS="--max-old-space-size=512"
export npm_config_prefer_offline=true
export npm_config_audit=false
```

**2. Faster Package Installation:**
```bash
# Use npm's fast package manager alternative
npm install -g pnpm
alias npm=pnpm
```

**3. Optimize tmux Performance:**
```bash
# Add to ~/.tmux.conf
set -g status-interval 5
set -g display-time 1000
set -g escape-time 0
```

## Pro Tips

### 1. Keyboard Shortcuts for Mobile
- Use external Bluetooth keyboard for better experience
- Learn tmux shortcuts by heart
- Use vim key bindings in terminal (set -o vi)
- Configure swipe gestures in Termux settings

### 2. Battery Management
```bash
# Create battery monitoring script
echo '#!/bin/bash
BATTERY=$(termux-battery-status | jq -r .percentage)
if [ $BATTERY -lt 20 ]; then
    termux-notification --title "Low Battery" --content "Battery: ${BATTERY}%"
fi' > ~/workspace/dev/scripts/battery-check.sh

chmod +x ~/workspace/dev/scripts/battery-check.sh

# Add to crontab (if available) or run manually
*/10 * * * * ~/workspace/dev/scripts/battery-check.sh
```

### 3. Efficient AI Prompting
- Be specific in your requests
- Provide context about mobile constraints
- Ask for mobile-optimized solutions
- Use follow-up questions for clarification
- Save good prompts as templates

### 4. Project Organization
```bash
# Create project templates
mkdir -p ~/dev/templates/{node,react,python,static}

# Use consistent naming conventions
# project-name (kebab-case)
# Use semantic versioning
# Keep README files updated
```

### 5. Backup Strategy
```bash
# Weekly backup script
echo '#!/bin/bash
cd ~/dev
tar -czf /mnt/sdcard/weekly-backup-$(date +%Y%m%d).tar.gz \
    --exclude="node_modules" \
    --exclude=".git" \
    projects/ scripts/ configs/' > ~/dev/scripts/weekly-backup.sh

chmod +x ~/dev/scripts/weekly-backup.sh
```

### 6. Collaborative Development
```bash
# Set up SSH for remote collaboration
pkg install openssh
sshd

# Share tmux sessions
tmux new-session -s shared-session
# Others can join with: tmux attach-session -t shared-session
```

### 7. Learning Resources
- Keep a learning log in `~/dev/learning.md`
- Save useful AI conversations
- Document common patterns and solutions
- Create code snippets library

### 8. Security Best Practices
```bash
# Use environment variables for secrets
echo 'export API_KEY="your-secret-key"' >> ~/.env
echo 'source ~/.env' >> ~/.bashrc

# Add .env to .gitignore globally
git config --global core.excludesfile ~/.gitignore_global
echo '.env' >> ~/.gitignore_global
```

## Conclusion

This guide provides a complete mobile vibecoding setup with AI assistance. The combination of Termux, Alpine Linux, tmux, Claude Code, and Gemini CLI creates a powerful development environment that rivals desktop setups.

Key benefits:
- ✅ Full Alpine Linux development environment on mobile
- ✅ AI-powered coding assistance
- ✅ Session persistence with tmux
- ✅ Efficient mobile-optimized workflows
- ✅ Professional development capabilities

Remember: Vibecoding is about finding your flow state with AI assistance. Experiment with different workflows, customize your setup, and most importantly, enjoy the process of coding with AI on mobile!

---

**Happy Vibecoding! 🚀📱💻**

*Last updated: July 2025*
*Version: 1.0.0*

---

### Contributing
Found improvements or issues? Please contribute to this guide:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

### License
This guide is released under MIT License. Feel free to use, modify, and share!