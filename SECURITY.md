# Security Policy

## Reporting a Vulnerability

**Please do NOT open public GitHub issues for security vulnerabilities.**

If you discover a security vulnerability, please report it responsibly:

1. Email: **security@twigloop.dev**
2. Include:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

## Response Timeline

- **Acknowledgment**: Within 48 hours
- **Initial assessment**: Within 5 business days
- **Fix timeline**: Depends on severity, typically within 14 days for critical issues

## Scope

This policy applies to:
- The Twig Loop application code
- API endpoints and authentication
- Data handling and storage

## Out of Scope

- Issues in third-party dependencies (report to the upstream project)
- Social engineering attacks
- Denial of service attacks against development infrastructure

## Current Security Status

Twig Loop is in **Public Beta**. Known limitations:
- JWT stored in httpOnly cookies (browser) and Authorization headers (API clients)
- Rate limiting is per-instance (not distributed)
- No server-side token revocation yet

These are documented in our [tech debt roadmap](docs/pilot/05-tech-debt-roadmap.md).
