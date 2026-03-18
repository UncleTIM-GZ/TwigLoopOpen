# TwigLoopOpen

AI-native project collaboration platform. Structure ideas into actionable tasks, match collaborators, and track real progress.

> This is the open-source edition of [Twig Loop](https://github.com/UncleTIM-GZ/TwigLoopOpen). It contains a runnable subset of the platform for local development, learning, and contribution.

## What is Twig Loop?

Twig Loop helps people turn ideas and needs into structured, real collaboration:

- **Initiate** — Describe your project; the platform structures it into work packages and task cards
- **Match** — Collaborators browse projects, find matching roles, and apply
- **Collaborate** — Trial collaboration with clear goals and completion criteria
- **Verify** — Progress tracked through real signals (GitHub commits, code reviews), not self-reporting

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 14, TypeScript, Tailwind CSS, TanStack Query |
| Backend | FastAPI, Python 3.12+, SQLAlchemy 2.0 |
| Database | PostgreSQL 16, Redis 7 |
| Events | NATS JetStream |
| Workflows | Temporal |
| Analytics | ClickHouse |
| AI | MCP (Model Context Protocol) |
| Storage | MinIO (S3-compatible) |

## Quick Start

```bash
# Clone
git clone https://github.com/UncleTIM-GZ/TwigLoopOpen.git
cd TwigLoopOpen

# Copy environment variables
cp .env.example .env

# Start infrastructure
docker compose up -d

# Backend
cd apps/core-api
alembic upgrade head
uvicorn app.main:app --reload

# Frontend (new terminal)
cd apps/web
npm install
npm run dev
```

Open http://localhost:3000

## What's Included

| Feature | Status |
|---------|--------|
| User registration & authentication | Available |
| Project creation & structuring | Available |
| Work packages & task cards with EWU | Available |
| Collaboration applications & seats | Available |
| Verifiable credentials (VC) | Available |
| MCP Server | Available (stdio/SSE) |
| State machine & quota enforcement | Available |
| Admin API (read-only) | Available |

## What's NOT Included

| Feature | Status |
|---------|--------|
| GitHub source sync | WIP (webhook handler ready) |
| Temporal durable workflows | Code present, not enabled |
| ClickHouse analytics | Infrastructure ready, no consumers |
| Admin management UI | API-only |
| Production deployment configs | Not included |

## Work Units (v1)

- **EWU** (Effort Work Unit) — Base unit: `base_weight × avg(complexity, criticality, collaboration) × risk_multiplier`
- **RWU** (Reward Work Unit) — `EWU × 1.2` for recruitment projects
- **SWU** (Sponsor Work Unit) — `EWU × 1.0` (v1) for sponsored public-benefit projects

Details: [docs/ewu-rwu-swu.md](docs/ewu-rwu-swu.md)

## Project Types

| Type | Description |
|------|------------|
| General | Standard collaboration |
| Public Benefit | Open-source/social-good, mandatory human review |
| Recruitment | Hiring through real task trials |

## Documentation

| Document | Description |
|----------|------------|
| [Installation](docs/installation.md) | System requirements and setup |
| [Local Run Guide](docs/local-run.md) | Step-by-step local development |
| [Architecture](docs/architecture.md) | System overview |
| [Rules](docs/rules-overview.md) | Project types, states, quotas |
| [EWU/RWU/SWU](docs/ewu-rwu-swu.md) | Work unit rules |
| [Boundary](docs/public-boundary.md) | What's open, what's not |

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development workflow, testing, and submission guidelines.

## Security

See [SECURITY.md](SECURITY.md). **Do NOT open public issues for vulnerabilities.**

## License

[AGPL-3.0](LICENSE) — Modifications must remain open source, even when deployed as a hosted service.

<!-- webhook-test: 2026-03-18T05:00:30Z -->
<!-- signal-test: 1773810198 -->
<!-- live-signal: 1773811660 -->
<!-- signal-final: 1773812672 -->
<!-- final-signal: 1773812939 -->
<!-- mapped-signal: 1773813575 -->
