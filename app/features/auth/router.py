from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token
from app.db.session import get_db
from app.features.accounts.dependencies import get_current_account
from app.features.accounts.models import Account, AccountRole, AccountStatus
from app.features.accounts.schemas import AuthUser, PasswordChangeRequest
from app.features.accounts.service import change_account_password, record_login, to_auth_user
from app.features.activity_logs.schemas import ActivityLogCreate
from app.features.activity_logs.service import create_activity_log, get_actor_role_label
from app.features.activity_logs.websocket import activity_log_manager
from app.features.auth.schemas import LoginRequest, LoginResponse
from app.features.auth.service import authenticate_account

router = APIRouter(prefix="/auth", tags=["auth"])


def is_login_scope_allowed(account: Account, login_scope: str) -> bool:
    if login_scope == "enterprise":
        return account.role == AccountRole.ENTERPRISE

    return account.role != AccountRole.ENTERPRISE


def get_auth_log_category(account: Account) -> str:
    if account.role == AccountRole.ADMIN:
        return "Admin Operation"
    if account.role == AccountRole.IT:
        return "IT Activity"
    if account.role == AccountRole.STAFF:
        return "Staff Operation"
    return "Enterprise Activity"


@router.post("/login", response_model=LoginResponse)
async def login(payload: LoginRequest, db: Annotated[AsyncSession, Depends(get_db)]) -> LoginResponse:
    account = await authenticate_account(db, payload.username, payload.password)
    if account is None or account.status != AccountStatus.ACTIVE or not is_login_scope_allowed(account, payload.loginScope):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password.")

    await record_login(db, account)
    await record_auth_log(
        db,
        category=get_auth_log_category(account),
        severity="Info",
        actor=account.display_name,
        actor_role=get_actor_role_label(account),
        action="Login",
        target=account.email,
        summary=f"{account.display_name} signed in to TANAW.",
        source_id=account.id,
    )
    token = create_access_token(account.id, {"role": account.role.value, "must_change_password": account.must_change_password})
    return LoginResponse(token=token, user=to_auth_user(account))


@router.get("/me", response_model=AuthUser)
async def me(account: Annotated[Account, Depends(get_current_account)]) -> AuthUser:
    return to_auth_user(account)


@router.post("/logout")
async def logout(
    account: Annotated[Account, Depends(get_current_account)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, str]:
    await record_auth_log(
        db,
        category=get_auth_log_category(account),
        severity="Info",
        actor=account.display_name,
        actor_role=get_actor_role_label(account),
        action="Logout",
        target=account.email,
        summary=f"{account.display_name} signed out of TANAW.",
        source_id=account.id,
    )
    return {"status": "ok"}


@router.post("/change-password", response_model=LoginResponse)
async def change_password(
    payload: PasswordChangeRequest,
    account: Annotated[Account, Depends(get_current_account)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> LoginResponse:
    changed = await change_account_password(db, account, payload.currentPassword, payload.newPassword)
    if not changed:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Current password is incorrect.")

    await record_auth_log(
        db,
        category=get_auth_log_category(account),
        severity="Success",
        actor=account.display_name,
        actor_role=get_actor_role_label(account),
        action="Password Changed",
        target=account.email,
        summary=f"{account.display_name} changed their account password.",
        source_id=account.id,
    )
    token = create_access_token(account.id, {"role": account.role.value, "must_change_password": False})
    return LoginResponse(token=token, user=to_auth_user(account))


async def record_auth_log(
    db: AsyncSession,
    *,
    category: str,
    severity: str,
    actor: str,
    actor_role: str,
    action: str,
    target: str,
    summary: str,
    source_id: str,
) -> None:
    log = await create_activity_log(
        db,
        ActivityLogCreate(
            category=category,  # type: ignore[arg-type]
            severity=severity,  # type: ignore[arg-type]
            actor=actor,
            actorRole=actor_role,  # type: ignore[arg-type]
            action=action,
            target=target,
            summary=summary,
            sourceId=source_id,
        ),
    )
    await activity_log_manager.broadcast(log)
