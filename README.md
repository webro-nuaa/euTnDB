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
| Testing | pytest (backend, 172 tests) + vitest (frontend, 10 tests) |

## Project Structure

```
euTnDB/
├── backend/app/             # FastAPI (api, core, models, schemas, tasks)
├── frontend/src/            # Vue 3 + TypeScript + Element Plus
├── docker/                  # Docker deployment (compose, nginx, Dockerfiles)
└── .github/workflows/       # CI pipeline
```

## Quick Start

```bash
cd docker
cp .env.docker.example .env.docker
# Edit .env.docker — set ADMIN_PASSWORD and SECRET_KEY
./deploy.sh
```

The site is available at `http://localhost`, API docs at `http://localhost/docs`.

## API

Full interactive docs at `http://localhost/docs` after deployment.

| Prefix | Description |
|---|---|
| `/auth` | Login, logout, user info, password change |
| `/tn` | CRUD for TE entries, public browse & search |
| `/blast` | BLAST search jobs |
| `/minetn` | De novo TE mining jobs |
| `/review` | Admin review queue |
| `/export` | FASTA / EMBL export |
| `/download-request` | Moderated data access with email |
| `/import` | Excel bulk import |
| `/analyze` | Sequence analysis (TIR, TSD, ORF prediction) |
| `/admin/users`, `/admin/settings` | Admin dashboard |

## Testing

```bash
# Backend (172 tests)
cd backend
pytest tests/ -v

# Frontend (10 tests)
cd frontend
npx vitest run
```
