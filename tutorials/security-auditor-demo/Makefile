.PHONY: help install audit test-audit eval clean install-hook test-hook demo

# Default target
help:
	@echo "Security Auditor Demo - Available targets:"
	@echo "  make install       - Install dependencies"
	@echo "  make audit         - Run security audit on src/"
	@echo "  make test-audit    - Test pattern scanner"
	@echo "  make eval          - Evaluate auditor performance"
	@echo "  make install-hook  - Install git pre-commit hook"
	@echo "  make test-hook     - Test pre-commit hook"
	@echo "  make clean         - Clean generated files"
	@echo "  make demo          - Run full demo (audit + eval)"

# Install dependencies
install:
	@echo "Installing dependencies..."
	@pip install pyyaml > /dev/null 2>&1 || true
	@command -v jq >/dev/null 2>&1 || echo "Warning: jq not installed (needed for JSON parsing)"
	@command -v claude >/dev/null 2>&1 || echo "Warning: Claude Code not installed"
	@echo "Dependencies checked."

# Run security audit
audit:
	@echo "Running security audit..."
	@mkdir -p audit/reports
	@bash audit/runners/run_audit.sh src audit/reports

# Test pattern scanner only
test-audit:
	@echo "Testing pattern scanner..."
	@mkdir -p audit/reports
	@python3 audit/runners/pattern_scanner.py src > audit/reports/pattern_test.json
	@echo "Pattern scan complete. Results:"
	@jq '.summary' audit/reports/pattern_test.json 2>/dev/null || cat audit/reports/pattern_test.json

# Evaluate auditor performance
eval:
	@echo "Evaluating security auditor..."
	@python3 scripts/eval_seeded_vulns.py

# Install git hook
install-hook:
	@bash scripts/install_git_hook.sh

# Test git hook
test-hook:
	@echo "Testing pre-commit hook..."
	@git add src/vulnerable.py 2>/dev/null || true
	@git commit -m "test: security audit hook" --dry-run || echo "Hook working correctly!"

# Clean generated files
clean:
	@echo "Cleaning generated files..."
	@rm -rf audit/reports/*.json audit/reports/*.md
	@rm -f .git/hooks/pre-commit
	@find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
	@find . -name "*.pyc" -delete 2>/dev/null || true
	@echo "Clean complete."

# Full demo
demo: install audit eval
	@echo ""
	@echo "Demo complete! Check audit/reports/ for results."
	@echo "To see the latest report:"
	@echo "  cat audit/reports/latest_report.md"

# Add vulnerable file and commit (for testing)
test-commit:
	@git add src/vulnerable.py
	@git commit -m "feat: add authentication system" || echo "Commit blocked by security audit!"

# Quick audit with just pattern scanner
quick-audit:
	@mkdir -p audit/reports
	@python3 audit/runners/pattern_scanner.py src | tee audit/reports/quick_scan.json | jq '.summary'

# Show latest report
show-report:
	@if [ -f audit/reports/latest_report.md ]; then \
		cat audit/reports/latest_report.md; \
	else \
		echo "No report found. Run 'make audit' first."; \
	fi

# CI/CD simulation
ci: install audit eval
	@echo "CI pipeline complete."