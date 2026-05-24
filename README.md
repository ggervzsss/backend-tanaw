# TANAW Backend

FastAPI backend for TANAW authentication and operational APIs.

## Local PostgreSQL Setup

1. Create a local PostgreSQL database named `tanaw_local` in pgAdmin or psql.
2. Copy `.env.example` to `.env`.
3. Update `DATABASE_URL` if your local PostgreSQL username, password, host, port, or database name differs.
4. Start the API:

```bash
uvicorn main:app --reload
```

On startup, the API creates the current tables if needed and seeds the default IT account when it does not already exist:

- Username: `default@email.tanaw`
- Password: `default`

Change the default password before using the system beyond local bootstrap.

## Backend Structure

The backend is organized by shared infrastructure and feature domains:

```text
app/
  api/                 # Top-level API router composition
  core/                # Settings, security, and app-wide utilities
  db/                  # SQLAlchemy base, engine, sessions, metadata imports
  features/
    accounts/          # Account model, current-user dependency, seeding, account services
    auth/              # Login routes, auth schemas, authentication service
    operational/       # Data API placeholders for TANAW operational modules
```

Keep backend work focused on persisted data, authentication, and API workflows. Desktop-specific ML processing, including future YOLOv8 work, should stay in the desktop application and only send resulting records or events to this backend when backend integration is added.
