#!/usr/bin/env python3
"""Run Stage 2 tests and generate UI preview."""

import subprocess
import sys
import os
from pathlib import Path

def run_stage2_tests():
    """Run all Stage 2 tests."""
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    print("🧪 Stage 2 - Document Upload & Display Tests")
    print("=" * 60)
    
    test_suites = [
        ("Unit Tests - Document Parser", "pytest tests/unit/test_document_parser.py -v"),
        ("Unit Tests - Storage Service", "pytest tests/unit/test_storage_service.py -v"),
        ("Integration Tests - File Upload", "pytest tests/integration/test_file_upload_workflow.py -v"),
        ("Smoke Tests - Document Processing", "pytest tests/smoke/test_document_processing.py -v"),
    ]
    
    results = []
    
    for suite_name, command in test_suites:
        print(f"\n📋 Running {suite_name}...")
        print("-" * 40)
        
        result = subprocess.run(
            command.split(),
            capture_output=False,
            text=True
        )
        
        results.append({
            "suite": suite_name,
            "passed": result.returncode == 0
        })
        
        if result.returncode == 0:
            print(f"✅ {suite_name} PASSED")
        else:
            print(f"❌ {suite_name} FAILED")
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Stage 2 Test Summary:")
    print("-" * 40)
    
    all_passed = True
    for result in results:
        status = "✅ PASSED" if result["passed"] else "❌ FAILED"
        print(f"{result['suite']}: {status}")
        if not result["passed"]:
            all_passed = False
    
    print("=" * 60)
    
    if all_passed:
        print("🎉 All Stage 2 tests passed!")
        print("\n📱 Stage 2 Ready for UI Review!")
        print("Run: python3 generate_stage2_ui_preview.py")
        return 0
    else:
        print("❌ Some Stage 2 tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(run_stage2_tests())