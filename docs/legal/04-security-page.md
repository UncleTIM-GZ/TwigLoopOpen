# Security

**Last updated:** 2026-03-16
**Service:** Twig Loop (twigloop.tech)
**Stage:** Public Beta

---

## Reporting a Vulnerability

If you discover a security vulnerability in Twig Loop, please report it responsibly:

- **Email:** security@twigloop.tech
- **Do not** report security vulnerabilities through public GitHub issues, social media, or other public channels.

Please include:
- A description of the vulnerability.
- Steps to reproduce (if possible).
- The potential impact as you understand it.
- Your contact information (so I can follow up).

---

## Response Timeline

| Step | Timeframe |
|------|-----------|
| Acknowledge your report | Within 48 hours |
| Initial assessment | Within 7 days |
| Status update to reporter | After assessment is complete |
| Fix deployed (if confirmed) | As soon as reasonably possible |

I will keep you informed of progress and let you know when the issue has been resolved.

---

## What We Do

Twig Loop implements the following security measures:

- **HTTPS everywhere:** All traffic between your browser and Twig Loop is encrypted via TLS.
- **Password hashing:** Passwords are hashed using bcrypt before storage. Plaintext passwords are never stored.
- **httpOnly cookies:** Authentication tokens are stored in httpOnly, secure cookies that are not accessible to client-side JavaScript.
- **Rate limiting:** API endpoints are rate-limited to prevent brute force and abuse.
- **Input validation:** User inputs are validated on the server side to prevent injection attacks.
- **CORS policy:** Cross-origin requests are restricted to trusted origins.
- **Parameterized queries:** Database queries use parameterized statements to prevent SQL injection.
- **Cloudflare protection:** DDoS mitigation and bot management via Cloudflare.

---

## What We Do Not Promise

Twig Loop is in Public Beta. I am honest about what that means for security:

- I do not claim to be "bank-grade" or "military-grade" secure.
- I cannot guarantee that the service is free of all vulnerabilities.
- Security measures are continuously improving, but beta software carries inherent risk.
- I am a sole operator, not a security team of dozens.

I take security seriously, but I also believe in being straightforward about the current stage of the project.

---

## Scope

The following are **in scope** for security reports:

- Application code at twigloop.tech
- API endpoints
- Authentication and authorization system
- Session management
- Data exposure or leakage

---

## Out of Scope

The following are **out of scope:**

- Third-party services (Railway, Cloudflare, GitHub) — please report issues to those providers directly.
- Social engineering attacks (phishing, pretexting).
- Denial-of-service (DoS/DDoS) attacks.
- Physical security.
- Issues in software or infrastructure I do not control.
- Automated scan results without a demonstrated exploit.

---

## Bug Bounty

There is **no bug bounty program** at this time. I appreciate responsible disclosure and will credit reporters (with permission) when vulnerabilities are confirmed and fixed.

---

## Contact

- **Security reports:** security@twigloop.tech
- **General questions:** hello@twigloop.tech
