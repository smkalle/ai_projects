#!/usr/bin/env python3
"""Generate static HTML preview of the UI for review without running Streamlit."""

from pathlib import Path
from datetime import datetime

def generate_ui_preview():
    """Generate static HTML previews of all UI pages."""
    project_root = Path(__file__).parent
    preview_dir = project_root / "ui_preview"
    preview_dir.mkdir(exist_ok=True)
    
    print("🎨 Generating UI Preview...")
    print("=" * 60)
    
    # Common CSS for all pages
    common_css = """
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: #f8fafc;
            color: #1f2937;
        }
        .container {
            display: flex;
            height: 100vh;
        }
        .sidebar {
            width: 300px;
            background: white;
            border-right: 1px solid #e5e7eb;
            padding: 20px;
            overflow-y: auto;
        }
        .main {
            flex: 1;
            padding: 40px;
            overflow-y: auto;
        }
        .app-header {
            background: linear-gradient(90deg, #1e3a8a, #3b82f6);
            color: white;
            padding: 2rem;
            border-radius: 10px;
            margin-bottom: 2rem;
            text-align: center;
        }
        .feature-card {
            background: white;
            border: 1px solid #e5e7eb;
            border-radius: 10px;
            padding: 1.5rem;
            margin: 1rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .feature-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 20px;
            margin: 20px 0;
        }
        .button {
            background: #1e3a8a;
            color: white;
            border: none;
            border-radius: 5px;
            padding: 10px 20px;
            cursor: pointer;
            font-weight: 600;
            margin: 10px 0;
            display: inline-block;
        }
        .button:hover {
            background: #3b82f6;
        }
        .metric {
            text-align: center;
            padding: 10px;
            background: #f8fafc;
            border-radius: 8px;
            margin: 10px 0;
        }
        .metric-value {
            font-size: 24px;
            font-weight: bold;
            color: #1e3a8a;
        }
        .metric-label {
            color: #6b7280;
            font-size: 14px;
        }
        .tabs {
            display: flex;
            border-bottom: 2px solid #e5e7eb;
            margin: 20px 0;
        }
        .tab {
            padding: 10px 20px;
            cursor: pointer;
            border-bottom: 2px solid transparent;
            margin-bottom: -2px;
        }
        .tab.active {
            border-bottom-color: #1e3a8a;
            color: #1e3a8a;
            font-weight: 600;
        }
        .file-upload {
            border: 2px dashed #cbd5e1;
            border-radius: 10px;
            padding: 40px;
            text-align: center;
            background: white;
            margin: 20px 0;
        }
        .info-box {
            background: #dbeafe;
            border-left: 4px solid #3b82f6;
            padding: 1rem;
            border-radius: 0 5px 5px 0;
            margin: 1rem 0;
        }
        .warning-box {
            background: #fef3c7;
            border-left: 4px solid #f59e0b;
            padding: 1rem;
            border-radius: 0 5px 5px 0;
            margin: 1rem 0;
        }
        h1 { font-size: 2.5rem; margin-bottom: 10px; }
        h2 { font-size: 2rem; margin: 20px 0 10px; }
        h3 { font-size: 1.5rem; margin: 15px 0 10px; }
        p { line-height: 1.6; margin: 10px 0; }
    </style>
    """
    
    # Generate Home Page
    home_html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Contract Intelligence Platform - Home</title>
    {common_css}
</head>
<body>
    <div class="container">
        <div class="sidebar">
            <h3>🏠 Navigation</h3>
            <div class="metric">
                <div class="metric-label">Documents</div>
                <div class="metric-value">0</div>
            </div>
            <div class="metric">
                <div class="metric-label">Analyses</div>
                <div class="metric-value">0</div>
            </div>
            <hr style="margin: 20px 0;">
            <h4>⚙️ Features</h4>
            <p>OCR: ✅</p>
            <p>Comparison: ✅</p>
            <p>Redlining: ✅</p>
            <p>Collaboration: ✅</p>
            <hr style="margin: 20px 0;">
            <h4>🔗 Quick Links</h4>
            <p><a href="#">📖 User Guide</a></p>
            <p><a href="#">🎥 Video Tutorials</a></p>
            <p><a href="#">💬 Support</a></p>
        </div>
        <div class="main">
            <div class="app-header">
                <h1>⚖️ Contract Intelligence Platform</h1>
                <p>AI-powered contract analysis, risk assessment, and compliance checking</p>
            </div>
            
            <h2>Welcome to Contract Intelligence Platform</h2>
            <p>Transform your contract review process with AI-powered analysis. Upload contracts, 
            get instant insights, assess risks, and ensure compliance with just a few clicks.</p>
            
            <h3>🚀 Platform Features</h3>
            <div class="feature-grid">
                <div class="feature-card">
                    <div style="font-size: 2.5rem;">📄</div>
                    <h4 style="color: #1e3a8a;">Document Analysis</h4>
                    <p>Upload and analyze contracts instantly. Extract key terms, parties, 
                    dates, and obligations with AI precision.</p>
                    <button class="button">📄 Analyze Document</button>
                </div>
                
                <div class="feature-card">
                    <div style="font-size: 2.5rem;">⚖️</div>
                    <h4 style="color: #1e3a8a;">Risk Assessment</h4>
                    <p>Identify potential risks, liability issues, and compliance gaps 
                    before you sign.</p>
                    <button class="button">⚖️ Assess Risks</button>
                </div>
                
                <div class="feature-card">
                    <div style="font-size: 2.5rem;">🔄</div>
                    <h4 style="color: #1e3a8a;">Contract Comparison</h4>
                    <p>Compare contract versions side-by-side and identify critical 
                    changes and their impact.</p>
                    <button class="button">🔄 Compare Contracts</button>
                </div>
                
                <div class="feature-card">
                    <div style="font-size: 2.5rem;">✏️</div>
                    <h4 style="color: #1e3a8a;">Automated Redlining</h4>
                    <p>Get AI-powered suggestions for contract improvements and 
                    risk mitigation strategies.</p>
                    <button class="button">✏️ Review & Redline</button>
                </div>
                
                <div class="feature-card">
                    <div style="font-size: 2.5rem;">📊</div>
                    <h4 style="color: #1e3a8a;">Analytics Dashboard</h4>
                    <p>View comprehensive analytics and reports on your contract 
                    portfolio and compliance status.</p>
                    <button class="button">📊 View Dashboard</button>
                </div>
                
                <div class="feature-card">
                    <div style="font-size: 2.5rem;">📝</div>
                    <h4 style="color: #1e3a8a;">Generate Reports</h4>
                    <p>Create professional reports for stakeholders with executive 
                    summaries and detailed findings.</p>
                    <button class="button">📝 Generate Report</button>
                </div>
            </div>
        </div>
    </div>
</body>
</html>"""
    
    # Generate Upload Page
    upload_html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Upload Contract - Contract Intelligence</title>
    {common_css}
</head>
<body>
    <div class="container">
        <div class="sidebar">
            <h3>🏠 Navigation</h3>
            <p><a href="home.html">← Back to Home</a></p>
            <hr style="margin: 20px 0;">
            <h4>📊 File Limits</h4>
            <p>Max size: 50MB</p>
            <p>Max pages: 500</p>
            <p>Timeout: 300s</p>
        </div>
        <div class="main">
            <h1>📄 Upload & Analyze Contract</h1>
            <p>Upload your contract documents for AI-powered analysis</p>
            
            <h3>📁 Document Upload</h3>
            <div class="file-upload">
                <p style="font-size: 48px;">📁</p>
                <p>Drag and drop files here</p>
                <p>or</p>
                <button class="button">Browse Files</button>
                <p style="color: #6b7280; font-size: 14px; margin-top: 10px;">
                    Supported formats: PDF, DOCX, DOC, TXT • Max size: 50MB
                </p>
            </div>
            
            <div class="info-box">
                <h4>How to upload contracts:</h4>
                <ol style="margin-left: 20px;">
                    <li>Click the "Browse files" button above</li>
                    <li>Select one or more contract files (PDF, DOCX, DOC, TXT)</li>
                    <li>Files will be automatically uploaded and ready for analysis</li>
                    <li>Click "Analyze" to start AI-powered contract review</li>
                </ol>
            </div>
            
            <h3>📋 Try Sample Contracts</h3>
            <p>Don't have a contract ready? Try our sample documents:</p>
            <div style="display: flex; gap: 10px;">
                <button class="button">📄 Service Agreement Sample</button>
                <button class="button">🤝 NDA Template</button>
                <button class="button">💼 Employment Contract</button>
            </div>
        </div>
    </div>
</body>
</html>"""
    
    # Generate Dashboard Page
    dashboard_html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Analysis Dashboard - Contract Intelligence</title>
    {common_css}
</head>
<body>
    <div class="container">
        <div class="sidebar">
            <h3>🏠 Navigation</h3>
            <p><a href="home.html">← Back to Home</a></p>
            <hr style="margin: 20px 0;">
            <h4>📊 Quick Actions</h4>
            <button class="button" style="width: 100%;">⚖️ Compliance Check</button>
            <button class="button" style="width: 100%;">🔄 Compare</button>
            <button class="button" style="width: 100%;">📝 Report</button>
        </div>
        <div class="main">
            <h1>📊 Analysis Dashboard</h1>
            <p>Comprehensive view of your contract analysis results</p>
            
            <div class="warning-box">
                ⚠️ No contracts uploaded yet. Please upload contracts first.
            </div>
            
            <div class="tabs">
                <div class="tab active">📋 Overview</div>
                <div class="tab">📈 Risk Analysis</div>
                <div class="tab">👥 Parties & Terms</div>
                <div class="tab">📅 Obligations</div>
            </div>
            
            <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin: 20px 0;">
                <div class="metric" style="background: white; border: 1px solid #e5e7eb;">
                    <div class="metric-label">Total Contracts</div>
                    <div class="metric-value">0</div>
                </div>
                <div class="metric" style="background: white; border: 1px solid #e5e7eb;">
                    <div class="metric-label">Analysis Complete</div>
                    <div class="metric-value">0</div>
                </div>
                <div class="metric" style="background: white; border: 1px solid #e5e7eb;">
                    <div class="metric-label">High Risk Issues</div>
                    <div class="metric-value">0</div>
                </div>
                <div class="metric" style="background: white; border: 1px solid #e5e7eb;">
                    <div class="metric-label">Compliance Score</div>
                    <div class="metric-value">N/A</div>
                </div>
            </div>
            
            <h3>📄 Uploaded Contracts</h3>
            <div class="info-box">
                No contracts uploaded yet. Upload contracts to see analysis results here.
            </div>
        </div>
    </div>
</body>
</html>"""
    
    # Save all preview files
    pages = [
        ("home.html", home_html),
        ("upload.html", upload_html),
        ("dashboard.html", dashboard_html)
    ]
    
    for filename, content in pages:
        filepath = preview_dir / filename
        filepath.write_text(content)
        print(f"✅ Generated: {filename}")
    
    # Create index page
    index_html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Contract Intelligence - UI Preview</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 40px 20px;
            background: #f8fafc;
        }}
        h1 {{ color: #1e3a8a; }}
        .preview-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 30px;
            margin-top: 30px;
        }}
        .preview-card {{
            background: white;
            border: 1px solid #e5e7eb;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        .preview-card img {{
            width: 100%;
            height: 250px;
            object-fit: cover;
            border-bottom: 1px solid #e5e7eb;
        }}
        .preview-card-content {{
            padding: 20px;
        }}
        .preview-card h3 {{
            margin: 0 0 10px 0;
            color: #1e3a8a;
        }}
        .preview-card a {{
            display: inline-block;
            margin-top: 10px;
            padding: 8px 16px;
            background: #1e3a8a;
            color: white;
            text-decoration: none;
            border-radius: 5px;
        }}
        .metadata {{
            color: #6b7280;
            margin-bottom: 30px;
        }}
    </style>
</head>
<body>
    <h1>Contract Intelligence Platform - Stage 1 UI Preview</h1>
    <p class="metadata">Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    
    <p>This is a static HTML preview of the UI. Click on each page to view the full layout:</p>
    
    <div class="preview-grid">
        <div class="preview-card">
            <div class="preview-card-content">
                <h3>🏠 Home Page</h3>
                <p>Main landing page with feature cards and navigation</p>
                <a href="home.html" target="_blank">View Page →</a>
            </div>
        </div>
        
        <div class="preview-card">
            <div class="preview-card-content">
                <h3>📄 Upload Contract</h3>
                <p>File upload interface with drag & drop support</p>
                <a href="upload.html" target="_blank">View Page →</a>
            </div>
        </div>
        
        <div class="preview-card">
            <div class="preview-card-content">
                <h3>📊 Analysis Dashboard</h3>
                <p>Contract analysis results and metrics</p>
                <a href="dashboard.html" target="_blank">View Page →</a>
            </div>
        </div>
    </div>
    
    <h2 style="margin-top: 40px;">📋 Stage 1 Sign-off Checklist</h2>
    <ul style="line-height: 2;">
        <li>✅ Professional legal theme with blue color scheme</li>
        <li>✅ Responsive layout with sidebar navigation</li>
        <li>✅ 6 feature cards on home page</li>
        <li>✅ File upload interface with clear instructions</li>
        <li>✅ Dashboard with tabs and metrics</li>
        <li>✅ Consistent styling across all pages</li>
        <li>✅ Clear call-to-action buttons</li>
        <li>✅ Informative placeholder content</li>
    </ul>
    
    <p style="margin-top: 30px; padding: 20px; background: #fef3c7; border: 1px solid #fbbf24; border-radius: 8px;">
        <strong>Note:</strong> This is a static preview. For full interactivity, run the actual Streamlit app with:
        <code style="background: #f3f4f6; padding: 2px 6px; border-radius: 3px;">streamlit run app/main.py</code>
    </p>
</body>
</html>"""
    
    index_path = preview_dir / "index.html"
    index_path.write_text(index_html)
    
    print(f"\n✅ UI Preview generated in: {preview_dir}")
    print(f"📄 Open in browser: file://{index_path.absolute()}")
    print("\n🎉 You can now review the UI without running Streamlit!")

if __name__ == "__main__":
    generate_ui_preview()