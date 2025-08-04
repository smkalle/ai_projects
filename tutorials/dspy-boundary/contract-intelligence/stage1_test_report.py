#!/usr/bin/env python3
"""Generate Stage 1 test report for sign-off."""

import subprocess
import json
import time
from pathlib import Path
from datetime import datetime

def generate_test_report():
    """Generate comprehensive test report for Stage 1."""
    project_root = Path(__file__).parent
    report_dir = project_root / "test_reports"
    report_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = report_dir / f"stage1_report_{timestamp}.html"
    
    print("📊 Generating Stage 1 Test Report...")
    print("=" * 60)
    
    # Run tests and capture results
    test_results = {}
    
    # Unit tests
    print("\n🧪 Running unit tests...")
    unit_result = subprocess.run(
        ["pytest", "tests/unit", "-v", "--tb=short", "--json-report", "--json-report-file=unit_report.json"],
        capture_output=True,
        text=True
    )
    test_results["unit"] = {
        "passed": unit_result.returncode == 0,
        "output": unit_result.stdout,
        "errors": unit_result.stderr
    }
    
    # Integration tests
    print("🔗 Running integration tests...")
    integration_result = subprocess.run(
        ["pytest", "tests/integration", "-v", "--tb=short", "--json-report", "--json-report-file=integration_report.json"],
        capture_output=True,
        text=True
    )
    test_results["integration"] = {
        "passed": integration_result.returncode == 0,
        "output": integration_result.stdout,
        "errors": integration_result.stderr
    }
    
    # Smoke tests
    print("🔥 Running smoke tests...")
    smoke_result = subprocess.run(
        ["pytest", "tests/smoke", "-v", "--tb=short", "--json-report", "--json-report-file=smoke_report.json"],
        capture_output=True,
        text=True
    )
    test_results["smoke"] = {
        "passed": smoke_result.returncode == 0,
        "output": smoke_result.stdout,
        "errors": smoke_result.stderr
    }
    
    # Generate HTML report
    html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Stage 1 Test Report - Contract Intelligence Platform</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            background: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #1e3a8a;
            margin-bottom: 10px;
        }}
        .metadata {{
            color: #666;
            margin-bottom: 30px;
        }}
        .summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .summary-card {{
            border: 1px solid #e5e7eb;
            border-radius: 8px;
            padding: 20px;
            text-align: center;
        }}
        .summary-card.passed {{
            border-color: #10b981;
            background: #f0fdf4;
        }}
        .summary-card.failed {{
            border-color: #ef4444;
            background: #fef2f2;
        }}
        .test-section {{
            margin-bottom: 30px;
            border: 1px solid #e5e7eb;
            border-radius: 8px;
            overflow: hidden;
        }}
        .test-header {{
            background: #f8fafc;
            padding: 15px 20px;
            border-bottom: 1px solid #e5e7eb;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .test-header.passed {{
            border-left: 4px solid #10b981;
        }}
        .test-header.failed {{
            border-left: 4px solid #ef4444;
        }}
        .test-content {{
            padding: 20px;
        }}
        .status-badge {{
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 14px;
            font-weight: 500;
        }}
        .status-badge.passed {{
            background: #10b981;
            color: white;
        }}
        .status-badge.failed {{
            background: #ef4444;
            color: white;
        }}
        pre {{
            background: #f8fafc;
            border: 1px solid #e5e7eb;
            border-radius: 4px;
            padding: 15px;
            overflow-x: auto;
            font-size: 13px;
            line-height: 1.5;
        }}
        .checklist {{
            background: #f8fafc;
            border-radius: 8px;
            padding: 20px;
            margin-top: 30px;
        }}
        .checklist h3 {{
            margin-top: 0;
            color: #1e3a8a;
        }}
        .checklist-item {{
            display: flex;
            align-items: center;
            margin: 10px 0;
        }}
        .checkbox {{
            width: 20px;
            height: 20px;
            border: 2px solid #cbd5e1;
            border-radius: 4px;
            margin-right: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        .checkbox.checked {{
            background: #10b981;
            border-color: #10b981;
        }}
        .checkbox.checked::after {{
            content: '✓';
            color: white;
            font-weight: bold;
        }}
        .sign-off {{
            background: #fef3c7;
            border: 1px solid #fbbf24;
            border-radius: 8px;
            padding: 20px;
            margin-top: 30px;
        }}
        .sign-off h3 {{
            margin-top: 0;
            color: #92400e;
        }}
        .sign-off-field {{
            margin: 15px 0;
            display: flex;
            align-items: center;
        }}
        .sign-off-field label {{
            font-weight: 500;
            margin-right: 10px;
            min-width: 100px;
        }}
        .sign-off-field input {{
            border: 1px solid #d1d5db;
            border-radius: 4px;
            padding: 5px 10px;
            flex: 1;
            max-width: 300px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Stage 1 Test Report - Contract Intelligence Platform</h1>
        <div class="metadata">
            Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br>
            Stage: Foundation & Basic UI
        </div>
        
        <div class="summary">
            <div class="summary-card {'passed' if test_results['unit']['passed'] else 'failed'}">
                <h3>Unit Tests</h3>
                <div class="status-badge {'passed' if test_results['unit']['passed'] else 'failed'}">
                    {'PASSED' if test_results['unit']['passed'] else 'FAILED'}
                </div>
            </div>
            <div class="summary-card {'passed' if test_results['integration']['passed'] else 'failed'}">
                <h3>Integration Tests</h3>
                <div class="status-badge {'passed' if test_results['integration']['passed'] else 'failed'}">
                    {'PASSED' if test_results['integration']['passed'] else 'FAILED'}
                </div>
            </div>
            <div class="summary-card {'passed' if test_results['smoke']['passed'] else 'failed'}">
                <h3>Smoke Tests</h3>
                <div class="status-badge {'passed' if test_results['smoke']['passed'] else 'failed'}">
                    {'PASSED' if test_results['smoke']['passed'] else 'FAILED'}
                </div>
            </div>
        </div>
"""
    
    # Add test details
    for test_type, results in test_results.items():
        status_class = 'passed' if results['passed'] else 'failed'
        html_content += f"""
        <div class="test-section">
            <div class="test-header {status_class}">
                <h3>{test_type.title()} Tests</h3>
                <div class="status-badge {status_class}">
                    {'PASSED' if results['passed'] else 'FAILED'}
                </div>
            </div>
            <div class="test-content">
                <h4>Output:</h4>
                <pre>{results['output'][:2000]}...</pre>
                {f"<h4>Errors:</h4><pre>{results['errors']}</pre>" if results['errors'] else ""}
            </div>
        </div>
"""
    
    # Add checklist
    all_passed = all(r['passed'] for r in test_results.values())
    html_content += f"""
        <div class="checklist">
            <h3>Stage 1 Completion Checklist</h3>
            <div class="checklist-item">
                <div class="checkbox checked"></div>
                Project structure created
            </div>
            <div class="checklist-item">
                <div class="checkbox checked"></div>
                Configuration files in place
            </div>
            <div class="checklist-item">
                <div class="checkbox checked"></div>
                Basic Streamlit app with navigation
            </div>
            <div class="checklist-item">
                <div class="checkbox checked"></div>
                All 5 placeholder pages created
            </div>
            <div class="checklist-item">
                <div class="checkbox {'checked' if test_results['unit']['passed'] else ''}"></div>
                Unit tests passing
            </div>
            <div class="checklist-item">
                <div class="checkbox {'checked' if test_results['integration']['passed'] else ''}"></div>
                Integration tests passing
            </div>
            <div class="checklist-item">
                <div class="checkbox {'checked' if test_results['smoke']['passed'] else ''}"></div>
                Smoke tests passing (no mocks)
            </div>
            <div class="checklist-item">
                <div class="checkbox"></div>
                UI screenshots captured for review
            </div>
        </div>
        
        <div class="sign-off">
            <h3>Stage 1 Sign-off</h3>
            <p>By signing below, you confirm that Stage 1 has been completed successfully and meets all requirements.</p>
            
            <div class="sign-off-field">
                <label>Reviewer:</label>
                <input type="text" placeholder="Your name">
            </div>
            <div class="sign-off-field">
                <label>Date:</label>
                <input type="date" value="{datetime.now().strftime('%Y-%m-%d')}">
            </div>
            <div class="sign-off-field">
                <label>Status:</label>
                <select>
                    <option>Pending Review</option>
                    <option {'selected' if all_passed else ''}>Approved</option>
                    <option>Needs Revision</option>
                </select>
            </div>
            <div class="sign-off-field">
                <label>Comments:</label>
                <textarea style="flex: 1; max-width: 500px; height: 60px; border: 1px solid #d1d5db; border-radius: 4px; padding: 5px 10px;"></textarea>
            </div>
        </div>
    </div>
</body>
</html>
"""
    
    # Save report
    report_file.write_text(html_content)
    
    print(f"\n✅ Test report generated: {report_file}")
    print(f"📄 Open in browser: file://{report_file.absolute()}")
    
    return str(report_file)

if __name__ == "__main__":
    generate_test_report()