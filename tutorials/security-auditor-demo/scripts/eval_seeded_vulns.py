#!/usr/bin/env python3
"""
Evaluation script for security auditor
Tests the auditor's ability to find known vulnerabilities
"""

import json
import glob
import os
import sys
from typing import Dict, List, Tuple
from collections import defaultdict

# Expected vulnerabilities in our test code
EXPECTED_VULNS = {
    "sql_injection": {
        "count": 1,
        "severity": "high",
        "file": "src/vulnerable.py",
        "description": "SQL injection in login function"
    },
    "hardcoded_secret": {
        "count": 2,  # API_KEY and SECRET_KEY
        "severity": "critical",
        "file": "src/vulnerable.py",
        "description": "Hardcoded AWS key and secret"
    },
    "command_injection": {
        "count": 1,
        "severity": "critical",
        "file": "src/vulnerable.py",
        "description": "Command injection in search endpoint"
    },
    "insecure_deserialization": {
        "count": 1,
        "severity": "high",
        "file": "src/vulnerable.py",
        "description": "Pickle deserialization vulnerability"
    },
    "path_traversal": {
        "count": 1,
        "severity": "high",
        "file": "src/vulnerable.py",
        "description": "Path traversal in download endpoint"
    },
    "weak_crypto": {
        "count": 1,
        "severity": "medium",
        "file": "src/vulnerable.py",
        "description": "MD5 hash usage"
    },
    "cors_misconfiguration": {
        "count": 1,
        "severity": "medium",
        "file": "src/vulnerable.py",
        "description": "CORS wildcard configuration"
    }
}

def load_audit_results(report_path: str) -> Dict:
    """Load audit results from JSON report"""
    try:
        with open(report_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading report {report_path}: {e}")
        return {"findings": [], "summary": {}}

def categorize_findings(findings: List[Dict]) -> Dict[str, List[Dict]]:
    """Categorize findings by vulnerability type"""
    categorized = defaultdict(list)
    
    for finding in findings:
        # Map pattern IDs to vulnerability types
        pattern_id = finding.get('pattern_id', '')
        vuln_type = None
        
        if 'sql' in pattern_id.lower():
            vuln_type = 'sql_injection'
        elif 'aws' in pattern_id.lower() or 'api_key' in pattern_id.lower() or 'password' in pattern_id.lower():
            vuln_type = 'hardcoded_secret'
        elif 'command' in pattern_id.lower():
            vuln_type = 'command_injection'
        elif 'pickle' in pattern_id.lower():
            vuln_type = 'insecure_deserialization'
        elif 'path' in pattern_id.lower():
            vuln_type = 'path_traversal'
        elif 'md5' in pattern_id.lower() or 'sha1' in pattern_id.lower():
            vuln_type = 'weak_crypto'
        elif 'cors' in pattern_id.lower():
            vuln_type = 'cors_misconfiguration'
        
        if vuln_type:
            categorized[vuln_type].append(finding)
    
    return dict(categorized)

def calculate_metrics(expected: Dict, found: Dict[str, List[Dict]]) -> Tuple[int, int, int, float, float]:
    """Calculate TP, FP, FN, precision, and recall"""
    tp = 0  # True positives
    fp = 0  # False positives
    fn = 0  # False negatives
    
    # Check each expected vulnerability
    for vuln_type, expected_info in expected.items():
        expected_count = expected_info['count']
        found_count = len(found.get(vuln_type, []))
        
        if found_count > 0:
            # Found at least one instance
            tp += min(found_count, expected_count)
            if found_count > expected_count:
                fp += found_count - expected_count
        else:
            # Missed this vulnerability type
            fn += expected_count
    
    # Check for false positives (findings not in expected)
    for vuln_type, findings in found.items():
        if vuln_type not in expected:
            fp += len(findings)
    
    # Calculate precision and recall
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    
    return tp, fp, fn, precision, recall

def print_evaluation_report(expected: Dict, found: Dict[str, List[Dict]], metrics: Tuple):
    """Print a detailed evaluation report"""
    tp, fp, fn, precision, recall = metrics
    f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    
    print("=" * 60)
    print("Security Auditor Evaluation Report")
    print("=" * 60)
    print()
    
    print("Expected Vulnerabilities:")
    for vuln_type, info in expected.items():
        print(f"  - {vuln_type}: {info['count']} instances ({info['severity']})")
    print()
    
    print("Found Vulnerabilities:")
    for vuln_type, findings in found.items():
        severity = findings[0].get('severity', 'unknown') if findings else 'unknown'
        print(f"  - {vuln_type}: {len(findings)} instances ({severity})")
    print()
    
    print("Metrics:")
    print(f"  True Positives:  {tp}")
    print(f"  False Positives: {fp}")
    print(f"  False Negatives: {fn}")
    print(f"  Precision:       {precision:.2%}")
    print(f"  Recall:          {recall:.2%}")
    print(f"  F1 Score:        {f1_score:.2%}")
    print()
    
    # Detailed breakdown
    print("Detailed Analysis:")
    for vuln_type, expected_info in expected.items():
        found_count = len(found.get(vuln_type, []))
        expected_count = expected_info['count']
        
        if found_count == 0:
            print(f"  ❌ MISSED: {vuln_type} - Expected {expected_count}, found 0")
        elif found_count < expected_count:
            print(f"  ⚠️  PARTIAL: {vuln_type} - Expected {expected_count}, found {found_count}")
        elif found_count == expected_count:
            print(f"  ✅ FOUND: {vuln_type} - Expected {expected_count}, found {found_count}")
        else:
            print(f"  ⚠️  OVER-DETECTED: {vuln_type} - Expected {expected_count}, found {found_count}")
    
    # Check for unexpected findings
    for vuln_type in found:
        if vuln_type not in expected:
            print(f"  ⚠️  UNEXPECTED: {vuln_type} - Found {len(found[vuln_type])} instances")
    
    print()
    print("=" * 60)

def main():
    # Look for the latest audit report
    report_paths = glob.glob("audit/reports/security_audit_*.json")
    
    if not report_paths:
        # Try pattern scan results
        report_paths = glob.glob("audit/reports/pattern_scan_*.json")
    
    if not report_paths:
        print("No audit reports found. Run the security audit first.")
        sys.exit(1)
    
    # Use the most recent report
    latest_report = max(report_paths, key=os.path.getctime)
    print(f"Evaluating report: {latest_report}")
    print()
    
    # Load and analyze results
    audit_results = load_audit_results(latest_report)
    findings = audit_results.get('findings', [])
    
    # Categorize findings
    categorized = categorize_findings(findings)
    
    # Calculate metrics
    metrics = calculate_metrics(EXPECTED_VULNS, categorized)
    
    # Print evaluation report
    print_evaluation_report(EXPECTED_VULNS, categorized, metrics)
    
    # Return non-zero exit code if recall is below threshold
    _, _, _, _, recall = metrics
    if recall < 0.8:  # 80% recall threshold
        print(f"\n⚠️  Warning: Recall ({recall:.2%}) is below 80% threshold")
        sys.exit(1)

if __name__ == "__main__":
    main()