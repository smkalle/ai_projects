#!/usr/bin/env bash
set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

HOOK=".git/hooks/pre-commit"

echo -e "${YELLOW}[Git Hook]${NC} Installing pre-commit security audit hook..."

# Create the pre-commit hook
cat > "$HOOK" <<'EOF'
#!/usr/bin/env bash
set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}[pre-commit]${NC} Running security audit..."

# Create temp files for output
TMP_MD=$(mktemp)
TMP_JSON=$(mktemp)

# Ensure we're in the git root directory
GIT_ROOT=$(git rev-parse --show-toplevel)
cd "$GIT_ROOT"

# Check if we have the pattern scanner
if [ ! -f "audit/runners/pattern_scanner.py" ]; then
    echo -e "${RED}[pre-commit]${NC} Pattern scanner not found. Skipping security audit."
    exit 0
fi

# Run pattern-based scanner (always available)
echo -e "${YELLOW}[pre-commit]${NC} Running pattern-based security scan..."
python3 audit/runners/pattern_scanner.py src > "$TMP_JSON"

# Check if Claude Code is available
if command -v claude &> /dev/null; then
    echo -e "${YELLOW}[pre-commit]${NC} Running Claude Code security auditor..."
    claude agent run security-auditor \
        --path src \
        --out "$TMP_MD" \
        --json-out "$TMP_JSON" 2>/dev/null || {
        echo -e "${YELLOW}[pre-commit]${NC} Claude Code not available, using pattern scan only"
    }
fi

# Parse results
if [ -f "$TMP_JSON" ]; then
    CRITICALS=$(jq -r '.summary.critical // 0' "$TMP_JSON" 2>/dev/null || echo "0")
    HIGHS=$(jq -r '.summary.high // 0' "$TMP_JSON" 2>/dev/null || echo "0")
    
    if [ "$CRITICALS" -gt 0 ] || [ "$HIGHS" -gt 0 ]; then
        echo -e "\n${RED}[pre-commit]${NC} ❌ Security audit failed!"
        echo -e "${RED}[pre-commit]${NC} Found $CRITICALS critical and $HIGHS high severity issues:"
        echo ""
        
        # Show findings
        if command -v jq &> /dev/null; then
            jq -r '.findings[] | select(.severity == "critical" or .severity == "high") | 
                   "  [\(.severity|ascii_upcase)] \(.file):\(.line) - \(.description)"' "$TMP_JSON" 2>/dev/null || true
        fi
        
        # Show markdown report if available
        if [ -f "$TMP_MD" ] && [ -s "$TMP_MD" ]; then
            echo ""
            echo "Full report:"
            cat "$TMP_MD"
        fi
        
        # Clean up
        rm -f "$TMP_MD" "$TMP_JSON"
        
        echo ""
        echo -e "${YELLOW}[pre-commit]${NC} Fix the security issues before committing."
        echo -e "${YELLOW}[pre-commit]${NC} To bypass (NOT recommended): git commit --no-verify"
        exit 1
    else
        echo -e "${GREEN}[pre-commit]${NC} ✅ Security audit passed."
    fi
else
    echo -e "${YELLOW}[pre-commit]${NC} No security scan results found."
fi

# Clean up
rm -f "$TMP_MD" "$TMP_JSON"
EOF

# Make the hook executable
chmod +x "$HOOK"

echo -e "${GREEN}[Git Hook]${NC} ✅ Pre-commit hook installed at: $HOOK"
echo -e "${YELLOW}[Git Hook]${NC} The hook will:"
echo "  - Run pattern-based security scanning"
echo "  - Run Claude Code security auditor (if available)"
echo "  - Block commits with Critical/High severity issues"
echo ""
echo -e "${YELLOW}[Git Hook]${NC} To test: make a commit in this repository"
echo -e "${YELLOW}[Git Hook]${NC} To bypass: git commit --no-verify (NOT recommended)"