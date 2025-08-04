#!/usr/bin/env python3
"""Test runner for Contract Intelligence Platform."""

import subprocess
import sys
import os
from pathlib import Path

def run_tests():
    """Run all test suites."""
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    print("🧪 Contract Intelligence Platform - Test Suite")
    print("=" * 60)
    
    test_suites = [
        ("Unit Tests", "pytest tests/unit -v"),
        ("Integration Tests", "pytest tests/integration -v"),
        ("Smoke Tests", "pytest tests/smoke -v"),
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
    print("📊 Test Summary:")
    print("-" * 40)
    
    all_passed = True
    for result in results:
        status = "✅ PASSED" if result["passed"] else "❌ FAILED"
        print(f"{result['suite']}: {status}")
        if not result["passed"]:
            all_passed = False
    
    print("=" * 60)
    
    if all_passed:
        print("🎉 All tests passed!")
        return 0
    else:
        print("❌ Some tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(run_tests())