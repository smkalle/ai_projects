#!/usr/bin/env bash
# Run a SecOps security audit using Claude Code CLI.
#
# Usage:
#   bash scripts/run_audit.sh [target_path] [output_file]
#
# Examples:
#   bash scripts/run_audit.sh samples/vulnerable/
#   bash scripts/run_audit.sh src/ reports/my_audit.md

set -euo pipefail

TARGET="${1:-.}"
OUTPUT="${2:-reports/audit_$(date +%Y%m%d_%H%M%S).md}"

# Ensure output directory exists
mkdir -p "$(dirname "$OUTPUT")"

echo "SecOps Audit"
echo "============"
echo "Target:  $TARGET"
echo "Output:  $OUTPUT"
echo ""

# Check for Claude Code
if ! command -v claude &>/dev/null; then
    echo "Error: Claude Code CLI not found."
    echo "Install: npm i -g @anthropic-ai/claude-code"
    exit 1
fi

# Check skill is installed
if [ ! -f "$HOME/.claude/skills/secops/SKILL.md" ]; then
    echo "SecOps skill not installed. Installing..."
    SCRIPT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
    mkdir -p "$HOME/.claude/skills/secops"
    cp "$SCRIPT_DIR/skill/secops/SKILL.md" "$HOME/.claude/skills/secops/SKILL.md"
    echo "Installed."
fi

echo "Running audit..."
echo ""

# Run Claude Code with the secops skill
claude -p "/secops report $TARGET" | tee "$OUTPUT"

echo ""
echo "Report saved to: $OUTPUT"
