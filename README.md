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
