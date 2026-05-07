# Security Policy

## Reporting Vulnerabilities

Please report security issues privately to the maintainers before opening a public issue.

Include:

- affected component(s)
- reproduction steps
- expected vs actual behavior
- potential impact

## Secrets Handling

- Never commit API keys, credentials, or private documents.
- Use `.env.example` as a template and keep `.env` local.
- Rotate any key immediately if exposed.

## Safe Defaults

- Private URL ingestion is disabled by default (`ALLOW_PRIVATE_URLS=false`).
- Debug trace is enabled by default for development; disable in production if needed with `DEBUG=0`.
