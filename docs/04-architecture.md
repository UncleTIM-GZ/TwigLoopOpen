# Architecture Overview

## System Diagram

```
Browser ──→ Next.js (web)
               │
               ▼
          Core API (FastAPI) ──→ PostgreSQL
               │                     ↑
               ├──→ Redis        Alembic migrations
               ├──→ NATS JetStream
               │
MCP Clients ──→ MCP Server ──→ Core API
                    │
               AI Assist Service (suggestions only, never writes to DB)
```

## Service Boundaries

| Service | Role | Database Access |
|---------|------|----------------|
| **core-api** | Single source of truth for all transactional writes | Direct (SQLAlchemy) |
| **web** | Next.js frontend, consumes core-api | None (API only) |
| **mcp-server** | Standard MCP protocol server for LLM interaction | Via core-api HTTP |
| **source-sync-worker** | GitHub webhook processing, progress signals | Direct (isolated) |

## Key Invariants

1. **core-api** is the only write path to PostgreSQL from web/MCP
2. **ai-assist-service** outputs are never written directly to the database
3. **source-sync-worker** stays decoupled from core-api
4. Account (authentication) and Actor (business identity) are separate entities

## Layering (Backend)

```
Router (API endpoints)
  → Service (business logic)
    → Repository (data access)
      → Domain (pure calculation: EWU, state machine, quotas)
```

## Data Model

Core chain: **Project → WorkPackage → TaskCard**

Work units: Every task has `EWU`. Recruitment tasks add `RWU`, sponsored public-benefit tasks add `SWU`.

Six roles: `founder`, `collaborator`, `reviewer`, `sponsor`, `operator`, `admin`

## Events

- **NATS JetStream**: Inter-service events using `domain.entity.action` naming
- Consumers must be idempotent
- Current limitation: events published before DB commit (outbox pattern planned)
