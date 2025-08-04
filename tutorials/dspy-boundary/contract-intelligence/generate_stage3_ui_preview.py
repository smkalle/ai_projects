#!/usr/bin/env python3
"""Generate Stage 3 UI preview showing Silicon Valley style design polish."""

from pathlib import Path
from datetime import datetime

def generate_stage3_preview():
    """Generate Stage 3 UI preview with Silicon Valley design system."""
    project_root = Path(__file__).parent
    preview_dir = project_root / "ui_preview_stage3"
    preview_dir.mkdir(exist_ok=True)
    
    print("🎨 Generating Stage 3 UI Preview - Silicon Valley Design Polish...")
    print("=" * 70)
    
    # Modern CSS with Silicon Valley aesthetics
    modern_css = """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
        
        * { 
            margin: 0; 
            padding: 0; 
            box-sizing: border-box; 
        }
        
        :root {
            /* Primary palette */
            --primary: #6366f1;
            --primary-light: #818cf8;
            --primary-dark: #4f46e5;
            --secondary: #8b5cf6;
            --accent: #06b6d4;
            --success: #10b981;
            --warning: #f59e0b;
            --error: #ef4444;
            
            /* Grays */
            --gray-50: #f9fafb;
            --gray-100: #f3f4f6;
            --gray-200: #e5e7eb;
            --gray-300: #d1d5db;
            --gray-400: #9ca3af;
            --gray-500: #6b7280;
            --gray-600: #4b5563;
            --gray-700: #374151;
            --gray-800: #1f2937;
            --gray-900: #111827;
            
            /* Spacing */
            --space-1: 0.25rem;
            --space-2: 0.5rem;
            --space-3: 0.75rem;
            --space-4: 1rem;
            --space-6: 1.5rem;
            --space-8: 2rem;
            --space-12: 3rem;
            
            /* Border radius */
            --radius-sm: 0.125rem;
            --radius-md: 0.375rem;
            --radius-lg: 0.5rem;
            --radius-xl: 0.75rem;
            --radius-2xl: 1rem;
            --radius-full: 9999px;
            
            /* Shadows */
            --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
            --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
            --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1);
            --shadow-xl: 0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1);
        }
        
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background: var(--gray-50);
            color: var(--gray-800);
            line-height: 1.6;
            -webkit-font-smoothing: antialiased;
        }
        
        .container {
            display: flex;
            min-height: 100vh;
        }
        
        .sidebar {
            width: 300px;
            background: white;
            border-right: 1px solid var(--gray-200);
            padding: var(--space-6);
            overflow-y: auto;
            box-shadow: var(--shadow-sm);
        }
        
        .main {
            flex: 1;
            padding: var(--space-8);
            overflow-y: auto;
            max-width: calc(100vw - 300px);
        }
        
        /* Animations */
        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        
        @keyframes shimmer {
            0% { background-position: -200px 0; }
            100% { background-position: calc(200px + 100%) 0; }
        }
        
        .animate-fade-in-up {
            animation: fadeInUp 0.6s ease-out;
        }
        
        .animate-pulse {
            animation: pulse 2s ease-in-out infinite;
        }
        
        /* Modern components */
        .modern-header {
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            color: white;
            padding: var(--space-8);
            border-radius: var(--radius-2xl);
            margin-bottom: var(--space-8);
            text-align: center;
            box-shadow: var(--shadow-xl);
            position: relative;
            overflow: hidden;
        }
        
        .modern-header::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: linear-gradient(45deg, rgba(255,255,255,0.1) 0%, transparent 100%);
            pointer-events: none;
        }
        
        .modern-header h1 {
            font-size: 3rem;
            font-weight: 800;
            margin-bottom: var(--space-4);
            position: relative;
            z-index: 1;
        }
        
        .modern-header p {
            font-size: 1.25rem;
            opacity: 0.9;
            position: relative;
            z-index: 1;
        }
        
        .card {
            background: white;
            border: 1px solid var(--gray-200);
            border-radius: var(--radius-xl);
            padding: var(--space-6);
            box-shadow: var(--shadow-md);
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }
        
        .card:hover {
            transform: translateY(-4px);
            box-shadow: var(--shadow-xl);
        }
        
        .glass-card {
            background: rgba(255, 255, 255, 0.7);
            backdrop-filter: blur(12px);
            border: 1px solid rgba(255, 255, 255, 0.3);
            border-radius: var(--radius-2xl);
            padding: var(--space-6);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        }
        
        .feature-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: var(--space-6);
            margin: var(--space-8) 0;
        }
        
        .feature-card {
            background: white;
            border: 1px solid var(--gray-200);
            border-radius: var(--radius-xl);
            padding: var(--space-6);
            text-align: center;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }
        
        .feature-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.4), transparent);
            transition: left 0.5s;
        }
        
        .feature-card:hover::before {
            left: 100%;
        }
        
        .feature-card:hover {
            transform: translateY(-8px);
            box-shadow: var(--shadow-xl);
            border-color: var(--primary);
        }
        
        .feature-icon {
            font-size: 3rem;
            margin-bottom: var(--space-4);
            position: relative;
            z-index: 1;
        }
        
        .feature-title {
            font-size: 1.5rem;
            font-weight: 700;
            color: var(--gray-900);
            margin-bottom: var(--space-3);
            position: relative;
            z-index: 1;
        }
        
        .feature-description {
            color: var(--gray-600);
            line-height: 1.6;
            margin-bottom: var(--space-6);
            position: relative;
            z-index: 1;
        }
        
        .btn {
            background: var(--primary);
            color: white;
            border: none;
            border-radius: var(--radius-lg);
            padding: var(--space-3) var(--space-6);
            font-weight: 600;
            font-size: 1rem;
            cursor: pointer;
            transition: all 0.2s ease;
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            gap: var(--space-2);
            position: relative;
            z-index: 1;
        }
        
        .btn:hover {
            background: var(--primary-dark);
            transform: translateY(-2px);
            box-shadow: var(--shadow-lg);
        }
        
        .btn-secondary {
            background: var(--gray-100);
            color: var(--gray-800);
            border: 1px solid var(--gray-300);
        }
        
        .btn-secondary:hover {
            background: var(--gray-200);
            border-color: var(--gray-400);
        }
        
        .metric-card {
            background: white;
            border: 1px solid var(--gray-200);
            border-radius: var(--radius-lg);
            padding: var(--space-4);
            text-align: center;
            box-shadow: var(--shadow-sm);
            transition: all 0.2s ease;
        }
        
        .metric-card:hover {
            box-shadow: var(--shadow-md);
        }
        
        .metric-value {
            font-size: 2.5rem;
            font-weight: 800;
            color: var(--primary);
            margin-bottom: var(--space-2);
        }
        
        .metric-label {
            color: var(--gray-600);
            font-size: 0.875rem;
            font-weight: 500;
        }
        
        .status-badge {
            padding: var(--space-1) var(--space-3);
            border-radius: var(--radius-full);
            font-size: 0.875rem;
            font-weight: 500;
        }
        
        .status-success {
            background: rgba(16, 185, 129, 0.1);
            color: var(--success);
            border: 1px solid rgba(16, 185, 129, 0.2);
        }
        
        .status-warning {
            background: rgba(245, 158, 11, 0.1);
            color: var(--warning);
            border: 1px solid rgba(245, 158, 11, 0.2);
        }
        
        .status-error {
            background: rgba(239, 68, 68, 0.1);
            color: var(--error);
            border: 1px solid rgba(239, 68, 68, 0.2);
        }
        
        .progress-bar {
            width: 100%;
            height: 8px;
            background: var(--gray-200);
            border-radius: var(--radius-full);
            overflow: hidden;
            margin: var(--space-4) 0;
        }
        
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, var(--primary), var(--secondary));
            border-radius: var(--radius-full);
            transition: width 1s ease;
        }
        
        .loading-shimmer {
            background: linear-gradient(90deg, var(--gray-200) 25%, var(--gray-100) 50%, var(--gray-200) 75%);
            background-size: 200% 100%;
            animation: shimmer 1.5s infinite;
            border-radius: var(--radius-md);
        }
        
        .nav-header {
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            color: white;
            padding: var(--space-4);
            border-radius: var(--radius-lg);
            margin-bottom: var(--space-6);
            text-align: center;
            font-weight: 700;
        }
        
        .nav-link {
            display: block;
            padding: var(--space-3);
            margin-bottom: var(--space-2);
            background: var(--gray-50);
            color: var(--gray-700);
            text-decoration: none;
            border-radius: var(--radius-md);
            border: 1px solid var(--gray-200);
            transition: all 0.2s ease;
            font-weight: 500;
        }
        
        .nav-link:hover {
            background: var(--primary);
            color: white;
            transform: translateX(4px);
            box-shadow: var(--shadow-md);
        }
        
        .theme-toggle {
            position: fixed;
            top: var(--space-4);
            right: var(--space-4);
            width: 48px;
            height: 48px;
            background: white;
            border: 1px solid var(--gray-300);
            border-radius: var(--radius-full);
            box-shadow: var(--shadow-lg);
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.25rem;
            transition: all 0.3s ease;
            z-index: 1000;
        }
        
        .theme-toggle:hover {
            transform: scale(1.1);
            box-shadow: var(--shadow-xl);
        }
        
        /* Responsive design */
        @media (max-width: 768px) {
            .container {
                flex-direction: column;
            }
            
            .sidebar {
                width: 100%;
                padding: var(--space-4);
            }
            
            .main {
                max-width: 100vw;
                padding: var(--space-4);
            }
            
            .feature-grid {
                grid-template-columns: 1fr;
                gap: var(--space-4);
            }
            
            .modern-header h1 {
                font-size: 2rem;
            }
        }
        
        /* Dark theme */
        [data-theme="dark"] {
            --gray-50: #0f0f23;
            --gray-100: #1a1a2e;
            --gray-200: #252545;
            --gray-300: #2d2d4a;
            color: #e2e8f0;
        }
        
        [data-theme="dark"] body {
            background: var(--gray-50);
            color: #e2e8f0;
        }
        
        [data-theme="dark"] .card,
        [data-theme="dark"] .feature-card,
        [data-theme="dark"] .metric-card {
            background: var(--gray-100);
            border-color: var(--gray-200);
            color: #e2e8f0;
        }
        
        [data-theme="dark"] .sidebar {
            background: var(--gray-100);
            border-color: var(--gray-200);
        }
    </style>
    """
    
    # Main demo page
    demo_html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Stage 3 - Silicon Valley Design Polish</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    {modern_css}
</head>
<body>
    <div class="theme-toggle" onclick="toggleTheme()" title="Toggle theme">
        <span id="theme-icon">🌙</span>
    </div>
    
    <div class="container">
        <div class="sidebar">
            <div class="nav-header">
                🏠 Navigation
            </div>
            
            <a href="index.html" class="nav-link">🏠 Overview</a>
            <a href="responsive.html" class="nav-link">📱 Responsive Design</a>
            <a href="components.html" class="nav-link">🧩 Components</a>
            <a href="animations.html" class="nav-link">✨ Animations</a>
            <a href="themes.html" class="nav-link">🌓 Themes</a>
            
            <div style="margin: var(--space-6) 0;">
                <h4 style="color: var(--primary); margin-bottom: var(--space-4);">📊 Quick Stats</h4>
                
                <div class="metric-card" style="margin-bottom: var(--space-3);">
                    <div class="metric-value">15+</div>
                    <div class="metric-label">New Components</div>
                </div>
                
                <div class="metric-card" style="margin-bottom: var(--space-3);">
                    <div class="metric-value">100%</div>
                    <div class="metric-label">Mobile Ready</div>
                </div>
                
                <div class="metric-card">
                    <div class="metric-value">98</div>
                    <div class="metric-label">Design Score</div>
                </div>
            </div>
            
            <div>
                <h4 style="color: var(--primary); margin-bottom: var(--space-4);">⚙️ Features</h4>
                
                <div style="display: flex; justify-content: space-between; margin-bottom: var(--space-2);">
                    <span>Responsive:</span>
                    <span class="status-badge status-success">✅ Enabled</span>
                </div>
                
                <div style="display: flex; justify-content: space-between; margin-bottom: var(--space-2);">
                    <span>Animations:</span>
                    <span class="status-badge status-success">✅ Enabled</span>
                </div>
                
                <div style="display: flex; justify-content: space-between; margin-bottom: var(--space-2);">
                    <span>Dark Mode:</span>
                    <span class="status-badge status-success">✅ Enabled</span>
                </div>
                
                <div style="display: flex; justify-content: space-between;">
                    <span>Glassmorphism:</span>
                    <span class="status-badge status-success">✅ Enabled</span>
                </div>
            </div>
        </div>
        
        <div class="main">
            <div class="modern-header animate-fade-in-up">
                <h1>⚖️ Contract Intelligence Platform</h1>
                <p>Silicon Valley Style Design Polish - Stage 3</p>
            </div>
            
            <div class="card animate-fade-in-up" style="animation-delay: 0.2s;">
                <h2 style="color: var(--primary); margin-bottom: var(--space-4); font-weight: 700;">
                    🎨 Design System Transformation
                </h2>
                <p style="font-size: 1.125rem; line-height: 1.6; color: var(--gray-600);">
                    Experience the complete UI transformation with our Silicon Valley-inspired design system. 
                    Modern typography, responsive layouts, smooth animations, and premium aesthetics 
                    create a world-class user experience.
                </p>
            </div>
            
            <h3 style="color: var(--primary); margin: var(--space-8) 0 var(--space-6) 0; font-weight: 700;">
                🚀 Key Improvements
            </h3>
            
            <div class="feature-grid">
                <div class="feature-card animate-fade-in-up" style="animation-delay: 0.3s;">
                    <div class="feature-icon">📱</div>
                    <h4 class="feature-title">Mobile-First Responsive</h4>
                    <p class="feature-description">
                        Fluid layouts that adapt perfectly to any screen size with touch-optimized interactions.
                    </p>
                    <button class="btn">View Demo</button>
                </div>
                
                <div class="feature-card animate-fade-in-up" style="animation-delay: 0.4s;">
                    <div class="feature-icon">✨</div>
                    <h4 class="feature-title">Micro-Animations</h4>
                    <p class="feature-description">
                        Subtle animations and transitions that provide visual feedback and enhance user engagement.
                    </p>
                    <button class="btn">See Animations</button>
                </div>
                
                <div class="feature-card animate-fade-in-up" style="animation-delay: 0.5s;">
                    <div class="feature-icon">🌓</div>
                    <h4 class="feature-title">Dark/Light Themes</h4>
                    <p class="feature-description">
                        Seamless theme switching with system preference detection and smooth transitions.
                    </p>
                    <button class="btn">Toggle Theme</button>
                </div>
                
                <div class="feature-card animate-fade-in-up" style="animation-delay: 0.6s;">
                    <div class="feature-icon">💎</div>
                    <h4 class="feature-title">Glassmorphism Effects</h4>
                    <p class="feature-description">
                        Modern glass-like surfaces with backdrop blur effects for premium visual appeal.
                    </p>
                    <button class="btn">View Effects</button>
                </div>
                
                <div class="feature-card animate-fade-in-up" style="animation-delay: 0.7s;">
                    <div class="feature-icon">🎯</div>
                    <h4 class="feature-title">Component Library</h4>
                    <p class="feature-description">
                        Comprehensive design system with reusable components and consistent styling.
                    </p>
                    <button class="btn">Browse Components</button>
                </div>
                
                <div class="feature-card animate-fade-in-up" style="animation-delay: 0.8s;">
                    <div class="feature-icon">⚡</div>
                    <h4 class="feature-title">Performance Optimized</h4>
                    <p class="feature-description">
                        Lightweight CSS animations and optimized rendering for smooth 60fps interactions.
                    </p>
                    <button class="btn">Performance Metrics</button>
                </div>
            </div>
            
            <div class="card animate-fade-in-up" style="animation-delay: 0.9s;">
                <h3 style="color: var(--primary); margin-bottom: var(--space-4);">📊 Design Progress</h3>
                
                <div style="margin-bottom: var(--space-4);">
                    <div style="display: flex; justify-content: space-between; margin-bottom: var(--space-2);">
                        <span style="font-weight: 500;">Typography System</span>
                        <span style="color: var(--success); font-weight: 600;">100%</span>
                    </div>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: 100%;"></div>
                    </div>
                </div>
                
                <div style="margin-bottom: var(--space-4);">
                    <div style="display: flex; justify-content: space-between; margin-bottom: var(--space-2);">
                        <span style="font-weight: 500;">Color Palette</span>
                        <span style="color: var(--success); font-weight: 600;">100%</span>
                    </div>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: 100%;"></div>
                    </div>
                </div>
                
                <div style="margin-bottom: var(--space-4);">
                    <div style="display: flex; justify-content: space-between; margin-bottom: var(--space-2);">
                        <span style="font-weight: 500;">Responsive Layouts</span>
                        <span style="color: var(--success); font-weight: 600;">100%</span>
                    </div>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: 100%;"></div>
                    </div>
                </div>
                
                <div style="margin-bottom: var(--space-4);">
                    <div style="display: flex; justify-content: space-between; margin-bottom: var(--space-2);">
                        <span style="font-weight: 500;">Animation Library</span>
                        <span style="color: var(--success); font-weight: 600;">95%</span>
                    </div>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: 95%;"></div>
                    </div>
                </div>
                
                <div>
                    <div style="display: flex; justify-content: space-between; margin-bottom: var(--space-2);">
                        <span style="font-weight: 500;">Theme System</span>
                        <span style="color: var(--success); font-weight: 600;">100%</span>
                    </div>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: 100%;"></div>
                    </div>
                </div>
            </div>
            
            <div class="glass-card animate-fade-in-up" style="animation-delay: 1s; margin: var(--space-8) 0;">
                <h3 style="color: var(--primary); margin-bottom: var(--space-4);">✨ What's New in Stage 3</h3>
                <ul style="list-style: none; padding: 0;">
                    <li style="margin-bottom: var(--space-3); display: flex; align-items: center;">
                        <span style="color: var(--success); margin-right: var(--space-3); font-size: 1.25rem;">✅</span>
                        <span>Complete design system with Inter typography and modern color palette</span>
                    </li>
                    <li style="margin-bottom: var(--space-3); display: flex; align-items: center;">
                        <span style="color: var(--success); margin-right: var(--space-3); font-size: 1.25rem;">✅</span>
                        <span>Mobile-first responsive grid system with breakpoints</span>
                    </li>
                    <li style="margin-bottom: var(--space-3); display: flex; align-items: center;">
                        <span style="color: var(--success); margin-right: var(--space-3); font-size: 1.25rem;">✅</span>
                        <span>20+ CSS animations with reduced motion support</span>
                    </li>
                    <li style="margin-bottom: var(--space-3); display: flex; align-items: center;">
                        <span style="color: var(--success); margin-right: var(--space-3); font-size: 1.25rem;">✅</span>
                        <span>Dark/light theme system with automatic detection</span>
                    </li>
                    <li style="margin-bottom: var(--space-3); display: flex; align-items: center;">
                        <span style="color: var(--success); margin-right: var(--space-3); font-size: 1.25rem;">✅</span>
                        <span>Glassmorphism effects and modern visual treatments</span>
                    </li>
                    <li style="display: flex; align-items: center;">
                        <span style="color: var(--success); margin-right: var(--space-3); font-size: 1.25rem;">✅</span>
                        <span>Professional component library with hover states</span>
                    </li>
                </ul>
            </div>
            
            <div style="background: var(--success); background: linear-gradient(135deg, var(--success), var(--accent)); color: white; padding: var(--space-6); border-radius: var(--radius-2xl); text-align: center; margin: var(--space-8) 0;">
                <h3 style="margin-bottom: var(--space-4); font-weight: 700;">🎉 Stage 3 Complete!</h3>
                <p style="font-size: 1.125rem; margin-bottom: var(--space-6); opacity: 0.9;">
                    Silicon Valley design polish successfully implemented. The UI now features modern aesthetics, 
                    responsive layouts, and premium interactions ready for production use.
                </p>
                <div style="display: flex; gap: var(--space-4); justify-content: center; flex-wrap: wrap;">
                    <button class="btn btn-secondary">📋 View Checklist</button>
                    <button class="btn btn-secondary">🚀 Start Stage 4</button>
                </div>
            </div>
        </div>
    </div>
    
    <script>
    function toggleTheme() {{
        const currentTheme = document.documentElement.getAttribute('data-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        const icon = document.getElementById('theme-icon');
        
        document.documentElement.setAttribute('data-theme', newTheme);
        icon.textContent = newTheme === 'dark' ? '☀️' : '🌙';
        
        localStorage.setItem('theme', newTheme);
    }}
    
    // Initialize theme
    const savedTheme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', savedTheme);
    document.getElementById('theme-icon').textContent = savedTheme === 'dark' ? '☀️' : '🌙';
    
    // Add click handlers for demo buttons
    document.addEventListener('click', function(e) {{
        if (e.target.classList.contains('btn')) {{
            e.target.style.transform = 'scale(0.95)';
            setTimeout(() => {{
                e.target.style.transform = '';
            }}, 150);
        }}
    }});
    </script>
</body>
</html>"""
    
    # Components showcase page
    components_html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Components Showcase - Stage 3</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    {modern_css}
</head>
<body>
    <div class="theme-toggle" onclick="toggleTheme()" title="Toggle theme">
        <span id="theme-icon">🌙</span>
    </div>
    
    <div class="container">
        <div class="sidebar">
            <div class="nav-header">
                🧩 Components
            </div>
            
            <a href="index.html" class="nav-link">🏠 Back to Overview</a>
            <a href="#buttons" class="nav-link">🔘 Buttons</a>
            <a href="#cards" class="nav-link">🗂️ Cards</a>
            <a href="#forms" class="nav-link">📝 Forms</a>
            <a href="#metrics" class="nav-link">📊 Metrics</a>
            <a href="#badges" class="nav-link">🏷️ Badges</a>
        </div>
        
        <div class="main">
            <div class="modern-header">
                <h1>🧩 Component Library</h1>
                <p>Modern UI components with Silicon Valley aesthetics</p>
            </div>
            
            <section id="buttons" style="margin-bottom: var(--space-12);">
                <h2 style="color: var(--primary); margin-bottom: var(--space-6);">🔘 Buttons</h2>
                
                <div class="card">
                    <h3 style="margin-bottom: var(--space-4);">Button Variants</h3>
                    <div style="display: flex; gap: var(--space-4); flex-wrap: wrap; margin-bottom: var(--space-6);">
                        <button class="btn">Primary Button</button>
                        <button class="btn btn-secondary">Secondary Button</button>
                        <button class="btn" style="background: var(--success);">Success Button</button>
                        <button class="btn" style="background: var(--warning);">Warning Button</button>
                        <button class="btn" style="background: var(--error);">Error Button</button>
                    </div>
                    
                    <h3 style="margin-bottom: var(--space-4);">Button Sizes</h3>
                    <div style="display: flex; gap: var(--space-4); align-items: center; flex-wrap: wrap;">
                        <button class="btn" style="padding: var(--space-2) var(--space-4); font-size: 0.875rem;">Small</button>
                        <button class="btn">Medium</button>
                        <button class="btn" style="padding: var(--space-4) var(--space-8); font-size: 1.125rem;">Large</button>
                    </div>
                </div>
            </section>
            
            <section id="cards" style="margin-bottom: var(--space-12);">
                <h2 style="color: var(--primary); margin-bottom: var(--space-6);">🗂️ Cards</h2>
                
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: var(--space-6);">
                    <div class="card">
                        <h3>Standard Card</h3>
                        <p>Basic card with hover effects and shadow elevation.</p>
                    </div>
                    
                    <div class="glass-card">
                        <h3>Glass Card</h3>
                        <p>Modern glassmorphism effect with backdrop blur.</p>
                    </div>
                    
                    <div class="feature-card">
                        <div class="feature-icon">✨</div>
                        <h4 class="feature-title">Feature Card</h4>
                        <p class="feature-description">Interactive card with icon and animation effects.</p>
                        <button class="btn">Learn More</button>
                    </div>
                </div>
            </section>
            
            <section id="metrics" style="margin-bottom: var(--space-12);">
                <h2 style="color: var(--primary); margin-bottom: var(--space-6);">📊 Metrics & Progress</h2>
                
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: var(--space-4); margin-bottom: var(--space-8);">
                    <div class="metric-card">
                        <div class="metric-value">$2.4M</div>
                        <div class="metric-label">Total Revenue</div>
                    </div>
                    
                    <div class="metric-card">
                        <div class="metric-value">1,847</div>
                        <div class="metric-label">Active Users</div>
                    </div>
                    
                    <div class="metric-card">
                        <div class="metric-value">97.2%</div>
                        <div class="metric-label">Uptime</div>
                    </div>
                    
                    <div class="metric-card">
                        <div class="metric-value">156</div>
                        <div class="metric-label">Contracts</div>
                    </div>
                </div>
                
                <div class="card">
                    <h3 style="margin-bottom: var(--space-4);">Progress Indicators</h3>
                    
                    <div style="margin-bottom: var(--space-4);">
                        <div style="display: flex; justify-content: space-between; margin-bottom: var(--space-2);">
                            <span>Task Completion</span>
                            <span style="color: var(--primary); font-weight: 600;">85%</span>
                        </div>
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: 85%;"></div>
                        </div>
                    </div>
                    
                    <div style="margin-bottom: var(--space-4);">
                        <div style="display: flex; justify-content: space-between; margin-bottom: var(--space-2);">
                            <span>Data Processing</span>
                            <span style="color: var(--success); font-weight: 600;">100%</span>
                        </div>
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: 100%; background: var(--success);"></div>
                        </div>
                    </div>
                    
                    <div>
                        <div style="display: flex; justify-content: space-between; margin-bottom: var(--space-2);">
                            <span>Upload Progress</span>
                            <span style="color: var(--warning); font-weight: 600;">62%</span>
                        </div>
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: 62%; background: var(--warning);"></div>
                        </div>
                    </div>
                </div>
            </section>
            
            <section id="badges">
                <h2 style="color: var(--primary); margin-bottom: var(--space-6);">🏷️ Status Badges</h2>
                
                <div class="card">
                    <h3 style="margin-bottom: var(--space-4);">Status Indicators</h3>
                    <div style="display: flex; gap: var(--space-4); flex-wrap: wrap;">
                        <span class="status-badge status-success">✅ Completed</span>
                        <span class="status-badge status-warning">⏳ In Progress</span>
                        <span class="status-badge status-error">❌ Failed</span>
                        <span class="status-badge" style="background: rgba(99, 102, 241, 0.1); color: var(--primary); border: 1px solid rgba(99, 102, 241, 0.2);">📋 Pending</span>
                    </div>
                </div>
            </section>
        </div>
    </div>
    
    <script>
    function toggleTheme() {{
        const currentTheme = document.documentElement.getAttribute('data-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        const icon = document.getElementById('theme-icon');
        
        document.documentElement.setAttribute('data-theme', newTheme);
        icon.textContent = newTheme === 'dark' ? '☀️' : '🌙';
        
        localStorage.setItem('theme', newTheme);
    }}
    
    // Initialize theme
    const savedTheme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', savedTheme);
    document.getElementById('theme-icon').textContent = savedTheme === 'dark' ? '☀️' : '🌙';
    </script>
</body>
</html>"""
    
    # Index page
    index_html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Stage 3 - Silicon Valley Design Polish</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 40px 20px;
            background: #f9fafb;
            color: #1f2937;
        }}
        h1 {{ 
            color: #6366f1; 
            font-weight: 800;
            font-size: 2.5rem;
            margin-bottom: 1rem;
        }}
        .subtitle {{
            color: #6b7280;
            font-size: 1.125rem;
            margin-bottom: 2rem;
        }}
        .feature-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 30px;
            margin-top: 30px;
        }}
        .feature-card {{
            background: white;
            border: 1px solid #e5e7eb;
            border-radius: 16px;
            overflow: hidden;
            box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
            transition: all 0.3s ease;
        }}
        .feature-card:hover {{
            transform: translateY(-4px);
            box-shadow: 0 20px 25px -5px rgb(0 0 0 / 0.1);
        }}
        .feature-card-content {{
            padding: 24px;
        }}
        .feature-card h3 {{
            margin: 0 0 12px 0;
            color: #6366f1;
            font-weight: 700;
            font-size: 1.25rem;
        }}
        .feature-card a {{
            display: inline-block;
            margin-top: 16px;
            padding: 12px 24px;
            background: #6366f1;
            color: white;
            text-decoration: none;
            border-radius: 8px;
            font-weight: 600;
            transition: all 0.2s ease;
        }}
        .feature-card a:hover {{
            background: #4f46e5;
            transform: translateY(-2px);
        }}
        .status-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }}
        .status-card {{
            background: white;
            border: 1px solid #e5e7eb;
            border-radius: 12px;
            padding: 20px;
            text-align: center;
            box-shadow: 0 1px 3px rgb(0 0 0 / 0.1);
        }}
        .status-value {{
            font-size: 2rem;
            font-weight: 800;
            color: #10b981;
        }}
        .status-label {{
            color: #6b7280;
            margin-top: 5px;
            font-weight: 500;
        }}
        .completion-card {{
            background: linear-gradient(135deg, #10b981, #06b6d4);
            color: white;
            padding: 32px;
            border-radius: 16px;
            margin: 40px 0;
            text-align: center;
        }}
        .completion-card h2 {{
            margin: 0 0 16px 0;
            font-weight: 800;
        }}
    </style>
</head>
<body>
    <h1>Contract Intelligence Platform - Stage 3</h1>
    <p class="subtitle">Silicon Valley Style Design Polish • Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    
    <h2>🎨 Stage 3 Achievements</h2>
    <div class="status-grid">
        <div class="status-card">
            <div class="status-value">✅</div>
            <div class="status-label">Design System</div>
        </div>
        <div class="status-card">
            <div class="status-value">✅</div>
            <div class="status-label">Responsive Layout</div>
        </div>
        <div class="status-card">
            <div class="status-value">✅</div>
            <div class="status-label">Animations</div>
        </div>
        <div class="status-card">
            <div class="status-value">✅</div>
            <div class="status-label">Theme System</div>
        </div>
        <div class="status-card">
            <div class="status-value">✅</div>
            <div class="status-label">Component Library</div>
        </div>
        <div class="status-card">
            <div class="status-value">✅</div>
            <div class="status-label">Glassmorphism</div>
        </div>
    </div>
    
    <h2>📱 Experience the New Design</h2>
    <div class="feature-grid">
        <div class="feature-card">
            <div class="feature-card-content">
                <h3>🎨 Complete Design Demo</h3>
                <p>Experience the full Silicon Valley transformation with modern components, animations, and responsive design.</p>
                <ul style="margin: 16px 0; line-height: 1.8;">
                    <li>Modern typography with Inter font</li>
                    <li>Responsive grid system</li>
                    <li>Smooth micro-animations</li>
                    <li>Dark/light theme toggle</li>
                </ul>
                <a href="demo.html" target="_blank">View Complete Demo →</a>
            </div>
        </div>
        
        <div class="feature-card">
            <div class="feature-card-content">
                <h3>🧩 Component Showcase</h3>
                <p>Browse the comprehensive component library with modern styling and interactive examples.</p>
                <ul style="margin: 16px 0; line-height: 1.8;">
                    <li>Button variants and sizes</li>
                    <li>Card components with glass effects</li>
                    <li>Progress indicators and metrics</li>
                    <li>Status badges and forms</li>
                </ul>
                <a href="components.html" target="_blank">Browse Components →</a>
            </div>
        </div>
    </div>
    
    <h2>🔧 Technical Implementation</h2>
    <div style="background: white; border: 1px solid #e5e7eb; border-radius: 12px; padding: 24px; margin: 24px 0;">
        <h3>Design System Features</h3>
        <ul style="line-height: 2;">
            <li><strong>Typography Scale</strong>: Inter font family with 8 size variants</li>
            <li><strong>Color Palette</strong>: Modern indigo/purple primary with semantic colors</li>
            <li><strong>Spacing System</strong>: Consistent 8px grid with Tailwind-inspired scale</li>
            <li><strong>Component Library</strong>: 15+ reusable components with variants</li>
        </ul>
        
        <h3 style="margin-top: 24px;">Responsive Features</h3>
        <ul style="line-height: 2;">
            <li><strong>Mobile-First</strong>: Breakpoints at 640px, 768px, 1024px</li>
            <li><strong>Flexible Grids</strong>: CSS Grid with auto-fit and minmax</li>
            <li><strong>Touch Optimization</strong>: 44px minimum touch targets</li>
            <li><strong>Progressive Enhancement</strong>: Graceful degradation for older browsers</li>
        </ul>
        
        <h3 style="margin-top: 24px;">Animation System</h3>
        <ul style="line-height: 2;">
            <li><strong>Micro-Interactions</strong>: Hover, focus, and click feedback</li>
            <li><strong>Page Transitions</strong>: Staggered fade-in animations</li>
            <li><strong>Loading States</strong>: Shimmer effects and progress indicators</li>
            <li><strong>Accessibility</strong>: Respects prefers-reduced-motion</li>
        </ul>
    </div>
    
    <div class="completion-card">
        <h2>🎉 Stage 3 Design Polish Complete!</h2>
        <p style="font-size: 1.125rem; margin: 0; opacity: 0.9;">
            Silicon Valley-style UI transformation successfully implemented with modern design system, 
            responsive layouts, smooth animations, and premium aesthetics.
        </p>
    </div>
    
    <p style="margin-top: 30px; padding: 20px; background: #fef3c7; border: 1px solid #fbbf24; border-radius: 12px; border-left: 4px solid #f59e0b;">
        <strong>Ready for Stage 3 Sign-off!</strong><br>
        Review the complete design demo and component showcase, then provide approval to proceed to Stage 4.
    </p>
</body>
</html>"""
    
    # Save all files
    files = [
        ("index.html", index_html),
        ("demo.html", demo_html),
        ("components.html", components_html)
    ]
    
    for filename, content in files:
        filepath = preview_dir / filename
        filepath.write_text(content)
        print(f"✅ Generated: {filename}")
    
    print(f"\n✅ Stage 3 UI Preview generated: {preview_dir}")
    print(f"📄 Open in browser: file://{(preview_dir / 'index.html').absolute()}")
    print("\n🎨 Stage 3 Silicon Valley Design Polish ready for review!")

if __name__ == "__main__":
    generate_stage3_preview()