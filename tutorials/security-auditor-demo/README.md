# Security Auditor Demo - Claude Code Subagent

A fully functional security auditing subagent prototype for Claude Code v1.0.60+. This demo showcases how to build custom subagents that perform specialized tasks like OWASP-style security reviews with structured output.

## Features

- **Pattern-based security scanning** with regex rules for common vulnerabilities
- **Claude Code subagent integration** for AI-powered security analysis
- **Git pre-commit hooks** to prevent committing vulnerable code
- **Structured output** in both Markdown and JSON formats
- **Evaluation framework** to test auditor effectiveness
- **CI/CD ready** with example GitHub Actions workflow

## Quick Start

1. **Install dependencies:**
   ```bash
   make install
   ```

2. **Run security audit:**
   ```bash
   make audit
   ```

3. **Install git hook:**
   ```bash
   make install-hook
   ```

4. **Run full demo:**
   ```bash
   make demo
   ```

## Project Structure

```
security-auditor-demo/
├── .claude/agents/           # Claude Code agent definitions
│   └── security-auditor.agent.json
├── audit/                    # Audit configuration and tools
│   ├── prompts/             # System prompts for AI
│   ├── rules/               # Security pattern rules
│   └── runners/             # Audit execution scripts
├── scripts/                 # Utility scripts
├── src/                     # Source code to audit
│   └── vulnerable.py        # Demo vulnerable code
└── Makefile                 # Build automation
```

## Security Vulnerabilities Detected

The auditor can detect various security issues including:

- **SQL Injection** - String interpolation in database queries
- **Command Injection** - Shell command execution with user input
- **Hardcoded Secrets** - API keys, passwords in source code
- **Insecure Deserialization** - Pickle/YAML vulnerabilities
- **Path Traversal** - Directory traversal attacks
- **Weak Cryptography** - MD5, SHA1 usage
- **CORS Misconfiguration** - Wildcard origins
- **And more...**

## Usage Examples

### Run Pattern-Based Scan Only
```bash
python3 audit/runners/pattern_scanner.py src
```

### Run Full Audit (Pattern + AI)
```bash
bash audit/runners/run_audit.sh src audit/reports
```

### Evaluate Auditor Performance
```bash
make eval
```

### Test Git Hook
```bash
make test-hook
```

## Customization

### Adding New Security Patterns

Edit `audit/rules/patterns.yaml`:
```yaml
patterns:
  - id: your-pattern-id
    lang: python  # optional language filter
    regex: "your.*regex"
    severity: high  # critical|high|medium|low
    description: "Clear description of the issue"
```

### Modifying AI Prompt

Edit `audit/prompts/security-auditor.system.md` to customize the AI's security analysis behavior.

### Extending the Agent

Modify `.claude/agents/security-auditor.agent.json` to:
- Change context inclusion/exclusion rules
- Adjust token limits
- Enable/disable tools
- Modify output formats

## Integration with CI/CD

### GitHub Actions Example

The project includes a sample workflow in the tutorial. Key steps:

1. Install Claude Code CLI
2. Run security audit
3. Fail build on critical/high issues
4. Generate artifacts

### Pre-commit Hook

The included git hook will:
- Run pattern scanning on staged files
- Optionally run Claude Code AI audit
- Block commits with severe vulnerabilities
- Allow bypass with `--no-verify` (not recommended)

## Evaluation Metrics

The evaluation script tracks:
- **True Positives (TP)** - Correctly identified vulnerabilities
- **False Positives (FP)** - Non-issues flagged as vulnerabilities
- **False Negatives (FN)** - Missed vulnerabilities
- **Precision** - TP / (TP + FP)
- **Recall** - TP / (TP + FN)
- **F1 Score** - Harmonic mean of precision and recall

## Troubleshooting

### Pattern Scanner Not Finding Issues
- Check regex patterns in `patterns.yaml`
- Verify file extensions are included in scan
- Run with verbose output for debugging

### Claude Code Not Available
- The tool gracefully falls back to pattern scanning
- Install Claude Code: `npm i -g @anthropic-ai/claude-code`
- Verify with: `claude --version`

### Git Hook Not Working
- Ensure hook is executable: `chmod +x .git/hooks/pre-commit`
- Check Python/jq dependencies are installed
- Test with: `make test-hook`

## Going Further

### Multi-Agent Swarms

Extend with specialized subagents:
- `secrets-hunter` - Deep secret scanning
- `license-checker` - License compliance
- `sbom-auditor` - Dependency vulnerabilities
- `config-sentinel` - Configuration security

### Advanced Features

- Add auto-fix capabilities for common issues
- Integrate with security tools (Semgrep, Bandit)
- Create custom severity scoring algorithms
- Build security dashboards and reporting

## License

MIT - See LICENSE file

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new patterns
4. Ensure evaluation metrics pass
5. Submit a pull request

---

Built with Claude Code v1.0.60+ subagent capabilities