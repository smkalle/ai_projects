---
name: secops
version: 1.0.0
description: "Security Operations — AI-assisted vulnerability discovery, code auditing, and secure development practices."
metadata:
  category: "security"
  inspired_by: "Anthropic x Mozilla Firefox security audit (2025)"
---

# SecOps — AI-Assisted Security Operations

Security Operations skill for vulnerability discovery, code auditing, and secure development. Inspired by Anthropic's collaboration with Mozilla where Claude discovered 22 vulnerabilities (14 high-severity) in Firefox by scanning ~6,000 C++ files.

## Capabilities

### 1. Source Code Audit
Scan source files for common vulnerability classes:
- **Memory safety**: Use-After-Free, double-free, buffer overflows, dangling pointers
- **Injection flaws**: SQL injection, command injection, XSS, template injection
- **Authentication/Authorization**: broken access control, privilege escalation
- **Cryptographic issues**: weak algorithms, hardcoded secrets, improper key management
- **Concurrency bugs**: race conditions, TOCTOU, deadlocks
- **Input validation**: missing bounds checks, integer overflows, format string bugs

### 2. Task Verifier Pattern
Following the Mozilla audit methodology — always verify findings with a second check:
- After identifying a vulnerability, propose a fix
- Verify the fix removes the vulnerability
- Confirm the fix preserves program functionality (no regressions)
- Produce minimal test cases and proofs-of-concept

### 3. Vulnerability Report Generation
For each finding, produce:
- **Severity rating** (Critical / High / Medium / Low / Informational)
- **CWE classification** (e.g., CWE-416 Use After Free)
- **Minimal reproducer** — smallest code/input that triggers the bug
- **Proof-of-concept** — demonstration of exploitability
- **Candidate patch** — proposed fix with rationale
- **Impact assessment** — what an attacker could achieve

### 4. Secure Code Review Checklist
When reviewing PRs or code changes:
- [ ] No new injection vectors introduced
- [ ] Input validation at system boundaries
- [ ] Secrets not hardcoded or logged
- [ ] Error messages don't leak internals
- [ ] Dependencies are pinned and non-vulnerable
- [ ] Authentication/authorization checks present
- [ ] Resource limits enforced (no unbounded allocations)
- [ ] Safe deserialization practices

### 5. Dependency Audit
- Check for known CVEs in project dependencies
- Identify outdated packages with security patches available
- Flag transitive dependencies with known issues

## Usage

### Quick scan a file or directory
```
/secops scan <path>
```
Reads source files and reports potential vulnerabilities with severity ratings.

### Audit a specific vulnerability class
```
/secops audit --class memory-safety <path>
```
Focus the scan on a single vulnerability category.

### Generate a security report
```
/secops report <path>
```
Produce a structured vulnerability report with CWE IDs, reproducers, and patches.

### Review a PR for security
```
/secops review
```
Check staged/changed files against the secure code review checklist.

### Check dependencies
```
/secops deps
```
Audit project dependencies for known vulnerabilities.

## Workflow

1. **Scope** — Identify the target: files, directories, or changed code
2. **Scan** — Read and analyze code for vulnerability patterns
3. **Verify** — Confirm findings aren't false positives (task verifier pattern)
4. **Report** — Generate structured findings with severity, CWE, PoC, and fix
5. **Patch** — Propose minimal, correct fixes
6. **Validate** — Confirm patches resolve issues without regressions

## Instructions

When invoked:
1. Determine scope from user input (specific files, directory, git diff, etc.)
2. Read the target source files using the Read tool
3. Analyze for vulnerabilities systematically by category
4. For each finding, classify severity and map to CWE
5. Write a minimal reproducer where possible
6. Propose a candidate patch
7. Summarize all findings in a structured report

### Output Format
```
## Security Audit Report

**Target:** <path or description>
**Files scanned:** <count>
**Findings:** <count> (Critical: N, High: N, Medium: N, Low: N, Info: N)

### Finding 1: <Title>
- **Severity:** High
- **CWE:** CWE-XXX <Name>
- **Location:** `file.py:42`
- **Description:** <what the vulnerability is>
- **Reproducer:** <minimal test case>
- **Fix:** <proposed patch>
- **Impact:** <what an attacker could do>
```

## Responsible Disclosure

Follow coordinated vulnerability disclosure principles:
- Report findings to maintainers before public disclosure
- Allow reasonable time for fixes (typically 90 days)
- Provide actionable information: reproducer, patch, impact
- Do not develop weaponized exploits beyond proof-of-concept

## Tips
- Start with high-impact, isolated components (like Mozilla started with the JS engine)
- Use grep/glob to find patterns before deep-reading files
- Focus on system boundaries where untrusted input enters
- Memory-unsafe languages (C/C++) warrant extra attention on memory management
- Check error handling paths — they're often less tested
- Look for asymmetry: if allocation happens in one place, ensure deallocation matches
