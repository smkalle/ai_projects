#!/bin/bash
set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

clear
echo -e "${BLUE}=== Security Auditor Demo ===${NC}"
echo ""
echo "This demo showcases a Claude Code security auditor subagent"
echo "that performs automated security reviews of Python code."
echo ""
echo "Press Enter to continue..."
read

echo -e "\n${YELLOW}Step 1: Viewing vulnerable code${NC}"
echo "Let's look at our intentionally vulnerable code:"
echo ""
echo "src/vulnerable.py contains:"
echo "- SQL injection vulnerability"
echo "- Hardcoded AWS credentials"
echo "- Command injection"
echo "- Insecure deserialization"
echo "- Path traversal"
echo "- Weak cryptography (MD5)"
echo "- CORS misconfiguration"
echo ""
echo "Press Enter to run security audit..."
read

echo -e "\n${YELLOW}Step 2: Running pattern-based security scan${NC}"
python3 audit/runners/pattern_scanner.py src | jq '.'
echo ""
echo "Press Enter to see summary..."
read

echo -e "\n${YELLOW}Step 3: Security audit summary${NC}"
python3 audit/runners/pattern_scanner.py src | jq '.summary'
echo ""
echo -e "${RED}Found critical and high severity issues!${NC}"
echo ""
echo "Press Enter to test git hook..."
read

echo -e "\n${YELLOW}Step 4: Testing pre-commit hook${NC}"
echo "Let's try to commit this vulnerable code..."
echo ""

# Ensure hook is installed
bash scripts/install_git_hook.sh > /dev/null 2>&1

# Stage a file and try to commit
git add src/vulnerable.py 2>/dev/null || true
if git commit -m "test: vulnerable code" 2>&1 | grep -q "Security audit failed"; then
    echo -e "${RED}✗ Commit blocked by security audit!${NC}"
    echo "The pre-commit hook prevented committing vulnerable code."
else
    echo -e "${GREEN}✓ Demo file already committed${NC}"
fi

echo ""
echo "Press Enter to run evaluation..."
read

echo -e "\n${YELLOW}Step 5: Evaluating auditor performance${NC}"
python3 scripts/eval_seeded_vulns.py

echo -e "\n${GREEN}Demo complete!${NC}"
echo ""
echo "Next steps:"
echo "1. Customize patterns in audit/rules/patterns.yaml"
echo "2. Modify the system prompt in audit/prompts/security-auditor.system.md"
echo "3. Integrate with CI/CD using .github/workflows/security-audit.yml"
echo "4. Create additional subagents for specialized security tasks"
echo ""
echo "For more info, see README.md"