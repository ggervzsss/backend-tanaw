from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.features.accounts.dependencies import get_current_operational_account
from app.features.accounts.models import Account, AccountRole, AccountStatus

router = APIRouter(prefix="/operational", tags=["operational"])


@router.get("/lgu-accounts")
async def list_lgu_accounts(_: Annotated[Account, Depends(get_current_operational_account)]) -> list[dict]:
    return []


@router.get("/enterprise-accounts")
async def list_enterprise_accounts(_: Annotated[Account, Depends(get_current_operational_account)]) -> list[dict]:
    return []


@router.get("/map-enterprises")
async def list_map_enterprises(_: Annotated[Account, Depends(get_current_operational_account)]) -> list[dict]:
    return []


@router.get("/alerts")
async def list_alerts(_: Annotated[Account, Depends(get_current_operational_account)]) -> list[dict]:
    return []


@router.get("/system-activities")
async def list_system_activities(_: Annotated[Account, Depends(get_current_operational_account)]) -> list[dict]:
    return []


@router.get("/system-logs")
async def list_system_logs(_: Annotated[Account, Depends(get_current_operational_account)]) -> list[dict]:
    return []


@router.get("/reports/intake")
async def list_intake_reports(_: Annotated[Account, Depends(get_current_operational_account)]) -> list[dict]:
    return []


@router.get("/reports/final")
async def list_final_reports(_: Annotated[Account, Depends(get_current_operational_account)]) -> list[dict]:
    return []


@router.get("/reports/enterprises")
async def list_report_enterprises(
    _: Annotated[Account, Depends(get_current_operational_account)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[dict]:
    result = await db.scalars(
        select(Account)
        .where(Account.role == AccountRole.ENTERPRISE, Account.status == AccountStatus.ACTIVE)
        .order_by(Account.enterprise_name.asc(), Account.display_name.asc())
    )
    return [
        {
            "id": account.enterprise_id or account.id,
            "name": account.enterprise_name or account.display_name,
            "category": account.category or "Uncategorized",
            "barangay": account.barangay or "Unassigned",
            "complianceOwner": account.manager_name or account.email,
        }
        for account in result
    ]
