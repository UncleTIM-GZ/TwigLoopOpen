# Twig Loop

AI-native project collaboration platform. Structure ideas into actionable tasks, match collaborators, and track real progress.

## What is Twig Loop?

Twig Loop helps people turn ideas and needs into structured, real collaboration:

- **Initiate** — Describe your project, the platform structures it into work packages and task cards
- **Match** — Collaborators browse projects, find matching roles, and apply
- **Collaborate** — Trial collaboration starts with clear goals and completion criteria
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
| AI Integration | MCP (Model Context Protocol) |
| Storage | MinIO (S3-compatible) |

## Quick Start

```bash
# Clone
git clone https://github.com/UncleTIM-GZ/TwigLoop.git
cd TwigLoop

# Start infrastructure
docker compose up -d

# Backend
cd apps/core-api
cp ../../.env.example .env  # adjust if needed
alembic upgrade head
uvicorn app.main:app --reload

# Frontend (new terminal)
cd apps/web
npm install
npm run dev
```

Open http://localhost:3000

## Project Types

| Type | Description | Work Units |
|------|------------|------------|
| General | Standard collaboration projects | EWU |
| Public Benefit | Open-source / social-good, requires human review | EWU + SWU |
| Recruitment | Hiring through real task trials | EWU + RWU |

## Work Units (v1)

- **EWU** (Effort Work Unit) — Base unit measuring task complexity
- **RWU** (Reward Work Unit) — EWU × 1.2, for recruitment projects
- **SWU** (Sponsor Work Unit) — EWU × 1.0 (v1), for sponsored public-benefit projects

Rules: [docs/ewu-rwu-swu-rules.md](docs/ewu-rwu-swu-rules.md)

## Documentation

| Document | Description |
|----------|------------|
| [Installation](docs/public-repo/02-installation.md) | System requirements and setup |
| [Local Run Guide](docs/public-repo/03-local-run.md) | Step-by-step local development |
| [Architecture](docs/public-repo/04-architecture.md) | System architecture overview |
| [Rules Overview](docs/public-repo/05-rules-overview.md) | Project types, states, quotas |
| [EWU/RWU/SWU](docs/ewu-rwu-swu-rules.md) | Work unit calculation rules |
| [Contributing](CONTRIBUTING.md) | How to contribute |

## Current Status: Public Beta

Twig Loop is in **Public Beta**. Core features are operational:

- User registration and authentication
- Project creation and structuring
- Work packages and task cards with EWU
- Collaboration applications and seats
- Verifiable credentials (VC) for completed work
- MCP Server for AI-assisted interaction

**Not yet available:**
- GitHub source sync (webhook handler ready, worker WIP)
- Temporal durable workflows (code ready, not enabled)
- ClickHouse analytics (infrastructure ready, no consumers)
- Admin management UI (API-only)

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development workflow, testing requirements, and submission guidelines.

## License

[AGPL-3.0](LICENSE)
