from typing import Annotated

from fastapi import APIRouter, Depends

from app.features.accounts.dependencies import get_current_operational_account
from app.features.accounts.models import Account

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
async def list_report_enterprises(_: Annotated[Account, Depends(get_current_operational_account)]) -> list[dict]:
    return []
