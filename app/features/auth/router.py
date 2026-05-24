from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token
from app.db.session import get_db
from app.features.accounts.dependencies import get_current_account
from app.features.accounts.models import Account, AccountStatus
from app.features.accounts.schemas import AuthUser
from app.features.accounts.service import record_login, to_auth_user
from app.features.auth.schemas import LoginRequest, LoginResponse
from app.features.auth.service import authenticate_account

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponse)
async def login(payload: LoginRequest, db: Annotated[AsyncSession, Depends(get_db)]) -> LoginResponse:
    account = await authenticate_account(db, payload.username, payload.password)
    if account is None or account.status != AccountStatus.ACTIVE:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password.")

    await record_login(db, account)
    token = create_access_token(account.id, {"role": account.role.value})
    return LoginResponse(token=token, user=to_auth_user(account))


@router.get("/me", response_model=AuthUser)
async def me(account: Annotated[Account, Depends(get_current_account)]) -> AuthUser:
    return to_auth_user(account)
