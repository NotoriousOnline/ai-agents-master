# AI Agents Master Repo

Production-grade monorepo for multiple AI agents: **Python 3.11+**, **FastAPI**, **Supabase/Postgres**, **Alembic**, **Poetry**.

## Features

- **FastAPI** API layer with health check and version endpoint
- **SQLAlchemy 2.0 (async)** + **Alembic** migrations targeting Postgres (local or Supabase)
- **Pydantic Settings** for configuration via environment variables
- **Agents** directory pattern: add new agents under `app/agents/<agent_name>/`
- **Docker Compose** for local Postgres (+ optional pgAdmin)
- **Ruff** + **Black** + **pre-commit** and **GitHub Actions** CI

## Requirements

- Python 3.11+
- [Poetry](https://python-poetry.org/docs/#installation)
- Docker & Docker Compose (optional, for local Postgres)

---

## Quick start (local)

### 1. Clone and install

```bash
git clone <your-repo-url>
cd ai-agents-master   # or your repo folder name
cp .env.example .env
poetry install
```

### 2. Start local Postgres (Docker)

```bash
docker compose up -d
```

This starts Postgres on `localhost:5432` and (optional) pgAdmin. Default DB: `ai_agents`, user: `postgres`, password: `postgres`.

### 3. Run migrations

```bash
poetry run alembic upgrade head
```

### 4. Run the API

```bash
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

- API: http://localhost:8000  
- Docs: http://localhost:8000/docs  
- Health: http://localhost:8000/health  
- Version: http://localhost:8000/version  
- DB connectivity: http://localhost:8000/db/ping  

---

## Database: Local vs Supabase

The app supports two modes. A single **resolver** picks the database:

- **If `SUPABASE_DB_URL` is set** → use Supabase (remote), with SSL.
- **Else** → use `LOCAL_DB_URL` (e.g. Docker Postgres).

You do **not** set `DATABASE_URL` yourself; it is resolved from the two URLs above.

### How to find the Supabase connection string

1. Open [Supabase](https://supabase.com) and select your project.
2. Go to **Project Settings** (gear) → **Database**.
3. Under **Connection string**, choose:
   - **URI** for a full URL.
   - **Transaction** (recommended) for pooled connections (port **6543**). Use **Session** only if you need session-mode pooling.
4. Copy the URI. It looks like:
   - `postgresql://postgres.[PROJECT-REF]:[YOUR-PASSWORD]@aws-0-[REGION].pooler.supabase.com:6543/postgres`
5. Replace `[YOUR-PASSWORD]` with your **database password** (from the same page, or set in **Database → Database password**).
6. For the **app** (async), use driver `postgresql+asyncpg://` instead of `postgresql://`:
   - `postgresql+asyncpg://postgres.[PROJECT-REF]:[YOUR-PASSWORD]@aws-0-[REGION].pooler.supabase.com:6543/postgres`
7. For **Alembic** (sync), use the same URI with `postgresql://` and add `?sslmode=require` if your client does not enable SSL by default:
   - `postgresql://postgres.[PROJECT-REF]:[YOUR-PASSWORD]@aws-0-[REGION].pooler.supabase.com:6543/postgres?sslmode=require`

### How to set env vars

In `.env` (never commit this file; copy from `.env.example`):

**Local only (Docker Postgres):**

```env
LOCAL_DB_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/ai_agents
ALEMBIC_LOCAL_DB_URL=postgresql://postgres:postgres@localhost:5432/ai_agents
# Leave SUPABASE_DB_URL and ALEMBIC_SUPABASE_DB_URL unset or commented out
```

**Supabase (remote):**

```env
LOCAL_DB_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/ai_agents
SUPABASE_DB_URL=postgresql+asyncpg://postgres.[ref]:YOUR_PASSWORD@aws-0-xx.pooler.supabase.com:6543/postgres

ALEMBIC_LOCAL_DB_URL=postgresql://postgres:postgres@localhost:5432/ai_agents
ALEMBIC_SUPABASE_DB_URL=postgresql://postgres.[ref]:YOUR_PASSWORD@aws-0-xx.pooler.supabase.com:6543/postgres?sslmode=require
```

The app and Alembic both use the **Supabase** URL when `SUPABASE_DB_URL` / `ALEMBIC_SUPABASE_DB_URL` are set; otherwise they use the Local URL. SSL is enabled automatically for Supabase connections.

### DB connectivity check: `GET /db/ping`

A lightweight connectivity check runs `SELECT 1` against the **resolved** database (Supabase or Local):

```bash
curl http://localhost:8000/db/ping
```

- **200** `{"status":"ok","database":"connected"}` — DB reachable.
- **503** — DB unreachable (wrong URL, network, or credentials).

Use this for readiness probes or to verify env vars and SSL.

### How to run migrations against Supabase safely

1. **Confirm target:** Ensure `.env` has the correct `ALEMBIC_SUPABASE_DB_URL` (and no typo in password). The resolver uses it if set; otherwise migrations run against `ALEMBIC_LOCAL_DB_URL`.
2. **Optional backup:** In Supabase Dashboard → **Database** → **Backups**, or use `pg_dump` with the same connection string.
3. **Run migrations:**
   ```bash
   poetry run alembic upgrade head
   ```
4. **Verify:** Call `GET /db/ping` or inspect tables in Supabase **Table Editor**.

To run migrations against **local** only, unset or comment out `ALEMBIC_SUPABASE_DB_URL` so the resolver falls back to `ALEMBIC_LOCAL_DB_URL`.

---

## Project structure

```
.
├── app/
│   ├── main.py              # FastAPI app entry
│   ├── config.py            # Pydantic settings
│   ├── api/
│   │   ├── db.py            # GET /db/ping connectivity check
│   │   ├── deps.py          # Shared dependencies (e.g. DB session)
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── router.py   # Aggregates v1 routes
│   │       └── health.py   # Health & version
│   ├── db/
│   │   ├── __init__.py
│   │   ├── base.py         # Declarative base
│   │   └── session.py      # Async session factory
│   └── agents/
│       ├── __init__.py
│       └── example/        # Example agent skeleton
│           ├── __init__.py
│           ├── router.py
│           └── service.py
├── alembic/
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
├── tests/
├── scripts/
├── docker-compose.yml
├── pyproject.toml
├── .env.example
├── Makefile
└── README.md
```

---

## Makefile / scripts

From repo root:

| Command | Description |
|--------|-------------|
| `make install` | `poetry install` |
| `make run` | Run API with uvicorn (reload) |
| `make migrate` | `alembic upgrade head` |
| `make migrate-new "name"` | Create new migration |
| `make test` | Run pytest |
| `make lint` | Ruff check |
| `make format` | Ruff + Black format |
| `make docker-up` | Start Postgres (and pgAdmin) |
| `make docker-down` | Stop containers |

---

## Development

- **Linting:** `make lint` or `poetry run ruff check app tests`
- **Formatting:** `make format` or `poetry run black app tests alembic`
- **Pre-commit:** `poetry run pre-commit install` then hooks run on commit
- **Tests:** `make test` or `poetry run pytest`

---

## License

MIT
