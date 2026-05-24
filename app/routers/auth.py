from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_account
from app.models import Account, AccountStatus
from app.schemas import AuthUser, LoginRequest, LoginResponse
from app.security import create_access_token, verify_password

router = APIRouter(prefix="/auth", tags=["auth"])


def to_auth_user(account: Account) -> AuthUser:
    return AuthUser(
        id=account.id,
        email=account.email,
        displayName=account.display_name,
        role=account.role.value,
        title=account.title,
    )


@router.post("/login", response_model=LoginResponse)
async def login(payload: LoginRequest, db: Annotated[AsyncSession, Depends(get_db)]) -> LoginResponse:
    account = await db.scalar(select(Account).where(Account.email == payload.username.lower()))
    if account is None or account.status != AccountStatus.ACTIVE or not verify_password(payload.password, account.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password.")

    account.last_login_at = datetime.now(UTC)
    await db.commit()

    token = create_access_token(account.id, {"role": account.role.value})
    return LoginResponse(token=token, user=to_auth_user(account))


@router.get("/me", response_model=AuthUser)
async def me(account: Annotated[Account, Depends(get_current_account)]) -> AuthUser:
    return to_auth_user(account)
