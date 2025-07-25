#!/usr/bin/env python3
"""
Test the pattern scanner to ensure it's working correctly
"""

import subprocess
import json
import sys

def test_pattern_scanner():
    """Run pattern scanner and verify it finds expected vulnerabilities"""
    
    print("Testing pattern scanner...")
    
    # Run the pattern scanner
    result = subprocess.run(
        ["python3", "audit/runners/pattern_scanner.py", "src"],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print(f"Error running pattern scanner: {result.stderr}")
        return False
    
    # Parse the output
    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON output: {e}")
        print(f"Output was: {result.stdout}")
        return False
    
    # Check summary
    summary = data.get('summary', {})
    print(f"\nSummary:")
    print(f"  Critical: {summary.get('critical', 0)}")
    print(f"  High: {summary.get('high', 0)}")
    print(f"  Medium: {summary.get('medium', 0)}")
    print(f"  Low: {summary.get('low', 0)}")
    
    # Verify we found critical issues
    if summary.get('critical', 0) == 0:
        print("\n❌ FAIL: No critical issues found!")
        return False
    
    # Check for specific vulnerabilities
    findings = data.get('findings', [])
    found_types = set()
    
    for finding in findings:
        pattern_id = finding.get('pattern_id', '')
        if 'sql' in pattern_id.lower():
            found_types.add('sql_injection')
        elif 'aws' in pattern_id.lower():
            found_types.add('hardcoded_aws_key')
        elif 'command' in pattern_id.lower():
            found_types.add('command_injection')
        elif 'pickle' in pattern_id.lower():
            found_types.add('pickle_deserialize')
        elif 'path' in pattern_id.lower():
            found_types.add('path_traversal')
    
    print(f"\nFound vulnerability types: {found_types}")
    
    # Check if we found the main vulnerabilities
    expected = {'sql_injection', 'hardcoded_aws_key', 'command_injection', 'pickle_deserialize', 'path_traversal'}
    missing = expected - found_types
    
    if missing:
        print(f"\n⚠️  WARNING: Missing expected vulnerabilities: {missing}")
    
    print("\n✅ Pattern scanner test completed successfully!")
    return True

if __name__ == "__main__":
    success = test_pattern_scanner()
    sys.exit(0 if success else 1)