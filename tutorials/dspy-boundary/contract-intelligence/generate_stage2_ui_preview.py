#!/usr/bin/env python3
"""Generate Stage 2 UI preview showing upload functionality."""

from pathlib import Path
from datetime import datetime

def generate_stage2_preview():
    """Generate Stage 2 UI preview with upload functionality."""
    project_root = Path(__file__).parent
    preview_dir = project_root / "ui_preview_stage2"
    preview_dir.mkdir(exist_ok=True)
    
    print("🎨 Generating Stage 2 UI Preview...")
    print("=" * 60)
    
    # Common CSS
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
        .button {
            background: #1e3a8a;
            color: white;
            border: none;
            border-radius: 5px;
            padding: 10px 20px;
            cursor: pointer;
            font-weight: 600;
            margin: 10px 5px;
            display: inline-block;
            text-decoration: none;
        }
        .button:hover { background: #3b82f6; }
        .button.primary { background: #059669; }
        .button.secondary { background: #6b7280; }
        
        .file-upload {
            border: 2px dashed #cbd5e1;
            border-radius: 10px;
            padding: 40px;
            text-align: center;
            background: white;
            margin: 20px 0;
            transition: border-color 0.2s;
        }
        .file-upload:hover { border-color: #3b82f6; }
        
        .file-card {
            background: white;
            border: 1px solid #e5e7eb;
            border-radius: 8px;
            padding: 15px;
            margin: 10px 0;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }
        
        .file-info {
            display: flex;
            align-items: center;
            gap: 15px;
        }
        
        .file-icon {
            width: 40px;
            height: 40px;
            background: #dbeafe;
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 18px;
        }
        
        .file-details h4 {
            margin: 0 0 5px 0;
            color: #1f2937;
        }
        
        .file-details p {
            margin: 0;
            color: #6b7280;
            font-size: 14px;
        }
        
        .status-badge {
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: 500;
        }
        .status-valid { background: #d1fae5; color: #065f46; }
        .status-processing { background: #fef3c7; color: #92400e; }
        .status-completed { background: #dbeafe; color: #1e40af; }
        .status-error { background: #fee2e2; color: #991b1b; }
        
        .progress-bar {
            width: 100%;
            height: 8px;
            background: #e5e7eb;
            border-radius: 4px;
            overflow: hidden;
            margin: 10px 0;
        }
        .progress-fill {
            height: 100%;
            background: #059669;
            border-radius: 4px;
            transition: width 0.3s ease;
        }
        
        .metadata-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }
        
        .metadata-item {
            background: #f8fafc;
            padding: 10px;
            border-radius: 6px;
            border-left: 3px solid #3b82f6;
        }
        
        .metadata-item h5 {
            margin: 0 0 5px 0;
            color: #374151;
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .metadata-item p {
            margin: 0;
            color: #1f2937;
            font-weight: 500;
        }
        
        .preview-area {
            background: white;
            border: 1px solid #e5e7eb;
            border-radius: 8px;
            padding: 20px;
            margin: 20px 0;
            font-family: 'Courier New', monospace;
            font-size: 14px;
            line-height: 1.5;
            max-height: 300px;
            overflow-y: auto;
        }
        
        h1 { color: #1e3a8a; margin-bottom: 10px; }
        h2 { color: #374151; margin: 20px 0 10px; }
        h3 { color: #4b5563; margin: 15px 0 10px; }
    </style>
    """
    
    # Upload page with file processing
    upload_html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Upload Contract - Stage 2 Demo</title>
    {common_css}
</head>
<body>
    <div class="container">
        <div class="sidebar">
            <h3>🏠 Navigation</h3>
            <a href="index.html" class="button" style="width: 90%;">← Back to Overview</a>
            <hr style="margin: 20px 0;">
            
            <h4>📊 Upload Stats</h4>
            <div class="metadata-item">
                <h5>Files Uploaded</h5>
                <p>3 documents</p>
            </div>
            <div class="metadata-item">
                <h5>Total Size</h5>
                <p>2.4 MB</p>
            </div>
            <div class="metadata-item">
                <h5>Success Rate</h5>
                <p>100%</p>
            </div>
        </div>
        
        <div class="main">
            <h1>📄 Upload & Analyze Contract</h1>
            <p>Upload your contract documents for AI-powered analysis</p>
            
            <h2>📁 Document Upload</h2>
            <div class="file-upload">
                <p style="font-size: 48px; margin-bottom: 10px;">📁</p>
                <h3>Drag and drop files here</h3>
                <p style="margin: 10px 0;">or</p>
                <button class="button primary">Browse Files</button>
                <p style="color: #6b7280; margin-top: 15px;">
                    Supported: PDF, DOCX, DOC, TXT • Max size: 50MB
                </p>
            </div>
            
            <h2>📋 Processing Queue</h2>
            <div class="file-card">
                <div class="file-info">
                    <div class="file-icon">📄</div>
                    <div class="file-details">
                        <h4>service_agreement.pdf</h4>
                        <p>2.1 MB • PDF Document</p>
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: 100%"></div>
                        </div>
                    </div>
                </div>
                <div>
                    <span class="status-badge status-completed">✅ Completed</span>
                    <button class="button secondary">👁️ View</button>
                </div>
            </div>
            
            <div class="file-card">
                <div class="file-info">
                    <div class="file-icon">📄</div>
                    <div class="file-details">
                        <h4>nda_template.docx</h4>
                        <p>245 KB • Word Document</p>
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: 75%"></div>
                        </div>
                    </div>
                </div>
                <div>
                    <span class="status-badge status-processing">⏳ Processing</span>
                    <button class="button secondary">⏹️ Cancel</button>
                </div>
            </div>
            
            <div class="file-card">
                <div class="file-info">
                    <div class="file-icon">📄</div>
                    <div class="file-details">
                        <h4>employment_contract.txt</h4>
                        <p>89 KB • Text Document</p>
                    </div>
                </div>
                <div>
                    <span class="status-badge status-valid">📋 Queued</span>
                    <button class="button">🚀 Process</button>
                </div>
            </div>
            
            <h2>📊 Document Analysis</h2>
            <div style="background: white; border: 1px solid #e5e7eb; border-radius: 8px; padding: 20px;">
                <h3>📄 service_agreement.pdf - Analysis Complete</h3>
                
                <div class="metadata-grid">
                    <div class="metadata-item">
                        <h5>Document Type</h5>
                        <p>Service Agreement</p>
                    </div>
                    <div class="metadata-item">
                        <h5>Pages</h5>
                        <p>8 pages</p>
                    </div>
                    <div class="metadata-item">
                        <h5>Confidence</h5>
                        <p>98.5%</p>
                    </div>
                    <div class="metadata-item">
                        <h5>Parsing Method</h5>
                        <p>Direct Text</p>
                    </div>
                    <div class="metadata-item">
                        <h5>Parties Detected</h5>
                        <p>2 parties</p>
                    </div>
                    <div class="metadata-item">
                        <h5>Processing Time</h5>
                        <p>2.3 seconds</p>
                    </div>
                </div>
                
                <h4>📖 Content Preview:</h4>
                <div class="preview-area">
SERVICE AGREEMENT

This Service Agreement ("Agreement") is entered into on August 3, 2025,
between Contract Intelligence Platform Inc. ("Company") and Test Client Corp. ("Client").

ARTICLE 1 - PARTIES

1.1 Company Information:
    Name: Contract Intelligence Platform Inc.
    Address: 123 AI Street, Tech City, TC 12345
    Email: legal@contractintelligence.com

1.2 Client Information:
    Name: Test Client Corp.
    Address: 456 Business Ave, Commerce City, CC 67890
    Email: contracts@testclient.com

ARTICLE 2 - SERVICES

2.1 Service Description:
The Company agrees to provide AI-powered contract analysis services including:
a) Document parsing and content extraction
b) Risk assessment and compliance checking
c) Contract comparison and change detection...

[Content continues...]
                </div>
                
                <div style="margin-top: 20px;">
                    <button class="button primary">📊 Full Analysis</button>
                    <button class="button">⚖️ Compliance Check</button>
                    <button class="button">📥 Download</button>
                    <button class="button secondary">🗑️ Delete</button>
                </div>
            </div>
        </div>
    </div>
</body>
</html>"""
    
    # Processing demo page
    processing_html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Document Processing Demo - Stage 2</title>
    {common_css}
</head>
<body>
    <div class="container">
        <div class="sidebar">
            <h3>🔄 Processing</h3>
            <a href="upload.html" class="button" style="width: 90%;">← Back to Upload</a>
            <hr style="margin: 20px 0;">
            
            <h4>⏱️ Processing Stats</h4>
            <div class="metadata-item">
                <h5>Current Job</h5>
                <p>nda_template.docx</p>
            </div>
            <div class="metadata-item">
                <h5>Progress</h5>
                <p>75% complete</p>
            </div>
            <div class="metadata-item">
                <h5>ETA</h5>
                <p>30 seconds</p>
            </div>
        </div>
        
        <div class="main">
            <h1>🔄 Document Processing</h1>
            <p>Real-time processing of uploaded documents</p>
            
            <h2>📊 Current Processing Job</h2>
            <div style="background: white; border: 1px solid #e5e7eb; border-radius: 8px; padding: 20px;">
                <div class="file-card" style="border: none; padding: 0;">
                    <div class="file-info">
                        <div class="file-icon">📄</div>
                        <div class="file-details">
                            <h4>nda_template.docx</h4>
                            <p>245 KB • Microsoft Word Document</p>
                        </div>
                    </div>
                    <span class="status-badge status-processing">⏳ Processing</span>
                </div>
                
                <h3 style="margin: 20px 0 10px;">Processing Steps:</h3>
                
                <div style="margin: 15px 0;">
                    <div style="display: flex; align-items: center; margin: 8px 0;">
                        <span style="color: #059669; margin-right: 10px;">✅</span>
                        <span>File validation and virus scan</span>
                    </div>
                    <div style="display: flex; align-items: center; margin: 8px 0;">
                        <span style="color: #059669; margin-right: 10px;">✅</span>
                        <span>Document format detection</span>
                    </div>
                    <div style="display: flex; align-items: center; margin: 8px 0;">
                        <span style="color: #059669; margin-right: 10px;">✅</span>
                        <span>Text extraction from DOCX</span>
                    </div>
                    <div style="display: flex; align-items: center; margin: 8px 0;">
                        <span style="color: #f59e0b; margin-right: 10px;">⏳</span>
                        <span><strong>Metadata extraction and analysis</strong></span>
                    </div>
                    <div style="display: flex; align-items: center; margin: 8px 0;">
                        <span style="color: #6b7280; margin-right: 10px;">⭕</span>
                        <span style="color: #6b7280;">Content parsing and structuring</span>
                    </div>
                    <div style="display: flex; align-items: center; margin: 8px 0;">
                        <span style="color: #6b7280; margin-right: 10px;">⭕</span>
                        <span style="color: #6b7280;">Final validation and storage</span>
                    </div>
                </div>
                
                <div class="progress-bar" style="margin: 20px 0;">
                    <div class="progress-fill" style="width: 75%"></div>
                </div>
                <p style="text-align: center; color: #6b7280;">75% Complete - Estimated 30 seconds remaining</p>
            </div>
            
            <h2>📋 Processing Queue</h2>
            <div style="background: white; border: 1px solid #e5e7eb; border-radius: 8px; padding: 20px;">
                <h4>Next in Queue:</h4>
                <div class="file-card" style="border: 1px solid #e5e7eb;">
                    <div class="file-info">
                        <div class="file-icon">📄</div>
                        <div class="file-details">
                            <h4>employment_contract.txt</h4>
                            <p>89 KB • Text Document</p>
                        </div>
                    </div>
                    <span class="status-badge status-valid">📋 Queued</span>
                </div>
                
                <h4 style="margin-top: 20px;">Recently Completed:</h4>
                <div class="file-card" style="border: 1px solid #e5e7eb;">
                    <div class="file-info">
                        <div class="file-icon">📄</div>
                        <div class="file-details">
                            <h4>service_agreement.pdf</h4>
                            <p>2.1 MB • PDF Document</p>
                        </div>
                    </div>
                    <span class="status-badge status-completed">✅ Completed</span>
                </div>
            </div>
            
            <h2>🛠️ Processing Features</h2>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px;">
                <div style="background: white; border: 1px solid #e5e7eb; border-radius: 8px; padding: 20px;">
                    <h4>📄 Multi-Format Support</h4>
                    <p>Supports PDF, DOCX, DOC, and TXT files with intelligent format detection.</p>
                </div>
                <div style="background: white; border: 1px solid #e5e7eb; border-radius: 8px; padding: 20px;">
                    <h4>🔍 OCR Processing</h4>
                    <p>Automatic OCR for scanned documents when text extraction fails.</p>
                </div>
                <div style="background: white; border: 1px solid #e5e7eb; border-radius: 8px; padding: 20px;">
                    <h4>⚡ Fast Processing</h4>
                    <p>Optimized processing pipeline with sub-30 second turnaround.</p>
                </div>
                <div style="background: white; border: 1px solid #e5e7eb; border-radius: 8px; padding: 20px;">
                    <h4>🔒 Secure Storage</h4>
                    <p>Encrypted storage with automatic backup and deduplication.</p>
                </div>
            </div>
        </div>
    </div>
</body>
</html>"""
    
    # Create index page
    index_html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Stage 2 - Document Upload & Display</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 40px 20px;
            background: #f8fafc;
        }}
        h1 {{ color: #1e3a8a; }}
        .feature-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 30px;
            margin-top: 30px;
        }}
        .feature-card {{
            background: white;
            border: 1px solid #e5e7eb;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        .feature-card-content {{
            padding: 20px;
        }}
        .feature-card h3 {{
            margin: 0 0 10px 0;
            color: #1e3a8a;
        }}
        .feature-card a {{
            display: inline-block;
            margin-top: 15px;
            padding: 10px 20px;
            background: #1e3a8a;
            color: white;
            text-decoration: none;
            border-radius: 5px;
            font-weight: 600;
        }}
        .feature-card a:hover {{
            background: #3b82f6;
        }}
        .status-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }}
        .status-card {{
            background: white;
            border: 1px solid #e5e7eb;
            border-radius: 8px;
            padding: 20px;
            text-align: center;
        }}
        .status-value {{
            font-size: 2rem;
            font-weight: bold;
            color: #059669;
        }}
        .status-label {{
            color: #6b7280;
            margin-top: 5px;
        }}
        .metadata {{
            color: #6b7280;
            margin-bottom: 30px;
        }}
    </style>
</head>
<body>
    <h1>Contract Intelligence Platform - Stage 2</h1>
    <p class="metadata">Document Upload & Display • Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    
    <h2>🎯 Stage 2 Features Implemented</h2>
    <div class="status-grid">
        <div class="status-card">
            <div class="status-value">✅</div>
            <div class="status-label">File Upload</div>
        </div>
        <div class="status-card">
            <div class="status-value">✅</div>
            <div class="status-label">Document Parsing</div>
        </div>
        <div class="status-card">
            <div class="status-value">✅</div>
            <div class="status-label">OCR Support</div>
        </div>
        <div class="status-card">
            <div class="status-value">✅</div>
            <div class="status-label">Storage Service</div>
        </div>
        <div class="status-card">
            <div class="status-value">✅</div>
            <div class="status-label">Metadata Display</div>
        </div>
        <div class="status-card">
            <div class="status-value">✅</div>
            <div class="status-label">Testing Suite</div>
        </div>
    </div>
    
    <h2>📱 UI Demos</h2>
    <div class="feature-grid">
        <div class="feature-card">
            <div class="feature-card-content">
                <h3>📄 File Upload Interface</h3>
                <p>Interactive file upload with drag & drop, validation, and real-time processing status.</p>
                <ul>
                    <li>Multi-file upload support</li>
                    <li>Real-time validation</li>
                    <li>Progress tracking</li>
                    <li>Error handling</li>
                </ul>
                <a href="upload.html" target="_blank">View Upload Demo →</a>
            </div>
        </div>
        
        <div class="feature-card">
            <div class="feature-card-content">
                <h3>🔄 Document Processing</h3>
                <p>Real-time document processing pipeline with step-by-step progress tracking.</p>
                <ul>
                    <li>Processing queue</li>
                    <li>Step-by-step progress</li>
                    <li>ETA calculations</li>
                    <li>Error recovery</li>
                </ul>
                <a href="processing.html" target="_blank">View Processing Demo →</a>
            </div>
        </div>
    </div>
    
    <h2>🔧 Technical Implementation</h2>
    <div style="background: white; border: 1px solid #e5e7eb; border-radius: 8px; padding: 20px; margin: 20px 0;">
        <h3>Backend Services</h3>
        <ul style="line-height: 2;">
            <li><strong>Document Parser Service</strong>: PDF, DOCX, TXT parsing with OCR fallback</li>
            <li><strong>Storage Service</strong>: Secure file storage with deduplication</li>
            <li><strong>Validation Engine</strong>: File type, size, and content validation</li>
            <li><strong>Metadata Extraction</strong>: Automatic document metadata parsing</li>
        </ul>
        
        <h3 style="margin-top: 20px;">Frontend Features</h3>
        <ul style="line-height: 2;">
            <li><strong>Drag & Drop Upload</strong>: Modern file upload interface</li>
            <li><strong>Real-time Processing</strong>: Live progress and status updates</li>
            <li><strong>Content Preview</strong>: Text and metadata preview</li>
            <li><strong>Error Handling</strong>: User-friendly error messages</li>
        </ul>
    </div>
    
    <h2>📋 Stage 2 Completion Checklist</h2>
    <div style="background: #f0fdf4; border: 1px solid #22c55e; border-radius: 8px; padding: 20px;">
        <ul style="line-height: 2;">
            <li>✅ File upload component with validation</li>
            <li>✅ Document parser service (PDF, DOCX, TXT)</li>
            <li>✅ OCR support for scanned documents</li>
            <li>✅ Document preview and metadata display</li>
            <li>✅ Storage service with deduplication</li>
            <li>✅ Unit tests for all services</li>
            <li>✅ Integration tests for upload workflow</li>
            <li>✅ Smoke tests with real documents</li>
            <li>✅ UI demonstrations ready for review</li>
        </ul>
    </div>
    
    <p style="margin-top: 30px; padding: 20px; background: #fef3c7; border: 1px solid #fbbf24; border-radius: 8px;">
        <strong>Ready for Stage 2 Sign-off!</strong><br>
        Review the upload and processing demos, then provide approval to proceed to Stage 3.
    </p>
</body>
</html>"""
    
    # Save all files
    files = [
        ("index.html", index_html),
        ("upload.html", upload_html),
        ("processing.html", processing_html)
    ]
    
    for filename, content in files:
        filepath = preview_dir / filename
        filepath.write_text(content)
        print(f"✅ Generated: {filename}")
    
    print(f"\n✅ Stage 2 UI Preview generated: {preview_dir}")
    print(f"📄 Open in browser: file://{(preview_dir / 'index.html').absolute()}")
    print("\n🎉 Stage 2 UI ready for review!")

if __name__ == "__main__":
    generate_stage2_preview()