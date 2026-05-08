# euTnDB — Eukaryotic Transposon Database

A web platform for browsing, searching, classifying, and analyzing eukaryotic transposable elements with BLAST search and de novo TE mining.

## Features

- **Browse & Search** — full-text search and faceted filtering of transposon entries by family, status, and origin
- **Classification System** — hierarchical TE classification (class → subclass → order → superfamily → family → group)
- **BLAST Search** — submit DNA sequences against the TE database via NCBI BLAST+ with async job processing
- **MineTn** — de novo transposable element mining from uploaded genome assemblies
- **Data Export** — download entries in FASTA, EMBL, or JSON format
- **Excel Import** — bulk import TE entries from spreadsheet templates
- **Download Requests** — moderated data access workflow with email notification
- **Review Queue** — admin review pipeline for submitted entries
- **User Management** — role-based access control with admin dashboard
- **Statistics** — TE distribution by family, classification, and origin

## Tech Stack

| Layer | Technology |
|---|---|
| Backend API | FastAPI (Python 3.11+) with async SQLAlchemy 2.0 |
| Database | PostgreSQL 15 |
| Async Tasks | Celery with Redis broker |
| Frontend | Vue 3 + TypeScript + Element Plus + Pinia |
| Build | Vite |
| Containerization | Docker Compose (6 services: frontend, backend, worker, db, redis, backup) |
| CI | GitHub Actions |
| Testing | pytest (backend, 161 tests) + vitest (frontend, 10 tests) |

## Project Structure

```
euTnDB/
├── backend/
│   ├── app/
│   │   ├── api/v1/          # REST API routers (16 endpoints)
│   │   ├── core/            # Config, database, security, rate limiting
│   │   ├── models/          # SQLAlchemy ORM models (8 tables)
│   │   ├── schemas/         # Pydantic request/response schemas
│   │   ├── tasks/           # Celery async workers (BLAST, MineTn)
│   │   └── main.py          # FastAPI application entry point
│   ├── migrations/          # Alembic database migrations
│   └── tests/               # Backend test suite (17 files, 161 tests)
├── frontend/
│   ├── src/
│   │   ├── api/             # Axios API client modules
│   │   ├── router/          # Vue Router routes
│   │   ├── stores/          # Pinia state management
│   │   ├── types/           # TypeScript type definitions
│   │   └── views/           # Vue components (public + admin)
│   └── package.json
├── docker/                  # Docker Compose deployment configs
├── .github/workflows/       # CI pipeline
└── README.md
```

## Quick Start

### Docker (recommended)

```bash
cd docker
cp .env.docker.example .env.docker
# Edit .env.docker — set ADMIN_PASSWORD and SECRET_KEY
./deploy.sh
```

The site will be available at `http://localhost`.

### Manual Development

**Backend:**

```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your database/redis settings
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

**Frontend:**

```bash
cd frontend
npm install
npm run dev
```

The dev server runs at `http://localhost:3000`.

## API Endpoints

| Prefix | Description |
|---|---|
| `GET /health` | Health check |
| `POST /api/v1/auth/login` | Login (returns Bearer token + httpOnly cookie) |
| `POST /api/v1/auth/logout` | Logout (clears cookie) |
| `GET /api/v1/auth/me` | Current user info |
| `POST /api/v1/auth/change-password` | Change password (authed) |
| `GET /api/v1/tn` | List TE entries (paginated, filterable) |
| `GET /api/v1/tn/{name}` | TE entry detail |
| `POST /api/v1/tn` | Submit new TE entry |
| `PUT /api/v1/tn/{name}` | Update TE entry (admin) |
| `DELETE /api/v1/tn/{name}` | Delete TE entry (admin) |
| `GET /api/v1/search` | Full-text search |
| `GET /api/v1/classification` | Classification tree |
| `GET /api/v1/stats` | Public statistics |
| `POST /api/v1/analyze` | Sequence analysis |
| `GET /api/v1/export/{name}` | Export single entry (FASTA/EMBL/JSON) |
| `POST /api/v1/export/batch` | Batch export |
| `GET /api/v1/import/template` | Download Excel template (admin) |
| `POST /api/v1/import/excel` | Upload Excel import (admin) |
| `POST /api/v1/blast` | Submit BLAST job |
| `GET /api/v1/blast/{job_id}` | Get BLAST job status/results |
| `POST /api/v1/minetn` | Submit MineTn job |
| `GET /api/v1/minetn/{task_id}` | Get MineTn task status/results |
| `GET /api/v1/review/pending` | List pending review entries (admin) |
| `POST /api/v1/review/{name}` | Approve/reject entry (admin) |
| `GET /api/v1/review/history` | Review history (admin) |
| `POST /api/v1/download-request` | Submit download request |
| `GET /api/v1/download-request/pending` | Pending download requests (admin) |
| `GET /api/v1/download-request/history` | Download request history (admin) |
| `POST /api/v1/download-request/{id}/review` | Approve/reject download request (admin) |
| `GET /api/v1/admin/stats` | Admin dashboard stats |
| `GET /api/v1/admin/users` | List users (admin) |
| `POST /api/v1/admin/users` | Create user (admin) |
| `PUT /api/v1/admin/users/{id}` | Update user (admin) |
| `DELETE /api/v1/admin/users/{id}` | Delete user (admin) |
| `GET /api/v1/admin/settings` | System settings (admin) |
| `PUT /api/v1/admin/settings` | Update settings (admin) |

Interactive API docs: `http://localhost:8000/docs`

## Testing

```bash
# Backend (161 tests)
cd backend
pytest tests/ -v

# Frontend (10 tests)
cd frontend
npx vitest run
```
