#!/usr/bin/env bash
set -euo pipefail

# Default values
AUDIT_PATH="${1:-src}"
OUTPUT_DIR="${2:-audit/reports}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
REPORT_MD="${OUTPUT_DIR}/security_audit_${TIMESTAMP}.md"
REPORT_JSON="${OUTPUT_DIR}/security_audit_${TIMESTAMP}.json"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}[Security Audit]${NC} Starting security audit..."
echo -e "${YELLOW}[Security Audit]${NC} Scanning path: ${AUDIT_PATH}"

# Create output directory if it doesn't exist
mkdir -p "${OUTPUT_DIR}"

# Run pattern-based scanning first
echo -e "${YELLOW}[Security Audit]${NC} Running pattern-based security scan..."
python3 audit/runners/pattern_scanner.py "${AUDIT_PATH}" > "${OUTPUT_DIR}/pattern_scan_${TIMESTAMP}.json"

# Run Claude Code security auditor (if available)
if command -v claude &> /dev/null; then
    echo -e "${YELLOW}[Security Audit]${NC} Running Claude Code security auditor..."
    claude agent run security-auditor \
        --path "${AUDIT_PATH}" \
        --out "${REPORT_MD}" \
        --json-out "${REPORT_JSON}" || {
        echo -e "${RED}[Security Audit]${NC} Claude Code audit failed, falling back to pattern scan only"
    }
fi

# Parse results and check severity
if [ -f "${REPORT_JSON}" ]; then
    CRITICALS=$(jq -r '.summary.critical // 0' "${REPORT_JSON}")
    HIGHS=$(jq -r '.summary.high // 0' "${REPORT_JSON}")
    MEDIUMS=$(jq -r '.summary.medium // 0' "${REPORT_JSON}")
    LOWS=$(jq -r '.summary.low // 0' "${REPORT_JSON}")
    
    echo -e "\n${YELLOW}[Security Audit]${NC} Summary:"
    echo -e "  Critical: ${CRITICALS}"
    echo -e "  High:     ${HIGHS}"
    echo -e "  Medium:   ${MEDIUMS}"
    echo -e "  Low:      ${LOWS}"
    
    if [ "${CRITICALS}" -gt 0 ] || [ "${HIGHS}" -gt 0 ]; then
        echo -e "\n${RED}[Security Audit]${NC} ❌ FAILED - Critical/High severity issues found!"
        echo -e "${YELLOW}[Security Audit]${NC} Report saved to: ${REPORT_MD}"
        exit 1
    else
        echo -e "\n${GREEN}[Security Audit]${NC} ✅ PASSED - No critical/high severity issues found"
        echo -e "${YELLOW}[Security Audit]${NC} Report saved to: ${REPORT_MD}"
    fi
else
    echo -e "${YELLOW}[Security Audit]${NC} No JSON report generated, check pattern scan results"
fi

# Create a latest symlink for easy access
ln -sf "$(basename "${REPORT_MD}")" "${OUTPUT_DIR}/latest_report.md" 2>/dev/null || true
ln -sf "$(basename "${REPORT_JSON}")" "${OUTPUT_DIR}/latest_report.json" 2>/dev/null || true