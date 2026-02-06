# Student Telegram Bot

A small project that provides a Telegram-based interface and a web frontend to manage student information and interact with students. The repository contains a FastAPI backend and a Vue 3 + Vite frontend. MongoDB is used as the primary datastore.

## Features
- REST API for student and user management (CRUD)
- Authentication (JWT)
- Excel import/export support for student data
- Web frontend built with Vue 3, Pinia and Vuetify
- Docker Compose for local development (MongoDB, backend, frontend)

## Tech stack
- Backend: Python, FastAPI, Uvicorn
- Database: MongoDB (pymongo)
- Frontend: Vue 3, Vite, Pinia, Vuetify
- Dev tools: Docker, Docker Compose

## Repo layout

- `backend/` - FastAPI application and backend code
	- `requirement.txt` - Python requirements
	- `run_backend.py` - Uvicorn launcher
	- `app/` - application package (models, schemas, crud, main)
- `frontend/` - Vue 3 + Vite frontend
- `docker-compose.yaml` - Compose file to start MongoDB, backend and frontend

## Quickstart - Docker (recommended)
1. Ensure Docker and Docker Compose are installed.
2. From the repository root, run:

```bash
docker compose up --build
```

This will start:
- MongoDB on port `27017`
- Backend (FastAPI + Uvicorn) on port `8000`
- Frontend (Vite) on port `5173`

Open the frontend at: http://localhost:5173
Open the API docs (FastAPI) at: http://localhost:8000/docs

## Local development (without Docker)

Backend:

1. Create and activate a virtual environment (example shown for Windows PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r backend/requirement.txt
```

2. Start the backend from the repository root:

```bash
python backend/run_backend.py
```

The backend serves OpenAPI docs at `/docs` (e.g. http://localhost:8000/docs).

Environment variables:
- `MONGODB_URL` - MongoDB connection string (default used by `docker-compose` is `mongodb://mongodb:27017`).
Place any required vars into a `.env` file if used by the backend.

Frontend:

1. Install dependencies and run dev server:

```bash
cd frontend
npm install
npm run dev
```

2. The frontend dev server runs at http://localhost:5173 by default.

## Notes on implementation
- Backend dependencies are listed in `backend/requirement.txt` and include `fastapi`, `uvicorn`, `pymongo`, JWT and helper libraries.
- The backend entrypoint is `backend/run_backend.py` which runs `app.main:app` with Uvicorn.
- Frontend is configured with Vite and uses Vue 3, Pinia for state and Vuetify for UI.
- The `docker-compose.yaml` provided wires MongoDB, backend and frontend together for a simple local stack.

## Contributing
- Fork the repo and submit pull requests for fixes or features.
- Open an issue to discuss larger changes before implementing.

## License
Add a license file if you intend to open-source this project.

---
If you want, I can also:
- run the app locally using Docker Compose and report any startup errors,
- add a short `.env.example` with environment variables, or
- expand API documentation with endpoint examples.


