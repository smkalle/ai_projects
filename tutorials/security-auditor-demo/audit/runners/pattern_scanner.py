#!/usr/bin/env python3
"""
Pattern-based security scanner
Scans code for known vulnerable patterns using regex
"""

import os
import re
import json
import yaml
import sys
from pathlib import Path
from typing import List, Dict, Any

def load_patterns(pattern_file: str = "audit/rules/patterns.yaml") -> List[Dict[str, Any]]:
    """Load security patterns from YAML file"""
    with open(pattern_file, 'r') as f:
        data = yaml.safe_load(f)
    return data.get('patterns', [])

def scan_file(filepath: str, patterns: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Scan a single file for security patterns"""
    findings = []
    
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            lines = content.splitlines()
    except Exception as e:
        return findings
    
    for pattern in patterns:
        # Skip language-specific patterns if they don't match
        if 'lang' in pattern:
            if pattern['lang'] == 'python' and not filepath.endswith('.py'):
                continue
            elif pattern['lang'] == 'javascript' and not filepath.endswith(('.js', '.jsx', '.ts', '.tsx')):
                continue
        
        regex = pattern['regex']
        try:
            for line_num, line in enumerate(lines, 1):
                if re.search(regex, line):
                    findings.append({
                        'file': filepath,
                        'line': line_num,
                        'pattern_id': pattern['id'],
                        'severity': pattern['severity'],
                        'description': pattern['description'],
                        'code': line.strip()
                    })
        except re.error:
            print(f"Invalid regex pattern: {regex}", file=sys.stderr)
    
    return findings

def scan_directory(path: str, patterns: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Recursively scan directory for security issues"""
    findings = []
    path_obj = Path(path)
    
    # Define extensions to scan
    scan_extensions = {'.py', '.js', '.jsx', '.ts', '.tsx', '.java', '.rb', '.php', '.go', 
                      '.yml', '.yaml', '.json', '.xml', '.conf', '.ini', '.env'}
    
    # Define paths to exclude
    exclude_dirs = {'node_modules', '.git', '__pycache__', 'venv', '.venv', 'dist', 'build'}
    
    for root, dirs, files in os.walk(path):
        # Remove excluded directories from scan
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        
        for file in files:
            filepath = os.path.join(root, file)
            
            # Check if file should be scanned
            if any(filepath.endswith(ext) for ext in scan_extensions):
                file_findings = scan_file(filepath, patterns)
                findings.extend(file_findings)
    
    return findings

def generate_summary(findings: List[Dict[str, Any]]) -> Dict[str, int]:
    """Generate summary statistics from findings"""
    summary = {
        'critical': 0,
        'high': 0,
        'medium': 0,
        'low': 0
    }
    
    for finding in findings:
        severity = finding.get('severity', 'low').lower()
        if severity in summary:
            summary[severity] += 1
    
    return summary

def main():
    if len(sys.argv) < 2:
        print("Usage: pattern_scanner.py <path_to_scan>", file=sys.stderr)
        sys.exit(1)
    
    scan_path = sys.argv[1]
    
    # Load patterns
    patterns = load_patterns()
    
    # Perform scan
    findings = scan_directory(scan_path, patterns)
    
    # Generate summary
    summary = generate_summary(findings)
    
    # Output results as JSON
    result = {
        'summary': summary,
        'findings': findings
    }
    
    print(json.dumps(result, indent=2))

if __name__ == '__main__':
    main()