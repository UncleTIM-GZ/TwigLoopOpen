# Privacy Policy

**Effective date:** 2026-03-16
**Last updated:** 2026-03-16
**Operator:** Timothy Ou
**Service:** Twig Loop (twigloop.tech)
**Stage:** Public Beta

---

## Introduction

Twig Loop is an AI-native project collaboration platform operated by Timothy Ou as a sole operator. This privacy policy explains what data I collect, why I collect it, and how I handle it.

I aim to handle your data responsibly and transparently. If you have questions, contact me at privacy@twigloop.tech.

---

## What Data I Collect

**Account information:**
- Email address (required for registration)
- Password (stored as a bcrypt hash — I never store your plaintext password)
- Display name and bio (optional, provided by you)

**Project data:**
- Projects, work packages, and task cards you create
- Applications, reviews, and collaboration activity
- Work unit records (EWU, RWU, SWU)

**Usage logs:**
- IP address
- Browser type and version
- Pages visited and actions taken
- Timestamps

**Authentication data:**
- Session tokens
- OAuth tokens (if you sign in via GitHub)

---

## Why I Collect This Data

- **To provide the service:** Your account and project data are necessary for Twig Loop to function.
- **For security:** Usage logs and IP addresses help detect abuse, unauthorized access, and other security threats.
- **To improve the service:** Aggregated, anonymized usage patterns help me understand how the platform is used and where to improve it.

---

## How Your Data Is Stored

- **Database:** PostgreSQL hosted on Railway (US region).
- **Session and rate-limiting data:** Redis hosted on Railway (US region).
- **Backups:** Automated database backups retained for 7 days on a rolling basis.
- **Encryption:** All data is transmitted over HTTPS (TLS). Data at rest is stored on Railway's infrastructure, which provides encryption at the storage level.

---

## Third Parties

I use the following third-party services to operate Twig Loop:

| Service | Purpose | Location |
|---------|---------|----------|
| Railway | Application hosting, PostgreSQL database, Redis | US |
| Cloudflare | CDN, DNS, DDoS protection | Global (edge network) |
| GitHub | OAuth sign-in (if you choose to use it), source code hosting | US |

I do not sell your data to anyone. I do not use advertising networks. I do not use third-party analytics services at this time.

---

## Cookies

During the beta period, Twig Loop uses **essential cookies only:**

- **Session cookie:** Maintains your logged-in session.
- **Authentication cookie:** Secure, httpOnly cookie for auth tokens.
- **Cloudflare cookies:** Cloudflare may set cookies for security and performance purposes (e.g., bot detection).

I do not use tracking cookies, advertising cookies, or third-party analytics cookies.

See the full [Cookie Notice](./03-cookie-notice.md) for more details.

---

## Your Rights

You have the right to:

- **Access** the personal data I hold about you.
- **Correct** inaccurate personal data.
- **Delete** your account and associated personal data.

To exercise any of these rights, email privacy@twigloop.tech. I will respond within 30 days. See [Privacy Requests](./05-privacy-requests.md) for details on the process.

---

## Data Retention

- **Account data:** Kept while your account is active. Deleted within 30 days of a deletion request.
- **Project data:** Kept while the project exists on the platform.
- **Server logs:** Retained for 30 days, then deleted.
- **Backups:** 7-day rolling retention.

After account deletion, some anonymized aggregate data (such as total project counts) may remain, but it will not be linked to your identity.

---

## Children

Twig Loop is not directed at anyone under the age of 16. I do not knowingly collect personal data from children under 16. If you believe a child under 16 has provided personal data to Twig Loop, please contact me at privacy@twigloop.tech and I will delete it.

---

## International Data Transfers

Twig Loop's infrastructure is hosted in the United States via Railway. If you access the service from outside the US, your data will be transferred to and processed in the US. By using Twig Loop, you acknowledge this transfer.

---

## Changes to This Policy

I may update this privacy policy from time to time. Changes will be posted on this page with an updated "Last updated" date. For significant changes, I will make reasonable efforts to notify active users (e.g., via email or an in-app notice).

---

## Contact

For privacy-related questions or requests:

- **Email:** privacy@twigloop.tech
- **Mailing address:** Available upon request
