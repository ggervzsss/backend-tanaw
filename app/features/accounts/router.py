from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.features.accounts.dependencies import require_roles
from app.features.accounts.models import Account, AccountRole, AccountStatus
from app.features.accounts.schemas import (
    AccountStatusUpdate,
    AccountSummary,
    DeliverySummary,
    EnterpriseAccountCreate,
    LguAccountCreate,
)
from app.features.accounts.service import (
    account_role_from_value,
    create_account_with_temporary_password,
    generate_enterprise_id,
    get_account_by_email,
    get_account_by_id,
    get_dev_delivery_by_id,
    list_accounts_by_roles,
    list_dev_deliveries,
    reset_account_password,
    to_account_summary,
    to_delivery_summary,
)

router = APIRouter(prefix="/accounts", tags=["accounts"])
dev_router = APIRouter(prefix="/dev", tags=["dev"])

ITAccount = Annotated[Account, Depends(require_roles({"it"}))]


@router.get("/lgu", response_model=list[AccountSummary])
async def list_lgu_accounts(
    _: ITAccount,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[AccountSummary]:
    accounts = await list_accounts_by_roles(db, [AccountRole.IT, AccountRole.ADMIN, AccountRole.STAFF])
    return [to_account_summary(account) for account in accounts]


@router.post("/lgu", response_model=AccountSummary, status_code=status.HTTP_201_CREATED)
async def create_lgu_account(
    payload: LguAccountCreate,
    _: ITAccount,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> AccountSummary:
    existing = await get_account_by_email(db, str(payload.email))
    if existing is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="An account with this email already exists.")

    role = account_role_from_value(payload.role)
    title_by_role = {
        AccountRole.ADMIN: "Admin",
        AccountRole.IT: "IT Personnel",
        AccountRole.STAFF: "LGU Staff",
    }
    account = await create_account_with_temporary_password(
        db,
        email=str(payload.email),
        phone=payload.phone,
        role=role,
        display_name=f"{payload.firstName} {payload.lastName}",
        title=title_by_role[role],
        first_name=payload.firstName,
        last_name=payload.lastName,
    )
    return to_account_summary(account)


@router.get("/enterprises", response_model=list[AccountSummary])
async def list_enterprise_accounts(
    _: ITAccount,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[AccountSummary]:
    accounts = await list_accounts_by_roles(db, [AccountRole.ENTERPRISE])
    return [to_account_summary(account) for account in accounts]


@router.post("/enterprises", response_model=AccountSummary, status_code=status.HTTP_201_CREATED)
async def create_enterprise_account(
    payload: EnterpriseAccountCreate,
    _: ITAccount,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> AccountSummary:
    existing = await get_account_by_email(db, str(payload.email))
    if existing is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="An account with this email already exists.")

    enterprise_id = await generate_enterprise_id(db, payload.enterpriseId or payload.enterpriseName)
    account = await create_account_with_temporary_password(
        db,
        email=str(payload.email),
        phone=payload.contactNumber,
        role=AccountRole.ENTERPRISE,
        display_name=payload.enterpriseName,
        title="Enterprise Account",
        enterprise_name=payload.enterpriseName,
        category=payload.category,
        manager_name=payload.managerName,
        barangay=payload.barangay,
        address=payload.address,
        enterprise_id=enterprise_id,
        gateway_status="Not Linked",
    )
    return to_account_summary(account)


@router.post("/{account_id}/reset-password", response_model=AccountSummary)
async def reset_password(
    account_id: str,
    _: ITAccount,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> AccountSummary:
    account = await get_account_by_id(db, account_id)
    if account is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found.")
    return to_account_summary(await reset_account_password(db, account))


@router.patch("/{account_id}/status", response_model=AccountSummary)
async def update_account_status(
    account_id: str,
    payload: AccountStatusUpdate,
    _: ITAccount,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> AccountSummary:
    account = await get_account_by_id(db, account_id)
    if account is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found.")

    account.status = AccountStatus(payload.status)
    await db.commit()
    await db.refresh(account)
    return to_account_summary(account)


@dev_router.get("/deliveries", response_model=list[DeliverySummary])
async def get_dev_deliveries(
    _: ITAccount,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[DeliverySummary]:
    deliveries = await list_dev_deliveries(db)
    return [to_delivery_summary(delivery) for delivery in deliveries]


@dev_router.get("/deliveries/{delivery_id}", response_model=DeliverySummary)
async def get_dev_delivery(
    delivery_id: str,
    _: ITAccount,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> DeliverySummary:
    delivery = await get_dev_delivery_by_id(db, delivery_id)
    if delivery is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Delivery not found.")
    return to_delivery_summary(delivery)
