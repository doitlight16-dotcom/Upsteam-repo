# Appex Asset Suite -- backend

Async, multi-tenant backend built with FastAPI, following Clean Architecture:
API depends on Application, Application depends on Domain, and
Infrastructure implements interfaces (ports) that Application defines --
never the other way around.

## Layout

```
backend/app/
  core/            Config, logging, cross-cutting middleware. No business rules.
  domain/          Entities, value objects, domain exceptions. Zero framework imports.
  application/     Use cases + ports (interfaces). Depends on domain only.
  infrastructure/  Concrete adapters implementing application ports (DB, Telegram, AI module, cache).
  api/             FastAPI routers and Pydantic schemas -- the public HTTP contract.
ai-module/         Standalone placeholder service implementing the AI module HTTP contract.
```

## Running locally

```bash
cp backend/.env.example backend/.env
# edit backend/.env -- at minimum set JWT_SECRET_KEY and TELEGRAM_BOT_TOKEN

docker compose up --build
```

The API comes up at `http://localhost:8000`, docs at `http://localhost:8000/docs`,
health check at `http://localhost:8000/api/v1/health`.

## Running tests

```bash
cd backend
uv sync --all-groups
uv run pytest
uv run ruff check .
uv run mypy app
```

## Status

**Built (this step):** project scaffolding, layered package structure,
Pydantic Settings configuration, structured JSON logging, request-id
middleware, health-check endpoint, Dockerfiles, docker-compose for local
dev, CI pipeline, ai-module placeholder service.

**Not yet built (upcoming steps):**
- Domain entities (Tenant, Asset, User) and value objects
- Database layer: SQLAlchemy models, Alembic migrations, the
  `appex_app` / `appex_migrator` role split, and the Row-Level Security
  policies themselves
- Tenant-context middleware with `SET LOCAL app.tenant_id` transaction binding
- Telegram `initData` validator and the `TelegramBotProvider` port
  (shared-bot MVP implementation, with tenant resolved via WebApp launch
  parameter + verified `user_tenant_membership`, per the approved design)
- JWT issuance/verification (`core/security.py`)
- `AIModulePort` interface and its HTTP adapter calling the ai-module service
- Production docker-compose with Traefik + automatic TLS

See the architecture discussion in the project history for the full
reasoning behind these decisions, particularly the defense-in-depth
tenant isolation strategy and the provider-abstraction pattern used
consistently for tenancy, the AI module, and the Telegram bot.
