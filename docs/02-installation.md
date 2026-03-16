# Installation Guide

## System Requirements

| Component | Version |
|-----------|---------|
| Python | 3.12+ |
| Node.js | 20+ |
| Docker | 24+ |
| Docker Compose | 2.20+ |
| uv | 0.4+ (Python package manager) |

## Infrastructure Services

Docker Compose provides:
- PostgreSQL 16
- Redis 7
- NATS 2.10 (JetStream)
- Temporal 1.25
- ClickHouse 24.8
- MinIO (S3-compatible storage)

## Setup Steps

### 1. Clone the Repository

```bash
git clone https://github.com/UncleTIM-GZ/TwigLoop.git
cd TwigLoop
```

### 2. Environment Variables

```bash
cp .env.example .env
```

Edit `.env` as needed. Default values work for local development.

Key variables:
```
DATABASE_URL=postgresql+asyncpg://twigloop:twigloop@localhost:5432/twigloop
REDIS_URL=redis://localhost:6379/0
NATS_URL=nats://localhost:4222
JWT_SECRET=<your-secret-at-least-32-chars>
CORS_ORIGINS=http://localhost:3000
```

### 3. Start Infrastructure

```bash
docker compose up -d
```

Verify all services are healthy:
```bash
docker compose ps
```

### 4. Backend Setup

```bash
cd apps/core-api

# Install Python dependencies
uv sync

# Run database migrations
alembic upgrade head

# Start the API server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 5. Frontend Setup

```bash
cd apps/web

# Install Node dependencies
npm install

# Start the dev server
npm run dev
```

### 6. Verify

- Frontend: http://localhost:3000
- API docs: http://localhost:8000/docs
- NATS monitoring: http://localhost:8222
- Temporal UI: http://localhost:8233
