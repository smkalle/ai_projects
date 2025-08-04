#!/usr/bin/env python3
"""Capture screenshots of the UI for visual sign-off."""

import subprocess
import time
import os
from pathlib import Path
from datetime import datetime

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
except ImportError:
    print("❌ Selenium not installed. Installing...")
    subprocess.run(["pip", "install", "selenium"])
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options

def capture_screenshots():
    """Capture screenshots of all app pages."""
    project_root = Path(__file__).parent
    screenshots_dir = project_root / "screenshots"
    screenshots_dir.mkdir(exist_ok=True)
    
    # Create timestamped subdirectory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    session_dir = screenshots_dir / f"stage1_{timestamp}"
    session_dir.mkdir(exist_ok=True)
    
    print("📸 Contract Intelligence Platform - UI Screenshot Capture")
    print("=" * 60)
    
    # Start Streamlit app
    print("🚀 Starting Streamlit app...")
    app_process = subprocess.Popen(
        ["streamlit", "run", "app/main.py", "--server.headless", "true", "--server.port", "8504"],
        cwd=project_root,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Wait for app to start
    time.sleep(5)
    
    # Setup Chrome driver (headless)
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    
    try:
        # Try to use Chrome
        driver = webdriver.Chrome(options=chrome_options)
    except:
        print("⚠️ Chrome driver not found. Please install ChromeDriver.")
        print("Visit: https://chromedriver.chromium.org/")
        app_process.terminate()
        return
    
    pages = [
        ("home", "http://localhost:8504", "Contract Intelligence Platform"),
        ("upload", "http://localhost:8504/1_📄_Upload_Contract", "Upload Contract"),
        ("dashboard", "http://localhost:8504/2_📊_Analysis_Dashboard", "Analysis Dashboard"),
        ("compliance", "http://localhost:8504/3_⚖️_Compliance_Check", "Compliance Check"),
        ("compare", "http://localhost:8504/4_🔄_Compare_Contracts", "Compare Contracts"),
        ("reports", "http://localhost:8504/5_📝_Reports", "Reports")
    ]
    
    screenshots_captured = []
    
    for page_name, url, expected_title in pages:
        try:
            print(f"\n📄 Capturing {page_name} page...")
            driver.get(url)
            
            # Wait for page to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            time.sleep(2)  # Extra wait for rendering
            
            # Take screenshot
            screenshot_path = session_dir / f"{page_name}.png"
            driver.save_screenshot(str(screenshot_path))
            
            print(f"✅ Saved: {screenshot_path.name}")
            screenshots_captured.append(screenshot_path)
            
        except Exception as e:
            print(f"❌ Error capturing {page_name}: {e}")
    
    # Cleanup
    driver.quit()
    app_process.terminate()
    app_process.wait()
    
    # Create summary HTML
    print("\n📝 Creating summary report...")
    summary_html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Stage 1 - UI Screenshots</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1 {{ color: #1e3a8a; }}
        .screenshot {{ margin: 20px 0; border: 1px solid #ddd; padding: 10px; }}
        img {{ max-width: 100%; height: auto; }}
        .metadata {{ color: #666; font-size: 14px; }}
    </style>
</head>
<body>
    <h1>Contract Intelligence Platform - Stage 1 UI Screenshots</h1>
    <p class="metadata">Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    
    <h2>Screenshots for Visual Sign-off</h2>
"""
    
    for screenshot in screenshots_captured:
        summary_html += f"""
    <div class="screenshot">
        <h3>{screenshot.stem.title()}</h3>
        <img src="{screenshot.name}" alt="{screenshot.stem}">
    </div>
"""
    
    summary_html += """
</body>
</html>
"""
    
    summary_path = session_dir / "index.html"
    summary_path.write_text(summary_html)
    
    print(f"\n✅ Screenshots saved to: {session_dir}")
    print(f"📄 View summary at: {summary_path}")
    print("\n🎉 Screenshot capture complete!")
    
    return str(session_dir)

if __name__ == "__main__":
    capture_screenshots()