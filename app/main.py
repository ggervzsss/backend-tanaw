from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import get_settings
from app.db.base import Base
from app.db.session import AsyncSessionLocal, engine
from app.features.accounts.seed import seed_default_it_account


async def ensure_account_onboarding_schema(connection) -> None:
    statements = [
        "ALTER TABLE accounts ADD COLUMN IF NOT EXISTS phone VARCHAR(40)",
        "ALTER TABLE accounts ADD COLUMN IF NOT EXISTS first_name VARCHAR(60)",
        "ALTER TABLE accounts ADD COLUMN IF NOT EXISTS last_name VARCHAR(60)",
        "ALTER TABLE accounts ADD COLUMN IF NOT EXISTS enterprise_name VARCHAR(120)",
        "ALTER TABLE accounts ADD COLUMN IF NOT EXISTS category VARCHAR(120)",
        "ALTER TABLE accounts ADD COLUMN IF NOT EXISTS manager_name VARCHAR(120)",
        "ALTER TABLE accounts ADD COLUMN IF NOT EXISTS barangay VARCHAR(120)",
        "ALTER TABLE accounts ADD COLUMN IF NOT EXISTS address VARCHAR(255)",
        "ALTER TABLE accounts ADD COLUMN IF NOT EXISTS latitude DOUBLE PRECISION",
        "ALTER TABLE accounts ADD COLUMN IF NOT EXISTS longitude DOUBLE PRECISION",
        "ALTER TABLE accounts ADD COLUMN IF NOT EXISTS location_source VARCHAR(40)",
        "ALTER TABLE accounts ADD COLUMN IF NOT EXISTS location_confidence DOUBLE PRECISION",
        "ALTER TABLE accounts ADD COLUMN IF NOT EXISTS geocoded_address VARCHAR(500)",
        "ALTER TABLE accounts ADD COLUMN IF NOT EXISTS location_updated_at TIMESTAMP WITH TIME ZONE",
        "ALTER TABLE accounts ADD COLUMN IF NOT EXISTS enterprise_id VARCHAR(120)",
        "ALTER TABLE accounts ADD COLUMN IF NOT EXISTS gateway_id VARCHAR(120)",
        "ALTER TABLE accounts ADD COLUMN IF NOT EXISTS gateway_status VARCHAR(40)",
        "ALTER TABLE accounts ADD COLUMN IF NOT EXISTS must_change_password BOOLEAN NOT NULL DEFAULT false",
        "ALTER TABLE accounts ADD COLUMN IF NOT EXISTS temporary_password_created_at TIMESTAMP WITH TIME ZONE",
        "ALTER TABLE accounts ADD COLUMN IF NOT EXISTS temporary_password_expires_at TIMESTAMP WITH TIME ZONE",
        "ALTER TABLE accounts ADD COLUMN IF NOT EXISTS password_changed_at TIMESTAMP WITH TIME ZONE",
        "ALTER TABLE accounts ADD COLUMN IF NOT EXISTS token_invalid_before TIMESTAMP WITH TIME ZONE",
    ]
    for statement in statements:
        await connection.exec_driver_sql(statement)
    await connection.exec_driver_sql("CREATE UNIQUE INDEX IF NOT EXISTS ix_accounts_enterprise_id ON accounts (enterprise_id)")
    await connection.exec_driver_sql(
        """
        CREATE TABLE IF NOT EXISTS activity_logs (
            id VARCHAR(36) PRIMARY KEY,
            timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
            category VARCHAR(40) NOT NULL,
            severity VARCHAR(20) NOT NULL,
            actor VARCHAR(120) NOT NULL,
            actor_role VARCHAR(40) NOT NULL,
            action VARCHAR(120) NOT NULL,
            target VARCHAR(255) NOT NULL,
            summary TEXT NOT NULL,
            source_id VARCHAR(120),
            metadata_json TEXT
        )
        """,
    )
    await connection.exec_driver_sql("CREATE INDEX IF NOT EXISTS ix_activity_logs_category ON activity_logs (category)")
    await connection.exec_driver_sql("CREATE INDEX IF NOT EXISTS ix_activity_logs_actor_role ON activity_logs (actor_role)")


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
        await ensure_account_onboarding_schema(connection)

    async with AsyncSessionLocal() as session:
        await seed_default_it_account(session)

    yield


settings = get_settings()
app = FastAPI(title=settings.app_name, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
