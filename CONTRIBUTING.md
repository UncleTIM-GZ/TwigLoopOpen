# Contributing to Twig Loop

Thank you for your interest in contributing to Twig Loop.

## Development Setup

```bash
# Prerequisites
# - Python 3.12+
# - Node.js 20+
# - Docker & Docker Compose
# - uv (Python package manager)

# Start infrastructure
docker compose up -d

# Backend
cd apps/core-api
uvicorn app.main:app --reload

# Frontend
cd apps/web
npm install
npm run dev
```

## Development Workflow

1. Fork the repository
2. Create a feature branch from `main`
3. Make your changes
4. Run tests and lint
5. Submit a pull request

## Branch Naming

```
feat/<scope>-<description>    # New features
fix/<scope>-<description>     # Bug fixes
docs/<description>            # Documentation
refactor/<scope>-<description> # Refactoring
```

Scopes: `web`, `core-api`, `mcp-server`, `db`, `infra`, `skills`

## Testing Requirements

All contributions must pass:

```bash
# Backend tests (375+ tests)
cd apps/core-api
python -m pytest tests/ -q

# Lint
python -m ruff check app/

# Format
python -m ruff format --check app/

# Frontend
cd apps/web
npm run lint
npm run build
```

## Commit Messages

Use [Conventional Commits](https://www.conventionalcommits.org/):

```
feat(core-api): add pagination to task list endpoint
fix(web): correct profile form validation
docs: update installation guide
```

## Code Style

- **Python**: Ruff for linting and formatting. Follow existing Router → Service → Repository layering
- **TypeScript**: ESLint + Prettier. Follow existing hooks and component patterns
- **API responses**: Use `ApiResponse` envelope: `{ success, data, error, meta }`
- **Immutability**: Create new objects, never mutate existing ones

## Pull Request Guidelines

- Keep PRs focused on a single concern
- Include tests for new functionality
- Update documentation if behavior changes
- Ensure all CI checks pass
- Describe the "why" in the PR description

## Reporting Issues

- **Bugs**: Use the bug report template
- **Features**: Use the feature request template
- **Security**: See [SECURITY.md](SECURITY.md) — do NOT open public issues for vulnerabilities
