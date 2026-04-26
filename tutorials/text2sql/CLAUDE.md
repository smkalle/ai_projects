# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This is a **text-to-SQL tutorial project** — a tutorials directory containing documentation for building an agentic natural language-to-SQL system using LangChain Deep Agents. The actual `text2sql` SDK lives in an external repo; this directory holds the tutorial and product specification.

**Key documents:**
- `tex2sql_tutorial.md` — Full hands-on tutorial for building a production-grade text-to-SQL agent
- `wardops-brd-prd.md` — Business and product requirements for "WardOps Dashboard", a hospital operations NL query interface

## Architecture Pattern

The text-to-SQL agent works via autonomous iteration:
1. Explore DB schema via `execute_sql` (PRAGMA / information_schema)
2. Draft SQL from natural language
3. Execute and validate; self-correct on errors
4. Optional: lookup_example from scenarios.md for domain guidance
5. Loop until success or max iterations (8)

**Security critical:** The `execute_sql` tool must be wrapped to reject non-SELECT statements. DB connections use read-only credentials.

## Key Dependencies

- **text2sql SDK** — `pip install text2sql` (from https://github.com/Text2SqlAgent/text2sql-framework)
- **LLM:** Claude Sonnet 4-6 (recommended) or GPT-4o
- **Framework:** LangChain Deep Agents
- **Backend:** FastAPI + SQLAlchemy
- **Database:** Any SQLAlchemy-compatible (SQLite for dev, PostgreSQL/MySQL for prod)

## No Code Present

This directory contains only documentation. There are no Python files, tests, or build scripts to run. All code examples in the tutorial reference external packages that must be installed separately.
