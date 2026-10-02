# CyberNews Feed API

A production-oriented full-stack cybersecurity news aggregator built for a Python Full Stack Developer portfolio. It ingests RSS/Atom feeds from security publications, normalizes and categorizes articles, deduplicates them in PostgreSQL, exposes a searchable REST API with FastAPI, and renders a responsive React feed.

## Architecture

```text
Security RSS / Atom feeds
        │
        ▼
Separate ingestion worker (APScheduler)
        │  fetch + normalize + classify + deduplicate
        ▼
PostgreSQL  ◄──── Alembic migrations
        │
        ▼
FastAPI REST API
        │
        ▼
React + Vite + Tailwind CSS
```

The worker is intentionally separate from the API process. Web dyno restarts or horizontal API scaling therefore do not create duplicate in-process schedulers.

## Features

- Five preconfigured cybersecurity sources: The Hacker News, BleepingComputer, Krebs on Security, SecurityWeek, and Schneier on Security.
- Async FastAPI + SQLAlchemy 2.x + PostgreSQL.
- RSS/Atom ingestion with `httpx`, retries, redirects, explicit timeouts, and feed validation.
- URL canonicalization strips common tracking parameters before deduplication.
- Secondary SHA-256 story fingerprint catches same-source/same-date headlines even if a publisher changes the URL.
- Many-to-many article categories with keyword-based starter classification.
- Search by title/summary, source filter, category filter, and bounded pagination.
- Request IDs, gzip responses, CORS allow-list, trusted-host middleware, and security headers.
- Liveness and database readiness probes.
- Alembic schema migration.
- Separate scheduler/worker process with `max_instances=1` and coalescing.
- Pytest API, ingestion, deduplication, and utility tests.
- React UI with debounced search, filters, loading/error/empty states, pagination, and source links.
- Docker Compose local stack and multi-stage frontend image.
- GitHub Actions backend/frontend CI.
- Render Blueprint for API + worker + PostgreSQL, plus Vercel config for the frontend.

## Repository structure

```text
cybernews-feed-api/
├── backend/
│   ├── alembic/
│   ├── app/
│   │   ├── api/routes/
│   │   ├── core/
│   │   ├── db/
│   │   ├── ingestion/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   ├── ingest_once.py
│   │   ├── main.py
│   │   ├── seed.py
│   │   └── worker.py
│   ├── tests/
│   ├── Dockerfile
│   └── pyproject.toml
├── frontend/
│   ├── src/
│   ├── Dockerfile
│   ├── nginx.conf
│   └── package.json
├── .github/workflows/ci.yml
├── docker-compose.yml
├── render.yaml
└── Makefile
```

## Quick start with Docker

Requirements: Docker + Docker Compose.

```bash
cp .env.example .env
docker compose up --build -d
```

On first boot the API container applies the Alembic migration. The worker seeds the source/category catalog, immediately performs one ingestion pass, then runs on the configured interval.

Open:

- Frontend: `http://localhost:4173`
- API: `http://localhost:8000`
- Swagger docs: `http://localhost:8000/docs`
- Liveness: `http://localhost:8000/api/v1/health/live`
- Readiness: `http://localhost:8000/api/v1/health/ready`

Inspect logs:

```bash
docker compose logs -f api worker
```

Stop the stack:

```bash
docker compose down
```

Use `docker compose down -v` only when you intentionally want to delete the PostgreSQL volume.

## Local development without Docker for app processes

Run PostgreSQL locally or via Docker, then create `backend/.env` or export the variables from `.env.example` with a localhost database hostname.

Backend:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -e '.[dev]'
alembic upgrade head
python -m app.seed
python -m app.ingest_once
uvicorn app.main:app --reload
```

Worker in another terminal:

```bash
cd backend
source .venv/bin/activate
python -m app.worker
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

For local Vite development, set `VITE_API_URL=http://localhost:8000/api/v1` if it is not already available in your environment.

## API

### `GET /api/v1/articles`

Query parameters:

| Parameter | Default | Notes |
|---|---:|---|
| `page` | `1` | Minimum 1 |
| `page_size` | `20` | 1–100 |
| `source` | — | Source slug, e.g. `bleepingcomputer` |
| `category` | — | Category slug, e.g. `ransomware` |
| `search` | — | 2–200 characters; searches title and summary |

Example:

```bash
curl 'http://localhost:8000/api/v1/articles?category=vulnerability&search=chrome&page=1&page_size=20'
```

### Other endpoints

```text
GET /api/v1/articles/{uuid}
GET /api/v1/sources
GET /api/v1/categories
GET /api/v1/health/live
GET /api/v1/health/ready
```

## Database model

`articles`

- UUID primary key
- source foreign key
- original URL and canonical URL, both unique
- SHA-256 content hash, unique
- title, summary, author, image URL
- published/fetched timestamps

`sources`

- source metadata and feed URL
- enable/disable flag
- last successful fetch timestamp
- last ingestion error retained internally for operations

`categories`

- normalized names/slugs
- many-to-many relationship through `article_categories`

## Deduplication strategy

1. Remove fragments and common analytics parameters from the URL.
2. Use the resulting canonical URL as the primary duplicate key.
3. Hash source + publication date + normalized title as an independent second unique key (with URL fallback for undated entries).
4. Perform a pre-insert existence check for efficiency.
5. Wrap each insert in a database savepoint so a race between workers cannot roll back previously inserted articles.

PostgreSQL unique constraints are the final source of truth; application checks are only an optimization.

## Ingestion reliability

Each source fetch uses redirects, an explicit User-Agent, timeout, and exponential retry for transport/time-out failures. One broken source is recorded and does not prevent the next source from being processed. The scheduler uses one job instance and coalesces missed runs.

RSS publishers occasionally change endpoints or block hosting-provider IP ranges. That is an operational source issue, not a database/API failure. Update the catalog in `backend/app/ingestion/catalog.py` or manage source rows directly if a publisher changes its feed.

## Testing

```bash
cd backend
pip install -e '.[dev]'
ruff check .
pytest -q
```

Tests use an isolated asynchronous SQLite database so CI does not require a PostgreSQL service. PostgreSQL remains the production datastore and Alembic migration target.

Frontend:

```bash
cd frontend
npm install
npm run lint
npm run build
```

## Environment variables

| Variable | Purpose |
|---|---|
| `APP_ENV` | `development`, `test`, `staging`, or `production` |
| `APP_DEBUG` | FastAPI/SQLAlchemy debug behavior |
| `DATABASE_URL` | Async SQLAlchemy database URL; plain hosted `postgresql://` URLs are normalized to asyncpg automatically |
| `CORS_ORIGINS` | Comma-separated frontend origins |
| `TRUSTED_HOSTS` | Comma-separated allowed Host headers |
| `DOCS_ENABLED` | Enable/disable Swagger and ReDoc |
| `INGESTION_INTERVAL_MINUTES` | Worker cadence |
| `INGESTION_HTTP_TIMEOUT_SECONDS` | Feed request timeout |
| `INGESTION_MAX_ENTRIES_PER_SOURCE` | Maximum entries parsed per run/source |
| `INGESTION_USER_AGENT` | User-Agent sent to feed publishers |
| `LOG_LEVEL` | Python logging level |
| `DB_POOL_SIZE` | Base SQLAlchemy PostgreSQL pool size per process |
| `DB_MAX_OVERFLOW` | Temporary extra PostgreSQL connections per process |
| `DB_POOL_TIMEOUT_SECONDS` | Connection checkout timeout |
| `VITE_API_URL` | Browser-visible API base URL at frontend build time |

Do not commit `.env` or production credentials.

## Production deployment

### Render backend + PostgreSQL

The included `render.yaml` defines a PostgreSQL database, web API, and background worker. Create a Render Blueprint from the repository, then set:

- `CORS_ORIGINS` to your deployed frontend origin, for example `https://your-app.vercel.app`.
- `TRUSTED_HOSTS` to the API hostname assigned by the platform (hostname only, without `https://` or a path).

Render runs `alembic upgrade head` as the API pre-deploy command before starting Uvicorn. The worker does not run migrations; it waits until the schema exists and then seeds/ingests.

### Vercel frontend

Import the repository and choose `frontend` as the root directory. Set:

```text
VITE_API_URL=https://YOUR_API_HOST/api/v1
```

Then redeploy so Vite embeds the production API URL.

### Alternative platforms

Railway/Fly.io/other container platforms can run the same images. Deploy three logical resources: PostgreSQL, API, and worker. Do not start the ingestion scheduler inside every API replica.

## Production hardening notes

For a portfolio deployment, this repository is intentionally public/read-only and does not include user accounts. Before turning it into a multi-user commercial service, consider adding:

- reverse-proxy/API-gateway rate limiting,
- centralized logs and metrics,
- Sentry/OpenTelemetry tracing,
- feed-source admin authentication,
- PostgreSQL full-text search or a dedicated search service at larger scale,
- Redis-backed caching,
- backup/restore testing and retention policy,
- dependency and container vulnerability scanning,
- publisher-specific ingestion adapters and terms/licensing review.

Only article metadata/short summaries are stored; the UI links readers to the original publisher rather than republishing full articles.

## Portfolio talking points

- Why the scheduler is a separate process instead of FastAPI startup code.
- Why URL checks alone are insufficient without database unique constraints.
- Why many-to-many categories are a better fit than a single `category` string.
- How `asyncpg` and SQLAlchemy async sessions work with FastAPI dependency injection.
- How readiness differs from liveness.
- How you would replace keyword classification with a rules engine or ML model.
- How you would scale ingestion with a queue and multiple workers while retaining idempotency.

## License

Use this project as a portfolio foundation. Verify each publisher's feed terms before operating it as a commercial aggregation service.
