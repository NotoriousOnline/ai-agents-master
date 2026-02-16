# AI Agents Master Repo

Production-grade monorepo for building and running multiple AI agents: **Python 3.11+**, **FastAPI**, **Supabase/Postgres**, **OpenAI (ChatGPT)**, **Alembic**. Use **Poetry** or **pip + venv**.

## Features

- **FastAPI** API layer with health, version, and **homepage** at `/` (tools list + how to create agents)
- **SQLAlchemy 2.0 (async)** + **Alembic** migrations — Postgres via **Supabase** (recommended) or local Docker
- **Pydantic + pydantic-settings** for config; `.env` loaded from **project root** (works regardless of cwd)
- **ChatGPT (OpenAI)** — `app/tools/chatgpt.py`; call `chatgpt_complete(prompt)` from any agent (set `OPENAI_API_KEY` in `.env`)
- **Agents** pattern: add agents under `app/agents/<agent_name>/` (router, service, schemas); see `app/agents/example/`
- **Docker Compose** optional for local Postgres
- **Ruff**, **Black**, **pre-commit**, **pytest**

## Requirements

- Python 3.11+
- [Poetry](https://python-poetry.org/docs/#installation) (optional; you can use pip + venv)
- Docker & Docker Compose (optional, for local Postgres)

---

## Setting up Python

The project expects **Python 3.11+**. A `.python-version` file is included (used by pyenv and some IDEs).

### Option A: Setup script (recommended)

From the repo root:

**Windows (PowerShell):**
```powershell
.\scripts\setup.ps1
```
Then activate and run:
```powershell
.\.venv\Scripts\Activate.ps1
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**macOS / Linux:**
```bash
chmod +x scripts/setup.sh
./scripts/setup.sh
source .venv/bin/activate
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The script creates a `.venv`, installs from `requirements.txt`, and installs the app in editable mode.

### Option B: Manual

1. Install Python 3.11+ from [python.org](https://www.python.org/downloads/) (or `pyenv install 3.11`).
2. From the repo root:
   ```bash
   python -m venv .venv
   .venv\Scripts\Activate.ps1   # Windows
   # or: source .venv/bin/activate  # macOS/Linux
   pip install -r requirements.txt
   pip install -e .
   ```

### Option C: Poetry

If you use [Poetry](https://python-poetry.org/docs/#installation), run `poetry install` and then `poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`.

---

## Quick start

### 1. Clone and install

```bash
git clone <your-repo-url>
cd ai-agents-master
cp .env.example .env
# Edit .env: set SUPABASE_DB_URL (and OPENAI_API_KEY if using ChatGPT)
```

**With pip (no Poetry):**
```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1   # Windows
# or: source .venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
pip install -e .
```

**With Poetry:** `poetry install`

### 2. Database: Supabase (recommended) or local

- **Supabase only:** Set `SUPABASE_DB_URL` and `ALEMBIC_SUPABASE_DB_URL` in `.env` (see [Database: Supabase](#database-local-vs-supabase)). No Docker needed.
- **Local Postgres:** `docker compose up -d` (Postgres on `localhost:5432`, DB `ai_agents`).

### 3. Run migrations (if you have migrations)

```bash
poetry run alembic upgrade head
# or: .\.venv\Scripts\python.exe -m alembic upgrade head
```

### 4. Run the API

```bash
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
# or: .\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

| URL | Description |
|-----|-------------|
| http://localhost:8000 | Homepage (tools + how to create agents) |
| http://localhost:8000/docs | Swagger API docs |
| http://localhost:8000/health | Health check |
| http://localhost:8000/version | API version |
| http://localhost:8000/db/ping | Database connectivity |  

---

## Database: Local vs Supabase

The app supports two modes. A single **resolver** picks the database:

- **If `SUPABASE_DB_URL` is set** → use Supabase (remote), with SSL.
- **Else** → use `LOCAL_DB_URL` (e.g. Docker Postgres).

You do **not** set `DATABASE_URL` yourself; it is resolved from the two URLs above.

### How to find the Supabase connection string

1. Open [Supabase](https://supabase.com) and select your project.
2. Go to **Project Settings** (gear) → **Database** → **Connection string**.
3. Use the **pooler** (Transaction or Session) — the direct connection (`db.xxx.supabase.co:5432`) uses IPv6 and often fails with `getaddrinfo failed` on Windows/home networks.
4. Copy the URI (e.g. Transaction mode, port **6543**). It looks like:
   - `postgresql://postgres.[PROJECT-REF]:[YOUR-PASSWORD]@aws-1-[REGION].pooler.supabase.com:6543/postgres`  
   (host may be `aws-0-` or `aws-1-` depending on region.)
5. Replace `[YOUR-PASSWORD]` with your **database password**. If the password has `$`, `!`, `#`, etc., URL-encode them (`$` → `%24`, `!` → `%21`).
6. For the **app**, use **`postgresql+asyncpg://`** at the start (async driver).
7. For **Alembic**, use `postgresql://` and append `?sslmode=require`.

### How to set env vars

In `.env` (never commit this file; copy from `.env.example`):

**Local only (Docker Postgres):**

```env
LOCAL_DB_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/ai_agents
ALEMBIC_LOCAL_DB_URL=postgresql://postgres:postgres@localhost:5432/ai_agents
# Leave SUPABASE_DB_URL and ALEMBIC_SUPABASE_DB_URL unset or commented out
```

**Supabase only (recommended):**

```env
# Copy exact URI from Dashboard → Database → Connection string → Transaction (port 6543)
# User: postgres.PROJECT_REF. Password: URL-encode if it has $ ! # etc.
SUPABASE_DB_URL=postgresql+asyncpg://postgres.PROJECT_REF:PASSWORD@aws-1-REGION.pooler.supabase.com:6543/postgres
ALEMBIC_SUPABASE_DB_URL=postgresql://postgres.PROJECT_REF:PASSWORD@aws-1-REGION.pooler.supabase.com:6543/postgres?sslmode=require
```

**Local only (Docker):** set `LOCAL_DB_URL` and `ALEMBIC_LOCAL_DB_URL`; leave Supabase vars unset.

The app and Alembic use **Supabase** when `SUPABASE_DB_URL` / `ALEMBIC_SUPABASE_DB_URL` are set; otherwise they use local. SSL is handled automatically for Supabase (including certificate handling for the pooler).

### If Supabase DB is not connecting

1. **Variable name** — Set **`SUPABASE_DB_URL=...`** in `.env` (a raw URL with no variable name is ignored).
2. **Async driver** — Use **`postgresql+asyncpg://`** for the app (not `postgresql://`).
3. **URL-encode password** — Encode `#` `$` `!` `%` `@` in the password (e.g. `$` → `%24`, `!` → `%21`).
4. **`[Errno 11001] getaddrinfo failed`** — Direct host `db.xxx.supabase.co` often doesn’t resolve on Windows/home networks. Use the **pooler** URL from Dashboard (Transaction or Session); host will be `aws-0-REGION` or `aws-1-REGION.pooler.supabase.com` (copy the exact URI from Connect).
5. **`CERTIFICATE_VERIFY_FAILED`** — The app uses an SSL context that skips certificate verification for the DB connection; restart the app so it picks up the code. If it still fails, check for proxy/firewall.

`.env` is loaded from the **project root** (parent of `app/`). Restart the app after editing `.env`, then try `GET /db/ping`.

### DB connectivity check: `GET /db/ping`

A lightweight connectivity check runs `SELECT 1` against the **resolved** database (Supabase or Local):

```bash
curl http://localhost:8000/db/ping
```

- **200** `{"status":"ok","database":"connected"}` — DB reachable.
- **503** — DB unreachable (wrong URL, network, or credentials).

Use this for readiness probes or to verify env vars and SSL.

---

## OpenAI / ChatGPT

The app includes a **ChatGPT** tool for agents. Set **`OPENAI_API_KEY`** in `.env` (get a key from [platform.openai.com](https://platform.openai.com/api-keys)).

**Use in an agent:**
```python
from app.tools import chatgpt_complete

reply = await chatgpt_complete("Explain async Python in one sentence.")
# Optional: model="gpt-4o-mini" (default), max_tokens=1024
```

If the key is missing, `chatgpt_complete` returns a short “not configured” message instead of calling the API.

---

## Deploying on Railway

The repo includes **Railway** config so the app binds to Railway's `PORT` and starts correctly.

1. **Connect the repo** to Railway (GitHub or CLI). Railway will use **Nixpacks** and install from `requirements.txt`; the start command is set in `railway.json`:  
   `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

2. **Set environment variables** in the Railway service (Variables tab). There is no `.env` in the deployment; everything comes from Railway's env:
   - **Required for DB:** `SUPABASE_DB_URL` (async URL: `postgresql+asyncpg://...`) and `ALEMBIC_SUPABASE_DB_URL` (sync URL with `?sslmode=require`). Use the **pooler** URL (port 6543) to avoid `getaddrinfo` issues.
   - **Optional:** `OPENAI_API_KEY` (for ChatGPT), `SUPABASE_URL`, `SUPABASE_SERVICE_KEY`.

3. **Public URL:** In the service → **Networking** → **Generate Domain**.

4. If you see **"Application failed to respond"**, open the **Deploy** tab and check the **logs** for:
   - Crash on startup (e.g. missing `SUPABASE_DB_URL` or import error).
   - Wrong port: the start command must use `$PORT` (Railway injects it). The provided `railway.json` and `Procfile` already do this.

---

## Tools for building AI agents

| Tool | Where it helps |
|------|----------------|
| **FastAPI** | Expose agents as HTTP APIs; type-safe request/response |
| **ChatGPT (OpenAI)** | LLM “brain” for agents — `app/tools/chatgpt.py` |
| **Supabase / SQLAlchemy** | Persist agent runs, history, state |
| **Pydantic** | Request/response schemas and config |
| **HTTPX** | Call external APIs from agents (dev dependency) |

Add new agents under `app/agents/<name>/` with `router.py`, `service.py`, `schemas.py`; register the router in `app/api/v1/router.py`. Use `app/agents/example/` as a template.

---

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
│   ├── config.py            # Pydantic settings (.env from project root)
│   ├── api/
│   │   ├── db.py            # GET /db/ping
│   │   ├── deps.py          # get_db (async session)
│   │   └── v1/
│   │       ├── router.py   # Aggregates v1 routes
│   │       └── health.py
│   ├── db/
│   │   ├── base.py
│   │   └── session.py      # Lazy async engine (Supabase SSL handled)
│   ├── static/
│   │   └── index.html      # Homepage at /
│   ├── tools/
│   │   ├── __init__.py
│   │   └── chatgpt.py      # chatgpt_complete() for agents
│   └── agents/
│       ├── example/        # Example agent (router, service, schemas)
│       └── <name>/         # Add new agents here
├── alembic/
├── tests/
├── scripts/
│   ├── setup.ps1           # Windows: venv + pip install
│   └── setup.sh             # macOS/Linux: same
├── docker-compose.yml      # Optional local Postgres
├── pyproject.toml
├── requirements.txt        # pip install -r requirements.txt
├── .python-version         # 3.11
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

## Release tags

Releases are tagged in Git (e.g. `v0.1.0`). Create a tag: `git tag -a v0.1.0 -m "Release 0.1.0"` then `git push origin v0.1.0`. Do not force-push or move tags after release.

---

## License

MIT
